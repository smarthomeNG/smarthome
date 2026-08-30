#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2017-2025   Martin Sinn                         m.sinn@gmx.de
#           2026-       Sebastian Helms            morg@knx-user-forum.de
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
#  http://knx-user-forum.de/
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
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################


"""
This script combines the earlier `build_plugin_config_files.py` and
`build_plugin_rst_files.py` to deduplicate code and save execution time.

It creates the files for including the plugin documentation into the main
documentation.

These are:

- plugins_gateway.rst
- plugins_interface.rst
- plugins_protocol.rst
- plugins_system.rst
- plugins_unclassified.rst
- plugins_web.rst
- config/<plugin>.rst

in the directory **doc/<user/developer>/source/plugins_doc** .

These files contain

- an include for a header file
- a toctree directive
- a table with information about the plugins and links to further information
- an include for a footer file
- the plugin documentation derived from plugins/<plugin>/plugin.yaml files.

"""

import html
import os
import subprocess
import sys
from typing import Optional

# find lib directory and import lib/item_conversion
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# um im Test-build_doc Umfeld zu laufen:
sys.path.insert(0, '..')
sys.path.insert(0, '../lib')
import shyaml  # type: ignore  # not in path

print('')
print(os.path.basename(__file__) + ' - Builds the .rst files for the documentation')
print('')
start_dir = os.getcwd()

type_unclassified = 'unclassified'
plugin_sections = {
    'gateway': {'de': 'Gateway', 'en': 'Gateway'},
    'interface': {'de': 'Interface', 'en': 'Interface'},
    'protocol': {'de': 'Protokoll', 'en': 'Protocol'},
    'system': {'de': 'System', 'en': 'System'},
    'web': {'de': 'Web/Cloud', 'en': 'Web/Cloud'},
    type_unclassified: {'de': 'nicht klassifizierte', 'en': 'non classified'},
    'all': {'de': 'Alle Plugins', 'en': 'All plugins'},
}

texts = {
    'type': {'de': 'Typ', 'en': 'type'},
    'conf': {'de': 'Konfiguration', 'en': 'Configuration'},
    'desc': {'de': 'Beschreibung', 'en': 'Description'},
    'info': {'de': 'zusätzliche Infos', 'en': 'additional information'},
    'supp': {'de': 'Unterstützung', 'en': 'support'},
    'pver': {'de': 'maximale Python-Version', 'en': 'maximum Python version'},
    'sver': {'de': 'maximale SmartHomeNG-Version', 'en': 'maximum SmartHomeNG-Version'},
    'stat': {'de': 'Plugin-Status', 'en': 'Plugin status'},
}

default_lang = 'en'


def bold(s: str) -> str:
    """mark string as bold if not empty"""
    return '**' + s + '**' if s else ''


# TODO: return generator?
def get_list_fromgit(name: str) -> list:
    """get filelist via git and return all matching files at first directory level"""
    # this could be written as a single nested comprehension, but gets quite unreadable
    # we gain speedup by using comprehensions
    plg_git = (
        subprocess.check_output(['git', 'ls-files', f'*/{name}'], stderr=subprocess.STDOUT)
        .decode()
        .strip('\n')
        .split('\n')
    )
    plglist = [x[0] for x in (p.split('/') for p in plg_git) if x[1] == name]
    return plglist


def get_pluginlist_fromgit() -> list:
    """get filelist of __init__.py files"""
    return get_list_fromgit('__init__.py')


# TODO: return generator?
def get_local_pluginlist() -> list:
    """like get_list_fromgit, but list files from local dir"""
    plglist = [x for x in os.listdir('.') if x[0] not in ['.', '_'] and x != 'deprecated_plugins']
    return plglist


def get_pluginyamllist_fromgit() -> list:
    """get filelist of plugin.yaml files"""
    return get_list_fromgit('plugin.yaml')


def get_info(from_dict: dict, section: str, link: bool = False) -> str:
    # as None can be returned as a value, or-it with '' to guarantee a str
    # remove newlines as we don't need visual layout
    text = (from_dict.get(section, '') or '').replace('\n', ' ')

    if link and text and not text.startswith('https://'):
        text = 'https://' + text
    if link:
        text = html.escape(text)
    return text


def get_version(section_dict: dict) -> str:
    """return version from dict with v or empty string"""
    version = get_info(section_dict, 'version')
    return 'v' + version if version else ''


def get_description(section_dict: dict, lang: str = 'en', key: str = 'description') -> str:
    """get description from dict in specified or fallback language as single line string"""
    desc = ''
    try:
        # as None can be returned as a value, or-it with '' to guarantee a str
        desc = (section_dict[key].get(lang, '') or '').replace('\n', ' ')
    except Exception:
        pass
    if not desc:
        lang2 = 'de' if lang == 'en' else default_lang
        try:
            desc = (section_dict[key].get(lang2, '') or '').replace('\n', ' ')
        except Exception:
            pass
    return desc


def get_doc_description(from_dict: dict, language: str, key: str = 'description', index: Optional[int] = None) -> str:
    if index is None:
        # return description
        desc = get_description(from_dict, language, key + '_long')
        if not desc:
            desc = get_description(from_dict, language, key)
        return desc
    else:
        # return entry of valid_description list
        desc = get_description(from_dict, language, key)
        if not desc:
            return ''
        try:
            return desc[index]
        except IndexError:
            print(f'Zu kurze Liste {desc} für index {index}')
            return ''


