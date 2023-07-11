#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2018-       Martin Sinn                         m.sinn@gmx.de
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
This script creates a list showing the care status of the metadata file
of the plugins on the .../plugins folder.

The result is printed to stdout
"""

import os
import argparse

VERSION = '1.8.3'

start_dir = os.getcwd()

import sys
# find lib directory and import lib/item_conversion
os.chdir(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, '..')
sys.path.insert(0, '../lib')
import shyaml


type_unclassified = 'unclassified'
plugin_sections = [ ['gateway', 'Gateway', 'Gateway'],
                    ['interface', 'Interface', 'Interface'],
                    ['protocol', 'Protocol', 'Protokoll'],
                    ['system', 'System', 'System'],
                    [type_unclassified, 'Non classified', 'nicht klassifizierte'],
                    ['web', 'Web/Cloud', 'Web/Cloud']
                  ]

MISSING_TEXT = 'Missing'

# ==================================================================================
#   Functions of the tool
#

def get_local_pluginlist(pluginsdirectory=None):
    if pluginsdirectory is None:
        plglist = os.listdir('.')
    else:
        plglist = os.listdir(pluginsdirectory)

    for entry in plglist:
        if os.path.isfile(entry):
            plglist.remove(entry)
    for entry in plglist:
        if entry[0] in ['.' ,'_'] or entry == 'deprecated_plugins':
            plglist.remove(entry)
    for entry in plglist:
        if entry[0] in ['.' ,'_']:
            plglist.remove(entry)
    for entry in plglist:
        if entry.lower().endswith('.md') or entry.lower().endswith('.rst'):
            plglist.remove(entry)
    #for entry in plglist:
    #    if entry[0] in ['.' ,'_']:
    #        plglist.remove(entry)
    return sorted(plglist)


def get_plugintype(plgName):

    fn = './'+plgName+'/__init__.py'
    try:
        with open(fn, "r") as myfile:
            code = myfile.read()
    except:
        return 'None' \
               ''
    if (code.find('(SmartPlugin') == -1) and (code.find('( SmartPlugin') == -1) and \
       (code.find('(MqttPlugin') == -1) and (code.find('( MqttPlugin') == -1):
        return 'Classic'
    return 'Smart'



def readMetadata(metaplugin, plugins_local):

    metafile = metaplugin + '/plugin.yaml'
    plg_dict = {}
    plugin_yaml = {}
    if metaplugin in plugins_local:  # pluginsyaml_local
        if os.path.isfile(metafile):
            try:
                plugin_yaml = shyaml.yaml_load(metafile, ordered=True)
            except KeyboardInterrupt:
                exit(0)
    else:
        print("There is no plugin named '" + metaplugin + "'")
        print()
        return None
    return plugin_yaml


# ==================================================================================
#   Functions to list plugin information
#

def list_formatted(plugin, plgvers, plgstate, plgtype, plgGlobal, plgParams, plgAttr, plgFunc='', plgLog='', list_versions=False):
    if plgstate == 'qa-passed':
        plgstate = 'qa-pass'
    if not list_versions:
        print('{plugin:<14.14} {plgvers:<8.8} {plgstate:<7.7} {plgtype:<5.5} {plgGlobal:<7.7} {plgParams:<7.7} {plgAttr:<10.10} {plgFunc:<7.7} {plgLog:<7.7}'
              .format( plugin=plugin,
                       plgvers=plgvers,
                       plgstate=plgstate,
                       plgtype=plgtype,
                       plgGlobal=plgGlobal,
                       plgParams=plgParams,
                       plgAttr=plgAttr,
                       plgFunc=plgFunc, plgLog=plgLog))
    else:
        print('{plugin:<14.14} {plgvers:<8.8} {plgstate:<7.7} {plgtype:<7.7} {plgShngMin:<9.9} {plgShngMax:<9.9} {plgPyMin:<9.9} {plgPyMax:<9.9}'
              .format( plugin=plugin,
                       plgvers=plgvers,
                       plgstate=plgstate,
                       plgtype=plgtype,
                       plgShngMin=plgGlobal,
                       plgShngMax=plgParams,
                       plgPyMin=plgAttr,
                       plgPyMax=plgFunc))


def list_plugins(option, suboption=None, list_versions=False):

    option = option.strip().lower()
    if suboption:
        suboption = suboption.strip().lower()

    plugins_local = get_local_pluginlist()

    header_displayed = False
    plgcount = 0
    allplgcount = 0
    priv_plgcount = 0
    priv_allplgcount = 0
    for plg in sorted(plugins_local):
        version = '-'
#        sectionPlg = '-'
        sectionParam = '-'
        sectionIAttr = '-'
        sectionFunc = '-'
        sectionLogics = '-'
        sectionIStruct = ''
        comment = ''
        shng_min_vers = '?'
        shng_max_vers = '?'
        py_min_vers = '?'
        py_max_vers = '?'
        metadata = readMetadata(plg, plugins_local)
        if metadata == None:
            return
        if metadata.get('plugin', None) == None:
            sectionPlg = MISSING_TEXT
            plgstate = 'NOMETA'
        else:
            sectionPlg = 'Ok'
            version = metadata['plugin'].get('version', '-')
            plgstate = metadata['plugin'].get('state', '-')
            if not plgstate in ['qa-passed', 'ready', 'develop', 'deprecated']:
                plgstate = 'INVALID'
            shng_min_vers = str(metadata['plugin'].get('sh_minversion', '-'))
            shng_max_vers = str(metadata['plugin'].get('sh_maxversion', '-'))
            py_min_vers = str(metadata['plugin'].get('py_minversion', '-'))
            py_max_vers = str(metadata['plugin'].get('py_maxversion', '-'))
        plgtype = get_plugintype(plg)
        if plgtype == 'Smart':
            if version == '-':
                version = '?'

            if metadata.get('parameters', None) == None:
                sectionParam = MISSING_TEXT
            elif metadata.get('parameters', None) == 'NONE':
                sectionParam = 'Ok'
            else:
                sectionParam = 'Ok'
                sectionParam += ' (' + str(len(metadata['parameters'])) + ')'

            if metadata.get('item_attributes', None) == None:
                sectionIAttr = MISSING_TEXT
            elif metadata.get('item_attributes', None) == 'NONE':
                sectionIAttr = 'Ok'
            else:
                sectionIAttr = 'Ok'
                sectionIAttr += ' (' + str(len(metadata['item_attributes'])) + ')'

            if metadata.get('item_structs', None) == None:
                sectionIStruct = ''
            elif metadata.get('item_structs', None) == 'NONE':
                sectionIStruct = ''
            else:
                sectionIStruct = ',St'

            if metadata.get('item_attributes', None) == None:
                sectionIAttr = MISSING_TEXT
            elif metadata.get('item_attributes', None) == 'NONE':
                sectionIAttr = 'Ok'
            else:
                sectionIAttr = 'Ok'
                sectionIAttr += ' (' + str(len(metadata['item_attributes'])) + sectionIStruct + ')'

            if metadata.get('plugin_functions', None) == None:
                sectionFunc = MISSING_TEXT
            elif metadata.get('plugin_functions', None) == 'NONE':
                sectionFunc = 'Ok'
            else:
                sectionFunc = 'Ok'
                sectionFunc += ' (' + str(len(metadata['plugin_functions'])) + ')'

            if metadata.get('logic_parameters', None) == None:
                sectionLogics = MISSING_TEXT
            elif metadata.get('logic_parameters', None) == 'NONE':
                sectionLogics = 'Ok'
            else:
                sectionLogics = 'Ok'
                sectionLogics += ' (' + str(len(metadata['logic_parameters'])) + ')'

        if (option == 'all') or \
           (option == 'state' and plgstate.lower() == suboption) or \
           (option == 'state' and suboption == 'other' and (plgstate.lower() not in ['qa-passed', 'ready', 'develop', 'deprecated'])) or \
           (option == plgtype.lower()) or \
           (option == 'inc' and (plgstate == 'INVALID' or sectionPlg == MISSING_TEXT or sectionParam == MISSING_TEXT or sectionIAttr == MISSING_TEXT or sectionFunc == MISSING_TEXT or sectionLogics == MISSING_TEXT)) or \
           (option == 'compl' and (plgtype.lower() != 'classic' and sectionPlg != MISSING_TEXT and sectionParam != MISSING_TEXT and sectionIAttr != MISSING_TEXT and sectionFunc != MISSING_TEXT) and (sectionLogics != MISSING_TEXT)) or \
           (option == 'inc_para' and sectionParam == MISSING_TEXT) or (option == 'inc_attr' and sectionIAttr == MISSING_TEXT):
            if not list_versions:
                if not header_displayed:
                    ul = '-------------------------------'
                    list_formatted('',       '',        '',      'Plugin', '',     'Plugin', 'Item',    'Plugin', 'Plugin')
                    list_formatted('Plugin', 'Version', 'State', 'Type',   'Info', 'Params', 'Attrib.', 'Funct.', 'Logics')
                    list_formatted(ul, ul, ul, ul, ul, ul, ul, ul, ul)
                    header_displayed = True
                list_formatted(plg, version, plgstate, plgtype, sectionPlg, sectionParam, sectionIAttr, sectionFunc, sectionLogics)
            else:
#----
                if not header_displayed:
                    ul = '-------------------------------'
                    list_formatted('',       '',        '',      'Plugin', 'shng',       'shng',       'Python', 'Python', list_versions=True)
                    list_formatted('Plugin', 'Version', 'State', 'Type',   'min. Vers.', 'max. Vers.', 'min. Vers.', 'max. Vers.', list_versions=True)
                    list_formatted(ul, ul, ul, ul, ul, ul, ul, ul, list_versions=True)
                    header_displayed = True
                list_formatted(plg, version, plgstate, plgtype, shng_min_vers, shng_max_vers, py_min_vers, py_max_vers, list_versions=True)
#----
            plgcount += 1
            if plg.startswith('priv_'):
                priv_plgcount += 1
        allplgcount += 1
        if plg.startswith('priv_'):
            priv_allplgcount += 1
    print()
    if (option != 'all'):
        if priv_plgcount > 0:
            print("{} ({}) plugins of ".format(plgcount, plgcount+priv_plgcount), end='')
        else:
            print("{} plugins of ".format(plgcount), end='')
    if priv_allplgcount > 0:
        print("{} ({}) plugins total".format(allplgcount, allplgcount+priv_allplgcount))
    else:
        print("{} plugins total".format(allplgcount))

    print()
    return


# ==================================================================================
#   Functions to display information of one plugin
#

def disp_formatted(lbl, val):
    val = val.replace('\n', ' ')
    print('{lbl:<19.19} {val:<55.55}'.format(lbl=lbl, val=val))
    while len(val) > 55:
        val = val[55:]
        print('{lbl:<19.19} {val:<55.55}'.format(lbl='', val=val))


def disp_formatted2(lbl, typ, val=''):
    print('{lbl:<19.19}{typ:<12.12} {val:<48.48}'.format(lbl=lbl, typ=typ, val=val))
    while len(val) > 48:
        val = val[48:]
        print('{lbl:<19.19}{typ:<13.13}{val:<48.48}'.format(lbl='', typ='', val=val))


def disp_formatted3(lbl, typ, val=''):
    print('{lbl:<22.22}{typ:<55.55}'.format(lbl=lbl, typ=typ))
    emptyline = False
    while len(typ) > 55:
        emptyline = True
        typ = typ[55:]
        print('{lbl:<22.22}{typ:<55.55}'.format(lbl='', typ=typ))
    if emptyline:
        print()

def display_definition(name, dict):

    val = ''
    val2 = ''
    if dict.get('mandatory', False) == True:
        val += 'Mandatory'
    if dict.get('default', None) != None:
        if val != '':
            val += ', '
        if dict.get('default', None) == 'None*':
            val += "default=None"
        else:
            val += "default='" + str(dict.get('default', None)) + "'"
    if dict.get('valid_min', None) != None:
        if val != '':
            val += ', '
        val += "valid_min='" + str(dict.get('valid_min', None)) + "'"
    if dict.get('valid_max', None) != None:
        if val != '':
            val += ', '
        val += "valid_max='" + str(dict.get('valid_max', None)) + "'"
    if dict.get('valid_list', None) != None:
        if val != '':
            val += ', '
        val += "valid_list=" + str(dict.get('valid_list', None))
    disp_formatted2(name, dict.get('type', 'foo'), val)


def display_struct_definition(name, dict):

    val = ''
    val2 = ''
    if dict.get('default', None) != None:
        if val != '':
            val += ', '
        if dict.get('default', None) == 'None*':
            val += "default=None"
        else:
            val += "default='" + str(dict.get('default', None)) + "'"
    disp_formatted3(name, dict.get('name', '-'), val)


def display_def_description(name, dict):
    if name != '':
        print(name)
    if dict.get('description', None) != None:
        disp_formatted('- Description (DE)', dict['description'].get('de', '-'))
        disp_formatted('- Description (EN)', dict['description'].get('en', '-'))


def display_metadata(plg, with_description):

    plg_type = get_plugintype(plg)
    plugins_local = get_local_pluginlist()
    metadata = readMetadata(plg, plugins_local)
    if metadata == None:
        return
    print("Display metadata for {} plugin '{}'".format(plg_type, plg))
    print()

    if metadata.get('plugin', None) == None:
        print("ERROR: Section 'plugin' not defined in metadata")
        print()
    else:
        if metadata['plugin'].get('description', None) != None:
            disp_formatted('Description (DE)', metadata['plugin']['description'].get('de', '-'))
            disp_formatted('Description (EN)', metadata['plugin']['description'].get('en', '-'))
            print()

        disp_formatted('Version', metadata['plugin'].get('version', '-'))
        disp_formatted('State', metadata['plugin'].get('state', '-'))
        disp_formatted('Type', metadata['plugin'].get('type', '-'))
        disp_formatted('Multi Instance', str(metadata['plugin'].get('multi_instance', '-')))
        disp_formatted('Restartable', str(metadata['plugin'].get('restartable', '-')))
        disp_formatted('shNG min. Version', str(metadata['plugin'].get('sh_minversion', '-')))
        disp_formatted('shNG max. Version', str(metadata['plugin'].get('sh_maxversion', '-')))
        disp_formatted('Python min. Version', str(metadata['plugin'].get('py_minversion', '-')))
        disp_formatted('Python max. Version', str(metadata['plugin'].get('py_maxversion', '-')))
        disp_formatted('Classname', metadata['plugin'].get('classname', '-'))

        disp_formatted('Maintainer', metadata['plugin'].get('maintainer', '-'))
        disp_formatted('Tester', metadata['plugin'].get('tester', '-'))
        disp_formatted('Keywords', metadata['plugin'].get('keywords', '-'))
        disp_formatted('Documentation', metadata['plugin'].get('documentation', '-'))
        disp_formatted('Support', metadata['plugin'].get('support', '-'))
        print()



    if plg_type == 'Classic':
        return

    # Display section 'parameters'
    if metadata.get('parameters', None) == None:
        print("ERROR: Section 'parameters' not defined in metadata")
        print()
    elif metadata.get('parameters', None) == 'NONE':
        print("Parameters")
        print("----------")
        print("No parameters defined for this plugin")
        print()
    else:
        print("Parameters")
        print("----------")
        for par in metadata.get('parameters', None):
            par_dict = metadata['parameters'][par]
            display_definition(par, par_dict)
        print()
        if with_description:
            for par in metadata.get('parameters', None):
                par_dict = metadata['parameters'][par]
                display_def_description(par, par_dict)
            print()

    # Display section 'item_attributes'
    if metadata.get('item_attributes', None) == None:
        print("ERROR: Section 'item_attributes' not defined in metadata")
        print()
    elif metadata.get('item_attributes', None) == 'NONE':
        print("Item Attributes")
        print("---------------")
        print("No item attributes defined for this plugin")
        print()
    else:
        print("Item Attributes")
        print("---------------")
        for attr in metadata.get('item_attributes', None):
            attr_dict = metadata['item_attributes'][attr]
            display_definition(attr, attr_dict)
        print()
        if with_description:
            for attr in metadata.get('item_attributes', None):
                attr_dict = metadata['item_attributes'][attr]
                display_def_description(attr, attr_dict)
            print()

    # Display section 'item_structs'
    if metadata.get('item_structs', None) == None:
        print("ERROR: Section 'item_structs' not defined in metadata")
        print()
    elif metadata.get('item_structs', None) == 'NONE':
        print("Item Structs")
        print("------------")
        print("No item item_structs defined for this plugin")
        print()
    else:
        print("Item Structs")
        print("------------")
        for attr in metadata.get('item_structs', None):
            attr_dict = metadata['item_structs'][attr]
            display_struct_definition(attr, attr_dict)
        print()

    # Display section 'plugin_functions'
    if metadata.get('plugin_functions', None) == None:
        print("ERROR: Section 'plugin_functions' not defined in metadata")
        print()
    elif metadata.get('plugin_functions', None) == 'NONE':
        print("Plugin Functions")
        print("----------------")
        print("No functions have been defined for this plugin")
        print()
    else:
        print("Plugin Functions")
        print("----------------")
        for func in metadata.get('plugin_functions', None):
            func_dict = metadata['plugin_functions'][func]
            display_definition(func, func_dict)
            if with_description:
                display_def_description('', func_dict)
            if func_dict.get('parameters', None) != None:
                print("Parameters:")
                for param in func_dict.get('parameters', None):
                    param_dict = func_dict['parameters'][param]
                    display_definition(param, param_dict)
                    if with_description:
                        if param_dict.get('description', None) != None:
                            disp_formatted('- Description (DE)', param_dict['description'].get('de', '-'))
                            disp_formatted('- Description (EN)', param_dict['description'].get('en', '-'))
            print()
        print()

    return


# ==================================================================================
#   Functions to check the information of one plugin
#

errors = 0
warnings = 0
hints = 0
quiet = False

def disp_error_formatted_alt(level, msg):
    if level != '':
        level += ':'
    print('{level:<8.8} {msg:<65.65}'.format(level=level, msg=msg))
    while len(msg) > 65:
        msg = msg[65:]
        print('{level:<8.8} {msg:<65.65}'.format(level='', msg=msg))
    return


def disp_error_formatted(level, msg):
    if level != '':
        level += ':'

    words = msg.split()
    while len(words) > 0:
        line = ''

        while (len(words) > 0) and (len(line) + 1 + len(words[0]) <= 65):
            if len(line) > 0:
                line += ' '
            line += words[0]
            words.pop(0)

        print(f"{level:<8.8} {line:<65.65}")
        level = ''

    return


def disp_hints_formatted(hint, hint2):
    if hint != '':
        print()
        disp_error_formatted('', hint)
        if hint2 != '':
            print()
            disp_error_formatted('', hint2)
    print()


def disp_error(msg, hint='', hint2=''):
    global errors, quiet
    errors += 1
    if not quiet:
        disp_error_formatted('ERROR', msg)
        disp_hints_formatted(hint, hint2)
    return


def disp_warning(msg, hint='', hint2=''):
    global warnings, quiet
    warnings += 1
    if not quiet:
        disp_error_formatted('WARNING', msg)
        disp_hints_formatted(hint, hint2)
    return


def disp_hint(msg, hint='', hint2=''):
    global hints, quiet
    hints += 1
    if not quiet:
        disp_error_formatted('HINT', msg)
        disp_hints_formatted(hint, hint2)
    return


errors = 0
warnings = 0
hints = 0


def is_dict(test_dict):
    if test_dict is None:
        return False
    return (type(test_dict) is dict) or (str(type(test_dict)) == "<class 'collections.OrderedDict'>")


def test_description(section, par, par_dict):
    if not is_dict(par_dict):
        de = ''
        en = ''
    else:
        de = par_dict.get('de', '')
        en = par_dict.get('en', '')
    if par != '':
        par = " '" + par + "'"
    if de == '' and en == '':
        disp_error("No description of the "+section + par + " is given",
                   "Add the section 'description:' to the "+section+"'s section and fill the needed values")
    else:
        if de == '':
            disp_warning("No german description of the "+section+ par + " is given",
                         "Add 'de:' to the description section of the "+section+"")
        if en == '':
            disp_warning("No english description of the "+section + par + " is given",
                         "Add 'en:' to the description section of the "+section+"")
    return


def print_errorcount(checkname, errors, warnings, hints):

    disp_str = checkname + ': '
    if errors == 1:
        disp_str += f"{errors} error, "
    else:
        disp_str += f"{errors} errors, "
    if warnings == 1:
        disp_str += f"{warnings} warning, "
    else:
        disp_str += f"{warnings} warnings, "
    if hints == 1:
        disp_str += f"{hints} hint"
    else:
        disp_str += f"{hints} hints"

    print(disp_str)


def check_metadata(plg, with_description, check_quiet=False, only_inc=False, list_classic=False, pluginsdirectory=None, suppress_summery=False):

    global errors, warnings, hints, quiet
    quiet = check_quiet
    errors = 0
    warnings = 0
    hints = 0

    plg_type = get_plugintype(plg).lower()
    plugins_local = get_local_pluginlist(pluginsdirectory)
    metadata = readMetadata(plg, plugins_local)
    if metadata == None:
        return
    if not check_quiet:
        print(f"*** Check metadata of {plg_type}-plugin '{plg}' (plugin.yaml):")
        print()

    # Checking plugin name
    maxlen = 12
    if len(plg) > maxlen:
        disp_warning(f"A plugin name should not be longer than {maxlen} characters.", f"The plugin name '{plg}' is {len(plg)} characters long")
    if plg != plg.lower():
        disp_error(f"Invalid plugin name '{plg}'.", f"Plugin names have to be lower case. Use '{plg.lower()}' instead")

    # Checking global metadata
    if metadata.get('plugin', None) == None:
        disp_error("No global metadata defined", "Make sure to create a section 'plugin' and fill it with the necessary entries", "Take a look at the plugin development documentation of SmartHomeNG")
        return
    else:
        if metadata['plugin'].get('version', None) == None:
            disp_error('No version number given', "Add 'version:' to the plugin section")
        if metadata['plugin'].get('classname', None) == None:
            disp_error('No classname for the plugin', "Add 'classname:' to the plugin section and set it to the name of the Python class that implements the plugin")

        if metadata['plugin'].get('type', None) == None:
            disp_warning('No plugin type set', "Add 'type:' to the plugin section")
        if metadata['plugin'].get('maintainer', None) == None:
            disp_warning('The maintainer of the plugin is not documented', "Add 'maintainer:' to the plugin section")

    if (plg_type != 'classic' and not list_classic):

        if metadata.get('plugin', None) is None:
            disp_error("No section 'plugin' in metadata found")
        else:
            if metadata['plugin'].get('state', None) == None:
                disp_error('No development state given for the plugin', "Add 'state:' to the plugin section and set it to one of the following values ['develop', 'ready', 'qa-passed']", "The state'qa-passed' should only be set by the shNG core team")
            elif not metadata['plugin'].get('state', None) in ['qa-passed', 'ready', 'develop', 'deprecated', '-']:
                disp_error('An invalid development state is given for the plugin', "Set'state:' to one of the followind valid values ['develop', 'ready', 'qa-passed', 'deprecated']", "The state'qa-passed' should only be set by the shNG core team")

            doc_url = metadata['plugin'].get('documentation', '')
            if doc_url is None:
                    disp_error("The 'documentation' parameter in section 'plugin' is explicitly declared as None - That is not allowed",
                               "The parameter has to be an empty string or has to be omitted, if no documentation link should be configured.")
            if (doc_url is not None) and (doc_url != ''):
                if doc_url.endswith(f"plugins/{plg}/user_doc.html"):
                    disp_hint("The 'documentation' parameter in section 'plugin' should not contain an url to the SmartHomeNG documentation (user_doc)",
                                 "The 'documentation' parameter is optional and only to be used to link to additional documentation outside of SmartHomeNG", "If there is no additional documentation, leave this parameter empty")
                elif doc_url.endswith(f"plugins_doc/config/{plg}.html"):
                    disp_warning("The 'documentation' parameter in section 'plugin' should not contain an url to the SmartHomeNG documentation (configuration)",
                                 "The 'documentation' parameter is optional and only to be used to link to additional documentation outside of SmartHomeNG", "If there is no additional documentation, leave this parameter empty")

            if metadata['plugin'].get('support', '') == '':
                disp_hint("The 'support' parameter is empty.", "Is there no support thread for this plugin in the knx-user-forum?", "Enter the url to the support thread in the 'support' parameter.")

            if metadata['plugin'].get('multi_instance', None) == None:
                disp_warning('It is not documented if wether the plugin is multi-instance capable or not', "Add 'multi_instance:' to the plugin section")
            else:
                if not(metadata['plugin'].get('multi_instance', None) in [True, False]):
                    disp_error('multi_instance has to be True or False')
            if metadata['plugin'].get('restartable', None) == None:
                disp_hint('It is not documented if wether the plugin is restartable or not [stop() and run()]', "Add 'restartable:' to the plugin section")
            else:
                if not(metadata['plugin'].get('restartable', None) in [True, False, 'True', 'False', 'unknown']):
                    disp_error('restartable has to be True, False or unknown')
            if metadata['plugin'].get('sh_minversion', None) == None:
                disp_warning('No minimum version of the SmartHomeNG core given that is needed to run the plugin', "Add 'sh_minversion:' to the plugin section")

            if metadata['plugin'].get('tester', None) == None:
                disp_hint('The tester(s) of the plugin are not documented', "Add 'tester:' to the plugin section")

        # Checking parameter metadata
        if metadata.get('parameters', None) == None:
            disp_error("No parameters defined in metadata", "When defining parameters, make sure that you define ALL parameters of the plugin, but dont define global parameters like 'instance'. If only a part of the parameters are defined in the metadata, the missing parameters won't be handed over to the plugin at runtime.", "If the plugin has no parameters, document this by writing 'parameters: NONE' to the metadata file.")

        # Checking item attribute metadata
        if metadata.get('item_attributes', None) == None:
            disp_error("No item attributes defined in metadata", "If the plugin defines no item attributes, document this by creating an empty section. Write 'item_attributes: NONE' to the metadata file.")

        # Checking item struct definitions
        if metadata.get('item_structs', None) == None:
            disp_hint("No item structures defined in metadata", "If the plugin defines no item structures, document this by creating an empty section. Write 'item_structs: NONE' to the metadata file.")


        # Checking function metadata
        if metadata.get('plugin_functions', None) == None:
            disp_error("No public functions of the plugin defined in metadata", "If the plugin defines no public functions, document this by creating an empty section. Write 'plugin_functions: NONE' to the metadata file.")

        # Checking logic parameter metadata
        if metadata.get('logic_parameters', None) == None:
            disp_error("No logic parameters defined in metadata", "If the plugin defines no logic parameters, document this by creating an empty section. Write 'logic_parameters: NONE' to the metadata file.")

        # Checking if the descriptions are complete
        if metadata.get('plugin', None) != None:
            test_description('plugin', '', metadata['plugin'].get('description', None))

        if metadata.get('parameters', None) != None:
            if metadata.get('parameters', None) != 'NONE':
                for par in metadata.get('parameters', None):
                    if par.lower() in ['instance', 'webif_pagelength']:
                        disp_warning(f"parameter '{par}' should not be defined in the plugin", f"Parameter '{par}' is a globaly defined plugin parameter. You should not explicitly define it in your plugin '{plg}'")
                    else:
                        par_dict = metadata['parameters'][par]
                        if not is_dict(par_dict):
                            disp_error("Definition of parameter '{}' is not a dict".format(par), '')
                        else:
                            if par_dict.get('mandatory', False) != False and par_dict.get('default', None) != None:
                                disp_error("parameter '{}': mandatory and default cannot be used together".format(par), "If mandatory and a default value are specified togeather, mandatory has no effect, since a value for the parameter is already specified (the default value).")
                            test_description('parameter', par, par_dict.get('description', None))

        if metadata.get('item_attributes', None) != None:
            if metadata.get('item_attributes', None) != 'NONE':
                for par in metadata.get('item_attributes', None):
                    par_dict = metadata['item_attributes'][par]
                    if not is_dict(par_dict):
                        disp_error("Definition of item_attribute '{}' is not a dict".format(par), '')
                    else:
                        if par_dict.get('mandatory', False) != False and par_dict.get('default', None) != None:
                            disp_error("item '{}': mandatory and default cannot be used together".format(par), "If mandatory and a default value are specified togeather, mandatory has no effect, since a value for the parameter is already specified (the default value).")
                        test_description('item attribute', par, par_dict.get('description', None))

        if metadata.get('item_structs', None) != None:
            if metadata.get('item_structs', None) != 'NONE':
                for par in metadata.get('item_structs', None):
                    par_dict = metadata['item_structs'][par]
                    if not is_dict(par_dict):
                        disp_error("Definition of item_structs '{}' is not a dict".format(par), '')
                    else:
                        pass

        if metadata.get('plugin_functions', None) != None:
            if metadata.get('plugin_functions', None) != 'NONE':
                for func in metadata.get('plugin_functions', None):
                    func_dict = metadata['plugin_functions'][func]
                    test_description('plugin function', func, func_dict.get('description', None))

                    # Check function parameters
                    if func_dict.get('parameters', None) != None:
                        for par in func_dict.get('parameters', None):
                            par_dict = func_dict['parameters'][par]
                            test_description("parameter '"+par+"' of plugin function", func, par_dict.get('description', None))

    state = ''
    if metadata.get('plugin', None) != None:
        state = metadata['plugin'].get('state', '-')

    if (plg_type == 'classic' and list_classic) or (plg_type != 'classic' and not list_classic):
        #    global errors, warnings, hints
        if errors == 0 and warnings == 0 and hints == 0:
            res = 'OK'
        elif errors == 0 and warnings == 0:
            res = 'HINTS'
        else:
            res = 'TO DOs'
        if check_quiet:
            if not suppress_summery:
                if not(only_inc) or (only_inc and (errors!=0 or warnings!=0 or hints!=0 or state == '-')):
                    if state == 'qa-passed':
                        state = 'qa-pass'
                    summary = "{:<8.8} {:<7.7} {:<5.5} {:<8.8} {:<7.7} {}".format(res, state, plg_type, str(errors), str(warnings), str(hints))
                    print('{plugin:<14.14} {summary:<60.60}'.format(plugin=plg, summary=summary))
        else:
            if errors == 0 and warnings == 0 and hints == 0:
                print_errorcount('Metadata is complete', errors, warnings, hints)
            else:
                print_errorcount('Metadata', errors, warnings, hints)
            print()
    return


def check_plglist(option, list_classic=False):
    option = option.strip().lower()
    header_displayed = False;
    plgcount = 0
    allplgcount = 0
    priv_plgcount = 0
    priv_allplgcount = 0

    plugins_local = get_local_pluginlist()
    for plg in sorted(plugins_local):
        version = '-'
#        sectionPlg = '-'
        sectionParam = '-'
        sectionIAttr = '-'
        sectionFunc = '-'
        comment = ''
        metadata = readMetadata(plg, plugins_local)
        if metadata == None:
            return
        if metadata.get('plugin', None) == None:
            sectionPlg = MISSING_TEXT
        else:
            sectionPlg = 'Ok'
            version = metadata['plugin'].get('version', '-')
            plgstate = metadata['plugin'].get('state', '-')
            if not plgstate in ['qa-passed', 'ready', 'develop', '-']:
                plgstate = 'INVALID'
        plgtype = get_plugintype(plg)
        if plgtype == 'Smart':
            if version == '-':
                version = '?'

            if metadata.get('parameters', None) == None:
                sectionParam = MISSING_TEXT
            elif metadata.get('parameters', None) == 'NONE':
                sectionParam = 'Ok'
            else:
                sectionParam = 'Ok'
                sectionParam += ' (' + str(len(metadata['parameters'])) + ')'

            if metadata.get('item_attributes', None) == None:
                sectionIAttr = MISSING_TEXT
            elif metadata.get('item_attributes', None) == 'NONE':
                sectionIAttr = 'Ok'
            else:
                sectionIAttr = 'Ok'
                sectionIAttr += ' (' + str(len(metadata['item_attributes'])) + ')'

            if metadata.get('plugin_functions', None) == None:
                sectionFunc = MISSING_TEXT
            elif metadata.get('plugin_functions', None) == 'NONE':
                sectionFunc = 'Ok'
            else:
                sectionFunc = 'Ok'
                sectionFunc += ' (' + str(len(metadata['plugin_functions'])) + ')'

        if (option == 'all') or (option == 'inc') or \
           (option == plgtype.lower()) or \
           (option == 'incX' and (sectionPlg == MISSING_TEXT or sectionParam == MISSING_TEXT or sectionIAttr == MISSING_TEXT or sectionFunc == MISSING_TEXT)) or \
           (option == 'compl' and (plgtype.lower() != 'classic' and sectionPlg != MISSING_TEXT and sectionParam != MISSING_TEXT and sectionIAttr != MISSING_TEXT and sectionFunc != MISSING_TEXT)) or \
           (option == 'inc_para' and sectionParam == MISSING_TEXT) or (option == 'inc_attr' and sectionIAttr == MISSING_TEXT):
            if not header_displayed:
                ul = '-------------------------------'
                list_formatted('',       '',        '',      'Plugin', '',       '',         '',          '')
                list_formatted('Plugin', 'Summary', 'State', 'Type',   'Errors', 'Warnings', 'Hints', '', '')
                list_formatted(ul, ul, ul, ul, ul, ul, ul, '', '')
                header_displayed = True


            check_metadata(plg, False, check_quiet=True, only_inc=(option == 'inc'), list_classic=list_classic)
            if option == 'inc' and (errors > 0 or warnings > 0 or hints > 0):
                if ((not list_classic) and (plgtype.lower() != 'classic')) or (
                        list_classic and (plgtype.lower() == 'classic')):
                    plgcount += 1
                    if plg.startswith('priv_'):
                        priv_plgcount += 1
            elif option != 'inc':
                if ((not list_classic) and (plgtype.lower() != 'classic')) or (
                        list_classic and (plgtype.lower() == 'classic')):
                    plgcount += 1
                    if plg.startswith('priv_'):
                        priv_plgcount += 1

        allplgcount += 1
        if plg.startswith('priv_'):
            priv_allplgcount += 1
    print()

    if (option != 'all'):
        if priv_plgcount > 0:
            print("{} ({}) plugins of ".format(plgcount, plgcount+priv_plgcount), end='')
        else:
            print("{} plugins of ".format(plgcount), end='')
    if allplgcount > 0 or allplgcount+priv_allplgcount > 0:
        if priv_allplgcount > 0:
            print("{} ({}) plugins total".format(allplgcount, allplgcount+priv_allplgcount))
        else:
            print("{} plugins total".format(allplgcount))
    print()


def check_metadata_of_plugin(plg, quiet=False):

    BASE = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-2])

    # change the working diractory to the directory from which the converter is loaded (../tools)
    os.chdir(os.path.dirname(os.path.abspath(os.path.basename(__file__))))

    plugindirectory = '../plugins'
    #pluginabsdirectory = os.path.abspath(plugindirectory)
    pluginabsdirectory = os.path.join(BASE, 'plugins')

    os.chdir(pluginabsdirectory)

    check_metadata(plg, False, check_quiet=quiet, suppress_summery=quiet)
    return


# ==================================================================================
#   Main Routine of the tool
#

if __name__ == '__main__':
    print('')
    print(os.path.basename(__file__) + ' v' + VERSION + ' - Checks the care status of plugin metadata')
    print('')

    # change the working diractory to the directory from which the converter is loaded (../tools)
    os.chdir(os.path.dirname(os.path.abspath(os.path.basename(__file__))))

    plugindirectory = '../plugins'
    pluginabsdirectory = os.path.abspath(plugindirectory)

    os.chdir(pluginabsdirectory)

    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-la', '--list_all', action="store_true", default=False, help='list plugin information of all plugins')
    group.add_argument('-lcl', '--list_classic', action="store_true", default=False, help='list plugin information of classic plugins')
    group.add_argument('-lsm', '--list_smart', action="store_true", default=False, help='list plugin information of smart plugins')
    group.add_argument('-lst', '--list_state', action="store_true", default=False, help='list plugin information grouped by plugin state')
    group.add_argument('-li', '--list_inc', action="store_true", default=False, help='list information of plugins with incomplete metadata')
    group.add_argument('-lc', '--list_compl', action="store_true", default=False, help='list information of plugins with complete metadata')
    group.add_argument('-lip', action="store_true", default=False, help='list info of plugins with incomplete parameter data')
    group.add_argument('-lia', action="store_true", default=False, help='list info of plugins with incomplete item attribute data')
    group.add_argument('-d', dest='disp_plugin', help='display the metadata of a plugin')
    group.add_argument('-dd', dest='dispd_plugin', help='display the metadata of a plugin with description')
    group.add_argument('-c', dest='check_plugin', help='check the metadata of a plugin')
    # group.add_argument('-cq', dest='check_quiet', help='check the metadata of a plugin (quiet)')
    group.add_argument('-cl', '--check_list', action="store_true", default=False, help='check the metadata of all plugins')
    group.add_argument('-clc', '--check_clist', action="store_true", default=False, help='check the metadata of plugins with all metadata sections')
    group.add_argument('-cli', '--check_ilist', action="store_true", default=False, help='check the metadata of all plugins, list only incomplete plugins')
    group.add_argument('-v', '--list_versions', action="store_true", default=False, help='list versions instead of metadata checks')
    args = parser.parse_args()

    list_versions = False
    if args.list_versions:
        print("List Versions!")
        list_versions = True
    try:
        if args.list_versions:
            list_plugins('all', list_versions=list_versions)
        elif args.list_all:
            list_plugins('all')
        elif args.list_classic:
            list_plugins('classic')
        elif args.list_smart:
            list_plugins('smart')
        elif args.list_inc:
            list_plugins('inc')
        elif args.list_compl:
            list_plugins('compl')
        elif args.lip:
            list_plugins('inc_para')
        elif args.lia:
            list_plugins('inc_attr')
        elif args.list_state:
            list_plugins('state', 'qa-passed')
            list_plugins('state', 'ready')
            list_plugins('state', 'develop')
            list_plugins('state', 'deprecated')
            list_plugins('state', 'other')

        elif args.disp_plugin:
            display_metadata(args.disp_plugin, False)
        elif args.dispd_plugin:
            display_metadata(args.dispd_plugin, True)

        elif args.check_plugin:
            check_metadata(args.check_plugin, False)
#        elif args.check_quiet:
#            check_metadata(args.check_quiet, False, check_quiet=True)
        elif args.check_list:
            check_plglist('all')
        elif args.check_clist:
            check_plglist('compl', list_classic=False)
        elif args.check_ilist:
            check_plglist('inc', list_classic=True)
            check_plglist('inc', list_classic=False)
        else:
            parser.print_help()
            print()
    except ValueError as e:
        print("")
        print(e)
        print("")
        parser.print_help()
        print()
        exit(1)
