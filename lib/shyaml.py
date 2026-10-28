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

import io
import logging
import os
import re
import shutil

from collections import OrderedDict

from lib.constants import YAML_FILE


logger = logging.getLogger(__name__)

try:
    from ruamel.yaml import YAML
    from ruamel.yaml.comments import CommentedMap, CommentedSeq
    from ruamel.yaml.constructor import SafeConstructor
    from ruamel.yaml.representer import SafeRepresenter

    EDITING_ENABLED = True
except ImportError:
    EDITING_ENABLED = False
    logger.critical('shyaml: ruamel.yaml is not installed')
    exit(1)

#: indentation of mappings and sequences in files written by SmartHomeNG
_INDENT = 4
#: line width up to which the round trip dumper does not wrap scalars
_ROUNDTRIP_WIDTH = 12288
#: attribute of round trip loaded data: YAML version of the file ((1, 1) for '%YAML 1.1', None without directive)
_VERSION_ATTR = '_shng_yaml_version'
#: attribute of round trip loaded data: the file's directives section up to '---' (ruamel drops its comments)
_HEADER_ATTR = '_shng_yaml_header'
_HEADER = re.compile(r'\A((?:[ \t]*\n)*%[^\n]*\n(?:[%#][^\n]*\n|[ \t]*\n)*---)(?=[ \n])')


def editing_is_enabled():
    return EDITING_ENABLED


# ==================================================================================
#   Routines to handle yaml files
#


MERGE_TAG = 'tag:yaml.org,2002:merge'


def _ordered_constructor(source):
    """
    Build a safe constructor class that loads mappings as OrderedDict and logs a warning for every key
    defined twice in one mapping (the last definition wins).

    :param source: file name (or other label) shown in the warning
    :type source: str
    :return: constructor class
    """

    class OrderedConstructor(SafeConstructor):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._checked_mappings = set()

        def flatten_mapping(self, node):
            if id(node) not in self._checked_mappings:
                self._checked_mappings.add(id(node))
                self._warn_duplicate_keys(node)
            return super().flatten_mapping(node)

        def _warn_duplicate_keys(self, node):
            first_lines = {}
            for key_node, _value_node in node.value:
                if key_node.tag == MERGE_TAG:
                    continue
                key = (key_node.tag, key_node.value)
                line = key_node.start_mark.line + 1
                if key not in first_lines:
                    first_lines[key] = line
                else:
                    logger.warning(
                        f'{source}: duplicate key "{key_node.value}" in line {line}, first defined in line '
                        f'{first_lines[key]} - the last definition replaces the earlier ones'
                    )

    def construct_ordered_mapping(constructor, node):
        constructor.flatten_mapping(node)
        return OrderedDict(constructor.construct_pairs(node))

    OrderedConstructor.add_constructor('tag:yaml.org,2002:map', construct_ordered_mapping)
    return OrderedConstructor


def _safe_yaml(ordered, source):
    """
    Return a safe loader: plain dicts that reject duplicate keys, or (ordered) OrderedDicts that warn about them.

    :param ordered: load mappings as OrderedDict
    :param source: file name (or other label) shown in duplicate key warnings
    """
    yaml = YAML(typ='safe', pure=True)
    if ordered:
        yaml.Constructor = _ordered_constructor(source)
        yaml.allow_duplicate_keys = True
    return yaml


def _explain_load_error(estr):
    """Add a hint to the parser messages for the two most common mistakes (TABs, missing space after a colon)."""
    if "found character '\\t'" in estr:
        estr = estr[estr.find('line') :]
        estr = 'TABs are not allowed in YAML files, use spaces for indentation instead!\nError in ' + estr
    if ('while scanning a simple key' in estr) and ("could not find expected ':'" in estr):
        estr = estr[estr.find('column') : estr.find('could not')]
        estr = 'The colon (:) following a key has to be followed by a space. The space is missing!\nError in ' + estr
    return estr


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
        with open(filename, 'r', encoding='utf-8-sig') as stream:
            sdata = stream.read()
        y = _safe_yaml(ordered, filename).load(sdata)
    except Exception as e:
        estr = _explain_load_error(str(e))
        if '(line: ' in estr:
            estr += '\nNOTE: Look for the error at the expected <block end>, near the second specified line number'
        if '[Errno 2]' in estr:
            if not ignore_notfound:
                logger.warning(f"yaml_load: YAML-file '{filename}' not found")
        else:
            logger.error('YAML-file load error in {}:  \n{}'.format(filename, estr))

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
        y = _safe_yaml(ordered, '<string>').load(string)
    except Exception as e:
        estr = _explain_load_error(str(e))

    return y, estr


