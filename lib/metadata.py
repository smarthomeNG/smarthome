#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2017-       Martin Sinn                         m.sinn@gmx.de
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

import logging
import os
import sys
import collections

from lib.utils import Utils
from lib.utils import Version
import lib.shyaml as shyaml
from lib.constants import (YAML_FILE, FOO, META_DATA_TYPES, META_DATA_DEFAULTS)

META_MODULE_PARAMETER_SECTION = 'parameters'
META_PLUGIN_SECTION = 'plugin'
META_PLUGIN_PARAMETER_SECTION = 'parameters'
META_PLUGIN_ITEMATTRIBUTE_SECTION = 'item_attributes'
META_PLUGIN_ITEMATTRIBUTEPREFIX_SECTION = 'item_attribute_prefixes'
META_PLUGIN_LOGIC_PARAMETER_SECTION = 'logic_parameters'
META_PLUGIN_FUNCTION_SECTION = 'plugin_functions'

META_STRUCT_SECTION = 'item_structs'
#META_DATA_TYPES=['bool', 'int', 'float','num', 'scene', 'str', ['list','list(subtype)'], 'dict', 'ip', 'ipv4', 'ipv6', 'mac', 'knx_ga', 'foo']
#META_DATA_DEFAULTS={'bool': False, 'int': 0, 'float': 0.0, 'scene': 0, 'str': '', 'list': [], 'dict': {}, 'OrderedDict': {}, 'num': 0, 'scene': 0, 'ip': '0.0.0.0', 'ipv4': '0.0.0.0', 'mac': '00:00:00:00:00:00', 'knx_ga': '', 'foo': None}


logger = logging.getLogger(__name__)


# global variables to take definitions of multiple plugins
all_itemdefinitions = {}
all_itemprefixdefinitions = {}
all_prefixes_tuple = None

class Metadata():

    _version = '?'


    def __init__(self, sh, addon_name, addon_type, classpath=''):
        """
        Initialzes the metadata for an addon (plugin or module) from the definition file

        :param sh: SmartHomeNG main object
        :param addon_name:
        :param addon_type: 'plugin' or 'module'
        :param classpath:
        :type sh: object
        :type addon_name: str
        :type addon_type: str
        :type classpath: str
        """
        global all_itemdefinitions
        global all_itemprefixdefinitions

        self._sh = sh
        self._addon_name = addon_name.lower()
        self._addon_type = addon_type

        self._log_premsg = "{} '{}': ".format(addon_type, self._addon_name)

#        logger.warning(self._log_premsg+"classpath = '{}'".format( classpath ) )
        if classpath == '':
            if addon_type == 'plugin':
                addon_type_dir = 'plugins'
            elif addon_type == 'module':
                addon_type_dir = 'modules'
            else:
                return
            self.relative_filename = os.path.join( addon_type_dir, self._addon_name, addon_type+YAML_FILE )
        else:
            self.relative_filename = os.path.join( classpath.replace('.', os.sep), addon_type+YAML_FILE )
