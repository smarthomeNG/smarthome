#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2026-       Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
Assembles modules/admin/openapi.yaml from the ApiDoc metadata attached
directly to the exposed REST methods in modules/admin/api_*.py.

This replaces the old, hand-maintained modules/admin/api.raml, which went
stale because nothing forced it to change alongside the code it described.
The fix isn't a different file format - it's that the metadata now lives in
the same few lines as the route it documents (see modules/admin/rest.py's
ApiDoc/ApiParam), so a route change and its doc change are far more likely
to land in the same diff. This script only assembles what's already there;
it does not invent or infer anything.

The procedure is as follows:
1) statically import modules.admin (its __init__.py already does
   `from .api_X import *` for every controller - no live SmartHomeNG
   instance is started, no shng config is read)
2) walk every RESTResource subclass reachable from that namespace and every
   method defined directly on it
3) collect each method's `.api_doc` list (an ApiDoc per operation the
   method serves - some methods internally dispatch several distinct
   sub-resources by an `id`/`action` parameter and therefore document more
   than one operation)
4) assemble an OpenAPI 3.0 document and write it to
   modules/admin/openapi.yaml

modules/admin/openapi.yaml is generated, not hand-edited - same convention
as requirements/*.txt (see lib/shpypi.py).
"""

import inspect
import os
import sys

sh_basedir = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.insert(0, sh_basedir)

from ruamel.yaml import YAML

import bin.shngversion
import modules.admin as admin_pkg
from modules.admin.rest import RESTResource

VERSION = bin.shngversion.get_shng_version()

OUTPUT_FILE = os.path.join(sh_basedir, 'modules', 'admin', 'openapi.yaml')


def collect_operations():
    """
    Walk every RESTResource subclass reachable from modules.admin and
    gather every method's .api_doc entries.

    :return: list of (ApiDoc, controller class name, method name)
    :rtype: list
    """
    operations = []
    seen = {}
    for name in dir(admin_pkg):
        obj = getattr(admin_pkg, name)
        if not (inspect.isclass(obj) and issubclass(obj, RESTResource) and obj is not RESTResource):
            continue
        for method_name, method in vars(obj).items():
            api_doc = getattr(method, 'api_doc', None)
            if not api_doc:
                continue
            for doc in api_doc:
                key = (doc.method.lower(), doc.path)
                origin = f'{name}.{method_name}'
                if key in seen:
                    print(
                        f'WARNING: {origin} redeclares {doc.method.upper()} {doc.path}, '
                        f'already documented by {seen[key]} - check for a copy-paste path typo.',
                        file=sys.stderr,
                    )
                seen[key] = origin
                operations.append((doc, name, method_name))
    return operations


def param_to_openapi(param):
    """
    Convert one ApiParam into an OpenAPI parameter object.

    :type param: modules.admin.rest.ApiParam
    :rtype: dict
    """
    schema = {'type': param.type}
    if param.enum:
        schema['enum'] = list(param.enum)
    if param.default is not None:
        schema['default'] = param.default

    entry = {
        'name': param.name,
        'in': param.location,
        # OpenAPI requires path parameters to always be required, regardless
        # of what the annotation says.
        'required': True if param.location == 'path' else param.required,
        'schema': schema,
    }
    if param.description:
        entry['description'] = param.description
    return entry


def operation_to_openapi(doc):
    """
    Convert one ApiDoc into an OpenAPI operation object.

    :type doc: modules.admin.rest.ApiDoc
    :rtype: dict
    """
    op = {'summary': doc.summary}
    if doc.tags:
        op['tags'] = list(doc.tags)
    if doc.description:
        op['description'] = doc.description
    if doc.deprecated:
        op['deprecated'] = True
    op['security'] = [{'JWT': []}] if doc.auth else []

    if doc.params:
        op['parameters'] = [param_to_openapi(p) for p in doc.params]

    if doc.request_body:
        content_type = doc.request_body
        content_body = {'schema': {'type': 'object'}}
        if doc.request_example:
            content_body['example'] = doc.request_example
        op['requestBody'] = {'content': {content_type: content_body}}

    response = {'description': 'OK'}
    if doc.response_example:
        response['content'] = {'application/json': {'example': doc.response_example}}
    op['responses'] = {'200': response}

    return op


def build_spec(operations):
    """
    Assemble the full OpenAPI document from the collected operations.

    :type operations: list
    :rtype: dict
    """
    paths = {}
    for doc, cls_name, method_name in operations:
        path_item = paths.setdefault(doc.path, {})
        path_item[doc.method.lower()] = operation_to_openapi(doc)

    return {
        'openapi': '3.0.3',
        'info': {
            'title': 'SmartHomeNG Admin REST API',
            # Tracks the REST API contract itself (bump on breaking changes to it),
            # not the shng build - that goes in x-generated-from below instead.
            'version': '1.0.0',
            'description': (
                'Generated by tools/build_openapi.py from ApiDoc metadata attached directly to '
                'the route handlers in modules/admin/api_*.py - do not hand-edit this file, run '
                'the generator instead. See modules/admin/rest.py for the annotation format '
                '(ApiDoc/ApiParam) and modules/admin/README.md for the consumer-facing overview.'
            ),
            'x-generated-from': VERSION,
        },
        'servers': [{'url': '/api', 'description': 'Relative to the SmartHomeNG http module root'}],
        'components': {
            'securitySchemes': {
                'JWT': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT',
                    'description': 'Authorization: Bearer <token>, obtained from POST /authenticate/user',
                }
            }
        },
        'paths': dict(sorted(paths.items())),
    }


def main():
    operations = collect_operations()
    spec = build_spec(operations)

    # Round-trip mode (not 'safe') because it preserves dict insertion order -
    # 'safe' mode alphabetizes keys, which scrambles the natural
    # openapi/info/servers/components/paths reading order.
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    yaml.width = 100

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('# Generated by tools/build_openapi.py - do not hand-edit, run the generator instead.\n')
        yaml.dump(spec, f)

    print(f'File {OUTPUT_FILE} created ({len(operations)} operations across {len(spec["paths"])} paths).')


if __name__ == '__main__':
    main()
