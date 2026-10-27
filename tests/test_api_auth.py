#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Tests for modules/admin/api_auth.py's AuthController (login and token renewal)."""

import json
import logging
import os
import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import cherrypy
import jwt

from lib.utils import Utils
from modules.admin.api_auth import AuthController

SECRET = 'test-secret-with-at-least-32-bytes!'
PASSWORD = 'correct horse battery staple'
PASSWORD_HASH = Utils.create_hash(PASSWORD)


def make_controller(users=None, autorenew=True):
    """Return an AuthController wired to fake module/sh objects."""
    sh = SimpleNamespace(get_basedir=lambda: '/tmp', get_config_dir=lambda name: '/tmp')
    module = SimpleNamespace(
        _sh=sh,
        rest_dispatch_force_exception=False,
        jwt_secret=SECRET,
        mod_http=SimpleNamespace(get_user_dict=lambda: users or {}),
        shtime=SimpleNamespace(now=lambda: datetime.now(timezone.utc)),
        login_expiration=8,
        login_autorenew=autorenew,
    )
    return AuthController(module)


class AuthControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.headers = {}
        self.request.remote.ip = '192.0.2.1'
        patches = [
            patch.object(cherrypy, 'request', self.request),
            patch.object(cherrypy, 'url', lambda *a, **k: 'http://shng.test:8383/api/authenticate/user'),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def post_credentials(self, controller, credentials):
        body = json.dumps(credentials).encode('utf-8')
        self.request.headers = {'Content-Length': str(len(body))}
        self.request.body.read = lambda n: body
        return json.loads(controller.authenticate())


class TestAuthenticate(AuthControllerTestCase):
    users = {'admin': {'password_hash': PASSWORD_HASH, 'name': 'Admin', 'groups': ['admin']}}

    def test_valid_credentials_return_token(self):
        response = self.post_credentials(make_controller(self.users), {'username': 'admin', 'password': PASSWORD})

        decoded = jwt.decode(response['token'], SECRET, algorithms=['HS256'])
        self.assertEqual('Admin', decoded['name'])
        self.assertTrue(decoded['admin'])

    def test_salted_hash_login(self):
        users = {'admin': {'password_hash': Utils.hash_password(PASSWORD), 'name': 'Admin', 'groups': ['admin']}}
        response = self.post_credentials(make_controller(users), {'username': 'admin', 'password': PASSWORD})

        self.assertIn('token', response)

    def test_wrong_password_returns_no_token(self):
        response = self.post_credentials(make_controller(self.users), {'username': 'admin', 'password': 'nope'})

        self.assertNotIn('token', response)

    def test_without_users_autologin_token_is_returned(self):
        response = self.post_credentials(make_controller({}), {'username': '', 'password': ''})

        self.assertEqual('Autologin', jwt.decode(response['token'], SECRET, algorithms=['HS256'])['name'])

    def test_secrets_are_not_logged(self):
        controller = make_controller(self.users)
        with self.assertLogs(controller.logger, level=logging.DEBUG) as logs:
            response = self.post_credentials(controller, {'username': 'admin', 'password': PASSWORD})
            self.post_credentials(controller, {'username': 'admin', 'password': 'wrong-' + PASSWORD})

        logged = '\n'.join(logs.output)
        self.assertNotIn(PASSWORD, logged)
        self.assertNotIn(PASSWORD_HASH, logged)
        self.assertNotIn(response['token'], logged)


class TestRenewToken(AuthControllerTestCase):
    def setUp(self):
        super().setUp()
        self.old_token = {'name': 'Admin', 'admin': True, 'exp': 4102444800, 'iat': 1700000000}
        token = jwt.encode(self.old_token, SECRET, algorithm='HS256')
        self.request.headers = {'Authorization': 'Bearer ' + token}

    def test_token_is_renewed_with_autorenew(self):
        response = json.loads(make_controller(autorenew=True).renew_token())

        decoded = jwt.decode(response['token'], SECRET, algorithms=['HS256'])
        self.assertEqual('token renewed', response['description'])
        self.assertGreater(decoded['iat'], self.old_token['iat'])

    def test_old_token_is_returned_without_autorenew(self):
        response = json.loads(make_controller(autorenew=False).renew_token())

        self.assertEqual('token not renewed', response['description'])
        self.assertEqual(self.old_token, jwt.decode(response['token'], SECRET, algorithms=['HS256']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
