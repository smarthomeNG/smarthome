#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
#########################################################################
#  This file is part of SmartHomeNG.    https://github.com/smarthomeNG//
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

import logging, sys, re, os
import threading
import socket
import urllib.request
import urllib.parse
import urllib.error
import lib.connection

logger = logging.getLogger('')


class HTTPHandler(lib.connection.Stream):
    def __init__(self, smarthome, parser, dest, sock, source):
        lib.connection.Stream.__init__(self, sock, source)
        self._sh = smarthome
        self.terminator = b"\r\n\r\n"
        self.parser = parser
        self._lock = threading.Lock()
        self.dest = dest
        self.source = source

    def found_terminator(self, data):
        for line in data.decode().splitlines():
            if line.startswith('GET'):
                request = line.split(' ')[1].strip('/')
                request = urllib.parse.unquote_plus(request)
                if self.parser(self.source, self.dest, request) is not False:
                    parsedText=ParseText(self._sh, request)
                    parse_result = parsedText.parse_message()
                    if parse_result[1]:
                        self.send(bytes("HTTP/1.1 200 OK\r\nContent-type: text/html; charset=UTF-8\r\n\r\n%s" % parse_result[1][2], encoding="utf-8"), close=True)
                    else:
                        self.send(bytes("HTTP/1.1 200 OK\r\nContent-type: text/html; charset=UTF-8\r\n\r\n%s" % parse_result[0], encoding="utf-8"), close=True)
                else:
                        self.send(bytes("HTTP/1.1 200 OK\r\nContent-type: text/html; charset=UTF-8\r\n\r\n%s" % dictError['error'], encoding="utf-8"), close=True)
            else:
                self.send(b'HTTP/1.1 400 Bad Request\r\n\r\n', close=True)
            break

class HTTPDispatcher(lib.connection.Server):
    def __init__(self, smarthome, parser, ip, port):
        lib.connection.Server.__init__(self, ip, port)
        self._sh = smarthome
        self.parser = parser
        self.dest = 'http:' + ip + ':' + port
        self.connect()

    def handle_connection(self):
        sock, address = self.accept()
        if sock is None:
            return
        HTTPHandler(self._sh, self.parser, self.dest, sock, address)

class Speech_Parser():
    listeners = {}
    socket_warning = 10
    socket_warning = 2
    errorMessage = False

    def __init__(self, smarthome, ip='0.0.0.0', port='2788', acl='*', config_file="", default_access=""):
        self._sh = smarthome
        self.config = config_file
        self.acl = self.parse_acl(acl)
        self.default_access = default_access
        self.add_listener(ip, port, acl)
        logger.info("SP: Server Starts - %s:%s" % (ip, port))

        if os.path.exists(self.config):
            config_base = os.path.basename(self.config)
            if config_base == "speech.py":
                sys.path.append(os.path.dirname(os.path.expanduser(self.config)))
                global varParse, dictError
                from speech import varParse, dictError
            else:
                logger.error("Configuration file (%s) error, the filename should be speech.py" % config_base)
                return [self.errorMessage, False]
        else:
            logger.error("Configuration file not found")
            return [self.errorMessage, False]

    def add_listener(self, ip, port, acl='*'):
        dest = 'http:' + ip + ':' + port
        logger.info("SP: Adding listener on: {}".format(dest))
        dispatcher = HTTPDispatcher(self._sh, self.parse_input, ip, port)
        if not dispatcher.connected:
            return False
        acl = self.parse_acl(acl)
        self.listeners[dest] = {'items': {}, 'logics': {}, 'acl': acl}
        return True

    def parse_acl(self, acl):
        if acl == '*':
            return False
        if isinstance(acl, str):
            return [acl]
        return acl

    def parse_input(self, source, dest, data):
        if dest in self.listeners:
            parse_text = ParseText(self._sh, data)
            result = parse_text.parse_message()
            if not result[0]:
                result = result[1]
            else:
                errorMessage = result[0]
                return [False, errorMessage]
            name, value, answer, typ, varText = result
            logger.info('Speech Parse data: '+str(data)+' Result: '+str(result))
            #logger.debug("SP: Result: "+str(result))
            #logger.debug("SP: Item: "+name)
            #logger.debug("SP: Value: "+value)
            #logger.debug("SP: Answer: "+answer)
            #logger.debug("SP: Typ: "+typ)
            source, __, port = source.partition(':')
            gacl = self.listeners[dest]['acl']
            if typ == 'item':
                if name not in self.listeners[dest]['items']:
                    logger.error("SP: Item '{}' not available in the listener.".format(name))
                    return False
                iacl = self.listeners[dest]['items'][name]['acl']
                if iacl:
                    if source not in iacl:
                        logger.error("SP: Item '{}' acl doesn't permit updates from {}.".format(name, source))
                        return False
                elif gacl:
                    if source not in gacl:
                        logger.error("SP: Network acl doesn't permit updates from {}.".format(source))
                        return False

                item = self.listeners[dest]['items'][name]['item']
                # Parameter default_access added 141207 (KNXfriend)
                if item.conf['sp'] == 'rw' or self.default_access == 'rw':
                    item(value, source)

            elif typ == 'logic':
                if name not in self.listeners[dest]['logics']:
                    logger.error("SP: Logic '{}' not available in the listener.".format(name))
                    return False
                lacl = self.listeners[dest]['logics'][name]['acl']
                if lacl:
                    if source not in lacl:
                        logger.error("SP: Logic '{}' acl doesn't permit triggering from {}.".format(name, source))
                        return False
                elif gacl:
                    if source not in gacl:
                        logger.error("SP: Network acl doesn't permit triggering from {}.".format(source))
                        return False
                logic = self.listeners[dest]['logics'][name]['logic']
                logic.trigger(varText, source, value)
            else:
                logger.error("SP: Unsupporter key element {}. Data: {}".format(typ, data))
                return False
        else:
            logger.error("SP: Destination {}, not in listeners!".format(dest))
            return False
        return True

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_logic(self, logic):
        self.parse_obj(logic, 'logic')

    def parse_item(self, item):
        self.parse_obj(item, 'item')

    def parse_obj(self, obj, obj_type):
        # sp
        if obj_type == 'item':
            oid = obj.id()
        elif obj_type == 'logic':
            oid = obj.id()
        else:
            return

        if 'sp_acl' in obj.conf:
            acl = obj.conf['sp_acl']
        else:
            acl = False
        if 'sp' in obj.conf:  # adding object to listeners
            if obj.conf['sp'] in ['ro', 'rw', 'yes']:
                for dest in self.listeners:
                    self.listeners[dest][obj_type + 's'][oid] = {obj_type: obj, 'acl': acl}
            else:
                errorMessage = dictError['rights_error']