#        logger.warning(self._log_premsg+"relative_filename = '{}'".format( self.relative_filename ) )

        # read complete definitions from metadata file
        filename = os.path.join( self._sh.get_basedir(), self.relative_filename )
        self.meta = shyaml.yaml_load(filename, ordered=True)

        self.parameters = None
        self._paramlist = []
        self.itemdefinitions = None
        self.itemprefixdefinitions = None
        self.all_itemprefixdefinitions = {}
        self._itemdeflist = []
        self.itemstructs = None
        self._itemstructlist = []
        self.logic_parameters = None
        self._logic_paramlist = []
        self.plugin_functions = None
        self._plugin_functionlist = []

        # Add dummy prefixes only, if all_itemprefixdefinitions is still empty
        if all_itemprefixdefinitions == {}:
            # dummy 'my_' prefix for user's attributes for logics, etc.
            prefix_name = 'my_'
            all_itemprefixdefinitions[prefix_name] = {'type': 'foo',
                                                      'description': {'de': 'Attribute für verschiedene Tests',
                                                                      'en': 'Attributes for various tests'},
                                                      'listtype': ['foo'], 'listlen': 0, '_addon_name': 'lib_metadata',
                                                      '_addon_type': 'plugin', '_name': prefix_name, '_type': 'prefix'}

            # dummy '_' prefix for hidden user's attributes for logics, etc.
            prefix_name = '_'
            all_itemprefixdefinitions[prefix_name] = {'type': 'foo',
                                                      'description': {'de': 'Attribute für internes Handling (z.B. in structs',
                                                                      'en': 'Attributes for internal handling (e.g. in structs)'},
                                                      'listtype': ['foo'], 'listlen': 0, '_addon_name': 'lib_metadata',
                                                      '_addon_type': 'plugin', '_name': prefix_name, '_type': 'prefix'}

            logger.info(f"Definierte spezielle Präfixe für Namen von Attributen: {list(all_itemprefixdefinitions.keys())}")

        if self.meta is not None:
            # read paramter and item definition sections
            if self._addon_type == 'module':
                self.parameters = self.meta.get(META_MODULE_PARAMETER_SECTION)
                self.itemstructs = self.meta.get(META_STRUCT_SECTION)
            else:
                self.global_parameters = self.get_global_plugin_parameters()
                self.parameters = self.meta.get(META_PLUGIN_PARAMETER_SECTION, {})
                if self.parameters is None or isinstance(self.parameters, str):
                    # if plugin parameter section is empty or is declared as NONE
                    self.parameters = self.global_parameters
                else:
                    self.parameters.update(self.global_parameters)
                self.itemdefinitions = self.meta.get(META_PLUGIN_ITEMATTRIBUTE_SECTION)
                self.itemprefixdefinitions = self.meta.get(META_PLUGIN_ITEMATTRIBUTEPREFIX_SECTION)
                self.itemstructs = self.meta.get(META_STRUCT_SECTION)
                self.logic_parameters = self.meta.get(META_PLUGIN_LOGIC_PARAMETER_SECTION)
                self.plugin_functions = self.meta.get(META_PLUGIN_FUNCTION_SECTION)

            # test validity of parameter definition section
            if self.parameters is not None:
                if self.parameters == 'NONE':
                    self.parameters = None
                else:
                    for param_name in self.parameters.keys():
                        if self.parameters.get(param_name, None) is not None:
                            self.parameters[param_name]['_name'] = param_name
                            self.parameters[param_name]['_type'] = 'parameter'
                    self._paramlist = list(self.parameters.keys())
                    logger.info(self._log_premsg+"Metadata paramlist = '{}'".format( str(self._paramlist) ) )
            if  self.parameters is not None:
                self._test_definitions(self._paramlist, self.parameters)
            else:
                logger.debug(self._log_premsg+"has no parameter definitions in metadata")

            # test validity of item definition section
            if self.itemdefinitions is not None:
                if self.itemdefinitions == 'NONE':
                    self.itemdefinitions = None
                else:
                    self._itemdeflist = list(self.itemdefinitions.keys())
                    logger.info(self._log_premsg+"Metadata itemdeflist = '{}'".format( str(self._itemdeflist) ) )
            if  self.itemdefinitions is not None:
                self._test_definitions(self._itemdeflist, self.itemdefinitions)
            else:
                logger.debug(self._log_premsg+"has no item definitions in metadata")

            # test validity of item-prefix definition section
            if self.itemprefixdefinitions is not None:
                if self.itemprefixdefinitions == 'NONE':
                    self.itemprefixdefinitions = None
                else:
                    self._itemprefixdeflist = list(self.itemprefixdefinitions.keys())
                    logger.info(self._log_premsg+"Metadata itemprefixdeflist = '{}'".format( str(self._itemprefixdeflist) ) )
            if  self.itemprefixdefinitions is not None:
                self._test_definitions(self._itemprefixdeflist, self.itemprefixdefinitions)
            else:
                logger.debug(self._log_premsg+"has no item definitions in metadata")

            # build dict for checking of item attributes and their values
            if self.itemdefinitions is not None:
                for attr_name in self.itemdefinitions:
                    all_itemdefinitions[attr_name] = self.itemdefinitions[attr_name]
                    all_itemdefinitions[attr_name]['_addon_name'] = self._addon_name
                    all_itemdefinitions[attr_name]['_addon_type'] = self._addon_type
                    all_itemdefinitions[attr_name]['_name'] = attr_name
                    all_itemdefinitions[attr_name]['_type'] = 'attribute'

            # build dict for checking of item attributes and their values
            if self.itemprefixdefinitions is not None:
                # add all prefixes loaded from metadate of the plugin
                for prefix_name in self.itemprefixdefinitions:
                    all_itemprefixdefinitions[prefix_name] = self.itemprefixdefinitions[prefix_name]
                    all_itemprefixdefinitions[prefix_name]['_addon_name'] = self._addon_name
                    all_itemprefixdefinitions[prefix_name]['_addon_type'] = self._addon_type
                    all_itemprefixdefinitions[prefix_name]['_name'] = prefix_name
                    all_itemprefixdefinitions[prefix_name]['_type'] = 'prefix'

            # test validity of logic-parameter definition section
            if self.logic_parameters is not None:
                if self.logic_parameters == 'NONE':
                    self.logic_parameters = None
                else:
                    self._logic_paramlist = list(self.logic_parameters.keys())
                    logger.info(self._log_premsg+"Metadata logic_paramlist = '{}'".format( str(self._logic_paramlist) ) )
            if  self.logic_parameters is not None:
                self._test_definitions(self._logic_paramlist, self.logic_parameters)
            else:
                logger.debug(self._log_premsg+"has no logic-parameter definitions in metadata")

            # test validity of plugin-function definition section
            if self.plugin_functions is not None:
                if self.plugin_functions == 'NONE':
                    self.plugin_functions = None
                else:
                    self._plugin_functionlist = list(self.plugin_functions.keys())
                    logger.info(self._log_premsg+"Metadata plugin_functionlist = '{}'".format( str(self._plugin_functionlist) ) )
            if  self.plugin_functions is not None:
                # self._test_definitions(self._plugin_functionlist, self.plugin_functions)
                pass
                dummy = self.get_plugin_function_defstrings(with_type=False, with_default=False)
                dummy = self.get_plugin_function_defstrings(with_type=True, with_default=False)
                dummy = self.get_plugin_function_defstrings(with_type=False, with_default=True)
                dummy = self.get_plugin_function_defstrings(with_type=True, with_default=True)
            else:
                logger.debug(self._log_premsg+"has no plugin-function definitions in metadata")


            # test validity of structs definition section
            if self.itemstructs is not None:
                if self.itemstructs == 'NONE':
                    self.itemstructs = None
                else:
                    logger.info(self._log_premsg + "Metadata itemstructlist = '{}'".format(self._itemstructlist))
