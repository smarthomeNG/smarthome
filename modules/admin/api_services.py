#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2018-      Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG.
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
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################


import os
import datetime
import logging
import collections
import json
import cherrypy

from lib.item import Items
from .rest import RESTResource

import bin.shngversion
from lib.item_conversion import convert_yaml as convert_yaml
from lib.item_conversion import parse_for_convert as parse_for_convert
from lib.shtime import Shtime


# ======================================================================
#  Controller for REST API /api/services
#
class ServicesController(RESTResource):
    """
    Controller for REST API /api/services
    """

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__)

        self.etc_dir = self._sh._etc_dir
        self.modules_dir = os.path.join(self.base_dir, 'modules')
        return


    def get_body(self, text=False):
        """
        Get content body of received request header

        :return:
        """
        cl = cherrypy.request.headers.get('Content-Length', 0)
        if cl == 0:
            # cherrypy.reponse.headers["Status"] = "400"
            # return 'Bad request'
            raise cherrypy.HTTPError(status=411)
        rawbody = cherrypy.request.body.read(int(cl))
        self.logger.debug("ServicesController(): get_body(): rawbody = {}".format(rawbody))
        try:
            if text:
                params = rawbody.decode('utf-8')
            else:
                params = json.loads(rawbody.decode('utf-8'))
        except Exception as e:
            self.logger.warning("ServicesController(): get_body(): Exception {}".format(e))
            return None
        return params


    def strip_empty_lines(self, txt):
        """
        Remove \\r from text and remove exessive empty lines from end
        """
        txt = txt.replace('\r', '').rstrip()
        while txt.endswith('\n'):
            txt = txt[:-1].rstrip()
        txt += '\n\n'
        #        self.logger.warning("strip_empty_lines: txt = {}".format(txt))
        return txt


    # ======================================================================
    #  eval_syntax_checker
    #
    def eval_syntax_checker(self, eval_code, relative_to):
        expanded_code = ''

        # set up environment for calculating eval-expression
        sh = self._sh
        shtime = Shtime.get_instance()
        items = Items.get_instance()
        import math
        import lib.userfunctions as uf


        eval_code = eval_code.replace('\r', '').replace('\n', ' ').replace('  ', ' ').strip()
        if relative_to == '':
            expanded_code = eval_code
        else:
            rel_to_item = items.return_item(relative_to)
            if rel_to_item is not None:
                expanded_code = rel_to_item.get_stringwithabsolutepathes(eval_code, 'sh.', '(')
                expanded_code = rel_to_item.get_stringwithabsolutepathes(expanded_code, 'sh.', '.property')
                value = rel_to_item()    #  item value for use in eval
            else:
                expanded_code = "Error: Item {} does not exist!".format(relative_to)
        try:
            value = eval(expanded_code)
        except Exception as e:
            check_result = "Problem evaluating {}:  {}".format(expanded_code, e)
        else:
            check_result = value
        return expanded_code, check_result


    # ======================================================================
    #  conf_yaml_converter
    #
    def conf_yaml_converter(self, conf_code):
        conf_code = self.strip_empty_lines(conf_code)
        yaml_code = ''
        ydata = parse_for_convert(conf_code=conf_code)
        if ydata != None:
            yaml_code = convert_yaml(ydata)
        return yaml_code


    # ======================================================================
    #  yaml_syntax_checker
    #
    def yaml_syntax_checker(self, yaml_code):
        check_result = ''
        if yaml_code == '':
            return check_result

        yaml_code = self.strip_empty_lines(yaml_code)

        import lib.shyaml as shyaml
        import lib.config as shconfig

        # load yaml code to dict ydata, get error message (if error occures) to estr
        ydata, estr = shyaml.yaml_load_fromstring(yaml_code, True)
        self.logger.info("yaml_syntax_checker(): type(ydata) = {},estr='{}'".format(type(ydata), estr))

        if estr != '':
            check_result = 'ERROR: \n\n' + estr
        elif not isinstance(ydata, collections.OrderedDict):
            check_result = 'ERROR: \n\n' + 'No valid YAML code'
        elif ydata != None:
            # found valid yaml code

            # Test if the loaded data items with 'struct' attribute
            config = collections.OrderedDict()
            self.items = Items.get_instance()
            struct_dict = self.items.structs._struct_definitions
            shconfig.search_for_struct_in_items(ydata, struct_dict, config)
            self.logger.info("ydata = {}".format(ydata))
            self.logger.info("config = {}".format(config))

            # return data structure converted back to yaml format
            check_result = convert_yaml(config).replace('\n\n', '\n')

        return check_result


    # ======================================================================
    #  /api/server/evalcheck
    #
    def evalcheck(self):
        """
        Check syntax of eval expression

        :return: status dict
        """
        params = self.get_body(text=False)
        if params is None:
            self.logger.warning("ServicesController(): evalcheck(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.info("ServicesController(): evalcheck(): {}".format(params))

        expanded_code, eval_result = self.eval_syntax_checker(params['expression'], params['relative_to'])
        result_type = str(type(eval_result))
        if result_type.startswith("<class '"):
            result_type = result_type[len("<class '"):]
            result_type = result_type[:-2]
        result = {'expression': expanded_code, 'result': eval_result, 'type': result_type}
        # return json.dumps({'expression': 'Expandierter Ausdruck (Antwort vom Server)', 'result': '42 (Antwort vom Server)'})
        return json.dumps(result)


    # ======================================================================
    #  /api/server/yamlcheck
    #
    def yamlcheck(self):
        """
        Check syntax of YAML configuration

        :return: status dict
        """
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("ServicesController(): yamlcheck(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.info("ServicesController(): yamlcheck(): '{}'".format(params))

        return self.yaml_syntax_checker(params)


    # ======================================================================
    #  /api/server/yamlconvert
    #
    def yamlconvert(self):
        """
        convert CONF configuration to YAML syntax

        :return: status dict
        """
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("ServicesController(): yamlconvert(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.info("ServicesController(): yamlconvert(): '{}'".format(params))

        return self.conf_yaml_converter(params)


    def cachecheck(self):
        """
        returns a list of items as json structure
        """
        unused_cache_files = []

        if self._sh.shng_status['code'] == 20:
            # {'code': 20, 'text': 'Running'}
            cache_path = os.path.join(self.base_dir, 'var', 'cache')
            onlyfiles = [f for f in os.listdir(cache_path) if os.path.isfile(os.path.join(cache_path, f))]

            for file in onlyfiles:
                if not file.find(".") == 0:  # filter .gitignore etc.
                    self.items = Items.get_instance()
                    item = self.items.return_item(file)
                    no_cache_file = False;
                    if item is None:
                        self.logger.debug("cachecheck: no item {}".format(file))
                        no_cache_file = True
                    elif not item._cache:
                        self.logger.debug("cachecheck: item {}, no _cache".format(file))
                        no_cache_file = True

                    if no_cache_file:
                        file_data = {}
                        file_data['last_modified'] = datetime.datetime.fromtimestamp(
                            int(os.path.getmtime(os.path.join(cache_path, file)))
                        ).strftime('%Y-%m-%d %H:%M:%S')
                        file_data['created'] = datetime.datetime.fromtimestamp(
                            int(os.path.getctime(os.path.join(cache_path, file)))
                        ).strftime('%Y-%m-%d %H:%M:%S')
                        file_data['filename'] = file
                        file_data['filename'] = file
                        unused_cache_files.append(file_data)

        return json.dumps(unused_cache_files)


    # cache_file_delete.html?filename="+filename
    def cachefile_delete(self, filename=''):
        """
        deletes a file from cache
        """
        self.logger.info("cachefile_delete: filename '{}'".format(filename))
        if filename[0] == '[':
            filenames = json.loads(filename)
        else:
            filenames = [filename]
        response = {'result': 'error', 'description': "cache file '" + filename + "' not found"}
        for filename in filenames:
            if len(filename) > 0:
                file_path = os.path.join(self.base_dir, 'var', 'cache', filename)
                if os.path.isfile(file_path):
                    self.logger.info("cachefile_delete: cachefile '{}' deleted".format(file_path))
                    os.remove(file_path);
                    response = {'result': 'ok'}

        return json.dumps(response)


    # ======================================================================
    #  GET /api/services/
    #
    def read(self, id=''):
        """
        Handle GET requests for server API
        """

        if id == 'cachecheck':
            return self.cachecheck()
        return None

    read.expose_resource = True
    read.authentication_needed = True


    def update(self, id='', filename=''):
        """
        Handle PUT requests for server API
        """
        self.logger.info("ServicesController.update('{}')".format(id))

        if id == 'evalcheck':
            return self.evalcheck()
        elif id == 'yamlcheck':
            return self.yamlcheck()
        elif id == 'yamlconvert':
            return self.yamlconvert()
        elif id == 'cachefile_delete':
            return self.cachefile_delete(filename)

        return None

    update.expose_resource = True
    update.authentication_needed = True
