#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2025   Martin Sinn                         m.sinn@gmx.de
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
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
Path-resolution helpers for Item.

Extracted from lib/item/item.py.

Public functions
----------------
get_absolutepath(item, relativepath, attribute='')
    Convert a relative item path (starting with '.') to an absolute path.
    Replaces Item.get_absolutepath().

get_stringwithabsolutepathes(item, evalstr, begintag, endtag, attribute='')
    Convert relative item path references inside a string to absolute paths.
    Replaces Item.get_stringwithabsolutepathes().

find_attribute(item, attr, default='', level=-1, strict=False)
    Search for an attribute value walking up the item tree.
    Replaces Item.find_attribute().

split_destitem_from_value(value)
    Parse 'dest = expr' syntax from an on_change/on_update attribute value.
    Replaces Item._split_destitem_from_value() — pure string operation,
    no item reference needed.

expand_relativepathes(item, attr, begintag, endtag)
    In-place conversion of relative paths in an item conf attribute.
    Replaces Item.expand_relativepathes().

All functions access only single-underscore attributes and public methods on
Item so no name-mangling issues arise.
"""

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# get_absolutepath  (replaces Item.get_absolutepath)
# ---------------------------------------------------------------------------


def get_absolutepath(item, relativepath, attribute=''):
    """
    Build an absolute item path relative to the current item.

    :param item:         the Item instance
    :param relativepath: string with the relative item path
    :param attribute:    name of the item attribute that contains the path (for log entries)
    :return:             string with the absolute item path
    """
    if not isinstance(relativepath, str):
        return relativepath
    if (len(relativepath) == 0) or (relativepath[0] != '.'):
        return relativepath

    relpath = relativepath.rstrip()
    rootpath = item._path

    while relpath and relpath[0] == '.':
        relpath = relpath[1:]
        if relpath and relpath[0] == '.':
            if rootpath.rfind('.') == -1:
                if rootpath == '':
                    relpath = ''
                    logger.error(
                        '{}.get_absolutepath(): Relative path trying to access above'
                        " root level on attribute '{}'".format(item._path, attribute)
                    )
                else:
                    rootpath = ''
            else:
                rootpath = rootpath[: rootpath.rfind('.')]

    trailing_str = ''
    if relpath.startswith('self') and len(relpath) > 4:
        if relpath[4] in '() +-*/<>!=&%':
            trailing_str = relpath[4:]
            relpath = ''

    if relpath:
        rootpath = (rootpath + '.' + relpath) if rootpath else relpath
    rootpath += trailing_str

    logger.info(
        "{}.get_absolutepath('{}'): Result = '{}' (for attribute '{}')".format(
            item._path, relativepath, rootpath, attribute
        )
    )
    if rootpath[-5:] == '.self':
        rootpath = rootpath.replace('.self', '')
    rootpath = rootpath.replace('.self.', '.')
    return rootpath


# ---------------------------------------------------------------------------
# get_stringwithabsolutepathes  (replaces Item.get_stringwithabsolutepathes)
# ---------------------------------------------------------------------------


def get_stringwithabsolutepathes(item, evalstr, begintag, endtag, attribute=''):
    """
    Convert a string containing relative item paths to absolute item paths.

    The begintag and the endtag remain in the result string.

    :param item:      the Item instance
    :param evalstr:   string with the statement that may contain relative item paths
    :param begintag:  string (or list) that signals the beginning of a relative path
    :param endtag:    string (or list) that signals the end of a relative path
    :param attribute: name of the item attribute (for log entries)
    :return:          string with absolute item paths
    """

    def _checkfortags(evalstr, begintag, endtag):
        pref = ''
        rest = evalstr
        while rest.find(begintag + '.') != -1:
            pref += rest[: rest.find(begintag + '.') + len(begintag)]
            rest = rest[rest.find(begintag + '.') + len(begintag) :]
            if endtag == '' or rest.find(endtag) == -1:
                rel = rest
                rest = ''
            else:
                rel = rest[: rest.find(endtag)]
            rest = rest[rest.find(endtag) :]
            pref += get_absolutepath(item, rel, attribute)
            # Re-combine string for next loop
            rest = pref + rest
            pref = ''
        pref += rest
        logger.debug(
            "{}.get_stringwithabsolutepathes('{}') with begintag = '{}', endtag = '{}': result = '{}'".format(
                item._path, evalstr, begintag, endtag, pref
            )
        )
        return pref

    if not isinstance(evalstr, str):
        return evalstr

    if isinstance(begintag, list):
        diff_len = len(begintag) - len(endtag)
        begintag = begintag + [''] * abs(diff_len) if diff_len < 0 else begintag
        endtag = endtag + [''] * diff_len if diff_len > 0 else endtag
        for i in range(len(begintag)):
            if evalstr.find(begintag[i] + '.') != -1:
                evalstr = _checkfortags(evalstr, begintag[i], endtag[i])
        return evalstr
    else:
        if evalstr.find(begintag + '.') == -1:
            return evalstr
        return _checkfortags(evalstr, begintag, endtag)


# ---------------------------------------------------------------------------
# find_attribute  (replaces Item.find_attribute)
# ---------------------------------------------------------------------------


def find_attribute(item, attr, default='', level=-1, strict=False):
    """
    Find attribute value from item (level == 0) or a parent item.

    If level < 0, search up the whole item tree.
    If strict is set and the requested level is not reached, return ''.

    :param item:    the Item instance
    :param attr:    attribute name to look for
    :param default: value returned when attribute is not found
    :param level:   number of parent-levels to search (< 0 = unlimited)
    :param strict:  if True, return default when level is not reached
    :return:        attribute value
    """
    current = item
    nolimit = level < 0
    while (level >= 1 or nolimit) and (strict or attr not in current.conf):
        if current._is_top_of_item_tree():
            return default
        current = current.return_parent()
        level -= 1

    return current.conf.get(attr, default)


# ---------------------------------------------------------------------------
# split_destitem_from_value  (replaces Item._split_destitem_from_value)
# ---------------------------------------------------------------------------


def split_destitem_from_value(value):
    """
    For on_change and on_update: split destination item from attribute value.

    Parses ``dest = expr`` syntax.  Pure string operation — no item needed.

    :param value: attribute value string
    :return:      (dest_item, value) tuple
    """
    dest_item = ''
    if ((value.find('=') != -1) and (value.find('(') == -1)) or (
        (value.find('=') != -1) and (value.find('=') < value.find('('))
    ):
        if value.find('==') != -1:
            if value.find('=') < value.find('=='):
                dest_item = value[: value.find('=')].strip()
                value = value[value.find('=') + 1 :].strip()
        else:
            dest_item = value[: value.find('=')]
            value = value[value.find('=') + 1 :].strip()
    return dest_item, value


# ---------------------------------------------------------------------------
# expand_relativepathes  (replaces Item.expand_relativepathes)
# ---------------------------------------------------------------------------


def expand_relativepathes(item, attr, begintag, endtag):
    """
    Convert a configuration attribute containing relative item paths to absolute paths.

    The item's attribute can be of type str or list (of strings).
    The begintag and the endtag remain in the result string.

    :param item:     the Item instance
    :param attr:     name of the attribute (or wildcard ending with '*')
    :param begintag: string or list of strings that signal the start of a relative path
    :param endtag:   string or list of strings that signal the end of a relative path
    """

    def _checkforentry(attr_name):
        if isinstance(item.conf[attr_name], str):
            if begintag != '' and endtag != '':
                item.conf[attr_name] = get_stringwithabsolutepathes(
                    item, item.conf[attr_name], begintag, endtag, attr_name
                )
            elif begintag == '' and endtag == '':
                item.conf[attr_name] = get_absolutepath(item, item.conf[attr_name], attr_name)
        elif isinstance(item.conf[attr_name], list):
            logger.debug('expand_relativepathes(1): to expand={}'.format(item.conf[attr_name]))
            new_attr = []
            for a in item.conf[attr_name]:
                if isinstance(a, dict):
                    a = list('{!s}:{!s}'.format(k, v) for (k, v) in a.items())[0]
                logger.debug('expand_relativepathes: before : to expand={}'.format(a))
                if begintag != '' and endtag != '':
                    a = get_stringwithabsolutepathes(item, a, begintag, endtag, attr_name)
                elif begintag == '' and endtag == '':
                    a = get_absolutepath(item, a, attr_name)
                logger.debug('expand_relativepathes: after: to expand={}'.format(a))
                new_attr.append(a)
            item.conf[attr_name] = new_attr
            logger.debug('expand_relativepathes(2): expanded={}'.format(item.conf[attr_name]))
        else:
            logger.warning(
                'expand_relativepathes: attr={} can not expand for type(item.conf[attr_name])={}'.format(
                    attr_name, type(item.conf[attr_name])
                )
            )

    if isinstance(attr, str) and attr.endswith('*'):
        for entry in item.conf:
            if attr[:-1] in entry:
                _checkforentry(entry)
    elif attr in item.conf:
        _checkforentry(attr)


# ---------------------------------------------------------------------------
# get_attr
# ---------------------------------------------------------------------------


def get_attr(item, attr, default=''):
    """
    Return the value of *attr* from *item*'s own configuration dict.

    :param item:    ``Item`` instance.
    :param attr:    Attribute name to look up.
    :param default: Value returned when *attr* is absent (default ``''``).
    :return:        Attribute value or *default*.
    """
    return item.conf.get(attr, default)