#                    for struct in self._itemstructlist:
#                        for i in self.itemstructs[struct]:
#                            self.itemstructs[struct][i] = dict(self.itemstructs[struct][i])
#                            for si in self.itemstructs[struct][i]:
#                                if type(self.itemstructs[struct][i][si]) is collections.OrderedDict:
#                                    self.itemstructs[struct][i][si] = dict(self.itemstructs[struct][i][si])
#                        logger.info(self._log_premsg + "Metadata itemstruct '{}' = '{}'".format(struct, dict(self.itemstructs[struct])))
#            if self.itemstructs is not None:
##                self._test_definitions(self._itemdeflist, self.itemdefinitions)
#                pass
            else:
                logger.info(self._log_premsg + "has no item-struct definitions in metadata")

        # Read global metadata for addon (either 'plugin' or 'module'
        if self.meta is not None:
            self.addon_metadata = self.meta.get(addon_type)
        else:
            self.addon_metadata = None

        return


    def get_global_plugin_parameters(self):

        result = {}

        if self._sh.modules.get_module('http') is not None:
            # only if http module is loaded:
            # global plugin parameter 'webif_pagelength'
            result['webif_pagelength'] = {}
            result['webif_pagelength']['type'] = 'int'
            result['webif_pagelength']['valid_list'] = [-1, 0, 25, 50, 100]
            result['webif_pagelength']['description'] = {}
            # get description of webif_pagelength-parameter in all available laguages
            result['webif_pagelength']['description'] = self._sh.modules.get_module('http')._metadata.meta['parameters']['webif_pagelength'].get('description', {'en': 'No description found!'})
            try:
                result['webif_pagelength']['default'] = self._sh.modules.get_module('http')._webif_pagelength
            except:
                result['webif_pagelength']['default'] = 0

        self.pluginsettings = self.meta.get(META_PLUGIN_SECTION)
        if self.pluginsettings.get('multi_instance', False):
            # only for multi-instance Plugins:
            # global plugin parameter 'instance'
            result['instance'] = {}
            result['instance']['type'] = 'str'
            result['instance']['description'] = {}
            result['instance']['description']['de'] = "Falls mehrere Instanzen eines Multi-Instance Plugins konfiguriert sind, muss hier ein eindeutiger Instanz-Name angegeben werden (eine Instanz darf ohnen Namen bleiben). Falls nur eine Instanz konfiguriert ist, sollte hier kein Name vergeben werden."
            result['instance']['description']['en'] = "If several instances of a multi-instance plugin are configured, a unique instance name must be specified here (one instance may remain without a name). If only one instance is configured, no name should be assigned here."
            result['instance']['description']['fr'] = "Si plusieurs instances d'un plug-in multi-instance sont configurées, un nom d'instance unique doit être spécifié ici (une instance peut rester sans nom). Si une seule instance est configurée, aucun nom ne doit être attribué ici."

        return result


    def get_plugin_function_defstrings(self, with_type=False, with_default=True):
        """
        Build the documentation strings of the plugin's functions

        used e.g. for code completion in logic editor
        """

        docstr_list = []
        if self.plugin_functions is not None:
            for f in sorted(self.plugin_functions):
                fp = ''
                func_param_yaml = self.plugin_functions[f].get('parameters', None)
                if func_param_yaml is not None:
                    for par in func_param_yaml:
                        if fp != '':
                            fp += ', '
                        fp += par
                        if with_type:
                            if func_param_yaml[par].get('type', None) != None:
                                type = str(func_param_yaml[par].get('type', None))
                                fp += ':' + type
                        if with_default:
                            if func_param_yaml[par].get('default', None) != None:
                                default = str(func_param_yaml[par].get('default', None))
                                if func_param_yaml[par].get('type', 'foo') == 'str':
                                    if default == 'None*':
                                        default = 'None'
                                    else:
                                        default = " '" + default + "'"
                                fp += '=' + default

                docstr_list.append(f + '(' + fp + ')')
        logger.info(self._log_premsg + "Metadata get_plugin_function_defstrings -> '{}'".format(docstr_list))
        return docstr_list


    def _test_definitions(self, definition_list, definition_dict):
        """
        Test parameter or item-attribute definitions for validity
        """
        definition_list = list(definition_dict.keys())
