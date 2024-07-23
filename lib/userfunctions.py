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

from lib.translation import translate
from lib.constants import DIR_UF

_logger = logging.getLogger(__name__)


_uf_subdir = DIR_UF

_func_dir = None
_sh = None
_user_modules = []


def import_user_module(m):
    """
    Import a module with userfunctions

    :param m: name of module to import from <shng_base_dir>/functions

    :return: True, if import was successful
    """
    modulename = _uf_subdir + '.' + m

    import importlib
    try:
        exec(f"globals()['{m}']=importlib.import_module('{modulename}')")
    except Exception as e:
        _logger.error(translate("Error importing userfunctions from '{module}': {error}", {'module': m, 'error': e}))
        return False
    else:
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

        _logger.notice(translate("Imported userfunctions from '{module}' v{version} - {description}", {'module': m, 'version':_uf_version, 'description': _uf_description}))

        return True


def init_lib(shng_base_dir=None, sh=None):
    """
    Initialize userfunctions module

    :param shng_base_dir: Base dir of SmartHomeNG installation
    """

    global _func_dir
    global _user_modules
    global _sh
    _sh = sh

    if shng_base_dir is not None:
        base_dir = shng_base_dir
    else:
        base_dir = os.getcwd()

    if _sh:
        _func_dir = _sh.get_functionsdir()
    else:
        _func_dir = os.path.join(base_dir, _uf_subdir)

    user_modules = []
    if os.path.isdir(_func_dir):
        wrk = os.listdir(_func_dir)
        for f in wrk:
            if f.endswith('.py'):
                user_modules.append(f.split(".")[0])

    _user_modules = sorted(user_modules)

    # Import all modules with userfunctions from <shng_base_dir>/functions
    for m in _user_modules:
        import_user_module(m)
    return


def get_uf_dir():

    return _func_dir


def reload(userlib):

    import importlib

    if userlib in _user_modules:
        try:
            exec( f"importlib.reload({userlib})")
        except Exception as e:
            if str(e) == f"name '{userlib}' is not defined":
                _logger.warning(translate("Error reloading userfunctions Modul '{module}': Module is not loaded, trying to newly import userfunctions '{module}' instead", {'module': userlib}))
                if import_user_module(userlib):
                    return True
                else:
                    return False
            else:
                _logger.error(translate("Error reloading userfunctions '{module}': {error} - old version of '{module}' is still active", {'module': userlib, 'error': e}))
                return False

        else:
            _logger.notice(translate("Reloaded userfunctions '{module}'", {'module': userlib}))
            return True
    else:
        if import_user_module(userlib):
            _user_modules.append(userlib)
            #_logger.notice(translate("Reload: Loaded new userfunctions '{module}'", {'module': userlib}))
            return True
        else:
            _logger.error(translate("Reload: Userfunctions '{module}' do not exist", {'module': userlib}))
            return False


def reload_all():

    if _user_modules == []:
        _logger.warning(translate('No userfunctions are loaded, nothing to reload'))
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