# TODO: test
def flatten(obj):
    """return flat list from nested list"""
    if isinstance(obj, list):
        for item in obj:
            yield from flatten(item)
    else:
        yield obj


def make_table_lines(lines: list, indent: int = 3, top: bool = False, wide: bool = False) -> list:
    """
    take a list and return rST lines

    If top is set, the list looks like
    * - foo
      - bar
      - baz

    If top is not set, the list looks like
    - foo

      bar

      baz
    """

    if not lines or lines == [None]:
        return []

    ind = ' ' * indent

    first, follow = '- ', '  '
    if top:
        first, follow = '* - ', '  - '

    result = []

    for i, line in enumerate(lines):
        if isinstance(line, list):
            if top:
                # get every non-empty line indented
                result += [ind + ln for ln in line if line]
            else:
                # get every non-empty line indented, add empty lines only between lines
                result += [ln for x in line if line for ln in (ind + x, ind)][:-1]
        else:
            # get line indented with first or follower list mark
            result += [ind + (follow if i else first) + line]
            if wide:
                result += ['']
    # don't return trailing empty line
    if result[-1:] == '':
        return result[:-1]
    return result


def make_table_bullet_lines(lines: list, indent: int = 3) -> list:
    """
    take a list and return rST lines with bullets

    (indented) list looks like

      + foo
      + bar
      + baz

    with correct empty line before and after

    If lines is empty, return
    <empty>
    |br|
    <empty>

    to enforce one empty line
    """
    if not lines or lines == [[], []]:
        return ['', '|br|', '']

    ind = ' ' * indent

    result = ['']
    for line in flatten(lines):
        result += [ind + '+ ' + line]
    result += ['']
    return result


def write_heading(fh, heading, level):

    liner1 = '=' * len(heading)
    # A section underline must be a single repeated character, matching or
    # exceeding the title's length - the previous ' - ' * len(heading) built
    # a garbage line like ' -  - ' instead, which RST reads as a bullet
    # list nested one level deeper per dash rather than a heading underline
    # (verified against docutils directly: the old string parsed 'id' as a
    # <definition_list> term with an empty, ever-deepening nested bullet
    # list body - exactly the malformed output seen on every plugin_functions
    # parameter in the rendered docs).
    liner2 = '-' * len(heading)

    fh.write('\n')
    if level == 1:
        fh.write(liner1 + '\n')
    fh.write(heading + '\n')
    if level in [1, 2]:
        fh.write(liner1 + '\n')
    elif level == 3:
        fh.write(liner2 + '\n')
    fh.write('\n')


def write_formatted(fh, str):

    for s in str.split('\\n'):
        if s.startswith(' '):
            if not s.startswith(' -'):
                s = s[1:]
        fh.write(s + '\n')
    fh.write('\n')


def build_pluginlist(plugins: list[str], changed_plugins: list[str], language: str = 'de') -> dict[str, list]:
    """
    Return a dict of <type>: <plugin_dict> for each plugin of the requested type
    The dict contains the plugin name, type and description as strings
    Keys are the plugin types, 'all' and 'changed'
    """
    results = {type_: list() for type_ in plugin_sections}
    results['changed'] = []

    # prevent division by zero
    if not plugins:
        return results

    num_pl = len(plugins)
    count = 0

    # read all plugins once
    for metaplugin in plugins:
        count += 1
        print(f'Lese Metadaten: {int(100 * count / num_pl)}%\r', end='')

        plg_dict = {}
        plg_dict['name'] = metaplugin.lower()
        plg_dict['type'] = type_unclassified
        plgtype = type_unclassified

        metafile = os.path.join(metaplugin, 'plugin.yaml')
        plugin_yaml = shyaml.yaml_load(metafile)

        if plugin_yaml:
            section_dict = plugin_yaml.get('plugin')

            if section_dict:
                plg_dict['version'] = get_version(section_dict)
                plg_dict['sh_minversion'] = str(section_dict.get('sh_minversion', ''))
                plg_dict['sh_maxversion'] = str(section_dict.get('sh_maxversion', ''))
                plg_dict['py_minversion'] = str(section_dict.get('py_minversion', ''))
                plg_dict['py_maxversion'] = str(section_dict.get('py_maxversion', ''))

                try:
                    if section_dict['type'].lower() in plugin_sections:
                        plgtype = section_dict['type'].lower()
                except Exception:
                    pass
                plg_dict['type'] = plgtype

                plg_dict['desc'] = get_description(section_dict, language)
                plg_dict['maint'] = get_info(section_dict, 'maintainer')
                plg_dict['test'] = get_info(section_dict, 'tester')
                plg_dict['state'] = get_info(section_dict, 'state')
                plg_dict['doc'] = get_info(section_dict, 'documentation', link=True)
                plg_dict['sup'] = get_info(section_dict, 'support', link=True)

        else:
            plg_dict['version'] = ''
            plg_dict['desc'] = 'No metadata (plugin.yaml) was provided for this plugin!'
            plg_dict['maint'] = ''
            plg_dict['test'] = ''
            plg_dict['doc'] = ''
            plg_dict['sup'] = ''

        results[plgtype].append(plg_dict)
        results['all'].append(plg_dict)
        if metaplugin in changed_plugins:
            results['changed'].append(plg_dict)
        # print(f'added {metaplugin} to {plgtype}')

    print('\n')
    return results