class _OrderedSafeRepresenter(SafeRepresenter):
    """Safe representer that writes an OrderedDict as a plain mapping."""


_OrderedSafeRepresenter.add_representer(
    OrderedDict, lambda representer, data: representer.represent_mapping('tag:yaml.org,2002:map', data.items())
)


def yaml_save(filename, data):
    """
    Save contents of an OrderedDict structure to a yaml file

    :param filename: name of the yaml file to save to
    :type filename: str
    :param data: configuration data to to save
    :type filename: str
    :type data: OrderedDict, dict

    :returns: Nothing
    """

    dict_type = 'OrderedDict' if isinstance(data, OrderedDict) else 'dict'
    logger.info("Saving '{}' to '{}'".format(dict_type, filename))
    yaml = YAML(typ='safe', pure=True)
    yaml.Representer = _OrderedSafeRepresenter
    yaml.default_flow_style = False
    yaml.indent(mapping=_INDENT, sequence=_INDENT, offset=0)
    yaml.width = 768
    yaml.allow_unicode = True
    stream = io.StringIO()
    yaml.dump(data, stream)
    sdata = _format_yaml_dump(stream.getvalue())
    with open(filename, 'w', encoding='utf8') as outfile:
        outfile.write(sdata)


# ==================================================================================


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
            if ldata[index + 1].strip()[0] != '-':
                rdata.append('')
            rdata.append(line)
        else:
            rdata.append(line)
    fdata = '\n'.join(rdata)
    return fdata


# ==================================================================================
#   Routines to handle editing of yaml files
#


def strip_yaml_extension(filename):
    """
    Strip a trailing .yaml or .yml (case-insensitive) from *filename*, if
    present. Callers are not always consistent about whether they pass a
    bare basename or one that already includes an extension - shng only
    ever reads/writes the .yaml form on disk, so this normalizes either
    input to the same basename.

    :param filename: Basename of a yaml file, with or without extension
    :type filename: str

    :return: filename with any trailing .yaml/.yml removed
    :rtype: str
    """
    lower = filename.lower()
    if lower.endswith('.yaml'):
        return filename[:-5]
    if lower.endswith('.yml'):
        return filename[:-4]
    return filename


def yaml_exists(filename):
    """
    Check whether the yaml file for *filename* exists on disk, regardless
    of whether *filename* already includes a .yaml/.yml extension or not.

    A bare ``os.path.isfile(filename + YAML_FILE)`` would silently return
    False (making callers wrongly conclude "doesn't exist yet") when
    *filename* already ends in an extension, since it would then look for
    a nonexistent ``...yaml.yaml`` path.

    :param filename: Basename of the yaml file, with or without extension
    :type filename: str

    :return: True if the file exists
    :rtype: bool
    """
    return os.path.isfile(strip_yaml_extension(filename) + YAML_FILE)


def _roundtrip_yaml(version=None):
    """
    Return a round trip loader/dumper: comments, key order, quotes and the YAML version of a file are kept;
    indentation is SmartHomeNG's (4 spaces, dashes below their key).

    :param version: YAML version to write ((1, 1) adds a '%YAML 1.1' directive), None for none
    """
    yaml = YAML(typ='rt')
    yaml.indent(mapping=_INDENT, sequence=_INDENT, offset=0)
    yaml.width = _ROUNDTRIP_WIDTH
    yaml.allow_unicode = True
    yaml.preserve_quotes = True
    if version is not None:
        yaml.version = version
    return yaml


