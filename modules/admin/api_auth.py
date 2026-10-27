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


import os
import logging
import json
import cherrypy
from datetime import timedelta

import jwt

# from lib.item import Items
from lib.utils import Utils
from lib.constants import DIR_ETC, DIR_MODULES

from .rest import ApiDoc, RESTResource


class AuthController(RESTResource):
    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(
            __name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:]
        )

        self.etc_dir = self._sh.get_config_dir(DIR_ETC)
        self.modules_dir = self._sh.get_config_dir(DIR_MODULES)

        if self.module.rest_dispatch_force_exception:
            self.logger.notice('REST_dispatch_execute warnlevel is set to EXCEPTION')

        # self._user_dict = user_dict
        self.jwt_secret = module.jwt_secret

        http_user_dict = self.module.mod_http.get_user_dict()
        self._user_dict = {user: data for user, data in http_user_dict.items() if data.get('password_hash')}

        return

    # ======================================================================
    #  /api/authenticate
    #
    def root(self):
        """
        returns information if the root of the REST API is called

        Note: the root of the REST API is not protected by authentication
        """
        raise cherrypy.HTTPError(400)

    # ======================================================================
    #  /api/authenticate/user (POST)
    #
    def authenticate(self):
        """
        Check the posted credentials and return a JWT for a valid login.

        Without configured users every request gets an admin token named 'Autologin'.

        :return: JSON with a 'token' key on success, an empty JSON object otherwise
        """
        cl = cherrypy.request.headers.get('Content-Length', 0)
        if cl == 0:
            raise cherrypy.HTTPError(status=411)
        rawbody = cherrypy.request.body.read(int(cl))
        try:
            credentials = json.loads(rawbody.decode('utf-8'))
        except Exception as e:
            self.logger.warning('AuthController.authenticate(): Exception {}'.format(e))
            return 'Bad, bad request'

        response = {}
        remote_ip = cherrypy.request.remote.ip
        if self._user_dict == {}:
            response['token'] = self._issue_token('Autologin', True, 7 * 24)
            self.logger.info(f'AuthController.authenticate(): Autologin from {remote_ip}')
        else:
            username = credentials.get('username', '')
            user = self._user_dict.get(username, None)
            if user and Utils.check_hashed_password(credentials.get('password', ''), user.get('password_hash', '')):
                admin = 'admin' in user.get('groups', [])
                response['token'] = self._issue_token(user.get('name', '?'), admin, self.module.login_expiration)
                self.logger.info(f"AuthController.authenticate(): login of user '{username}' from {remote_ip}")
            else:
                self.logger.warning(
                    f"AuthController.authenticate(): failed login for user '{username}' from {remote_ip}"
                )
        return json.dumps(response)

    def _issue_token(self, name: str, admin: bool, ttl_hours: float) -> str:
        """
        Return a signed JWT for a login.

        :param name: display name of the logged in user
        :param admin: True if the user belongs to the admin group
        :param ttl_hours: validity of the token in hours
        """
        url = cherrypy.url().split(':')[0] + ':' + cherrypy.url().split(':')[1]
        now = self.module.shtime.now()
        payload = {
            'iss': url,
            'iat': now,
            'jti': now.timestamp(),
            'exp': now + timedelta(hours=ttl_hours),
            'ttl': ttl_hours,
            'name': name,
            'admin': admin,
        }
        return self._encode_token(payload)

    def _encode_token(self, payload: dict) -> str:
        """Sign ``payload`` as HS256 JWT; PyJWT < 2 returns bytes, PyJWT >= 2 str."""
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        return token.decode('utf-8') if isinstance(token, bytes) else token

    # ======================================================================
    #  /api/authenticate/renew (PUT)
    #
    def renew_token(self):
        """
        Return the request's token, with a new expiry time if login_autorenew is set.

        :return: JSON with 'token', 'result' and 'description'
        """
        response = {}

        old_token = self.REST_get_jwt_token()
        self.logger.debug('- renew_token(): decoded old token = {}'.format(old_token))

        if self.module.login_autorenew:
            new_token = dict(old_token)
            new_token['iat'] = self.module.shtime.now()
            new_token['exp'] = self.module.shtime.now() + timedelta(hours=self.module.login_expiration)
            response['token'] = self._encode_token(new_token)
            self.logger.info(
                'AuthController.renew_token(): remote.ip = {}, user = {}'.format(
                    cherrypy.request.remote.ip, new_token['name']
                )
            )
            response['description'] = 'token renewed'
        else:
            response['token'] = self._encode_token(old_token)
            response['description'] = 'token not renewed'
        response['result'] = 'ok'

        return json.dumps(response)

    # ======================================================================
    #  Handling of http REST requests
    #
    @cherrypy.expose
    def read(self, id=None):
        """
        Handle GET requests
        """
        # self.logger.debug("AuthController.index(): /{}".format(id))

        if id is None:
            return self.root()

        # self.logger.info("AuthController.index(): /{} - unhandled".format(id))
        return None

    read.expose_resource = True
    read.authentication_needed = False

    @cherrypy.expose
    def add(self, id=''):
        """
        Handle POST requests
        """
        self.logger.info('AuthController.add(): /{}'.format(id))

        if id == 'user':
            return self.authenticate()

        self.logger.info('AuthController.add(): /{} - unhandled'.format(id))
        return None

    add.expose_resource = True
    add.authentication_needed = False
    add.api_doc = [
        ApiDoc(
            summary='Log in with username/password, get a JWT',
            method='post',
            path='/authenticate/user',
            auth=False,
            tags=['authenticate'],
            request_body='application/json',
            request_example='{"username": "<username>", "password": "<password>"}',
            response_example='{"token": "<jwt>"}',
        )
    ]

    @cherrypy.expose
    def update(self, id=''):
        """
        Handle PUT requests (hief kommt noch die Token Verlängerung rein)
        """
        self.logger.info('AuthController.update(): /{}'.format(id))

        if id == 'user':
            pass
            # return self.renew()
        if id == 'renew':
            return self.renew_token()

        self.logger.info('AuthController.update(): /{} - unhandled'.format(id))
        return None

    update.expose_resource = True
    update.authentication_needed = True
    update.api_doc = [
        ApiDoc(
            summary='Renew the current JWT before it expires',
            method='put',
            path='/authenticate/renew',
            tags=['authenticate'],
            response_example='{"token": "<renewed jwt>"}',
        )
    ]