#        logger.warning(self._log_premsg+"Metadata definition_list = '{}'".format( definition_list ) )
        for definition in definition_list:
            if definition_dict[definition] is not None:
                typ = str(definition_dict[definition].get('type', FOO)).lower()
                # to be implemented: timeframe
                definition_dict[definition]['listtype'] = [FOO]
                definition_dict[definition]['listlen'] = 0
                if definition_dict[definition].get('type', FOO) == 'list':
                    logger.debug(self._log_premsg+"definition = '{}' of type '{}'".format(definition, str(definition_dict[definition].get('type', FOO)).lower() ) )
                if not (typ in META_DATA_TYPES):
                    # test for list with specified datatype
                    if typ.startswith('list(') and typ.endswith(')'):
                        logger.debug(self._log_premsg+"definition = '{}' of type '{}'".format(definition, str(definition_dict[definition].get('type', FOO)).lower() ) )
                        definition_dict[definition]['type'] = 'list'
                        listparam = typ[5:]
                        listparam = listparam[:-1].strip().split(',')
                        if len(listparam) > 0:
                            if Utils.is_int(listparam[0]):
                                l = int(listparam[0])
                                if l < 0:
                                    l = 0
                                definition_dict[definition]['listlen'] = l
                                listparam.pop(0)
                            if len(listparam) == 0:
                                listparam = [FOO]
                        subtyp = ''
                        if len(listparam) > 0:
                            listparam2 = []
                            for i in range(0,len(listparam)):
                                if listparam[i].strip() in META_DATA_TYPES:
                                    listparam2.append(listparam[i].strip())
                                else:
                                    listparam2.append(FOO)
                                    logger.error(self._log_premsg+"definition = '{}': Invalid subtype '{}' specified, using '{}' instead (META_DATA_TYPES={})".format(definition, listparam[i], FOO, META_DATA_TYPES))
                            listparam = listparam2

                        definition_dict[definition]['listtype'] = listparam

                    else:
                        logger.error(self._log_premsg+"Invalid definition in metadata file '{}': type '{}' for parameter '{}' -> using type '{}' instead".format( self.relative_filename, typ, definition, FOO ) )
                        definition_dict[definition]['type'] = FOO

                if definition_dict[definition].get('type', FOO) == 'list':
                    logger.debug(self._log_premsg+"definition = '{}' list of subtype_list = {}, listlen={}".format(definition, definition_dict[definition]['listtype'], definition_dict[definition]['listlen'] ) )
                else:
                    logger.debug(self._log_premsg+"definition = '{}' list of listparam = >{}<, listlen={}".format(definition, definition_dict[definition]['listtype'], definition_dict[definition]['listlen'] ) )
            else:
                logger.info(self._log_premsg+"definition = '{}'".format( definition ) )
        return

    def _strip_quotes(self, string):
        if type(string) is str:
            string = string.strip()
            if len(string) >= 2:
                if string[0] in ['"', "'"]:  # check if string starts with ' or "
                    if string[0] == string[-1]:  # and end with it
                        if string.count(string[0]) == 2:  # if they are the only one
                            string = string[1:-1]  # remove them
        return string


    # ------------------------------------------------------------------------
    # Methods for global values
    #

    def get_string(self, key):
        """
        Return the value for a global key as a string

        :param key: global key to look up (in section 'plugin' or 'module')
        :type key: str

        :return: value for the key
        :rtype: str
        """
        if self.addon_metadata == None:
            return ''

        return self.addon_metadata.get(key, '')


    def get_mlstring(self, mlkey):
        """
        Return the value for a global multilanguage-key as a string

        It trys to lookup th value for the default language.
        If the value for the default language is empty, it trys to look up the value for English.
        If there is no value for the default language and for English, it trys to lookup the value for German.

        :param key: global multilanguage-key to look up (in section 'plugin' or 'module')
        :type key: str

        :return: value for the key
        :rtype: str
        """
        if self.addon_metadata is None:
            return ''

        key_dict = self.addon_metadata.get(mlkey)
        if key_dict is None:
            return ''
        try:
            result = key_dict.get(self._sh.get_defaultlanguage(), '')
        except:
            return ''
        if result == '':
            result = key_dict.get('en','')
            if result == '':
                result = key_dict.get('de','')
        return result


    def get_bool(self, key):
        """
        Return the value for a global key as a bool

        :param key: global key to look up (in section 'plugin' or 'module')
        :type key: str

        :return: value for the key
        :rtype: bool
        """
        if self.addon_metadata is None:
            return False

        return Utils.to_bool(self.addon_metadata.get(key, ''))


    def test_shngcompatibility(self):
        """
        Test if the actual running version of SmartHomeNG is in the range of supported versions for this addon (module/plugin)

        :return: True if the SmartHomeNG version is in the supported range
        :rtype: bool
        """
        shng_version = Version.format(self._sh.version.split('-')[0])
        min_shngversion = Version.format(str(self.get_string('sh_minversion')))
        max_shngversion = Version.format(str(self.get_string('sh_maxversion')))
        mod_version = Version.format(self.get_string('version'))

        if min_shngversion != '':
            # if min_shngversion > shng_version:
            if Version.compare(min_shngversion, shng_version, '>'):
                logger.error(f"{self._addon_type} '{self._addon_name}' {mod_version}: SmartHomeNG {shng_version} is too old for this {self._addon_type}. It requires at least version {Version.format(min_shngversion)}. The {self._addon_type} was not loaded.")
                return False
        if max_shngversion != '':
            # if max_shngversion < shng_version:
            if Version.compare(max_shngversion, shng_version, '<'):
                logger.error(f"{self._addon_type} '{self._addon_name}' {mod_version}: SmartHomeNG {shng_version} is too new for this {self._addon_type}. It requires a version up to {Version.format(max_shngversion)}. The {self._addon_type} was not loaded.")
                return False
        return True


    def test_pythoncompatibility(self):
        """
        Test if the actual running version of Python is in the range of supported versions for this addon (module/plugin)

        :return: True if the Python version is in the supported range
        :rtype: bool
        """
        l = sys.version_info
        py_version = Version.format(str(l[0])+'.'+str(l[1])+'.'+str(l[2]))
        min_pyversion = Version.format(str(self.get_string('py_minversion')))
        max = str(self.get_string('py_maxversion'))
        if len(max.split('.')) == 2:
            # if given max version has only two parts, make it the max for that version: 3.8 -> 3.8.999
            max += '.999'
        max_pyversion = Version.format(str(max))
        mod_version = Version.format(self.get_string('version'))

        #if min_pyversion != '' or max_pyversion != '':
        #    logger.notice(f"{self._addon_type} '{self._addon_name}' {mod_version}: Python Version: {py_version}, min: {min_pyversion}, max: {max_pyversion}")

        if min_pyversion != '':
            #self._compare_versions(min_pyversion, py_version, '>', (min_pyversion > py_version))
            # if min_pyversion > py_version:
            #if self._compare_versions(min_pyversion, py_version, '>', (min_pyversion > py_version)):
            if Version.compare(min_pyversion, py_version, '>'):
                logger.error(f"{self._addon_type} '{self._addon_name}' {mod_version}: The Python version {py_version} is too old for this {self._addon_type}. It requires at least version {min_pyversion}. The {self._addon_type} was not loaded.")
                return False
        if max_pyversion != '':
            #self._compare_versions(max_pyversion, py_version, '<', (max_pyversion < py_version))
            # if max_pyversion < py_version:
            #if self._compare_versions(max_pyversion, py_version, '<', (max_pyversion < py_version)):
            if Version.compare(max_pyversion, py_version, '<'):
                logger.error(f"{self._addon_type} '{self._addon_name}' {mod_version}: The Python version {py_version} is too new for this {self._addon_type}. It requires a version up to {max_pyversion}. The {self._addon_type} was not loaded.")
                return False
        return True


    def get_version(self):
        """
        Returns the version of the addon

        If test_version has been called before, the code_version is taken into account,
        otherwise the version of the metadata-file is returned

        :return: version
        :rtype: str
        """
        if self._version == '?':
            self._version = self.get_string('version')
        return self._version


    def test_version(self, code_version):
        """
        Tests if the loaded Python code has a version set and compares it to the metadata version.

        :param code_version: version of the python code
        :type code_version: str

        :return: True: version numbers match, or Python code has no version
        :rtype: bool
        """
        self._version = self.get_string('version')
        if code_version is None:
            logger.info("{} '{}' version not defined in Python code, metadata version is {}".format(self._addon_type, self._addon_name, self._version))
            return True
        else:
            if 2 > code_version.count('.') > 4:
                logger.warning(
                    "{} '{}' code version not compliant to plugin version schemas x.x.x or x.x.x.x ".format(
                        self._addon_type, self._addon_name))
            if self._version == '':
                logger.info("{} '{}' metadata contains no version number".format(self._addon_type, self._addon_name))
                self._version = code_version
            else:
                if 2 > str(self._version).count('.') < 4:
                    logger.warning(
                        "{} '{}' metadata version not compliant to plugin version schemas x.x.x or x.x.x.x ".format(
                            self._addon_type, self._addon_name))
                if str(code_version) != str(self._version):
                    logger.error("{} '{}' version differs between Python code ({}) and metadata ({})".format(self._addon_type, self._addon_name, str(code_version), self._version))
                    return False
            return True


    # ------------------------------------------------------------------------
    # Methods for parameter/attribute checking
    #

    def _test_valuetype(self, typ, subtype, value):
        """
        Returns True, if the value can be converted to the specified type
        """
