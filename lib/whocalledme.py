#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2024-       Martin Sinn                         m.sinn@gmx.de
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


import sys
import logging

_logger = logging.getLogger('lib.whocalledme')

LOG_INFO = False

def _log(text):

    if LOG_INFO:
        _logger.info(text)
        return

    try:
        _logger.notice(text)
    except:
        _logger.warning(text)
    return


def _cleanup_local_vars(locals):

    # clean up local vars
    local_vars = {}
    for lv in locals:
        if not str(type(locals[lv])) in ["<class 'module'>", "<class 'lib.smarthome.SmartHome'>", "<class 'lib.shtime.Shtime'>", "<class 'lib.item.items.Items'>"] :
            local_vars[lv] = locals[lv]
    return local_vars


def _build_called_by_chain():

    level = 4
    called_by = str(sys._getframe(level).f_code.co_name)
    while True:
        level += 1
        try:
            c_b = str(sys._getframe(level).f_code.co_name)
        except ValueError:
            c_b = ''
        if c_b == '':
            break
        called_by += ' -> ' + c_b
    return called_by


#####################################################################
# log_who_called_me
#####################################################################
def log_who_called_me(with_localvars=False, with_globalvars=False, log_info=False):
    """
    Display function deprecated warning
    """
    global LOG_INFO
    LOG_INFO = log_info

    func = str(sys._getframe(1).f_code.co_name) + '()'
    func_file = str(sys._getframe(1).f_code.co_filename)
    try:
        test = ' (' + str(sys._getframe(2).f_locals['self'].__module__) + ')'
    except:
        test = ''

    called_by = str(sys._getframe(2).f_code.co_name)
    in_class = ''
    try:
        in_class = 'class ' + str(sys._getframe(2).f_locals['self'].__class__.__name__) + test
    except:
        in_class = 'unknown type ' + test
    if called_by == '<module>':
        called_by = _build_called_by_chain()

    # clean up local vars
    local_vars =  _cleanup_local_vars(sys._getframe(3).f_locals)
    instance_text =' [' + str(local_vars.get('self', '')) + ']'

    if func_file.find('logics') > -1:
        # log calls from a logic
        init_by = str(local_vars.get('by', ''))
        if init_by != '':
            init_by = "initiated by '" + init_by + "'"
        if func == '<module>()':
            _log(f"Logic '{func_file}':")
            _log(f" - was called in '{in_class}' by '{called_by}' {init_by}")
        else:
            _log(f"Function '{func}' in logic '{func_file}':")
            if called_by.find('->') > -1:
                _log(f" - was called by the main routine of the logic")
            else:
                _log(f" - was called by function '{called_by}()' of the logic")
    else:
        # log calls from a module / class
        _log(f"Function '{func}'  [{func_file}]:")
        _log(f" - was called in '{in_class}'{instance_text} by '{called_by}'")

    if with_localvars:
#        local_vars = _cleanup_local_vars(sys._getframe(3).f_locals)
        _log(f" - Calling function '{sys._getframe(3).f_code.co_name}' had following local vars:")
        for lv in local_vars:
            _log(f"   - {lv} - {type(local_vars[lv])}  -  {local_vars[lv]}")

    if with_globalvars:
        class_vars = _cleanup_local_vars(sys._getframe(3).f_globals)
        _log(f" - Calling class '{sys._getframe(2).f_locals['self'].__class__.__name__}' had following local vars: {sys._getframe(2).f_locals}")
        for lv in class_vars:
            _log(f"   - {lv} - {type(class_vars[lv])}  -  {class_vars[lv]}")

    #_log(f"-> '{func}' [{func_file}]: Called in '{in_class}' by '{called_by}'")
    #_log(f"-> locals of {sys._getframe(3).f_code.co_name}: {sys._getframe(3).f_locals}")
    #for lv in local_vars:
    #    _log(f"  -> {lv} - {type(local_vars[lv])}  -  {local_vars[lv]}")
    return