def write_config_dummyfile(configfile_dir: str, namelist: list):
    """write dummy rst file to include plugin docs in hidden toctree"""
    outf_name = os.path.join(configfile_dir, 'dummy_config.rst')

    with open(outf_name, 'w', encoding='UTF-8') as fh_dummy:
        fh_dummy.write(':orphan:\n')
        fh_dummy.write('\n')
        fh_dummy.write(
            '.. This file is only created to suppress Sphinx warnings about plugins config .rst files not beeing included in any toctree.\n'
        )
        fh_dummy.write('\n')
        fh_dummy.write('.. toctree::\n')
        fh_dummy.write('   :maxdepth: 2\n')
        fh_dummy.write('   :glob:\n')
        fh_dummy.write('   :titlesonly:\n')
        fh_dummy.write('   :hidden:\n')
        fh_dummy.write('\n')
        for n in namelist:
            # fh_dummy.write('   /doc/user/source/plugins_doc/config/' + n+'.rst\n')
            fh_dummy.write('   ' + n + '.rst\n')


# ==================================================================================
#   write_struct


def write_struct(fh, conf, key, level=0):
    """
    Create output for a .rst file with struct tree views
    """
    indent = ' ' * 4

    def prefix(level):
        return indent * (level + 1)

    def write_entry(fh, text, level, folder=False, collapsed=True):
        msg = prefix(level)
        bit = ' - '
        # enable the next two lines for collapsible (and default collapsed) trees
        # NOTE: at the moment, this doesn't render properly in HTML, not sure why
        # bit = '-' if collapsed else '+'
        # bit = f' - [{bit}] ' if folder else ' - '
        msg = msg + bit + f':dir:`{"folder" if folder else "file"}` {text}\n'
        fh.write(msg)

    def write_item(fh, conf, name, level):
        # 'name'/'remark' is only a description here if it's a plain string -
        # several plugins (appletv, avm, bose_soundtouch, lms, pioneer,
        # robonect, ...) have a *child struct item* literally called 'name'
        # (e.g. a device's own display-name item), which would otherwise be
        # misread as this node's own description text instead of a nested
        # item to recurse into.
        desc = conf.get('name', conf.get('remark', '---'))
        if not isinstance(desc, str):
            desc = '---'
        # remove newlines to prevent linebreaks in YAML lists
        desc = (desc or '').replace('\n', ' ')
        ityp = conf.get('type', 'foo')
        text = f'{bold(name)} (`{ityp}`, {desc})'

        # test if item has children (rudimentary test, might fail for "empty" items)
        children = []
        for key in conf:
            if isinstance(conf[key], dict):
                children.append(key)

        folder = False
        if children:
            folder = True
        write_entry(fh, text, level, folder=folder)

        for c in children:
            write_item(fh, conf[c], c, level + 1)

    if level == 0:
        fh.write('.. treeview::\n')

    write_item(fh, conf, key, level)

    fh.write('\n')


# ==================================================================================
#   write_type_files


