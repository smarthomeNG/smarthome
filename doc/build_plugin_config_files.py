#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2017-       Martin Sinn                         m.sinn@gmx.de
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
This script creates the files for including the plugin documentation into the developer- and
user-documentation.

it creates the files:

- plugins_gateway.rst
- plugins_interface.rst
- plugins_protocol.rst
- plugins_system.rst
- plugins_unclassified.rst
- plugins_web.rst

in the directory **../doc/<user/developer>/source/plugins_doc** .

These files contain

- an include for a header file
- a toctree directive
- a table with information about the plugins and links to further information
- an include for a footer file

Further, this program creates the file with the configuration information for the plugins.
(see: write_configfile())
"""

#
# from _typeshed import structseq
import sys
import os
import subprocess
import textwrap


print('')
print(os.path.basename(__file__) + ' - Builds the .rst files for the documentation')
print('')
start_dir = os.getcwd()

# find lib directory and import lib/item_conversion
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, '../lib')
# import item_conversion

# um im Test-build_doc Umfeld zu laufen:
sys.path.insert(0, '..')
sys.path.insert(0, '../lib')
import shyaml

type_unclassified = 'unclassified'
plugin_sections = [
    ['gateway', 'Gateway', 'Gateway'],
    ['interface', 'Interface', 'Interface'],
    ['protocol', 'Protocol', 'Protokoll'],
    ['system', 'System', 'System'],
    [type_unclassified, 'Non classified', 'nicht klassifizierte'],
    ['web', 'Web/Cloud', 'Web/Cloud'],
]


def bold(s):
    return '**' + s + '**' if s else ''


def get_list_fromgit(name: str):
    """get filelist via git and return all matching files at first directory level"""
    # this could be written as a single nested comprehension, but gets quite unreadable
    # we gain speedup by using comprehensions and not splitting twice
    plg_git = (
        subprocess.check_output(['git', 'ls-files', f'*/{name}'], stderr=subprocess.STDOUT)
        .decode()
        .strip('\n')
        .split('\n')
    )
    plglist = [x[0] for x in (p.split('/') for p in plg_git) if x[1] == name]
    return plglist


def get_pluginlist_fromgit():
    return get_list_fromgit('__init__.py')


def get_local_pluginlist():
    plglist = [x for x in os.listdir('.') if x[0] not in ['.', '_'] and x != 'deprecated_plugins']
    return plglist


def get_pluginyamllist_fromgit():
    return get_list_fromgit('plugin.yaml')


def get_description(section_dict, maxlen=70, lang='en', textkey='description'):
    desc = ''
    try:
        desc = section_dict[textkey]['lang']
    except Exception:
        pass
    if desc == '':
        try:
            lang2 = 'de' if lang == 'en' else 'en'
            desc = section_dict[textkey]['lang2']
        except Exception:
            pass

    if type(desc) is list:
        return desc

    lines = textwrap.wrap(desc, maxlen, break_long_words=False)
    return lines or ['']


def get_doc_description(yml, language, key='description', index=None):
    if index is None:
        # return description
        desc = get_description(yml, 1024, language, key + '_long')
        if desc[0] == '':
            desc = get_description(yml, 1024, language, key)
        return desc[0]
    else:
        # return entry of valid_description list
        desc = get_description(yml, 1024, language, key)
        if desc == ['']:
            return ''
        if len(desc) < index + 1:
            print(f'Zu kurze Liste {desc} für index {index}')
            return ''
        return desc[index]


def get_maintainer(section_dict, maxlen=20):
    maint = section_dict.get('maintainer', '')
    lines = textwrap.wrap(maint, maxlen, break_long_words=False)
    return lines or ['']


def get_tester(section_dict, maxlen=20):
    maint = section_dict.get('tester', '')
    try:
        lines = textwrap.wrap(str(maint), maxlen, break_long_words=False)
    except Exception:
        print()
        print(f'section_dict: {section_dict}, maint: {maint}')
        print()
        lines = []
    return lines or ['']


def get_docurl(section_dict, maxlen=70):
    maint = section_dict.get('documentation', '')
    lines = textwrap.wrap(maint, maxlen, break_long_words=True)
    return lines or ['']


def get_supurl(section_dict, maxlen=70):
    maint = section_dict.get('support', '')
    lines = textwrap.wrap(maint, maxlen, break_long_words=True)
    return lines or ['']


def html_escape(str):
    #    str = str.rstrip().replace('<', '&lt;').replace('>', '&gt;')
    #    str = str.rstrip().replace('(', '&#40;').replace(')', '&#41;')
    #    str = str.rstrip().replace("'", '&#39;').replace('"', '&quot;')
    html = (
        str.rstrip().replace('ä', '&auml;').replace('ö', '&ouml;').replace('ü', '&uuml;')
        if str
        else ''
    )
    return html


def build_pluginlist(plugin_type='all'):
    """
    Return a list of dicts with a dict for each plugin of the requested type
    The dict contains the plugin name, type and description
    """
    result = []
    plugin_type = plugin_type.lower()

    # avoid division by zero in for loop
    if not plugins_git:
        return []

    num_pl = len(plugins_git)
    count = 0

    for metaplugin in plugins_git:
        count += 1
        print(f'Lese Metadaten: {int(100 * count / num_pl)}%\r', end='')
        metafile = metaplugin + '/plugin.yaml'
        plg_dict = {}
        plgtype = type_unclassified
        if metaplugin in plugins_git:  # pluginsyaml_git
            if os.path.isfile(metafile):
                plugin_yaml = shyaml.yaml_load(metafile, ordered=True)
            else:
                plugin_yaml = ''
            if plugin_yaml != '':
                try:
                    section_dict = plugin_yaml.get('plugin')
                except Exception as e:
                    raise AttributeError(f"'{metafile}: Exception {e}")
                if section_dict is not None:
                    if section_dict.get('type'):
                        if section_dict.get('type').lower() in plugin_types:
                            plgtype = section_dict.get('type', type_unclassified).lower()
                            plg_dict['name'] = metaplugin.lower()
                            plg_dict['type'] = plgtype
                            plg_dict['desc'] = get_description(section_dict, 85, language)
                            plg_dict['maint'] = get_maintainer(section_dict, 15)
                            plg_dict['test'] = get_tester(section_dict, 15)
                            plg_dict['doc'] = html_escape(section_dict.get('documentation', ''))
                            plg_dict['sup'] = html_escape(section_dict.get('support', ''))
                    elif plugin_type == type_unclassified:
                        print(
                            f"not found: plugin type '{section_dict.get('type')}' defined in plugin '{metaplugin}'"
                        )

                if (plgtype == type_unclassified) and (plugin_yaml != ''):
                    plg_dict['name'] = metaplugin.lower()
                    plg_dict['type'] = type_unclassified
                    plg_dict['desc'] = get_description(section_dict, 85, language)
                    plg_dict['maint'] = get_maintainer(section_dict, 15)
                    plg_dict['test'] = get_tester(section_dict, 15)
                    plg_dict['doc'] = html_escape(section_dict.get('documentation', ''))
                    plg_dict['sup'] = html_escape(section_dict.get('support', ''))
                    print(f'unclassified: metafile = {metafile}, plg_dict = {plg_dict!s}')

                plg_dict['desc'].append('')
            else:
                plg_dict['name'] = metaplugin.lower()
                plg_dict['type'] = type_unclassified
                plg_dict['desc'] = ['No metadata (plugin.yaml) was provided for this plugin!']
                plg_dict['maint'] = ['']
                plg_dict['test'] = ['']
                plg_dict['doc'] = ''
                plg_dict['sup'] = ''

            # Adjust list lengths
            maxlen = max(len(plg_dict['desc']), len(plg_dict['maint']), len(plg_dict['test']))
            while len(plg_dict['desc']) < maxlen:
                plg_dict['desc'].append('')
            while len(plg_dict['maint']) < maxlen:
                plg_dict['maint'].append('')
            while len(plg_dict['test']) < maxlen:
                plg_dict['test'].append('')

        if (plgtype == plugin_type) or (plugin_type == 'all'):
            # result.append(metaplugin)
            result.append(plg_dict)
    print('\n')
    return result


def write_dummyfile(configfile_dir, namelist):
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


def write_heading(fh, heading, level):

    liner1 = '=' * len(heading)
    liner2 = ' - ' * len(heading)

    fh.write('\n')
    if level == 1:
        fh.write(liner1 + '\n')
    fh.write(heading + '\n')
    if level in [1, 2]:
        fh.write(liner1 + '\n')
    elif level == 3:
        fh.write(liner2 + '\n')
    fh.write('\n')

    return


def write_formatted(fh, str):

    for s in str.split('\\n'):
        if s.startswith(' '):
            if not s.startswith(' -'):
                s = s[1:]
        fh.write(s + '\n')
    fh.write('\n')


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
        desc = conf.get('name', conf.get('remark', '---'))
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
#   write_configfile


def write_configfile(plg, configfile_dir, language='de'):
    """
    Create a .rst file with configuration information for the passed plugin
    """
    #    lparameter_yaml = []
    #    no_lparameters = (lparameter_yaml == 'NONE')

    plgname = plg['name']

    # ---------------------------------
    # read metadata for plugin
    # ---------------------------------
    metafile = plgname + '/plugin.yaml'
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
    requirements = get_description(plugin_yaml, 768, language, 'requirements')
    min_version = str(plugin_yaml.get('sh_minversion', ''))
    max_version = str(plugin_yaml.get('sh_maxversion', ''))
    min_py_version = str(plugin_yaml.get('py_minversion', ''))
    max_py_version = str(plugin_yaml.get('py_maxversion', ''))
    if (
        requirements[0] != ''
        or min_version != ''
        or max_version != ''
        or min_py_version != ''
        or max_py_version != ''
    ):
        write_heading(fh, 'Anforderungen', 2)
        fh.write('\n')
        write_formatted(fh, get_doc_description(plugin_yaml, language, 'requirements'))
        if min_version != '':
            fh.write(' - Minimum SmartHomeNG Version: ' + bold(min_version) + '\n')
        if max_version != '':
            fh.write(' - Maximum SmartHomeNG Version: ' + bold(max_version) + '\n')
        if min_py_version != '':
            fh.write(' - Minimum Python Version: ' + bold(min_py_version) + '\n')
        if max_py_version != '':
            fh.write(' - Maximum Python Version: ' + bold(max_py_version) + '\n')

    # ---------------------------------
    # write supported hardware section
    # ---------------------------------
    hardware = get_description(plugin_yaml, 768, language, 'hardware')
    if hardware[0] != '':
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
                    desc = get_doc_description(
                        parameter_yaml[p], language, key='valid_list_description', index=index
                    )
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
                    desc = get_doc_description(
                        iattributes_yaml[a], language, key='valid_list_description', index=index
                    )
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
        for l in sorted(lparameter_yaml):
            # ---------------------------------
            # write info for one attribute
            # ---------------------------------
            write_heading(fh, l, 2)
            fh.write('\n')
            write_formatted(fh, get_doc_description(lparameter_yaml[l], language))
            datatype = lparameter_yaml[l].get('type', '').lower()
            default = str(lparameter_yaml[l].get('default', ''))
            validlist = lparameter_yaml[l].get('valid_list', [])
            validmin = lparameter_yaml[l].get('valid_min', '')
            validmax = lparameter_yaml[l].get('valid_max', '')
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
                        lparameter_yaml[l], language, key='valid_list_description', index=index
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
    fh.write(
        'Das Plugin verfügt über folgende öffentliche Funktionen, die z.B. in Logiken aufgerufen werden können.\n'
    )
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
                    desc = get_doc_description(
                        functions_yaml[f], language, key='valid_list_description', index=index
                    )
                    if desc != '':
                        desc = ' |_| - |_| ' + desc
                    fh.write('   - ' + bold(str(v)) + desc + '\n')
                fh.write('\n')

            # func_param_yaml = functions_yaml[f].get('parameters', None)
            if func_param_yaml is not None:
                for par in func_param_yaml:
                    write_heading(fh, par, 3)
                    write_formatted(fh, get_doc_description(func_param_yaml[par], language))
                    datatype = func_param_yaml[par].get('type', '').lower()
                    default = str(func_param_yaml[par].get('default', ''))
                    validlist = func_param_yaml[par].get('valid_list', [])
                    validmin = func_param_yaml[par].get('valid_min', '')
                    validmax = func_param_yaml[par].get('valid_max', '')
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
                                func_param_yaml[par],
                                language,
                                key='valid_list_description',
                                index=index,
                            )
                            if desc != '':
                                desc = ' |_| - |_| ' + desc
                            fh.write('   - ' + bold(str(v)) + desc + '\n')
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

    global language
    language = 'en'

    if 'de' in sys.argv:
        language = 'de'
    if 'en' in sys.argv:
        language = 'en'

    global docu_type
    docu_type = start_dir.split('/')[-1:][0]  # developer / user

    print('Creating the configuration documentation pages for the plugins')
    print('Start directory        = ' + start_dir)
    print('Documentation type     = ' + docu_type)
    print('Documentation language = ' + language)
    print('')

    # change the working diractory to the directory from which the converter is loaded (../tools)
    os.chdir(os.path.dirname(os.path.abspath(os.path.basename(__file__))))

    plugindirectory = '../plugins'
    pluginabsdirectory = os.path.abspath(plugindirectory)

    os.chdir(pluginabsdirectory)

    plugins_git = get_pluginlist_fromgit()
    if 'xmpp' not in plugins_git:
        plugins_git.append('xmpp')

    print('--- Liste der Plugins auf github (' + str(len(plugins_git)) + '):')

    pluginsyaml_git = get_pluginyamllist_fromgit()
    #    if not 'xmpp' in plugins_git:
    #        plugins_git.append('xmpp')

    print('--- Liste der Plugins mit Metadaten auf github (' + str(len(pluginsyaml_git)) + '):')
    print()

    if docu_type == 'doc':
        plugin_rst_dir = os.path.join(start_dir, 'user', 'source')
    else:
        plugin_rst_dir = os.path.join(start_dir, 'source')
    print('zu schreiben in: ' + plugin_rst_dir)

    plugin_types = []
    for pl in plugin_sections:
        plugin_types.append(pl[0])

    configfile_dir = plugin_rst_dir + '/' + 'plugins_doc/config'
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
        plugins_git = plugins_new
    else:
        os.makedirs(configfile_dir)
    print('\n')

    print(f'zu schreiben: {len(plugins_git)} Dateien, {skip} noch aktuell')

    plglist = build_pluginlist()

    dummy_list = []
    print()
    for plg in plglist:
        write_configfile(plg, configfile_dir, language)
        print(f'plugin {plg["name"]}: ./config/{plg["name"]}.rst', ' ' * 20, end='\r')
        dummy_list.append(plg['name'])
    write_dummyfile(configfile_dir, dummy_list)
    print(' ' * 50)
    print()
