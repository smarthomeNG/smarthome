#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2017   Martin Sinn                         m.sinn@gmx.de
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
This library does the handling of the configuration files of SmartHomeNG in yaml format.
All file i/o from and to these configuration files goes through the functions which
are implemented in this library.


:Warning: This library is part of the core of SmartHomeNG. It **should not be called directly** from plugins!

"""

import logging
import os
import shutil

from collections import OrderedDict

from lib.constants import (YAML_FILE)


logger = logging.getLogger(__name__)

try:
    import ruamel.yaml as yaml
    EDITING_ENABLED = True
    # check to be enabled after migrating to the new ruamel.yaml api
#    if str(yaml.__version__) < '0.15.0':
#        logger.critical("shyaml: Loaded version of ruamel.yaml ({}) is too old".format(yaml.__version__))
#        exit(1)

except:
    EDITING_ENABLED = False
    logger.critical("shyaml: ruamel.yaml is not installed")
    exit(1)

yaml_version = '1.1'
indent_spaces = 4
block_seq_indent = 0

def editing_is_enabled():
    return(EDITING_ENABLED == True)


# ==================================================================================
#   Routines to handle yaml files
#

def convert_linenumber(s, occ=1):
    if occ == 1:
        s2 = s[s.find('line: ')+6:]
    elif occ == 2:
        p = s.find('line: ')+6
        s2 = s[s.find('line: ',p) + 6:]
    else:
        return '*' + s
    lineold = s2[:s2.find(')')]
    try:
        linenew = str(int((int(lineold)+1)/2))
    except:
        logger.warning('Unable to correct line number for yaml-file error. Wrong line number is {}'.format(lineold))
        linenew = str(lineold)
    lo = 'line '+lineold
    ln = 'line '+linenew
    lo2 = '(line: '+lineold+')'
    ln2 = '(line: '+linenew+')'
    s = s.replace(lo, ln)
    s = s.replace(lo2, ln2)
    return s


def yaml_load(filename, ordered=False, ignore_notfound=False):
    """
    Load contents of a configuration file into an dict/OrderedDict structure. The configuration file has to be a valid yaml file

    :param filename: name of the yaml file to load
    :type filename: str
    :param ordered: load to an OrderedDict? Default=False
    :type ordered: bool

    :return: configuration data loaded from the file (or None if an error occured)
    :rtype: Dict | OrderedDict | None
    """

    dict_type = 'dict'
    if ordered:
        dict_type = 'OrderedDict'
    logger.info("Loading '{}' to '{}'".format(filename, dict_type))
    y = None

    try:
        with open(filename, 'r') as stream:
            sdata = stream.read()
        sdata = sdata.replace('\n', '\n\n')
        if ordered:
            y = _ordered_load(sdata, yaml.SafeLoader)
        else:
            y = yaml.load(sdata, yaml.SafeLoader)
    except Exception as e:
        estr = str(e)
        if "found character '\\t'" in estr:
            estr = estr[estr.find('line'):]
            estr = 'TABs are not allowed in YAML files, use spaces for indentation instead!\nError in ' + estr
        if ("while scanning a simple key" in estr) and ("could not found expected ':'" in estr):
            estr = estr[estr.find('column'):estr.find('could not')]
            estr = 'The colon (:) following a key has to be followed by a space. The space is missing!\nError in ' + estr
        if '(line: ' in estr:
            line = convert_linenumber(estr)
            line = convert_linenumber(line, 2)
#            estr += '\nNOTE: To find correct line numbers: add 1 to line and divide by 2 -> '+line
            estr = line
            estr += '\nNOTE: Look for the error at the expected <block end>, near the second specified line number'
        if "[Errno 2]" in estr:
            if not ignore_notfound:
                logger.warning("YAML-file not found: {}".format(filename))
        else:
            logger.error("YAML-file load error in {}:  \n{}".format(filename, estr))

    return y


def yaml_load_fromstring(string, ordered=False):
    """
    Load contents of a string into an dict/OrderedDict structure. The string has to be valid yaml

    :param string: name of the yaml file to load
    :type string: str
    :param ordered: load to an OrderedDict? Default=False
    :type ordered: bool

    :return: configuration data loaded from the file (or None if an error occured) and error string
    :rtype: Dict|OrderedDict|None, str
    """

    dict_type = 'dict'
    if ordered:
        dict_type = 'OrderedDict'
    logger.info("Loading '{}' to '{}'".format(string, dict_type))
    y = None

    estr = ''
    try:
        sdata = string
#        sdata = sdata.replace('\n', '\n\n')
        if ordered:
            y = _ordered_load(sdata, yaml.SafeLoader)
        else:
            y = yaml.load(sdata, yaml.SafeLoader)
    except Exception as e:
        estr = str(e)
        if "found character '\\t'" in estr:
            estr = estr[estr.find('line'):]
            estr = 'TABs are not allowed in YAML files, use spaces for indentation instead!\nError in ' + estr
        if ("while scanning a simple key" in estr) and ("could not found expected ':'" in estr):
            estr = estr[estr.find('column'):estr.find('could not')]
            estr = 'The colon (:) following a key has to be followed by a space. The space is missing!\nError in ' + estr

    return y, estr


def yaml_save(filename, data):
    """
    Save contents of an OrderedDict structure to a yaml file

    :param filename: name of the yaml file to save to
    :type filename: str
    :param data: configuration data to to save
    :type filename: str
    :type data: OrderedDict

    :returns: Nothing
    """

    ordered = (type(data).__name__ == 'OrderedDict')
    dict_type = 'dict'
    if ordered:
        dict_type = 'OrderedDict'
    logger.info("Saving '{}' to '{}'".format(dict_type, filename))
    if ordered:
        sdata = _ordered_dump(data, Dumper=yaml.SafeDumper, indent=4, width=768, allow_unicode=True, default_flow_style=False)
    else:
        sdata = yaml.dump(data, Dumper=yaml.SafeDumper, indent=4, width=768, allow_unicode=True, default_flow_style=False)
    sdata = _format_yaml_dump( sdata )
    with open(filename, 'w') as outfile:
        outfile.write( sdata )

# ==================================================================================

def _format_yaml_load(data):
    """
    Reinsert '\n's that have been removed fom comments to make file more readable

    :param data: string to format

    :return: formatted string
    """

#    ptr = 0
#    cptr = data[ptr:].find('comment: ')

    data = data.replace('\n', '\n\n')
    return data


def _ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Ordered yaml loader
    Use this instead ot yaml.loader/yaml.saveloader to get an Ordereddict

    :param stream: stream to read from
    :param Loader: yaml-loader to use
    :object_pairs_hook: ...

    :return: OrderedDict structure
    """

    # usage example: ordered_load(stream, yaml.SafeLoader)
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def _format_yaml_dump(data):
    """
    Format yaml-dump to make file more readable
    (yaml structure must be dumped to a stream before using this function)
    | Currently does the following:
    | - Add an empty line before a new item

    :param data: string to format

    :return: formatted string
    """

    data = data.replace('\n\n', '\n')
    ldata = data.split('\n')
    rdata = []
    for index, line in enumerate(ldata):
        if line[-1:] == ':':
            # no empty line before list attributes
            if ldata[index+1].strip()[0] != '-':
                rdata.append('')
            rdata.append(line)
        else:
            rdata.append(line)
    fdata = '\n'.join(rdata)
    return fdata