def write_type_files(
    plg_dicts_by_type: dict[str, list],
    plugin_rst_dir: str,
    plgtype: str = 'all',
    plgtype_print: str = '',
    heading: str = '',
    language: str = 'en',
):
    """
    Create a .rst file for each plugin category
    """

    if not heading:
        title = plgtype + ' Plugins'
    else:
        title = heading

    plglist = [plg_dict for plg_dict in plg_dicts_by_type[plgtype]]

    rst_filename = os.path.join('plugins_doc', 'plugins_' + plgtype.lower() + '.rst')
    rst_dummyname = os.path.join('plugins_doc', 'dummy_' + plgtype.lower() + '.rst')

    print(f'Datei: {rst_filename}{" " * (26 - len(rst_filename))}  -  {len(plglist)} {title}')

    #    print("> Opening file "+plugin_rst_dir+'/'+rst_filename)
    with (
        open(plugin_rst_dir + '/' + rst_filename, 'w') as fh,
        open(plugin_rst_dir + '/' + rst_dummyname, 'w') as fh_dummy,
    ):
        #    fh.write(title+'\n')
        #    fh.write('-'*len(title)+'\n')
        # if plgtype != type_unclassified:
        #     fh.write(f'.. index:: Plugin Type; {plgtype_print}\n\n')
        fh.write(f'.. include:: /plugins_doc/plugins_{plgtype}_header.rst\n\n')

        # write toctree to dummy file to suppress warnings for not included README.md files.
        fh_dummy.write(':orphan:\n')
        fh_dummy.write('\n')
        fh_dummy.write(
            '.. This file is only created to suppress Sphinx warnings about README.md files not beeing included in any toctree.\n'
        )
        fh_dummy.write('\n')
        fh_dummy.write('.. toctree::\n')
        fh_dummy.write('   :maxdepth: 2\n')
        fh_dummy.write('   :glob:\n')
        fh_dummy.write('   :titlesonly:\n')
        fh_dummy.write('   :hidden:\n')
        fh_dummy.write('\n')

        # write toctree
        fh.write('.. toctree::\n')
        fh.write('   :maxdepth: 2\n')
        fh.write('   :glob:\n')
        fh.write('   :titlesonly:\n')
        fh.write('   :hidden:\n')
        fh.write('\n')

        if not plglist:
            if language == 'de':
                fh.write(f'Zur Zeit gibt es keine Plugins des Typs {plgtype_print}.\n')
            else:
                fh.write(f'At the moment there are no plugins of type {plgtype_print}\n')
            return

        for plg in plglist:
            if os.path.isfile(os.path.join(plg['name'], 'README.md')):
                fh_dummy.write(f'   /plugins/{plg["name"]}/README.md\n')

            fp = os.path.join(plg['name'], 'user_doc')
            if os.path.isfile(fp + '.rst') or os.path.isfile(fp + '.md'):
                fh.write(f'   /plugins/{fp}\n')

            # fh.write(f'   config/{plg["name"]}\n')
        fh.write('\n')

        # write table with details
        fh.write(f"""


.. list-table::
   :header-rows: 1

   * - Plugin ({texts['conf'][language]})
     - Version
     - {texts['desc'][language]}
     - Maintainer
     - Tester""")

        for plg in plglist:
            if os.path.isfile(os.path.join(plugin_rst_dir, 'plugins_doc', 'config', plg['name'] + '.rst')):
                # a generated <config>.rst exists
                plg_readme_link = f':doc:`{plg["name"]} <config/{plg["name"]}>`'
            else:
                # no generated <config>.rst exists (for english developer documentation
                plg_readme_link = plg['name']

            plg_doc = ''
            if plg['doc']:
                plg_doc = f'`{plg["name"]} {texts["info"][language]} <{plg["doc"]}>`_'

            plg_sup = ''
            if plg['sup']:
                plg_sup = f'`{plg["name"]} {texts["supp"][language]} <{plg["sup"]}>`_'

            desc = (
                [plg['desc']]
                + make_table_bullet_lines([plg_doc if plg['doc'] else []] + [plg_sup if plg['sup'] else []], 0)
                + ([f'Plugin {texts["type"][language]}: {bold(plg["type"])}'] if plgtype == 'all' else [])
            )

            if plg.get('py_maxversion'):
                desc += ['', f'{texts["pver"][language]}: {bold(plg["py_maxversion"])}']
            if plg.get('sh_maxversion'):
                desc += ['', f'{texts["sver"][language]}: {bold(plg["sh_maxversion"])}']
            if plg.get('state', '').lower() in ['deprecated', 'develop']:
                desc += ['', f'{texts["stat"][language]}: {bold(plg["state"])}']

            fh.write(
                '\n'
                + '\n'.join(
                    make_table_lines(
                        [
                            plg_readme_link,
                            plg['version'],
                            make_table_lines(desc, 2),
                            make_table_lines([x.strip() for x in plg['maint'].split(',')], 2, wide=True),
                            make_table_lines([x.strip() for x in plg['test'].split(',')], 2, wide=True),
                            [],
                        ],
                        top=True,
                    )
                )
            )

        fh.write('\n\n.. include:: /plugins_doc/plugins_footer.rst\n')


# ==================================================================================
#   write_configfile