#        logger.warning(self._log_premsg+"_test_valuetype-list: typ={}, subtype={}, value={}".format(typ, subtype, value))
        if typ == 'bool':
            return Utils.to_bool(value, default='?') != '?'
        elif typ == 'int':
            return Utils.is_int(value)
        elif typ in ['float','num']:
            return Utils.is_float(value)
        elif typ == 'scene':
            if Utils.is_int(value):
                return (int(value) >= 0) and (int(value) < 256)
            else:
                return False
        elif typ in ['str','password']:
            return True     # Everything can be converted to a string
        elif typ == 'list':
            if subtype != '' and subtype != FOO:
                result = True
                if isinstance(value, list):
                    for i in range(0, len(value)):
                        if i < len(subtype):
                            sub = subtype[i]
                        else:
                            sub = subtype[len(subtype)-1]
                        if not self._test_valuetype(sub, '', value[i]):
                            result = False
#                            logger.warning("_test_valuetype: value[{}] = {}, sub = {}, result = False".format(i, value[i], sub))
#                    logger.warning("_test_valuetype: value = {}, type(value) = {}, typ = {}, subtype = {}".format(value, type(value), typ, subtype))
                return result
            return (type(value) is list)
        elif typ == 'dict':
            try:
                d = dict(value)
            except:
                import ast
                try:
                    d = ast.literal_eval(value)
                except:
                    return False
            return (isinstance(d,dict))
        elif typ == 'ip':
            if Utils.is_ipv4(value):
                return True
            if Utils.is_ipv6(value):
                return True
            return Utils.is_hostname(value)
        elif typ == 'ipv4':
            return Utils.is_ipv4(value)
        elif typ == 'ipv6':
            return Utils.is_ipv6(value)
        elif typ == 'mac':
            return Utils.is_mac(value)
        elif typ == 'knx_ga':
            return Utils.is_knx_groupaddress(value)
        elif typ == FOO:
            return True


    def _test_value(self, value, definition):
        """
        Returns True, if the value can be converted to specified type

        :param value: value to be checked
        :param definition: definition dict of parameter/attribute
        :type value: str
        :type definition: dict

        :return: True, if value can be converted
        :rtype: bool
        """
        if definition is not None:
            typ = definition.get('type', 'foo')
            subtype = ''
            if typ == 'list':
                subtype = definition.get('listtype', ['?'])
            #    if subtype != '':
            #        logger.warning("_test_value '{}': before _test_valuetype(): typ = {}, subtype = {}, value = {}".format(param, typ, subtype, value))
            return self._test_valuetype(typ, subtype, value)
        return False


    def _expand_listvalues(self, value, definition):
        """
        If a parameter is defined as a list, but the value is of a basic datatype,
        value is expanded to a list. In all other cases, the value is returned nuchanged

        :param value: value to be expanded
        :param definition: definition dict of parameter/attribute
        :type value: str
        :type definition: dict

        :return: expanded value
        """
        result = value
        if definition is not None:
            typ = definition.get('type', 'foo')
            if (typ == 'list') and (not isinstance(value, list)):
                result = Utils.string_to_list(value)
