#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2021-     Martin Sinn                          m.sinn@gmx.de
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
This library imports modules with user-functions to be used in eval statements and in logics
"""

import os
import logging

_logger = logging.getLogger(__name__)


_uf_subdir = 'etc'
_uf_subdir = 'functions'

_func_dir = None
_user_modules = []


def init_lib(shng_base_dir=None):

    global _func_dir
    global _user_modules

    if shng_base_dir is not None:
        base_dir = shng_base_dir
        #_logger.notice("lib.userfunctions wurde initialisiert")
    else:
        #_logger.warning('lib.userfunctions wurde außerhalb von SmartHomeNG initialisiert')
        base_dir = os.getcwd()

    _func_dir = os.path.join(base_dir, _uf_subdir)

    user_modules = []
    if os.path.isdir(_func_dir):
        wrk = os.listdir(_func_dir)
        for f in wrk:
            if f.endswith('.py'):
                user_modules.append(f.split(".")[0])

    _user_modules = sorted(user_modules)


def import_user_modules():

    import importlib

    for m in _user_modules:
        modulename = _uf_subdir + '.' + m

        exec( f"globals()['{m}']=importlib.import_module('{modulename}')" )

        global _uf_version
        _uf_version = '?.?.?'
        try:
            exec( f"globals()['_uf_version'] = {m}._VERSION" )
        except:
            exec( f"{m}._VERSION = _uf_version" )

        global _uf_description
        _uf_description = '?'
        try:
            exec( f"globals()['_uf_description'] = {m}._DESCRIPTION" )
        except:
            exec( f"{m}._DESCRIPTION = _uf_description" )

        _logger.notice(f'Importing userfunctions uf.{m} v{_uf_version} - {_uf_description}')


def get_uf_dir():

    return _func_dir


def reload(userlib):

    import importlib

    if userlib in _user_modules:
        _logger.notice(f'Reloading userfunctions uf.{userlib}')
        exec( f"importlib.reload({userlib})")
        return True
    else:
        _logger.error(f'uf.reload: Userfunction uf.{userlib} do not exist')
        return False


def reload_all():

    if _user_modules == []:
        _logger.warning(f'No userfunctions are loaded, nothing to reload')
        return False
    else:
        result = True
        for lib in _user_modules:
            if not reload(lib):
                result = False
        return result


def list_userlib_files():

    for lib in _user_modules:
        _logger.warning(f'uf.{lib}')