def write_configfile(plg: dict, configfile_dir: str, language: str = 'de'):
    """
    Create a .rst file with configuration information for the passed plugin
    """
    #    lparameter_yaml = []
    #    no_lparameters = (lparameter_yaml == 'NONE')

    plgname = plg['name']

    # ---------------------------------
    # read metadata for plugin
    # ---------------------------------
    metafile = os.path.join(plgname, 'plugin.yaml')
    if os.path.isfile(metafile):
        meta_yaml = shyaml.yaml_load(metafile, ordered=True)
        plugin_yaml = meta_yaml.get('plugin', {})
        parameter_yaml = meta_yaml.get('parameters')
        iattributes_yaml = meta_yaml.get('item_attributes')
        lparameter_yaml = meta_yaml.get('logic_parameter')
        functions_yaml = meta_yaml.get('plugin_functions')
        structs_yaml = meta_yaml.get('item_structs')

        if parameter_yaml == 'NONE':
            parameter_yaml = {}

        if iattributes_yaml == 'NONE':
            iattributes_yaml = {}

        if lparameter_yaml == 'NONE':
            lparameter_yaml = {}

        if functions_yaml == 'NONE':
            functions_yaml = {}

        if structs_yaml == 'NONE':
            structs_yaml = {}

    else:
        plugin_yaml = {}
        parameter_yaml = {}
        iattributes_yaml = {}
        lparameter_yaml = {}
        functions_yaml = {}
        structs_yaml = {}

    # ---------------------------------
    # Create rST file
    # ---------------------------------
    outf_name = os.path.join(configfile_dir, plgname + '.rst')
    fh = open(outf_name, 'w', encoding='UTF-8')
    fh.write('.. |_| unicode:: 0xA0\n')
    fh.write('\n')

    write_heading(fh, f"Plugin '{plgname}' Konfiguration", 1)
    fh.write('\n')
    fh.write(f'.. index:: Plugins; {plgname} Konfiguration\n')
    fh.write('\n')

    # --------------------------------------------
    # write image for plugin-type and generic text
    # --------------------------------------------
    plgtype = plugin_yaml.get('type', '').lower()
    plgstate = plugin_yaml.get('state', '').lower()
    if plgtype != '':
        #        cwd = os.getcwd()
        plglogo = plgname + '/webif/static/img/plugin_logo'
        if os.path.isfile(plglogo + '.png'):
            ext = '.png'
        elif os.path.isfile(plglogo + '.jpg'):
            ext = '.jpg'
        elif os.path.isfile(plglogo + '.svg'):
            ext = '.svg'
        else:
            ext = '.???'
        if os.path.isfile(plglogo + ext):
            fh.write('.. image:: /plugins/' + plglogo + ext + '\n')
            fh.write('   :alt: plugin logo\n')
        else:
            print(f'Plugin {plgname}: Kein Plugin-Logo gefunden, Typ-Logo verwendet.')
            fh.write('.. image:: /_static/img/' + plgtype + '.svg\n')
            fh.write('   :alt: plugin type logo\n')
        fh.write('   :width: 300px\n')
        fh.write('   :height: 300px\n')
        fh.write('   :scale: 50%\n')
        fh.write('   :align: left\n')
        fh.write('\n')
        fh.write('.. |br| raw:: html\n')
        fh.write('\n')
        fh.write('   <br />\n')
        fh.write('\n')

    fh.write(
        'Im folgenden sind etwaige Anforderungen und unterstützte Hardware beschrieben. Danach folgt die \
              Beschreibung, wie das Plugin '
        + bold(plgname)
        + ' konfiguriert wird. Außerdem ist im folgenden \
              beschrieben, wie das Plugin in den Item Definitionen genutzt werden kann. [#f1]_ \n'
    )
    fh.write('\n')
    fh.write(f'Es handelt sich bei diesem Plugin um ein **{plgtype} Plugin**.\n')
    if plgstate == 'deprecated':
        fh.write('\n')
        fh.write(
            f'**ACHTUNG**: Dieses Plugin ist als {plgstate} gekennzeichnet. Es wird empfohlen auf eine \
                 Nachfolgelösung umzusteigen.\n'
        )
    if plgstate == 'develop':
        fh.write('\n')
        fh.write(
            f'**ACHTUNG**: Dieses Plugin ist als {plgstate} gekennzeichnet. Es kann daher sein, dass es \
                 noch nicht sämtliche Funktionen unterstützt oder noch fehlerhaft ist.\n'
        )

    fh.write('\n')
    fh.write('\n')

    write_heading(fh, 'Beschreibung', 2)
    write_formatted(fh, get_doc_description(plugin_yaml, language))

    # ---------------------------------
    # write a note block if special requirements exist
    # ---------------------------------
    py_versioncomment = str(plugin_yaml.get('py_versioncomment', ''))
    if py_versioncomment != '':
        fh.write('.. attention::\n')
        fh.write('\n')
        fh.write(f'    {py_versioncomment}\n')
        fh.write('\n')
        fh.write('\n')

    # ---------------------------------
    # write Requirements section
    # ---------------------------------
    requirements = get_description(plugin_yaml, language, 'requirements')
    min_version = str(plugin_yaml.get('sh_minversion', ''))
    max_version = str(plugin_yaml.get('sh_maxversion', ''))
    min_py_version = str(plugin_yaml.get('py_minversion', ''))
    max_py_version = str(plugin_yaml.get('py_maxversion', ''))
    if requirements or min_version or max_version or min_py_version or max_py_version:
        write_heading(fh, 'Anforderungen', 2)
        fh.write('\n')
        write_formatted(fh, get_doc_description(plugin_yaml, language, 'requirements'))
        if min_version:
            fh.write(' - Minimum SmartHomeNG Version: ' + bold(min_version) + '\n')
        if max_version:
            fh.write(' - Maximum SmartHomeNG Version: ' + bold(max_version) + '\n')
        if min_py_version:
            fh.write(' - Minimum Python Version: ' + bold(min_py_version) + '\n')
        if max_py_version:
            fh.write(' - Maximum Python Version: ' + bold(max_py_version) + '\n')

    # ---------------------------------
    # write supported hardware section
    # ---------------------------------
    hardware = get_description(plugin_yaml, language, 'hardware')
    if hardware:
        write_heading(fh, 'Unterstützte Hardware', 2)
        fh.write('\n')
        write_formatted(fh, get_doc_description(plugin_yaml, language, 'hardware'))

    # ---------------------------------
    # write Konfiguration section
    # ---------------------------------
    write_heading(fh, 'Konfiguration', 2)
    fh.write('\n')
    fh.write(
        'Im folgenden ist beschrieben, wie das Plugin '
        + bold(plgname)
        + ' konfiguriert wird. Außerdem ist im folgenden beschrieben, wie das Plugin in den Item Definitionen genutzt werden kann.\n'
    )
    fh.write('\n')

    # ---------------------------------
    # write Parameter section
    # ---------------------------------
    write_heading(fh, 'Parameter', 1)
    fh.write('\n')
    fh.write(
        'Das Plugin verfügt über folgende Parameter, die in der Datei ``../etc/plugin.yaml`` konfiguriert werden:\n'
    )
    fh.write('\n')

    if not parameter_yaml:
        if parameter_yaml == {}:
            fh.write('**Keine**\n')
        else:
            fh.write(
                'Keine Parameter in den Metadaten beschrieben - **Bitte in der README nachsehen** (siehe Fußnote)\n'
            )
    else:
        for p in sorted(parameter_yaml):
            # ---------------------------------
            # write info for one parameter
            # ---------------------------------
            write_heading(fh, p, 2)
            fh.write('\n')
            write_formatted(fh, get_doc_description(parameter_yaml[p], language))
            datatype = parameter_yaml[p].get('type', '').lower()
            default = str(parameter_yaml[p].get('default', ''))
            validlist = parameter_yaml[p].get('valid_list', [])
            validmin = parameter_yaml[p].get('valid_min', '')
            validmax = parameter_yaml[p].get('valid_max', '')
            fh.write(' - Datentyp: ' + bold(datatype) + '\n')
            if default != '':
                default_printable = default.replace('\r', '\\r')
                default_printable = default_printable.replace('\n', '\\n')
                fh.write(' - Standardwert: ' + bold(default_printable) + '\n')
            fh.write('\n')
            if validmin != '':
                fh.write(' - Minimalwert: ' + bold(str(validmin)) + '\n')
            if validmax != '':
                fh.write(' - Maximalwert: ' + bold(str(validmax)) + '\n')
            if len(validlist) > 0:
                fh.write(' - Mögliche Werte:\n')
                fh.write('\n')
                for index, v in enumerate(validlist):
                    desc = get_doc_description(parameter_yaml[p], language, key='valid_list_description', index=index)
                    if desc != '':
                        desc = ' |_| - |_| ' + desc
                    fh.write('   - ' + bold(str(v)) + desc + '\n')
                fh.write('\n')

    # ---------------------------------
    # write item_attribute section
    # ---------------------------------
    write_heading(fh, 'Item Attribute', 1)
    fh.write('\n')
    fh.write(
        'Das Plugin unterstützt folgende Item Attribute, die in den Dateien im Verzeichnis  ``../items`` verwendet werden:\n'
    )
    fh.write('\n')

    if not iattributes_yaml:
        if iattributes_yaml == {}:
            fh.write('**Keine**\n')
        else:
            fh.write(
                'Keine Item Attribute in den Metadaten beschrieben - **Bitte in der README nachsehen** (siehe Fußnote)\n'
            )
    else:
        for a in sorted(iattributes_yaml):
            # ---------------------------------
            # write info for one attribute
            # ---------------------------------
            write_heading(fh, a, 2)
            fh.write('\n')
            write_formatted(fh, get_doc_description(iattributes_yaml[a], language))
            datatype = iattributes_yaml[a].get('type', '').lower()
            default = str(iattributes_yaml[a].get('default', ''))
            validlist = iattributes_yaml[a].get('valid_list', [])
            validmin = iattributes_yaml[a].get('valid_min', '')
            validmax = iattributes_yaml[a].get('valid_max', '')
            fh.write(' - Datentyp: ' + bold(datatype) + '\n')
            if default != '':
                default_printable = default.replace('\r', '\\r')
                default_printable = default_printable.replace('\n', '\\n')
                fh.write(' - Standardwert: ' + bold(default_printable) + '\n')
            fh.write('\n')
            if validmin != '':
                fh.write(' - Minimalwert: ' + bold(str(validmin)) + '\n')
            if validmax != '':
                fh.write(' - Maximalwert: ' + bold(str(validmax)) + '\n')
            if len(validlist) > 0:
                fh.write(' - Mögliche Werte:\n')
                fh.write('\n')
                for index, v in enumerate(validlist):
                    desc = get_doc_description(iattributes_yaml[a], language, key='valid_list_description', index=index)
                    if desc != '':
                        desc = ' |_| - |_| ' + desc
                    fh.write('   - ' + bold(str(v)) + desc + '\n')
                fh.write('\n')

    # ---------------------------------
    # write item_structs section
    # ---------------------------------
    write_heading(fh, 'Item-Structs', 1)
    fh.write('\n')
    fh.write(
        'Das Plugin stellt die folgenden Item-Structs zur Verfügung. Diese Informationen sind aus der `plugin.yaml` entnommen und möglicherweise nicht vollständig.\n'
    )
    fh.write('\n')

    if not structs_yaml:
        fh.write('**Keine**\n')
    else:
        for struct in sorted(structs_yaml):
            write_heading(fh, struct, 2)
            conf = structs_yaml[struct]
            try:
                desc = conf.get('name', conf.get('remark', ''))
                if desc:
                    fh.write(desc + '\n')
            except Exception:
                pass
            fh.write('\n')
            write_struct(fh, structs_yaml[struct], struct)

    # ---------------------------------
    # write logic_parameter section
    # ---------------------------------
    write_heading(fh, 'Logik Parameter', 1)
    fh.write('\n')
    fh.write(
        'Das Plugin verfügt über folgende Parameter, die in der Datei ``../etc/logic.yaml`` konfiguriert werden:\n'
    )
    fh.write('\n')

    if not lparameter_yaml:
        if lparameter_yaml == {}:
            fh.write('**Keine**\n')
        else:
            fh.write(
                'Keine Logik Parameter in den Metadaten beschrieben - **Bitte in der README nachsehen** (siehe Fußnote)\n'
            )
    else:
        for logic in sorted(lparameter_yaml):
            # ---------------------------------
            # write info for one attribute
            # ---------------------------------
            write_heading(fh, logic, 2)
            fh.write('\n')
            write_formatted(fh, get_doc_description(lparameter_yaml[logic], language))
            datatype = lparameter_yaml[logic].get('type', '').lower()
            default = str(lparameter_yaml[logic].get('default', ''))
            validlist = lparameter_yaml[logic].get('valid_list', [])
            validmin = lparameter_yaml[logic].get('valid_min', '')
            validmax = lparameter_yaml[logic].get('valid_max', '')
            fh.write(' - Datentyp: ' + bold(datatype) + '\n')
            if default != '':
                default_printable = default.replace('\r', '\\r')
                default_printable = default_printable.replace('\n', '\\n')
                fh.write(' - Standardwert: ' + bold(default_printable) + '\n')
            fh.write('\n')
            if validmin != '':
                fh.write(' - Minimalwert: ' + bold(str(validmin)) + '\n')
            if validmax != '':
                fh.write(' - Maximalwert: ' + bold(str(validmax)) + '\n')
            if len(validlist) > 0:
                fh.write(' - Mögliche Werte:\n')
                fh.write('\n')
                for index, v in enumerate(validlist):
                    desc = get_doc_description(
                        lparameter_yaml[logic], language, key='valid_list_description', index=index
                    )
                    if desc != '':
                        desc = ' |_| - |_| ' + desc
                    fh.write('   - ' + bold(str(v)) + desc + '\n')
                fh.write('\n')

    # ---------------------------------
    # write plugin-function section
    # ---------------------------------
    write_heading(fh, 'Plugin Functions', 1)
    fh.write('\n')
    fh.write('Das Plugin verfügt über folgende öffentliche Funktionen, die z.B. in Logiken aufgerufen werden können.\n')
    fh.write('\n')

    if not functions_yaml:
        if functions_yaml == {}:
            fh.write('**Keine**\n')
        else:
            fh.write(
                'Keine Funktionen in den Metadaten beschrieben - **Bitte in der README nachsehen** (siehe Fußnote)\n'
            )
    else:
        for f in sorted(functions_yaml):
            # ---------------------------------
            # write info for one function
            # ---------------------------------
            fp = ''
            func_param_yaml = functions_yaml[f].get('parameters', None)
            if func_param_yaml is not None:
                for par in func_param_yaml:
                    if fp != '':
                        fp += ', '
                    fp += par
                    if func_param_yaml[par] is not None and isinstance(func_param_yaml[par], dict):
                        if func_param_yaml[par].get('default', None) is not None:
                            default = str(func_param_yaml[par].get('default', None))
                            if func_param_yaml[par].get('type', 'foo') == 'str':
                                default = " '" + default + "'"
                            fp += '=' + default
                    else:
                        print('\n\nFEHLER: Ungültige Plugin-Funktion:')
                        print(f'Plugin: {plgname}')
                        print(f'par   : {par}\n')
                        print(f'func_param_yaml: {func_param_yaml}\n')

            write_heading(fh, f + '(' + fp + ')', 2)
            fh.write('\n')
            #        desc = get_description(parameter_yaml[f], 768, language)
            #        fh.write(desc[0] + '\n')
            #       fh.write('\n')
            write_formatted(fh, get_doc_description(functions_yaml[f], language))
            datatype = functions_yaml[f].get('type', '').lower()
            default = str(functions_yaml[f].get('default', ''))
            validlist = functions_yaml[f].get('valid_list', [])
            validmin = functions_yaml[f].get('valid_min', '')
            validmax = functions_yaml[f].get('valid_max', '')
            if datatype == 'void':
                fh.write(' - Die Funktion liefert kein Ergebnis\n')
            else:
                fh.write(' - Ergebnistyp der Funktion: ' + bold(datatype) + '\n')
            if default != '':
                default_printable = default.replace('\r', '\\r')
                default_printable = default_printable.replace('\n', '\\n')
                fh.write(' - Standardwert: ' + bold(default_printable) + '\n')
            fh.write('\n')
            if validmin != '':
                fh.write(' - Minimalwert: ' + bold(str(validmin)) + '\n')
            if validmax != '':
                fh.write(' - Maximalwert: ' + bold(str(validmax)) + '\n')
            if len(validlist) > 0:
                fh.write(' - Mögliche Werte:\n')
                fh.write('\n')
                for index, v in enumerate(validlist):
                    desc = get_doc_description(functions_yaml[f], language, key='valid_list_description', index=index)
                    if desc != '':
                        desc = ' |_| - |_| ' + desc
                    fh.write('   - ' + bold(str(v)) + desc + '\n')
                fh.write('\n')

            # func_param_yaml = functions_yaml[f].get('parameters', None)
            #
            # Parameters are a *sub*-level of an already-h2 function heading -
            # rendered as their own h3 sections (write_heading level 3) they
            # were visually indistinguishable from the function itself (same
            # font weight/size in the RTD theme, which doesn't indent nested
            # sections at all - only Item Attributes' top-level h2 entries
            # looked fine, since that section has no third tier). A
            # definition list - term at the base indent, body indented under
            # it - renders with real visual indentation in this theme and
            # matches Item Attributes' own bullet-list style for the
            # Datentyp/Standardwert/etc. properties below each one.
            if func_param_yaml is not None:
                fh.write('**Parameter:**\n')
                fh.write('\n')
                for par in func_param_yaml:
                    datatype = func_param_yaml[par].get('type', '').lower()
                    default = str(func_param_yaml[par].get('default', ''))
                    validlist = func_param_yaml[par].get('valid_list', [])
                    validmin = func_param_yaml[par].get('valid_min', '')
                    validmax = func_param_yaml[par].get('valid_max', '')

                    fh.write(bold(par) + '\n')
                    desc = get_doc_description(func_param_yaml[par], language)
                    if desc:
                        fh.write('    ' + desc + '\n')
                    fh.write('\n')
                    fh.write('    - Datentyp: ' + bold(datatype) + '\n')
                    if default != '':
                        default_printable = default.replace('\r', '\\r')
                        default_printable = default_printable.replace('\n', '\\n')
                        fh.write('    - Standardwert: ' + bold(default_printable) + '\n')
                    if validmin != '':
                        fh.write('    - Minimalwert: ' + bold(str(validmin)) + '\n')
                    if validmax != '':
                        fh.write('    - Maximalwert: ' + bold(str(validmax)) + '\n')
                    if len(validlist) > 0:
                        fh.write('    - Mögliche Werte:\n')
                        fh.write('\n')
                        for index, v in enumerate(validlist):
                            vdesc = get_doc_description(
                                func_param_yaml[par], language, key='valid_list_description', index=index
                            )
                            if vdesc != '':
                                vdesc = ' |_| - |_| ' + vdesc
                            fh.write('       - ' + bold(str(v)) + vdesc + '\n')
                    fh.write('\n')

    fh.write('\n')

    if os.path.isfile(plg['name'] + '/README.md'):
        fh.write(
            '.. [#f1] Diese Seite wurde aus den Metadaten des Plugins erzeugt. Für den Fall, dass diese Seite nicht alle benötigten Informationen enthält, bitte auf die englischsprachige :doc:`README Datei <../../plugins/'
            + plgname
            + '/README>` des Plugins zugreifen.\n'
        )
    else:
        fh.write('.. [#f1] Diese Seite wurde aus den Metadaten des Plugins erzeugt.\n')

    fh.close()
    return