def _ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    """
    Ordered yaml dumper
    Use this instead ot yaml.Dumper/yaml.SaveDumper to get an Ordereddict

    :param stream: stream to write to
    :param Dumper: yaml-dumper to use
    :**kwds: Additional keywords

    :return: OrderedDict structure
    """

    # usage example: ordered_dump(data, Dumper=yaml.SafeDumper)
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


# ==================================================================================
#   Routines to handle editing of yaml files
#

def yaml_load_roundtrip(filename):
    """
    Load contents of a yaml file into an dict structure for editing (using Roundtrip Loader)

    :param filename: name of the yaml file to load
    :return: data structure loaded from file
    """

    if not EDITING_ENABLED:
        return None

    y = None
    if not filename.lower().endswith('.yaml'):
        filename += YAML_FILE
    try:
        with open(filename, 'r') as stream:
            sdata = stream.read()
        sdata = sdata.replace('\n', '\n\n')
        y = yaml.load(sdata, yaml.RoundTripLoader)
    except Exception as e:
        logger.error("yaml_load_roundtrip: YAML-file load error: '%s'" % (e))
        y = {}
    return y


def get_emptynode():
   """
   Return an empty node
   """
   return yaml.comments.CommentedMap([])


def get_commentedseq(l):
   """
   Convert a list to a commented sequence
   """
   return yaml.comments.CommentedSeq( l )