#            if (typ == 'list'):
#                logger.warning(self._log_premsg+"_expand_listvalues: value = >{}<, type(value) = >{}<, result = >{}<, type(result) = >{}<".format(value, type(value), result, type(result)))
        return result


    def _convert_valuetotype(self, typ, value):
        """
        Returns the value converted to the parameters type
        """
        if typ == 'bool':
            result = Utils.to_bool(value)
        elif typ in ['int','scene']:
            result = int(value)
        elif typ in ['float','num']:
            result = float(value)
        elif typ in ['str','password']:
            result = str(value)
        elif typ == 'list':
            if isinstance(value, list):
                result = value
            else:
                result = [value]
        elif typ == 'dict':
            try:
                result = dict(value)
            except:
                import ast
                try:
                    result = ast.literal_eval(value)
                except:
                    result = {}
        elif typ in ['ip', 'ipv4', 'ipv6', 'mac']:
            result = str(value)
        elif typ in ['knx_ga']:
            result = str(value)
        elif typ == FOO:
            result = value
        else:
            logger.error(self._log_premsg+"unhandled type {}".format(typ))
        return result


    def _convert_value(self, value, definition, is_default=False):
        """
        Returns the value converted to the parameters type
        """
        result = False
        if definition is not None:
            typ = definition.get('type', 'foo')
            result = self._convert_valuetotype(typ, value)
            orig = result
            if 'valid_list_ci' in definition.keys():
                orig = str(orig).lower()
            result = self._test_validity('', result, definition, is_default)
            if result != orig:
                # Für non-default Prüfung nur Warning
                if is_default:
                    logger.error(self._log_premsg+f"Invalid default '{orig}' in metadata file '{self.relative_filename}' for {definition['_type']} '{definition['_name']}' -> using '{result}' instead" )
                else:
                    logger.warning(self._log_premsg+f"Invalid value '{orig}' for {definition['_type']} '{definition['_name']}' -> using '{result}' instead {definition.get('_def_in', '')}" )
        return result


    def _test_against_valid_list(self, definition, value):
        """
        Test if value is in the valid list(s) of the metadata definition
        :param definition:
        :param value:
        :return:
        """
        # test against list of valid entries
        result = value

        valid_list_ci = definition.get('valid_list_ci', None)
        if (valid_list_ci is None) or (len(valid_list_ci) == 0):
            # test case sensitive
            valid_list = definition.get('valid_list', None)
            if (valid_list is None) or (len(valid_list) == 0):
                pass
            else:
                if result in valid_list:
                    pass
                else:
                    result = valid_list[0]
        else:
            if isinstance(result, str):
                # test case in-sensitive, return result in lower case
                if result.lower() in (entry.lower() for entry in valid_list_ci):
                    result = result.lower()
                else:
                    result = str(valid_list_ci[0]).lower()

        return result


    def _test_validity(self, param, value, definition=None, is_default=False):
        """
        Checks the value against a list of valid values.
        If valid, it returns the value.
        Otherwise it returns the first entry of the list of valid values.
        """
        result = value
        if definition is not None:
            if definition.get('type', 'foo') in ['int', 'float', 'num', 'scene']:
                valid_min = definition.get('valid_min')
                if valid_min != None:
                    if self._test_value(valid_min, definition):
                        if result < self._convert_valuetotype(definition.get('type', 'foo'), valid_min):
                            if is_default == False:
                                result = valid_min
                            else:
                                result = valid_min
                valid_max = definition.get('valid_max')
                if valid_max != None:
                    if self._test_value(valid_max, definition):
                        if result > self._convert_valuetotype(definition.get('type', 'foo'), valid_max):
                            if is_default == False:
                                result = valid_max
                            else:
                                result = valid_max
            elif definition.get('type', 'foo') in ['list']:
                 if definition['listlen'] > 0:
                     if definition['listlen'] != len(value):
                        logger.warning(self._log_premsg+"Invalid value '{}' in plugin configuration file for parameter '{}' -> length of list is not {}".format( value, param, self.parameters[param]['listlen'] ) )
                        while len(value) < definition['listlen']:
                            value.append('')
                        result = value
            elif definition.get('type', 'foo') in ['dict']:
                # No real testing for dicts
                result = value

            # test against list of valid entries
            result = self._test_against_valid_list(definition, result)

            return result

        elif self.parameters[param] != None:
            logger.warning("_test_validity: old version for param={}, value={}".format(param, value))
            if self.parameters[param].get('type') in ['int', 'float', 'num', 'scene']:
                valid_min = self.parameters[param].get('valid_min')
                if valid_min != None:
                    if self._test_value(valid_min, self.parameters[param]):
                        if result < self._convert_valuetotype(self.get_parameter_type(param), valid_min):
                            if is_default == False:
                                result = valid_min
                            else:
                                result = valid_min
                valid_max = self.parameters[param].get('valid_max')
                if valid_max != None:
                    if self._test_value(valid_max, self.parameters[param]):
                        if result > self._convert_valuetotype(self.get_parameter_type(param), valid_max):
                            if is_default == False:
                                result = valid_max
                            else:
                                result = valid_max
            elif self.parameters[param].get('type') in ['list']:
                 if self.parameters[param]['listlen'] > 0:
                     if self.parameters[param]['listlen'] != len(value):
                        logger.warning(self._log_premsg+"Invalid value '{}' in plugin configuration file for parameter '{}' -> length of list is not {}".format( value, param, self.parameters[param]['listlen'] ) )
                        while len(value) < self.parameters[param]['listlen']:
                            value.append('')
                        result = value

        if self.parameters[param] is None:
            logger.warning(self._log_premsg+"_test_validity: param {}".format(param))
        else:
            # test against list of valid entries
            result = self._test_against_valid_list(self.parameters[param], result)
        return result

    def _get_default_if_none(self, typ):
        """
        Returns the default value for  datatype.
        It is used, if no default value is defined for a parameter.
        """
        return META_DATA_DEFAULTS.get(typ, None)


    # ------------------------------------------------------------------------
    # Methods for accessing parameter / item definition definitions
    #

    def get_parameterlist(self):
        """
        Returns the list of parameter names

        :return: List of strings with parameter names
        :rtype: list of str
        """
        return self._paramlist


    def get_itemdefinitionlist(self):
        """
        Returns the list of item attribute definitions

        :return: List of strings with item attribute names
        :rtype: list of str
        """
        return self._itemdeflist


    def _get_definition_type(self, definition, definitions):
        """
        Returns the datatype of a parameter

        If the defined datatype is 'foo', None is returned

        :param param: Name of the parameter
        :type param: str

        :return: datatype of the parameter
        :rtype: str
        """
        if definitions is None:
            return FOO
        if definitions[definition] is None:
            return FOO
        return str(definitions[definition].get('type', FOO)).lower()

    def get_parameter_type(self, param):
        """
        Returns the datatype of a parameter
        """
        return self._get_definition_type(param, self.parameters)

    def get_itemdefinition_type(self, definition):
        """
        Returns the datatype of an item attribute definition
        """
        return self._get_definition_type(definition, self.itemdefinitions)


    def _get_definition_subtype(self, definition, definitions):
        """
        Returns the subtype of a parameter

        If the defined datatype is 'foo', None is returned
        If no subtype is defined (or definable), an empty string is returned

        :param param: Name of the parameter
        :type param: str

        :return: subtype of the parameter
        :rtype: str
        """
        if definitions is None:
            return FOO
        if definitions[definition] is None:
            return FOO
        result = str(definitions[definition].get('type', FOO)).lower()
        sub = ''
        if result == 'list':
            sub =  definitions[definition].get('listtype', ['?'])
        return sub

    def get_parameter_subtype(self, param):
        """
        Returns the subtype of a parameter
        """
        return self._get_definition_subtype(param, self.parameters)

    def get_itemdefinition_subtype(self, definition):
        """
        Returns the subtype of an item attribute definition
        """
        return self._get_definition_subtype(definition, self.itemdefinitions)


    def _get_definition_listlen(self, definition, definitions):
        """
        Returns the len of a parameter of type list of a parameter

        :param param: Name of the parameter
        :type param: str

        :return: subtype of the parameter
        :rtype: str or None
        """
        if definitions is None:
            return FOO
        if definitions[definition] is None:
            return FOO
        result = str(definitions.get('type', FOO)).lower()
        llen = 0
        if result == 'list':
            llen =  definitions.get('listlen', ['?'])
        return llen

    def get_parameter_listlen(self, param):
        """
        Returns the len of a parameter of type list of a parameter
        """
        return self.get_definition_listlen(param, self.parameters)

    def get_itemdefinition_listlen(self, definition):
        """
        Returns the len of a parameter of type list of an item attribute definition
        """
        return self.get_definition_listlen(definition, self.itemdefinitions)


    def _get_definition_type_with_subtype(self, definition, definitions):
        """
        Returns the datatype of a parameter with subtype (if subtype exists)

        If the defined datatype is 'foo', None is returned

        Subtypes are returnd for parameter type 'list'

        :param param: Name of the parameter
        :type param: str

        :return: datatype with subtype of the parameter
        :rtype: str
        """
        if definitions is None:
            return FOO
        if definitions[definition] is None:
            return FOO
        result = self._get_definition_type(definition, definitions)
        sub = self._get_definition_subtype(definition, definitions)
        if sub != '':
            llen = self._get_definition_listlen(definition, definitions)
            if llen > 0:
                sub = str(llen)+','+ str.join(',', sub)
            else:
                sub = str.join(',', sub)
            result = result+'(' + sub + ')'
        return result

    def get_parameter_type_with_subtype(self, param):
        """
        Returns the datatype of a parameter with subtype (if subtype exists)
        """
        return self._get_definition_type_with_subtype(param, self.parameters)

    def get_itemdefinition_type_with_subtype(self, definition):
        """
        Returns the datatype of an item attribute definition with subtype (if subtype exists)
        """
        return self._get_definition_type_with_subtype(definition, self.itemdefinitions)

    def _get_definition_defaultvalue(self, definition, definitions, definitionlist):
        """
        Returns the default value for the parameter

        If no default value is specified for the parameter, the default value for the datatype
        of the parameter is returned.

        If the parameter is not defined, None is returned

        :param param: Name of the parameter
        :type param: str

        :return: Default value
        :rtype: str or None
        """
        value = None
        if definition in definitionlist:
            if self.parameters[definition] is not None:
                if self._get_definition_type(definition, definitions) == 'dict':
                    if definitions[definition].get('default') is not None:
                        value = dict(definitions[definition].get('default'))
                        #import ast
                        #try:
                        #    value = ast.literal_eval(value)
                        #except:
                        #    value = {}
                else:
                    value = definitions[definition].get('default')
                typ = self._get_definition_type(definition, definitions)
                if value == 'None*':
                    logger.info("_get_definition_defaultvalue: default value is 'None*' -> None")
                    value = None
                else:
                    if value is None:
                        value = self._get_default_if_none(typ)
                    value = self._expand_listvalues(value, self.parameters[definition])
                    ###ms
                    if not self._test_value(value, self.parameters[definition]):
                        # Für non-default Prüfung nur Warning
                        logger.error(self._log_premsg+"Invalid data for type '{}' in metadata file '{}': default '{}' for parameter '{}' -> using '{}' instead".format( definitions[definition].get('type'), self.relative_filename, value, definition, self._get_default_if_none(typ) ) )
                        value = None
                    if value is None:
                        value = self._get_default_if_none(typ)
                    value = self._convert_value(value, self.parameters[definition], is_default=True)

                    orig_value = value
                    value = self._test_validity('', value, self.parameters[definition], is_default=True)
                    if value != orig_value:
                        # Für non-default Prüfung nur Warning
                        logger.error(self._log_premsg+"Invalid default '{}' in metadata file '{}' for parameter '{}' -> using '{}' instead".format( orig_value, self.relative_filename, definition, value ) )

        return value

    def get_parameter_defaultvalue(self, param):
        """
        Returns the default value for the parameter
        """
        return self._get_definition_defaultvalue(param, self.parameters, self._paramlist)

