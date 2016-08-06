from binascii import hexlify, unhexlify
import logging
import os
import pprint
import re
import sys
import zlib

from biplist import readPlistFromString, writePlistToString
from twisted.internet import protocol, reactor, ssl, threads
from twisted.protocols.basic import LineReceiver
from twisted.protocols.portforward import ProxyClientFactory

from shsiri import SmartHomeSiriPlugin

class SiriProxy(LineReceiver, object):
    """ Base class for the SiriProxy - performs the majority of the siri protocol and sirious plugin handling. """
    peer = None  # the other end! (self.peer.peer == self)
    blocking = False
    ref_id = None  # last refId seen
    ace_host = None  # The X-Ace-Host of the current user
    consumer = None

    def __init__(self, plugins=[], triggers=[]):
        self.zlib_d = zlib.decompressobj()
        self.zlib_c = zlib.compressobj()
        self.plugins = plugins  # registered plugins
        self.triggers = triggers  # two-tuple mapping regex->plugin_function
        self.logger = logging.getLogger('')

    def setPeer(self, peer):
        self.peer = peer

    def lineReceived(self, line):
        """ Handles simple HTTP-style headers
            @todo parse X-Ace-Host: header
        """
        direction = '>' if self.__class__ == SiriProxyServer else '<'
        self.logger.debug("%s %s" % (direction, line))
        self.peer.sendLine(line)
        try:
            key, val = line.split(':')
            if key.strip() == 'X-Ace-Host':
                self.ace_host = self.peer.ace_host = val.strip()
        except ValueError:
            pass
        if not line:
            self.setRawMode()

    def rawDataReceived(self, data):
        """
            This is where the main Siri protocol handling is done.
            Raw data consists of:
                (aaccee02)?<zlib_packed_data>
            Once decompressed the data takes the form:
                (header)(body)
            The header is a binary hex representation of is one of three things:
                0200000000
                0300000000
                0400000000
            Where:
                02... indicated a binary plist payload (followed by the payload size)
                03... indicates a iphone->server ping (followed by the sequence id)
                04... indicates a server->iphone pong (followed by the sequence id)
            And the trailing digits are provided in base 16.
            The body is a binary plist.

            The aaccee02 header is immediately forwarded, as are ping/pong packets.

            04... packets are parsed and passed through `process_plist` before
            being re-injected (or discarded).
        """
        if self.zlib_d.unconsumed_tail:
            data = self.zlib_d.unconsumed_tail + data
        if hexlify(data[0:4]) == 'aaccee02':
            self.peer.transport.write(data[0:4])
            data = data[4:]
        ## Add `data` to decompress stream
        udata = self.zlib_d.decompress(data)
        if udata:
            ## If we get decompressed output, process it
            header = hexlify(udata[0:5])
            if header[1] in [3, 4]:
                ## Ping/Pong packets - pass them straight through
                return self.peer.transport.write(data)
            size = int(header[2:], 16)
            body = udata[5:(size + 5)]
            if body:
                ## Parse the plist data
                plist = readPlistFromString(body)
                ## and have the server/client process it
                direction = '>' if self.__class__ == SiriProxyServer else '<'
                self.logger.info("%s %s %s" % (direction, plist['class'], plist.get('refId', '')))
                self.logger.debug("%s" % pprint.pformat(plist))
                plist = self.process_plist(plist)
                if plist:
                    ## Stop blocking if it's a new session
                    if self.blocking and self.ref_id != plist['refId']:
                        self.blocking = False
                    ## Never block transcription packets, they're too useful
                    if not self.blocking or plist['class'] == 'SpeechRecognized':
                        self.inject_plist(plist)
                    else:
                        self.logger.info("! %s %s" % (plist['class'], plist.get('refId', '')))
                    if plist['class'] == 'SpeechRecognized':
                        self.process_speech(plist)
                else:
                    self.logger.info("! %s %s" % (plist['class'], plist.get('refId', '')))

    def process_plist(self, plist):
        ## Offer plugins a chance to intercept/modify plists early on
        fname = 'plist_from_%s' % ('client' if self.__class__ == SiriProxyServer else 'server')
        for plugin in self.plugins:
            plist = getattr(plugin, fname)(plist)
            if not plist:
                self.logger.info('plist blocked by plugin %s' % (plugin.__class__.__name__))
                return  # If a plugin returns None, the plist has been blocked
        return plist

    def inject_plist(self, plist):
        """
            Inject a plist into the session.
            This is essentially a reverse of `rawDataReceived`:
                * the plist dictionary is converted into to a binary plist
                * the size is measured and the appropriate 02... header generated
                * header and body are concatenated, compressed, and injected.
        """
        if hasattr(plist, 'to_dict'):
            plist = plist.to_dict()
        if not isinstance(plist, dict):
            self.logger.warning('Rejecting inject invalid plist data %s' % plist)
            return
        self.logger.info("* %s %s" % (plist['class'], plist.get('refId', '')))
        ref_id = plist.get('refId', None)
        if ref_id:
            self.ref_id = ref_id
        data = writePlistToString(plist)
        data_len = len(data)
        if data_len > 0:
            ## Add data_len to 0x200000000 and convert to hex, zero-padded to 10 digits
            #header = '{:x}'.format(0x0200000000 + data_len).rjust(10, '0')
            header = '%x' % (0x0200000000 + data_len)       
            data = self.zlib_c.compress(unhexlify(header.rjust(10,'0')) + data)
            self.peer.transport.write(data)
            self.peer.transport.write(self.zlib_c.flush(zlib.Z_FULL_FLUSH))

    def get_next_phrase(self, consumer):
        self.consumer = consumer

    def process_speech(self, plist):
        phrase = ''
        for phrase_plist in plist['properties']['recognition']['properties']['phrases']:
            for token in phrase_plist['properties']['interpretations'][0]['properties']['tokens']:
                if token['properties']['removeSpaceBefore']:
                    phrase = phrase[:-1]
                phrase += token['properties']['text']
                if not token['properties']['removeSpaceAfter']:
                    phrase += ' '
        if phrase:
            self.logger.info('[Speech Recognised] "%s"' % phrase)
            if self.consumer:
                self.logger.info("Sending phrase to consumer")
                self.consumer(phrase)
                self.consumer = None
            else:
                for trigger, function, item in self.triggers:
                    match = trigger.search(phrase)
                    if match:
                        self.logger.info('Phrase matched "{0}" for item/logic {1}'.format(trigger.pattern, item))
                        args = [phrase, match, item]
                        threads.deferToThread(function, *args)

    def connectionLost(self, reason):
        """ Reset ref_id and disconnect peer """
        self.logger.info('Connection lost')
        self.ref_id = None
        if self.peer:
            self.peer.transport.loseConnection()
            self.setPeer(None)