def yaml_dump_roundtrip(data):
    """
    Dump yaml to a string using the RoundtripDumper and correct linespacing in output file

    :param data: data structure to save
    """

    sdata = yaml.dump(data, Dumper=yaml.RoundTripDumper, version=yaml_version, indent=indent_spaces, block_seq_indent=block_seq_indent, width=12288, allow_unicode=True)
    sdata = _format_yaml_dump2( sdata )
    return sdata


def yaml_save_roundtrip(filename, data, create_backup=False):
    """
    Dump yaml using the RoundtripDumper and correct linespacing in output file

    :param filename: name of the yaml file to save to
    :param data: data structure to save
    """

    if not EDITING_ENABLED:
        return
    sdata = yaml.dump(data, Dumper=yaml.RoundTripDumper, version=yaml_version, indent=indent_spaces, block_seq_indent=block_seq_indent, width=12288, allow_unicode=True)
    sdata = _format_yaml_dump2( sdata )

    if not filename.lower().endswith('.yaml'):
        filename += YAML_FILE
    if create_backup:
        if os.path.isfile(filename):
            shutil.copy2(filename, filename+'.bak')

    with open(filename, 'w') as outfile:
        outfile.write( sdata )



def _strip_empty_lines(data):
    ldata = data.split('\n')

    rdata = []
    for index, line in enumerate(ldata):
        if len(line.strip()) == 0:
            line = line.strip()
        rdata.append(line)

    fdata = '\n'.join(rdata)
    if fdata[0] == '\n':
        fdata = fdata[1:]
    return fdata


def _format_yaml_dump2(sdata):
    """
    Format yaml-dump to make file more readable, used by yaml_save_roundtrip()
    (yaml structure must be dumped to a stream before using this function)
    | Currently does the following:
    | - Insert empty line after section w/o a value
    | - Insert empty line before section (key w/o a value)
    | - Adjust indentation of list entries
    | - Remove double line spacing introduced by ruamel.yaml
    | - Multiline strings: Remove '4' inserted by ruamel.yaml after '|'
    | - Remove empty line after section w/o a value, if the following line is a child-line


    :param data: string to format

    :return: formatted string
    """

    # Strip lines containing only spaces and strip empty lines inserted by ruamel.yaml
    sdata = _strip_empty_lines(sdata)
    sdata = sdata.replace('\n\n\n', '\n')
    sdata = sdata.replace('\n\n', '\n')