def yaml_load_roundtrip(filename, raise_on_error=False):
    """
    Load contents of a yaml file into an dict structure for editing (using Roundtrip Loader)

    The YAML version of the file is kept with the returned data, so yaml_save_roundtrip() writes the
    file back in the same version; values would change their meaning otherwise (``yes`` is a boolean
    in YAML 1.1 and a string in 1.2, ``010`` is 8 in 1.1 and 10 in 1.2).

    :param filename: name of the yaml file to load
    :param raise_on_error: if True, re-raise a load/parse failure instead
                            of swallowing it into an empty dict. Callers
                            that go on to MODIFY and SAVE the result must
                            set this — treating a parse error the same as
                            "file is legitimately empty" makes the
                            following save() silently truncate the file
                            to just the one change being made, destroying
                            everything else in it.
    :type raise_on_error: bool

    :return: data structure loaded from file
    """

    if not EDITING_ENABLED:
        return None

    y = None
    filename = strip_yaml_extension(filename) + YAML_FILE
    try:
        with open(filename, 'r', encoding='utf-8-sig') as stream:
            sdata = stream.read()
        yaml = _roundtrip_yaml()
        y = yaml.load(sdata)
        if isinstance(y, (CommentedMap, CommentedSeq)):
            setattr(y, _VERSION_ATTR, yaml.version)
            header = _HEADER.match(sdata)
            setattr(y, _HEADER_ATTR, header.group(1) if header else None)
    except Exception as e:
        message = str(e)
        logger.error("yaml_load_roundtrip: YAML-file load error in %s: '%s'" % (filename, message))
        if raise_on_error:
            raise ValueError(message) from e
        y = {}
    return y


def get_emptynode():
    """
    Return an empty node
    """
    return CommentedMap([])


def get_commentedseq(lst):
    """
    Convert a list to a commented sequence
    """
    return CommentedSeq(lst)


def yaml_dump_roundtrip(data):
    """
    Dump yaml to a string using the round trip dumper

    Data loaded by yaml_load_roundtrip() is written in the YAML version of its file, with the file's own
    directives section (including comments in it); other data without a version directive (YAML 1.2).
    Indentation is always SmartHomeNG's (4 spaces, dashes below their key).

    :param data: data structure to save
    """

    stream = io.StringIO()
    _roundtrip_yaml(getattr(data, _VERSION_ATTR, None)).dump(data, stream)
    sdata = stream.getvalue()
    header = getattr(data, _HEADER_ATTR, None)
    if header:
        sdata = _HEADER.sub(lambda _match: header, sdata, count=1)
    return sdata


def yaml_save_roundtrip(filename, data, create_backup=False):
    """
    Dump yaml using the round trip dumper (see yaml_dump_roundtrip())

    :param filename: name of the yaml file to save to
    :param data: data structure to save
    """

    if not EDITING_ENABLED:
        return
    sdata = yaml_dump_roundtrip(data)

    filename = strip_yaml_extension(filename) + YAML_FILE
    if create_backup:
        if os.path.isfile(filename):
            shutil.copy2(filename, filename + '.bak')

    with open(filename, 'w', encoding='utf8') as outfile:
        outfile.write(sdata)


# ==================================================================================
#   support functions for class yamlfile
#


# Set a given data in a dictionary with position provided as a list
def setInDict(dataDict, path, value):
    mapList = path.split('.')
    try:
        for k in mapList[:-1]:
            dataDict = dataDict[k]
        dataDict[mapList[-1]] = value
    except (KeyError, TypeError):
        return False
    return True


# Get parent to a path
def get_parent(path):
    pathlist = path.split('.')
    parent = '.'.join(pathlist[0 : len(pathlist) - 1])
    return parent


# Get key without parent
def get_key(path):
    pathlist = path.split('.')
    key = pathlist[len(pathlist) - 1]
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
    if yaml_exists(filename):
        itemyamlfile.load()
    itemyamlfile.setleafvalue(itempath, itemattr, value)
    itemyamlfile.save()


# ==================================================================================
#   class yamlfile (for editing multiple entries at a time)
#