# ==================================================================================
#   Main Generator Routine
#

if __name__ == '__main__':
    #    print ('Number of arguments:', len(sys.argv), 'arguments.')
    #    print ('Argument List:', str(sys.argv))

    language = 'en'

    if 'de' in sys.argv:
        language = 'de'

    global docu_type
    docu_type = start_dir.split('/')[-1:][0]  # developer / user

    # change the working diractory to the directory from which the converter is loaded (../tools)
    os.chdir(os.path.dirname(os.path.abspath(os.path.basename(__file__))))

    plugindirectory = '../plugins'
    pluginabsdirectory = os.path.abspath(plugindirectory)

    os.chdir(pluginabsdirectory)

    print('Start directory        = ' + start_dir)
    print('Documentation type     = ' + docu_type)
    print('Documentation language = ' + language)
    print('')

    plugins_git = get_pluginlist_fromgit()
    if 'xmpp' not in plugins_git:
        plugins_git.append('xmpp')

    print('--- Liste der Plugins auf github (' + str(len(plugins_git)) + '):')

    pluginsyaml_git = get_pluginyamllist_fromgit()
    if 'xmpp' not in plugins_git:
        plugins_git.append('xmpp')

    print('--- Liste der Plugins mit Metadaten auf github (' + str(len(pluginsyaml_git)) + '):')
    print()

    if docu_type == 'doc':
        plugin_rst_dir = os.path.join(start_dir, 'user', 'source')
    else:
        plugin_rst_dir = os.path.join(start_dir, 'source')
    print('zu schreiben in: ' + plugin_rst_dir)

    #
    #   check outdated config files and build list
    #

    configfile_dir = os.path.join(plugin_rst_dir, 'plugins_doc', 'config')
    skip = 0
    if os.path.exists(configfile_dir):
        # try to check which files don't need recreating
        plugins_new = []

        for plg in plugins_git:
            plg_file = os.path.join(plugindirectory, plg, 'plugin.yaml')
            rst_file = os.path.join(configfile_dir, plg + '.rst')
            if not os.path.exists(rst_file):
                plugins_new.append(plg)
                continue
            if not os.path.exists(plg_file):
                plugins_new.append(plg)
                continue
            plg_time = os.path.getmtime(plg_file)
            rst_time = os.path.getmtime(rst_file)

            # recreate if rst file is older than plugin.yaml
            if rst_time < plg_time:
                plugins_new.append(plg)
            else:
                skip += 1
    else:
        os.makedirs(configfile_dir)
        plugins_new = plugins_git
    print('\n')

    plugins_by_type = build_pluginlist(plugins_git, plugins_new, language)

    #
    #   generate plugin config files
    #

    print('\n\n--- Schreibe Dokumentation aus plugin.yaml')
    print(f'zu schreiben: {len(plugins_by_type["changed"])} Dateien, {skip} noch aktuell\n')

    for plg in plugins_by_type['changed']:
        write_configfile(plg, configfile_dir, language)
        print(f'plugin {plg["name"]}: ./config/{plg["name"]}.rst', ' ' * 20, end='\r')

    print(' ' * 50 + '\n\n')

    write_config_dummyfile(configfile_dir, plugins_git)

    #
    #   generate plugin type files
    #

    print('--- Schreibe Listen nach Kategorien')

    for pl in plugin_sections:
        if plugins_by_type[pl] is None:
            print(f'Datei: plugins_doc/plugins_{pl.lower()}.rst: Daten unverändert, übersprungen')
        else:
            write_type_files(plugins_by_type, plugin_rst_dir, pl, plugin_sections[pl][language], language=language)
    print()