class ParseText():
    parseText = False
    errorMessage = False

    def __init__(self, smarthome, varText):
        self._sh = smarthome
        self.parseText = varText

    def parse_message(self):
        for parseline in varParse:
            varResult = self.get_expr(parseline)

            if varResult:
                answer = varResult[3]
                name = varResult[0]
                value = varResult[1]
                typ = varResult[4]
                logger.debug("SP: parseText: "+self.parseText)
                logger.debug("SP: Item: "+name)
                logger.debug("SP: Value: "+value)
                logger.debug("SP: List: "+str(varResult[2]))
                logger.debug("SP: Answer: "+answer)
                logger.debug("SP: Typ: "+typ)

                #get status if needed
                if value == '%status%':
                    value_received = str(self.get_item_value(name))
                    value_received = value_received.replace('.', ',') # Dezimal Zahlen werden mit Punkt getrennt, ersetzen durch Komma
                    answer = answer.replace('%status%', value_received) # Platzhalter %status% ersetzen

                return(False, [name, value, answer, typ, self.parseText])
            else:
                self.errorMessage = dictError['unknown_command']
        return [self.errorMessage, False]

    def get_expr(self, parseline):
        varItem = parseline[0]
        varValue = parseline[1]
        varVars = parseline[2]
        varAnswer = parseline[3]
        varList = []
        varList2 = []
        reg_ex = ".*"
        if len(parseline) == 5:
            varTyp = parseline[4].lower()
        else:
            varTyp = 'item'

        # Build regular expression
        for x in range(0,len(varVars)):
            reg_ex += '('
            if type(varVars[x]) == list:
                for var2 in varVars[x]:
                    for word in var2[1]:
                        reg_ex += str(word) + '|'
                reg_ex = reg_ex[:-1] + ')'
            else:
                reg_ex += str(varVars[x]) + ')'
            reg_ex += '.*'
            if len(varVars)-1 != x:
                reg_ex += ' '
        logger.debug("Regular Expression:\n>"+reg_ex+"<")
        # Test regulare Expressioin on transmited Text
        mo = re.match(reg_ex, self.parseText, re.IGNORECASE)

        if mo:
            for x in range(0,len(varVars)):
                if type(varVars[x]) == list:
                    for y in range(0,len(varVars[x])):
                        if mo.group(x+1).lower() in varVars[x][y][1]:
                            varList.append(str(varVars[x][y][0]))
                            varList2.append(str(varVars[x][y][1][0]))
                else:
                    varList.append(str(mo.group(x+1)))
                    varList2.append(str(mo.group(x+1)))
            for x in range(0,len(varList)):
                var = '%'+str(x)+'%'
                varItem = varItem.replace(var, str(varList[x]))
                varValue = varValue.replace(var, str(varList[x]))
                if varList[x].lower() == '%status%':
                    varAnswer = varAnswer.replace(var, '%status%')
                else:
                    varAnswer = varAnswer.replace(var, str(varList2[x]))
            return (varItem, varValue, varList, varAnswer, varTyp)
        self.errorMessage = dictError['unknown_command']
        return False

    def get_item_value(self, status_item):
        item = self._sh.return_item(status_item)
        if not item():
            self.errorMessage = dictError['status_error']
        return item()