class SiriProxyClient(SiriProxy):
    def connectionMade(self):
        self.logger.info('Connected to server')
        self.peer.setPeer(self)
        for plugin in self.plugins:
            plugin.proxy = self
        self.peer.transport.resumeProducing()


class SiriProxyClientFactory(ProxyClientFactory):
    protocol = SiriProxyClient


class SiriProxyServer(SiriProxy):
    root = None
    _lines = 0
    _serve_ca = False
    clientProtocolFactory = SiriProxyClientFactory

    def connectionMade(self):
        self.logger.info('Connect from client')
        self.transport.pauseProducing()
        self.logger.info('Building %s' % self.clientProtocolFactory.__name__)
        client = self.clientProtocolFactory()
        client.setServer(self)
        client.plugins = self.plugins
        client.triggers = self.triggers
        self.logger.info('Connecting to %s:%s with %s' % (self.factory.host, self.factory.port, client.__class__.__name__))
        reactor.connectSSL(self.factory.host, self.factory.port, client, ssl.ClientContextFactory())

    def lineReceived(self, line):
        self._lines += 1
        if self._lines == 1:
            method, path, _ver = line.split(' ')
            if method.lower() == 'get':
                self.logger.info('GET Request - blocking request')
                self._serve_ca = True
        if self._serve_ca and not line:
            self.logger.info('Serving CA Certificate')
            crt = file(os.path.join(self.root, 'certificates', 'ca.pem'), 'rb').read()
            headers = {
                'Content-Type': 'application/x-pem-file',
                'Content-Length': len(crt),
                'Content-Disposition': 'attachment; filename=sirious-ca.pem',
                'Server': 'Sirious',
                'Connection': 'Close'
            }
            self.transport.write("HTTP/1.0 200 OK\r\n")
            headers_str = "\r\n".join('%s: %s' % (key, val) for key, val in headers.iteritems())
            self.transport.write("%s\r\n\r\n" % headers_str)
            self.transport.write(crt)
        if not self._serve_ca:
            return SiriProxy.lineReceived(self, line)


class SiriProxyFactory(protocol.Factory):
    protocol = SiriProxyServer

    def __init__(self, smarthome, root, items, logics):
        # kryten.apple.com since iOS6
        self.host = '17.167.224.4'
        # guzzoni.apple.com for iOS5
        #self.host = '17.174.4.4'
        self.port = 443
        self.root = root
        self._items = items
        self._logics = logics
        self.logger = logging.getLogger('')
        self._sh = smarthome

    def buildProtocol(self, addr):
        self.logger.info('Building %s' % self.protocol.__name__)
        protocol = self.protocol()
        protocol.root = self.root
        
        self.logger.debug('Instantiating SmartHome Siri Plugin')
        instance = SmartHomeSiriPlugin(self._sh)
        instance.logger = logging.getLogger('')
        protocol.plugins.append(instance)

        for pattern, item in self._items:
            if '(?P<Num>' in pattern:
                function = instance.set_num
            elif '(?P<True>' in pattern:
                function = instance.set_bool
            else:
                continue
            
            trigger_re = re.compile(pattern, re.I)
            protocol.triggers.append((trigger_re, function, item))
        for pattern, logic in self._logics:
            trigger_re = re.compile(pattern, re.I)
            protocol.triggers.append((trigger_re, instance.trigger_logic, logic))
        
        protocol.factory = self
        return protocol