#    def get_itemdefinition_defaultvalue(self, definition):
#        """
#        Returns the default value for an item attribute definition
#        """
#        return self._get_definition_defaultvalue(definition, self.itemdefinitions, self._itemdeflist)

    def _get_definitioninfo(self, definition, key, definitions):
        """
        Returns the value for a key of a parameter as a string

        :param parameter: parameter to get the definition info from
        :param key: key of the definition info
        :type parameter: str
        :type key: str

        :return: List of strings with parameter names (None if parameter is not found)
        :rtype: str
        """
        try:
            result = definitions[definition].get('key')
        except:
            result = None
        return result

    def get_parameterdefinition(self, param, key):
        """
        Returns the value for a key of a parameter as a string
        """
        return self.__get_definitioninfo(param, key, self.parameters)

    def get_itemdefinition(self, definition, key):
        """
        Returns the value for a key of a parameter as a string
        """
        return self.__get_definitioninfo(definition, key, self.itemdefinitions)

    def check_parameters(self, args):
        """
        Checks the values of a dict of configured parameters.

        Returns a dict with all defined parameters with values and a bool indicating if all parameters are ok (True)
        or if a mandatory parameter is not configured (False). It returns default values
        for parameters that have not been configured. The resulting dict contains the
        values in the the datatype of the parameter definition

        :param args: Configured parameters with the values
        :type args: dict of parameter-values (values as string)

        :return: All defined parameters with values, Flag if all parameters are ok (no mandatory is missing)
        :rtype: dict, bool
        """
        addon_params = collections.OrderedDict()
        hide_params = collections.OrderedDict()
        if self.meta is None:
            logger.info(self._log_premsg+"No metadata found" )
            return (addon_params, True, hide_params)
        if self.parameters is None:
            logger.info(self._log_premsg+"No parameter definitions found in metadata" )
            return (addon_params, True, hide_params)

        allparams_ok = True
        if self._paramlist != []:
            for param in self._paramlist:
                value = Utils.strip_quotes(args.get(param))
                if value is None:
                    if self.parameters[param] is not None:
                        if self.parameters[param].get('mandatory'):
                            logger.error(self._log_premsg+"'{}' is mandatory, but was not found in /etc/{}".format(param, self._addon_type+YAML_FILE))
                            allparams_ok = False
                        else:
                            addon_params[param] = self.get_parameter_defaultvalue(param)
                            hide_params[param] = Utils.to_bool(self.parameters[param].get('hide'), default=False)
                            logger.info(self._log_premsg+"value not found in plugin configuration file for parameter '{}' -> using default value '{}' instead".format(param, addon_params[param] ) )
        #                    logger.warning(self._log_premsg+"'{}' not found in /etc/{}, using default value '{}'".format(param, self._addon_type+YAML_FILE, addon_params[param]))
                else:
                    value = self._expand_listvalues(value, self.parameters[param])
                    if self._test_value(value, self.parameters[param]):
                        addon_params[param] = self._convert_value(value, self.parameters[param])

                        if self.parameters[param] is None:
                            hide_params[param] = None
                        else:
                            hide_params[param] = Utils.to_bool(self.parameters[param].get('hide'), default=False)
                        logger.debug(self._log_premsg+"Found '{}' with value '{}' in /etc/{}".format(param, value, self._addon_type+YAML_FILE))
                    else:
                        if self.parameters.get(param) is not None:
                            if bool(self.parameters[param].get('mandatory', False)) is True:
                                logger.error(self._log_premsg+"'{}' is mandatory, but no valid value was found in /etc/{}".format(param, self._addon_type+YAML_FILE))
                                allparams_ok = False
                            else:
                                addon_params[param] = self.get_parameter_defaultvalue(param)
                                hide_params[param] = Utils.to_bool(self.parameters[param].get('hide'), default=False)
                                logger.error(self._log_premsg+"Found invalid value '{}' for parameter '{}' (type {}) in /etc/{}, using default value '{}' instead".format(value, param, self.parameters[param]['type'], self._addon_type+YAML_FILE, str(addon_params[param])))

        return (addon_params, allparams_ok, hide_params)


    def check_itemattribute(self, item, attribute, value, defined_in_file=None):
        """
        Checks the value of a plugin-specific item attribute
        and returnes the checked value or the default value if needed

        attribute name is checked
        - against list of valid attributes-names (defined by section 'item_attributes' of configured plugins)
        - against list of valid attribute-name prefixes (defined by section 'item_attribute_prefixes' of configured plugins)

        :param item: item object
        :param attribute:
        :param value:
        :return:
        """
        global all_prefixes_tuple

        self._log_premsg = "Item '{}', attribute '{}': ".format(item.id(), attribute)

        if all_prefixes_tuple is None:
            # Generate tuple on first call to this method
            all_prefixes_tuple = tuple(all_itemprefixdefinitions.keys())

        if defined_in_file is None:
            def_in = ''
        else:
            def_in = '(defined in ' + defined_in_file + ')'

        attr_definition = all_itemdefinitions.get(attribute, None)
        if attr_definition is None:
            for prefix in all_itemprefixdefinitions.keys():
                if attribute.startswith(prefix):
                    attr_definition = dict(all_itemprefixdefinitions[prefix])
                    attr_definition['_prefix'] = True
                    break
            if not(attribute.startswith(all_prefixes_tuple)):
                if not (item.id().startswith('env.core.') or item.id().startswith('env.system.')):
                    logger.notice(f"Item '{item.id()}', attribute '{attribute}': Attribute is undefined and has value '{value}' {def_in}")
                return value

        attr_definition['_def_in'] = def_in
        attr_type = attr_definition.get('type', 'foo')

        # If a parameter is defined as a list, but the value is of a basic datatype, value is expanded to a list.
        value = self._expand_listvalues(value, attr_definition)
        # test if value can be converted into defined type
        if self._test_value(value, attr_definition):
            value = self._convert_value(value, attr_definition)
        else:
            # handle invalid value that cannot be converted to defined type
            additional_text = ''
            default_value = attr_definition.get('default', None)
            if default_value is not None:
                additional_text = ", using default value '" + str(default_value) + "' instead"
            logger.warning("Item '{}', attribute '{}': value '{}' can not be converted to type '{}'{} {}".format(item.id(), attribute, value, attr_type, additional_text, def_in))
            if default_value is None:
                value = ''
            else:
                value = default_value

        return value


    def _compare_versions(self, vers1, vers2, operator, res_old=None):
        """
        Compare two version numbers and return if the condition is met

        :param vers1:
        :param vers2:
        :param operator:
        :type vers1: str
        :type vers2: str
        :type operator: str

        :return: true if condition is met
        :rtype: bool
        """
        v1 = self._version_to_list(vers1)
        v2 = self._version_to_list(vers2)

        result = False
        if v1 == v2 and operator in ['>=', '==', '<=']:
            result = True
        if v1 < v2 and operator in ['<', '<=']:
            result = True
        if v1 > v2 and operator in ['>', '>=']:
            result = True
        #logger.warning(f"_compare_versions: {self._addon_name:12} v1={v1}, v2={v2}, operator='{operator}', result={result}, res_old={res_old}")

        logger.debug("_compare_versions: - - - vers1 = {}, vers2 = {}, v1 = {}, v2 = {}, operator = '{}', result = {}".format(vers1, vers2, v1, v2, operator, result))
        return result


    def _version_to_list(self, vers):
        """
        Split version number to list and get rid of non-numeric parts

        :param vers:

        :return: version as list
        :rtype: list
        """
        # create list with [major,minor,revision,build]
        vsplit = vers.split('.')
        while len(vsplit) < 4:
            vsplit.append('0')

        import re

        # get rid of non numeric parts
        vlist = []
        for v in vsplit:
            #v = re.findall('\d+', v )[0]
            v = re.findall(r'\d+', v )[0]
            vi = 0
            try:
                vi = int(v)
            except:
                pass
            vlist.append(vi)

        return vlist
