# https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/steps-to-create-a-smart-home-skill
# https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import ssl
import json
import uuid

class AlexaService(object):
    def __init__(self, logger, version, devices, actions, host, port, auth=None, https_certfile=None, https_keyfile=None):
        self.sh = sh
        self.logger = logger
        self.version = version
        self.devices = devices
        self.actions = actions

        self.logger.info("Alexa: service setup at {}:{}".format(host, port))

        handler_factory = lambda *args: AlexaRequestHandler(logger, version, devices, actions, *args)
        self.server = HTTPServer((self.host, self.port), handler_factory)

        if https_certfile: # https://www.piware.de/2011/01/creating-an-https-server-in-python/
            self.logger.info("Alexa: enabling SSL/TLS support with cert-file {} & key-file {}".format(https_certfile, https_keyfile))
            # TODO: client-certificates can be handled here as well: https://docs.python.org/2/library/ssl.html
            self.server.socket = ssl.wrap_socket(self.server.socket, server_side=True, certfile=https_certfile, keyfile=https_keyfile)

    def start(self):
        self.logger.info("Alexa: service starting")
        self.shutdown = False
        while not self.shutdown:
            self.server.handle_request()

    def stop(self):
        self.logger.info("Alexa: service stopping")
        self.shutdown = True

class AlexaRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, logger, version, devices, actions, *args):
        self.logger = logger
        self.version = version
        self.devices = devices
        self.actions = actions
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)

    def do_POST(self):
        # XXX ignore self.path and just respond
        try:
            length = int(self.headers.getheader('Content-Length'))
            data = self.rfile.read(length)
            req = json.loads(data)
            header = req['header']
            payload = req['payload']

            if header['namespace'] == 'Alexa.ConnectedHome.System':
                return self.handle_system(header, payload)

            elif header['namespace'] == 'Alexa.ConnectedHome.Discovery':
                return self.handle_discovery(header, payload)

            elif header['namespace'] == 'Alexa.ConnectedHome.Control':
                return self.handle_control(header, payload)

            else:
                msg = "unknown `header.namespace` '{}'".format(header['namespace'])
                self.logger.error(msg)
                self.send_error(400, msg)
        except Exception as e:
            self.send_error(500, str(e))

    def respond(self, response):
        json = json.dumps(response).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(json))
        self.end_headers()
        self.wfile.write(json)

    def handle_system(self, header, payload):
        directive = header['name']
        self.logger.debug("Alexa: system-directive '{}' received".format(directive))

        if directive == 'HealthCheckRequest':
            self.respond(self.confirm_health(payload))
        else:
            msg = "unknown `header.name` '{}'".format(directive)
            self.logger.error(msg)
            self.send_error(400, msg)

    def confirm_health(self, payload):
        requested_on = payload['initiationTimestamp']
        self.logger.debug("Alexa: confirming health as requested on {}".format(requested_on))
        return {
            'header': self.header('HealthCheckResponse', 'Alexa.ConnectedHome.System'),
            'payload': {
                'description': 'The system is currently healthy',
                'isHealthy': True
            }
        }

    def handle_discovery(self, header, payload):
        directive = header['name']
        self.logger.debug("Alexa: discovery-directive '{}' received".format(directive))

        if directive == 'DiscoverAppliancesRequest':
            self.respond(self.discover_appliances())
        else:
            msg = "unknown `header.name` '{}'".format(directive)
            self.logger.error(msg)
            self.send_error(400, msg)

    # https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#discovery-messages
    def discover_appliances(self):
        discovered = []
        for device in self.devices.all():
            discovered.append({
                'actions': device.supported_actions(),
                'additionalApplianceDetails': {
                    'item{}'.format(idx+1) : item.id() for idx, item in enumerate(device.backed_items())
                },
                'applianceId': device.id,
                'friendlyDescription': device.description,
                'friendlyName': device.name,
                'isReachable': True,
                'manufacturerName': 'smarthomeNG.alexa',
                'modelName': 'smarthomeNG.alexa-device',
                'version': self.version
            })

        return {
            'header': self.header('DiscoverAppliancesResponse', 'Alexa.ConnectedHome.Discovery'),
            'payload': {
                'discoveredAppliances': discovered
            }
        }

    def handle_control(self, header, payload):
        directive = header['name']
        self.logger.debug("Alexa: control-directive '{}' received".format(directive))

        action = self.actions.for_directive(directive)
        if action:
            try:
                self.respond( action(payload) )
            except Exception as e:
                self.logger.error("Alexa: execution of control-directive '{}' failed: {}".format(directive, e))
                self.respond({
                    'header': self.header('DriverInternalError', 'Alexa.ConnectedHome.Control'),
                    'payload': {}
                })
        else:
            self.logger.error("Alexa: no action implemented for directive '{}'".format(directive))
            self.respond({
                'header': self.header('UnexpectedInformationReceivedError', 'Alexa.ConnectedHome.Control'),
                'payload': {}
            })

    def header(self, name, namespace):
        return {
            'messageId': uuid.uuid4().hex,
            'name': name,
            'namespace': namespace,
            'payloadVersion': '2'
        }
