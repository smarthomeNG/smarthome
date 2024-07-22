#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2018-      Martin Sinn                         m.sinn@gmx.de
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
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################


import base64
import os
import datetime
import logging
import json
import cherrypy

import lib.backup
from lib.item import Items
from .rest import RESTResource

import bin.shngversion
from lib.item_conversion import convert_yaml as convert_yaml
from lib.item_conversion import parse_for_convert as parse_for_convert
from lib.shtime import Shtime


# ======================================================================
#  Controller for REST API /api/files
#
class FilesController(RESTResource):
    """
    Controller for REST API /api/files
    """

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])

        self.etc_dir = self._sh.get_etcdir()
        self.items_dir = self._sh._items_dir
        self.functions_dir = self._sh.get_functionsdir()
        self.scenes_dir = self._sh._scenes_dir
        self.logics_dir = self._sh.get_logicsdir()
        self.extern_conf_dir = self._sh._extern_conf_dir
        self.modules_dir = os.path.join(self.base_dir, 'modules')
        return


    def get_body(self, text=False, binary=False):
        """
        Get content body of received request header (for file uploads)

        :return:
        """
        cl = cherrypy.request.headers.get('Content-Length', 0)
        if cl == 0:
            # cherrypy.reponse.headers["Status"] = "400"
            # return 'Bad request'
            raise cherrypy.HTTPError(status=411)
        rawbody = cherrypy.request.body.read(int(cl))
        self.logger.debug("ServicesController(): get_body(): rawbody = {}".format(rawbody))
        try:
            if binary:
                wrk = rawbody.decode('ascii').split(',')
                datatype = wrk[0].split(';')
                if datatype[1] == 'base64':
                    params = base64.b64decode(wrk[1])
                else:
                    self.logger.error("ServicesController(): get_body(): cannot decode: rawbody = {}".format(rawbody))
                    params = wrk[1]
            else:
                if text:
                    params = rawbody.decode('utf-8')
                else:
                    params = json.loads(rawbody.decode('utf-8'))
        except Exception as e:
            self.logger.warning("ServicesController(): get_body(): Exception {}".format(e))
            return None
        return params


    # def strip_empty_lines(self, txt):
    #     """
    #     Remove \r from text and remove exessive empty lines from end
    #     """
    #     txt = txt.replace('\r', '').rstrip()
    #     while txt.endswith('\n'):
    #         txt = txt[:-1].rstrip()
    #     txt += '\n\n'
    #     #        self.logger.warning("strip_empty_lines: txt = {}".format(txt))
    #     return txt


    # ======================================================================
    #  /api/files/logging
    #
    def get_logging_config(self):

        self.logger.info("FilesController.get_logging_config()")
        filename = os.path.join(self.etc_dir, 'logging.yaml')
        read_data = None
        with open(filename, encoding='UTF-8') as f:
            read_data = f.read()
        return cherrypy.lib.static.serve_file(filename, 'application/x-download',
                                 'attachment', 'logging.yaml')


    def save_logging_config(self):
        """
        Save logging configuration

        :return: status dict
        """
        params = None
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("FilesController.save_logging_config(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.debug("FilesController.save_logging_config(): '{}'".format(params))


        filename = os.path.join(self.etc_dir, 'logging.yaml')
        read_data = None
        with open(filename, 'w', encoding='UTF-8') as f:
            f.write(params)

        result = {"result": "ok"}
        return json.dumps(result)


    # ======================================================================
    #  /api/files/structs
    #
    def get_struct_config(self):

        self.logger.info("FilesController.get_struct_config()")
        filename = os.path.join(self.etc_dir, 'struct.yaml')
        if not(os.path.isfile(filename)):
            open(filename, 'a', encoding='UTF-8').close()
            self.logger.info("FilesController.get_struct_config(): created empty file {}".format(filename))

        read_data = None
        with open(filename, encoding='UTF-8') as f:
            read_data = f.read()
        return cherrypy.lib.static.serve_file(filename, 'application/x-download',
                                 'attachment', 'struct.yaml')


    def save_struct_config(self):
        """
        Save struct configuration

        :return: status dict
        """
        params = None
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("FilesController.save_struct_config(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.debug("FilesController.save_struct_config(): '{}'".format(params))


        filename = os.path.join(self.etc_dir, 'struct.yaml')
        read_data = None
        with open(filename, 'w', encoding='UTF-8') as f:
            f.write(params)

        result = {"result": "ok"}
        return json.dumps(result)


    # ======================================================================
    #  /api/files/items
    #
    def get_items_filelist(self):

        list = os.listdir( self.items_dir )
        filelist = []
        for filename in list:
            if filename.endswith('.yaml'):
                filelist.append(filename)
            if filename.endswith('.conf'):
                filelist.append(filename)

        self.logger.info("filelist = {}".format(filelist))
        self.logger.info("filelist.sort() = {}".format(filelist.sort()))
        return json.dumps(sorted(filelist))


    def get_items_config(self, fn):

        self.logger.info("FilesController.get_items_config({})".format(fn))
        filename = os.path.join(self.items_dir, fn + '.yaml')
        read_data = None
        with open(filename, encoding='UTF-8') as f:
            read_data = f.read()
        return cherrypy.lib.static.serve_file(filename, 'application/x-download',
                                 'attachment', fn + '.yaml')


    def save_items_config(self, filename):
        """
        Save items configuration

        :return: status dict
        """
        params = None
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("FilesController(): save_items_config(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.debug("FilesController(): save_items_config(): '{}'".format(params))


        filename = os.path.join(self.items_dir, filename + '.yaml')
        read_data = None
        with open(filename, 'w', encoding='UTF-8') as f:
            f.write(params)

        result = {"result": "ok"}
        return json.dumps(result)


    def delete_items_config(self, filename):
        """
        Delete an items configuration file

        :return: status dict
        """
        self.logger.debug("FilesController(): delete_items_config(): '{}'".format(filename))

        filename = os.path.join(self.items_dir, filename + '.yaml')
        os.remove(filename)

        result = {"result": "ok"}
        return json.dumps(result)


    # ======================================================================
    #  /api/files/scenes
    #
    def get_scenes_filelist(self):

        list = os.listdir( self.scenes_dir )
        filelist = []
        for filename in list:
            if filename.endswith('.yaml'):
                filelist.append(filename)
            if filename.endswith('.conf'):
                filelist.append(filename)

        self.logger.info("filelist = {}".format(filelist))
        self.logger.info("filelist.sort() = {}".format(filelist.sort()))
        return json.dumps(sorted(filelist))


    def get_scenes_config(self, fn):

        self.logger.info("FilesController.get_scenes_config({})".format(fn))
        filename = os.path.join(self.scenes_dir, fn + '.yaml')
        read_data = None
        with open(filename, encoding='UTF-8') as f:
            read_data = f.read()
        return cherrypy.lib.static.serve_file(filename, 'application/x-download',
                                 'attachment', fn + '.yaml')


    def save_scenes_config(self, filename):
        """
        Save scene configuration

        :return: status dict
        """
        params = None
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("FilesController.save_scenes_config(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.debug("FilesController.save_scenes_config(): '{}'".format(params))


        filename = os.path.join(self.scenes_dir, filename + '.yaml')
        read_data = None
        with open(filename, 'w', encoding='UTF-8') as f:
            f.write(params)

        result = {"result": "ok"}
        return json.dumps(result)


    def delete_scenes_config(self, filename):
        """
        Delete a scene configuration file

        :return: status dict
        """
        self.logger.debug("FilesController.delete_scenes_config(): '{}'".format(filename))

        filename = os.path.join(self.scenes_dir, filename + '.yaml')
        os.remove(filename)

        result = {"result": "ok"}
        return json.dumps(result)


    # ======================================================================
    #  /api/files/functions
    #
    def get_functions_filelist(self):

        list = os.listdir( self.functions_dir )
        filelist = []
        for filename in list:
            if filename.endswith('.py'):
                filelist.append(filename)

        self.logger.info("filelist = {}".format(filelist))
        self.logger.info("filelist.sort() = {}".format(filelist.sort()))
        return json.dumps(sorted(filelist))

    def get_functions_config(self, fn):

        self.logger.info("FilesController.get_functions_config({})".format(fn))
        if fn.endswith('.tpl'):
            filename = os.path.join(self.functions_dir, fn)
        else:
            filename = os.path.join(self.functions_dir, fn + '.py')
        read_data = None
        with open(filename, encoding='UTF-8') as f:
            read_data = f.read()
        return cherrypy.lib.static.serve_file(filename, 'application/x-download',
                                 'attachment', fn + '.py')


    def save_functions_config(self, filename):
        """
        Save function library

        :return: status dict
        """
        params = None
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("FilesController.save_functions_config(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.debug("FilesController.save_functions_config(): '{}'".format(params))


        filename = os.path.join(self.functions_dir, filename + '.py')
        read_data = None
        with open(filename, 'w', encoding='UTF-8') as f:
            f.write(params)

        result = {"result": "ok"}
        return json.dumps(result)


    def delete_functions_config(self, filename):
        """
        Delete a scene configuration file

        :return: status dict
        """
        self.logger.debug("FilesController.delete_functions_config(): '{}'".format(filename))

        filename = os.path.join(self.functions_dir, filename + '.py')
        os.remove(filename)

        result = {"result": "ok"}
        return json.dumps(result)

    # ======================================================================
    #  /api/files/logics
    #
    def get_logics_filelist(self):

        list = os.listdir( self.logics_dir )
        filelist = []
        for filename in list:
            if filename.endswith('.py'):
                filelist.append(filename)

        self.logger.info("filelist = {}".format(filelist))
        self.logger.info("filelist.sort() = {}".format(filelist.sort()))
        return json.dumps(sorted(filelist))


    def get_logics_config(self, fn):

        self.logger.info("FilesController.get_logics_config({})".format(fn))
        filename = os.path.join(self.logics_dir, fn)
        read_data = None
        with open(filename, encoding='UTF-8') as f:
            read_data = f.read()
        return cherrypy.lib.static.serve_file(filename, 'application/x-download',
                                 'attachment', fn)


    def save_logics_config(self, filename):
        """
        Save items configuration

        :return: status dict
        """
        params = None
        params = self.get_body(text=True)
        if params is None:
            self.logger.warning("FilesController.save_logics_config(): Bad, request")
            raise cherrypy.HTTPError(status=411)
        self.logger.debug("FilesController.save_logics_config(): '{}'".format(params))


        filename = os.path.join(self.logics_dir, filename)
        read_data = None
        with open(filename, 'w', encoding='UTF-8') as f:
            f.write(params)

        result = {"result": "ok"}
        return json.dumps(result)


    # ======================================================================
    #  /api/files/...
    #
    def cachecheck(self):
        """
        returns a list of items as json structure
        """
        unused_cache_files = []

        if self._sh.shng_status['code'] == 20:
            # {'code': 20, 'text': 'Running'}
            cache_path = os.path.join(self.base_dir, 'var', 'cache')
            onlyfiles = [f for f in os.listdir(cache_path) if os.path.isfile(os.path.join(cache_path, f))]

            for file in onlyfiles:
                if not file.find(".") == 0:  # filter .gitignore etc.
                    self.items = Items.get_instance()
                    item = self.items.return_item(file)
                    no_cache_file = False;
                    if item is None:
                        self.logger.debug("cachecheck: no item {}".format(file))
                        no_cache_file = True
                    elif not item._cache:
                        self.logger.debug("cachecheck: item {}, no _cache".format(file))
                        no_cache_file = True

                    if no_cache_file:
                        file_data = {}
                        file_data['last_modified'] = datetime.datetime.fromtimestamp(
                            int(os.path.getmtime(os.path.join(cache_path, file)))
                        ).strftime('%Y-%m-%d %H:%M:%S')
                        file_data['created'] = datetime.datetime.fromtimestamp(
                            int(os.path.getctime(os.path.join(cache_path, file)))
                        ).strftime('%Y-%m-%d %H:%M:%S')
                        file_data['filename'] = file
                        file_data['filename'] = file
                        unused_cache_files.append(file_data)

        return json.dumps(unused_cache_files)

    # --------------------------------------------------------------------------------------

    def get_config_backup(self):

        filename = lib.backup.create_backup(self.extern_conf_dir, self.base_dir)
        # self.logger.warning("FilesController.get_config_backup(): filename = '{}'".format(filename))

        read_data = None
        with open(filename, 'rb') as f:
            read_data = f.read()

        return read_data


    def get_config_backup2(self):

        filename = lib.backup.create_backup(self.extern_conf_dir, self.base_dir)
        # self.logger.warning("FilesController.get_config_backup2(): filename = '{}'".format(filename))
        cherrypy.lib.static.serve_file(filename, 'application/zip', 'attachment', 'shng_config_backup.zip')
        return json.dumps({"result": "ok"})


    def restore_config(self, filename):
        """
        Restore previously created backup

        :param filename:
        :return:
        """
        self.logger.info("FilesController.restore_config(filename='{}')".format(filename))

        old_shng_status = self._sh.shng_status
        if old_shng_status['code'] != 20:
            response = {'result': 'error', 'text': "SmartHomeNG is not in state 'running'"}
            return

        self._sh.shng_status = {'code': 101, 'text': 'Restore: Uploading'}

        # create restore directory, if it does not exist
        restore_dir = os.path.join(self.base_dir, 'var', 'restore')
        if not os.path.isdir(restore_dir):
            try:
                os.makedirs(restore_dir)
            except OSError as e:
                self.logger.error("Cannot create directory - No restore was created - Error {}".format(e))
                result = {"result": "Cannot create directory - No restore was created - Error {}".format(e)}
                self.shng_status = old_shng_status
                return result
            self.logger.info("FilesController.restore_config(): Directory '{}' created".format(restore_dir))


        params = None
        params = self.get_body(binary=True)
        if params is None:
            self.logger.warning("FilesController.restore_config(): Bad, request")
            self.shng_status = old_shng_status
            raise cherrypy.HTTPError(status=411)
        self.logger.debug("FilesController.restore_config(): '{}'".format(params))

        # write file to restore-directory

        # !!! make restore-directory empty !!!

        fn = os.path.join(restore_dir, filename)
        read_data = None
        with open(fn, 'w+b') as f:
            f.write(params)
        self.logger.info("FilesController.restore_config(): Configuration '{}' uploaded".format(filename))

        self._sh.shng_status = {'code': 102, 'text': 'Restore: Restoring'}
        fn = lib.backup.restore_backup(self.extern_conf_dir, self.base_dir)
        if fn is None:
            self.shng_status = old_shng_status
            result = {"result": "error"}
        else:
            self.logger.info("FilesController.restore_config(): Configuration '{}' restored".format(filename))
            self._sh.shng_status = {'code': 103, 'text': 'Restart clicked'}

            self._sh.restart('Restore Config')
            result = {"result": "ok"}

        return json.dumps(result)



    # ======================================================================
    #  GET /api/services/
    #
    def read(self, id='', filename=''):
        """
        Handle GET requests for server API
        """
        self.logger.info("FilesController.read(id='{}', filename='{}')".format(id, filename))

        if id == 'logging':
            cherrypy.response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
            return self.get_logging_config()
        elif id == 'structs':
            cherrypy.response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
            return self.get_struct_config()

        elif (id == 'items' and filename == ''):
            return self.get_items_filelist()
        elif id == 'items':
            cherrypy.response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
            return self.get_items_config(filename)

        elif (id == 'scenes' and filename == ''):
            return self.get_scenes_filelist()
        elif id == 'scenes':
            cherrypy.response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
            return self.get_scenes_config(filename)

        elif (id == 'functions' and filename == ''):
            return self.get_functions_filelist()
        elif id == 'functions':
            cherrypy.response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
            return self.get_functions_config(filename)

        elif (id == 'logics' and filename == ''):
            return self.get_logics_filelist()
        elif id == 'logics':
            cherrypy.response.headers['Cache-Control'] = 'no-cache, max-age=0, must-revalidate, no-store'
            return self.get_logics_config(filename)

        elif id == 'backup':
            return self.get_config_backup()
        return None

    read.expose_resource = True
    read.authentication_needed = True


    def update(self, id='', filename=''):
        """
        Handle PUT requests for server API
        """
        self.logger.info("FilesController.update(id='{}', filename='{}')".format(id, filename))

        if id == 'logging':
            return self.save_logging_config()
        elif id == 'structs':
            return self.save_struct_config()
        elif (id == 'items' and filename != ''):
            return self.save_items_config(filename)
        elif (id == 'scenes' and filename != ''):
            return self.save_scenes_config(filename)
        elif (id == 'functions' and filename != ''):
            return self.save_functions_config(filename)
        elif (id == 'logics' and filename != ''):
            return self.save_logics_config(filename)
        elif (id == 'restore' and filename != ''):
            return self.restore_config(filename)

        return None

    update.expose_resource = True
    update.authentication_needed = True


    def add(self, id='', filename=''):
        """
        Handle POST requests for server API
        """
        self.logger.info("FilesController.add(id='{}', filename='{}')".format(id, filename))

        #if (id == 'restore' and filename != ''):
        #    return self.restore_config(filename)

        return None

    add.expose_resource = True
    add.authentication_needed = True


    def delete(self, id='', filename=''):
        """
        Handle DELETE requests for server API
        """
        self.logger.info("FilesController.delete(id='{}', filename='{}')".format(id, filename))

        if (id == 'items' and filename != ''):
            return self.delete_items_config(filename)
        if (id == 'scenes' and filename != ''):
            return self.delete_scenes_config(filename)
        if (id == 'functions' and filename != ''):
            return self.delete_functions_config(filename)

        return None

    delete.expose_resource = True
    delete.authentication_needed = True