#    sdata = sdata.replace(': |4\n', ': |\n')    # Multiline strings: remove '4' inserted by ruyaml

    ldata = sdata.split('\n')
    rdata = []
    for index, line in enumerate(ldata):
        # Remove empty line after section w/o a value, if the following line is a child-line
        if len(line.strip()) == 0:
            try:
                nextline = ldata[index+1]
            except:
                nextline = ''
            indentprevline = len(ldata[index-1]) - len(ldata[index-1].lstrip(' '))
            indentnextline = len(nextline) - len(nextline.lstrip(' '))
            if indentnextline != indentprevline + indent_spaces:
                rdata.append(line)
        # Insert empty line after section w/o a value
        elif len(line.lstrip()) > 0 and  line.lstrip()[0] == '#':
            if line.lstrip()[-1:] == ':':
                rdata.append('')
            # only insert empty line, if last line was not a comment
            elif len(ldata[index-1].strip()) > 0 and ldata[index-1][0] != '#':
                # Only insert empty line, if next line is not commented out
                if len(ldata[index+1].strip()) > 0 and ldata[index+1][-1:] == ':' and ldata[index+1][0] != '#':
                    rdata.append('')
            rdata.append(line)

        # Insert empty line before section (key w/o a value)
        elif line[-1:] == ':':
            # only, if last line is not empty and last line is not a comment
            if len(ldata[index-1].lstrip()) > 0 and not (len(ldata[index-1].lstrip()) > 0 and ldata[index-1].lstrip()[0] == '#'):
                # no empty line before list attributes
                if ldata[index+1].strip() != '':
                    if ldata[index+1].strip()[0] != '-':
                        rdata.append('')
                else:
                    rdata.append('')
                rdata.append(line)
            else:
                rdata.append(line)
        else:
             rdata.append(line)

    sdata = '\n'.join(rdata)

    sdata = sdata.replace('\n---\n\n', '\n---\n')
    if sdata[0] == '\n':
        sdata = sdata[1:]
    return sdata


# ==================================================================================
#   support functions for class yamlfile
#

# Set a given data in a dictionary with position provided as a list
def setInDict(dataDict, path, value):
    mapList = path.split('.')
    try:
        for k in mapList[:-1]: dataDict = dataDict[k]
        dataDict[mapList[-1]] = value
    except:
        return False
    return True


# Get parent to a path
def get_parent(path):
    pathlist = path.split('.')
    parent = '.'.join(pathlist[0:len(pathlist)-1])
    return parent


# Get key without parent
def get_key(path):
    pathlist = path.split('.')
    key = pathlist[len(pathlist)-1]
    return key


# ==================================================================================
#   function for changing a single item-attribute in a yaml file
#

def writeBackToFile(filename, itempath, itemattr, value):
    """
    write the value of an item's attribute back to the yaml-file

    :param filename: name of the yaml-file (without the .yaml extension!)
    :param itempath: path of the item to modify
    :param itemattr: name of the item's attribute to modify
    :param value: new value for the attribute

    :return: formatted string
    """

    itemyamlfile = yamlfile(filename)
    if os.path.isfile(filename+YAML_FILE):
        itemyamlfile.load()
    itemyamlfile.setleafvalue(itempath, itemattr, value)
    itemyamlfile.save()


# ==================================================================================
#   class yamlfile (for editing multiple entries at a time)
#

