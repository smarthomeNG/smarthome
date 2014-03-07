#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2014 Marcus Popp                              marcus@popp.mx
#########################################################################
#  Free for non-commercial use
#########################################################################

import base64
import hashlib
import http.client
import logging
import random

logger = logging.getLogger('')


class Client():

    __paths = {}

    def basic_auth(self, username, password):
        return b'Basic ' + base64.b64encode((username + ':' + password).encode())

    def build_md5_hash(self, data):
        if isinstance(data, str):
            data = data.encode('utf-16le')
        elif isinstance(data, list):
            data = ":".join(data).encode()
        return hashlib.md5(data).hexdigest()

    def build_sha1_hash(self, data):
        if isinstance(data, str):
            data = data.encode()
        elif isinstance(data, list):
            data = ":".join(data).encode()
        return hashlib.sha1(data).hexdigest()

    def digest_auth(self, host, uri, headers, username, password, method):
        path = host + uri
        if 'www-authenticate' in headers:
            header = headers['www-authenticate']
            algorithm = header.get('algorithm', 'MD5').upper()
            qop = header.get('qop')
            realm = header['digest realm']
            nonce = header['nonce']
            count = 1
        elif path in self.__paths:
            qop, realm, nonce, count, algorithm = self.__paths[path]
            count += 1
        else:
            return ''
        if algorithm.startswith('MD5'):
            build_hash = self.build_md5_hash
        elif algorithm.startswith('SHA'):
            build_hash = self.build_sha1_hash
        else:
            logger.warning("WWW: unsupported algorithm: {}".format(algorithm))
            return ''
        cnonce = '{:02x}'.format(random.randrange(16 ** 32))
        nc = '{:08x}'.format(count)
        HA1 = build_hash([username, realm, password])
        if algorithm.endswith('-SESS'):
            HA1 = build_hash([HA1, nonce, cnonce])
        HA2 = build_hash([method, uri])
        if qop.startswith('auth'):
            response = build_hash([HA1, nonce, nc, cnonce, qop, HA2])
        else:
            response = build_hash([HA1, nonce, HA2])
        digest = 'Digest username="{}", realm="{}", nonce="{}", uri="{}", response="{}"'.format(username, realm, nonce, uri, response)
        if qop is not None:
            digest += ', qop="{}", nc="{}", cnonce="{}"'.format(qop, nc, cnonce)
        self.__paths[path] = qop, realm, nonce, count, algorithm
        return digest

    def fetch_url(self, url, auth=None, username=None, password=None, timeout=2, method='GET', headers={}, body=None):
        plain = True
        if url.startswith('https'):
            plain = False
        lurl = url.split('/')
        host = lurl[2]
        purl = '/' + '/'.join(lurl[3:])
        path = host + purl
        if plain:
            conn = http.client.HTTPConnection(host, timeout=timeout)
        else:
            conn = http.client.HTTPSConnection(host, timeout=timeout)
        if auth == 'basic':
            headers['Authorization'] = self.basic_auth(username, password)
        elif auth == 'digest' and path in self.__paths:
            headers['Authorization'] = self.digest_auth(host, purl, {}, username, password, method)
        try:
            conn.request(method, purl, body, headers)
            resp = conn.getresponse()
        except Exception as e:
            logger.warning("Problem fetching {0}: {1}".format(url, e))
            conn.close()
            return False
        if resp.status == 200:
            content = resp.read()
        elif resp.status == 401 and auth == 'digest':
            content = resp.read()
            rheaders = self.parse_headers(resp.getheaders())
            headers['Authorization'] = self.digest_auth(host, purl, rheaders, username, password, method)
            conn.request(method, purl, body, headers)
            resp = conn.getresponse()
            content = resp.read()
        else:
            logger.warning("Problem fetching {0}: {1} {2}".format(url, resp.status, resp.reason))
            content = False
        conn.close()
        return content

    def parse_headers(self, headers):
        result = {}
        for key, value in headers:
            if '=' in value:
                vdict = {}
                for entry in value.split(','):
                    key2, __, value2 = entry.partition('=')
                    if value2[0] == value2[-1] == '"':
                        value2 = value2[1:-1]
                    vdict[key2.lower()] = value2
                value = vdict
            result[key.lower()] = value
        return result
