# https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/steps-to-create-a-smart-home-skill
# https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference

import cherrypy
import simplejson
import uuid

class AlexaService(object):

    def __init__(self, sh, logger, version, devices, actions, host, port):
        self.sh = sh
        self.logger = logger
        self.version = version

        self.devices = devices
        self.actions = actions

        self.logger.info("Alexa: service setup at {}:{}".format(host, port))
        cherrypy.config.update({
            'server.socket_host': host,
            'server.socket_port': port,
        })
        #cherrypy.log.screen = True
        cherrypy.log.access_file = None
        #cherrypy.log.error_file = '/tmp/smarthome-alexa-errors.log'
        cherrypy.tree.mount(self, '/')

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        req = cherrypy.request.json
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
            raise cherrypy.HTTPError("400 Bad Request", msg)

    def start(self):
        cherrypy.engine.start()
        self.logger.info("Alexa: service started")

    def stop(self):
        cherrypy.engine.exit()
        self.logger.info("Alexa: service stopped")

    def handle_system(self, header, payload):
        directive = header['name']
        self.logger.debug("Alexa: system-directive '{}' received".format(directive))

        if directive == 'HealthCheckRequest':
            return self.confirm_health(payload)
        else:
            msg = "unknown `header.name` '{}'".format(directive)
            self.logger.error(msg)
            raise cherrypy.HTTPError("400 Bad Request", msg)

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
            return self.discover_appliances()
        else:
            msg = "unknown `header.name` '{}'".format(directive)
            self.logger.error(msg)
            raise cherrypy.HTTPError("400 Bad Request", msg)

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
                return action(payload)
            except Exception as e:
                self.logger.error("Alexa: execution of control-directive '{}' failed: {}".format(directive, e))
                return {
                    'header': self.header('DriverInternalError', 'Alexa.ConnectedHome.Control'),
                    'payload': {}
                }
        else:
            self.logger.error("Alexa: no action implemented for directive '{}'".format(directive))
            return {
                'header': self.header('UnexpectedInformationReceivedError', 'Alexa.ConnectedHome.Control'),
                'payload': {}
            }

    def header(self, name, namespace):
        return {
            'messageId': uuid.uuid4().hex,
            'name': name,
            'namespace': namespace,
            'payloadVersion': '2'
        }