class yamlfile:
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
        self.filename = strip_yaml_extension(filename)
        if filename_write == '':
            self.filename_write = self.filename
        else:
            self.filename_write = strip_yaml_extension(filename_write)
        self.filename_bak = self.filename_write + '.bak' + YAML_FILE
        self._create_bak = create_bak
        self.data = CommentedMap([])

    def load(self):
        """
        load the contents of the yaml-file to the data-structure

        A file whose root is literally ``null`` (e.g. after setvalue()
        removed its last top-level key) loads as ``None`` - normalize that
        to an empty CommentedMap, matching __init__'s default, so setvalue()
        doesn't silently no-op on every subsequent call (None[key] = ...
        raises TypeError, which setInDict() swallows and turns into a
        no-op).

        Raises on a genuine parse failure (e.g. a duplicate-key error
        elsewhere in the file) rather than treating it the same as an
        empty file - this class is used to load, modify ONE value, and
        save the whole file back; silently continuing with empty data
        would make save() overwrite the rest of the file's contents with
        nothing.
        """
        self.data = yaml_load_roundtrip(self.filename, raise_on_error=True)
        if self.data is None:
            self.data = CommentedMap([])

    def save(self):
        """
        save the contents of the data-structure to the yaml-file

        If the data-structure is now empty (e.g. the last item defined in
        this file was removed), delete the file instead of writing a
        redundant ``{}`` document - an empty file and a "file with an
        empty mapping" are equivalent for every reader in this codebase,
        so there's nothing worth keeping.
        """
        if self._create_bak and os.path.isfile(self.filename_write + YAML_FILE):
            os.rename(self.filename_write + YAML_FILE, self.filename_bak)
        if not self.data:
            filepath = self.filename_write + YAML_FILE
            if os.path.isfile(filepath):
                os.remove(filepath)
                logger.info("Deleted now-empty yaml file '{}'".format(filepath))
            return
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
        if value is None:
            parent_path = get_parent(path)
            # get_parent() returns '' for a top-level path; getnode('') does
            # not resolve to self.data, it's a lookup miss - special-case it.
            parent_node = self.data if parent_path == '' else self.getnode(parent_path)
            try:
                parent_node.pop(get_key(path), None)
            except AttributeError:
                pass
            if parent_path != '' and self.getnode(parent_path) == CommentedMap():
                node = self.getnode(get_parent(parent_path))
                root = node is None
                if root:
                    self.data[get_key(parent_path)] = CommentedMap()
                else:
                    node[get_key(parent_path)] = CommentedMap()
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
            if value is not None:
                self.setvalue(branch + '.' + leaf, value)

    # ----------------------------------------------------------

    # Add an empty branch
    def _ensurebranch(self, path):
        if self.getnodetype(path) == 'leaf':
            raise KeyError("Node-ERROR: Unable to set branch '" + path + "', it exists already as a leaf")
        elif self.getnodetype(path) == 'branch':
            pass
        else:
            if not self._addnode(path):
                raise KeyError("Node-ERROR: Unable to set branch '" + path + "' in item structure")

    # Add an empty branch
    def _addbranch(self, path):
        if self.getnodetype(path) == 'leaf':
            raise KeyError("Node-ERROR: Unable to set branch '" + path + "', it exists already as a leaf")
        elif self.getnodetype(path) == 'branch':
            raise KeyError("Node-ERROR: Unable to set branch '" + path + "', it exists already as a branch")
        else:
            if not self._addnode(path):
                raise KeyError("Node-ERROR: Unable to set branch '" + path + "' in item structure")

    # Add an empty node (internal for recursion)
    def _addnode(self, path):
        if self.getnodetype(path) != 'none':
            return False
        result = self._add_node_and_leaf(path, None)
        if not result:
            pathlist = path.split('.')
            parent = '.'.join(pathlist[0 : len(pathlist) - 1])
            if self._addnode(parent):
                result = self._add_node_and_leaf(path, None)
        return result

    # Add a leaf to an empty node
    def _add_node_and_leaf(self, path, value):
        """
        Set ``value`` at ``path``, creating missing ancestors as branches

        :return: False if an ancestor is a leaf holding a value, True otherwise
        """
        node = self.data
        for key in path.split('.')[:-1]:
            if node.get(key) is None:
                node[key] = CommentedMap()
            node = node[key]
            if not isinstance(node, dict):
                return False
        return setInDict(self.data, path, value)

    # Get a given data from a dictionary with position provided as a list
    def _getFromDict(self, path):
        dataDict = self.data
        nodetype = '-'
        mapList = path.split('.')
        try:
            for k in mapList:
                dataDict = dataDict[k]
        except (KeyError, TypeError):
            nodetype = 'none'
            dataDict = None
        else:
            if isinstance(dataDict, CommentedMap):
                nodetype = 'branch'
            else:
                nodetype = 'leaf'
        return dataDict, nodetype