class yamlfile():
    data = None
    filename = ''


    def __init__(self, filename, filename_write='', create_bak=False):
        """
        initialize class for handling a yaml-file (read/write)
        | It initializes an empty data-structure, which can be filled by the load() method
        | This class is to be used for editing of yaml-files, not for loading SmartHomeNG structures

        :param filename: name of the yaml-file (without the .yaml extension!)
        :param filename_write: name of the file to write the resluts to (if different from filename)
        :param create_bak: True, if a backup-file of the original file shall be created

        :return: formatted string
        """
        self.filename = filename
        if filename_write == '':
            self.filename_write = filename
        else:
            self.filename_write = filename_write
        self.filename_bak = self.filename_write + '.bak'+YAML_FILE
        self._create_bak = create_bak
        self.data = yaml.comments.CommentedMap([])


    def load(self):
        """
        load the contents of the yaml-file to the data-structure
        """
        self.data = yaml_load_roundtrip(self.filename)


    def save(self):
        """
        save the contents of the data-structure to the yaml-file
        """
        if self._create_bak and os.path.isfile(self.filename_write+YAML_FILE):
            os.rename(self.filename_write+YAML_FILE, self.filename_bak)
        yaml_save_roundtrip(self.filename_write, self.data)


    def getnode(self, path):
        """
        get the contents of a node (branch or leaf)

        :param path: path of the node to return

        :return: content of the node
        """
        returned, ret_nodetype = self._getFromDict(path)
        return returned


    def getvalue(self, path):
        """
        get the value of a leaf-node

        :param path: path of the node to return

        :return: value of the leaf (or None, if the node is no leaf-node)
        """
        returned, ret_nodetype = self._getFromDict(path)
        if ret_nodetype == 'leaf':
            return returned
        else:
            return None


    def getnodetype(self, path):
        """
        get the type of a node

        :param path: path of the node to return

        :return: node type ('branch', 'leaf' or 'none')
        """
        returned, ret_nodetype = self._getFromDict(path)
        return ret_nodetype


    def getvaluetype(self, path):
        """
        get the valuetype of a node

        :param path: path of the node to return

        :return: node valuetype
        """
        returned, ret_nodetype = self._getFromDict(path)
        result = str(type(returned))
        if result[0:8] == "<class '":
            result = result[8:-2]
        if result == 'ruamel.yaml.comments.CommentedSeq':
            result = 'list'
        return result


    # Add/set a leaf to an empty node, the branch node must exist
    def setvalue(self, path, value):
        """
        set the value of a leaf, specified by leaf-path

        :param path: path of the leaf-node to modify
        :param value: new value of the leaf-node
        """
        if value == None:
            try:
                self.getnode(get_parent(path)).pop(get_key(path), None)
            except AttributeError:
                pass
            if self.getnode(get_parent(path)) == yaml.comments.CommentedMap():
                node = self.getnode(get_parent(get_parent(path)))
                root = (node == None)
                if root:
                    self.data[get_key(get_parent(path))] = None
                else:
                    node[get_key(get_parent(path))] = None
            return
        else:
            return self._add_node_and_leaf(path, value)


    # Add/set a leaf with value, the branch is created if it does not exist
    def setleafvalue(self, branch, leaf, value):
        """
        set the value of a leaf, specified by branch-path and attribute name

        :param branch: path of the branch-node which contains th attribute
        :param attr: name of the attribute to modify
        :param value: new value of the attribute
        """
        try:
            self._ensurebranch(branch)
        except Exception as e:
            logger.error("shyaml.setleafvalue: Exception '{}'".format(str(e)))
        else:
            if value != None:
                self.setvalue(branch+'.'+leaf, value)

    # ----------------------------------------------------------

    # Add an empty branch
    def _ensurebranch(self, path):
        if self.getnodetype(path) == 'leaf':
            raise KeyError("Node-ERROR: Unable to set branch '"+path+"', it exists already as a leaf")
        elif self.getnodetype(path) == 'branch':
            pass
        else:
            if not self._addnode(path):
                raise KeyError("Node-ERROR: Unable to set branch '"+path+"' in item structure")


    # Add an empty branch
    def _addbranch(self, path):
        if self.getnodetype(path) == 'leaf':
            raise KeyError("Node-ERROR: Unable to set branch '"+path+"', it exists already as a leaf")
        elif self.getnodetype(path) == 'branch':
            raise KeyError("Node-ERROR: Unable to set branch '"+path+"', it exists already as a branch")
        else:
            if not self._addnode(path):
                raise KeyError("Node-ERROR: Unable to set branch '"+path+"' in item structure")


    # Add an empty node (internal for recursion)
    def _addnode(self, path):
        if self.getnodetype(path) != 'none':
            return False
        result = self._add_node_and_leaf(path, None)
        if not result:
            pathlist = path.split('.')
            parent = '.'.join(pathlist[0:len(pathlist)-1])
            if self._addnode(parent):
                result = self._add_node_and_leaf(path, None)
        return result


    # Add a leaf to an empty node
    def _add_node_and_leaf(self, path, value):
        if not setInDict(self.data, path, value):
            parent = get_parent(path)
            attr = path[len(parent)+1:]
            cm = yaml.comments.CommentedMap([(attr, value)])
            if not setInDict(self.data, parent, cm):
                return False
        return True


    # Get a given data from a dictionary with position provided as a list
    def _getFromDict(self, path):
        dataDict = self.data
        nodetype = '-'
        mapList = path.split('.')
        try:
            for k in mapList: dataDict = dataDict[k]
        except:
            nodetype = 'none'
            dataDict = None
        else:
            if isinstance(dataDict, yaml.comments.CommentedMap):
               nodetype = 'branch'
            else:
                nodetype = 'leaf'
        return dataDict, nodetype


