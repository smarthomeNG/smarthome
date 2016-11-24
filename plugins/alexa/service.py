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

        self.logger.info("Alexa service setup at {}:{}".format(host, port))
        cherrypy.config.update({
            'server.socket_host': host,
            'server.socket_port': port,
        })
        cherrypy.tree.mount(self, '/')

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        req = cherrypy.request.json
        header = req['header']
        payload = req['payload']

        if header['namespace'] == 'Alexa.ConnectedHome.System':
            return handle_system(header, payload)
        elif header['namespace'] == 'Alexa.ConnectedHome.Discovery':
            return handle_discovery(header, payload)
        elif header['namespace'] == 'Alexa.ConnectedHome.Control':
            return handle_control(header, payload)
        else:
            raise cherrypy.HTTPError("400 Bad Request", "unknown header/namespace '{}'".format(header['namespace']))

    def start(self):
        cherrypy.engine.start()
        self.logger.info("Alexa service started")

    def stop(self):
        cherrypy.engine.exit()
        self.logger.info("Alexa service stopped")

    def handle_system(header, payload):
        request_type = header['name']
        self.logger.debug("Alexa system-directive '{}' received".format(request_type))

        if request_type == 'HealthCheckRequest':
            return confirm_health(payload)
        else:
            raise cherrypy.HTTPError("400 Bad Request", "unknown header.name '{}'".format(request_type))

    def confirm_health(payload):
        requested_on = payload['initiationTimestamp']
        return {
            "header": {
                "messageId": uuid.uuid4(),
                "name": "HealthCheckResponse",
                "namespace": "Alexa.ConnectedHome.System",
                "payloadVersion": "2"
            },
            "payload": {
                "description": "The system is currently healthy",
                "isHealthy": True
            }
        }

    def handle_discovery(header, payload):
        request_type = header['name']
        self.logger.debug("Alexa discovery-directive '{}' received".format(request_type))

        if request_type == 'DiscoverAppliancesRequest':
            return discover_appliances()
        else:
            raise cherrypy.HTTPError("400 Bad Request", "unknown header.name '{}'".format(request_type))

    def discover_appliances():
        discovered = []
        for (device in self.devices.all()):
            discovered.append({
                "actions": device.supported_actions(),
                "additionalApplianceDetails": {
                    "extraDetail{}".format(idx+1) : item.id() for idx, item in enumerate(device.backed_items())
                },
                "applianceId": device.id,
                "friendlyDescription": device.description,
                "friendlyName": device.name,
                "isReachable": true,
                "manufacturerName": "smarthomeNG.Alexa",
                "modelName": '|'.join( [item.id() for item in device.backed_items()] ),
                "version": self.version
            })

        return {
            "header": {
                "messageId": uuid.uuid4(),
                "name": "DiscoverAppliancesResponse",
                "namespace": "Alexa.ConnectedHome.Discovery",
                "payloadVersion": "2"
            },
            "payload": {
                "discoveredAppliances": discovered
            }
        }

    def handle_control(header, payload):
        request_type = header['name']
        self.logger.debug("Alexa control-directive '{}' received".format(request_type))

        action = self.actions.by_request_type(request_type)
        if action is None:
            self.logger.error("no action specified for '{}'".format(request_type))
            return self.actions.create_response('UnexpectedInformationReceivedError')

        try:
            def get_items_by_device_id(device_id):
                device = self.devices.get(device_id)
                return device.get_items_for_action( action.alexa_action )

            return action(payload, get_items_by_device_id)

        except (Exception e):
            self.logger.error("execution of control-directive '{}' failed: {}".format(request_type, e))
            return self.actions.create_response('DriverInternalError')
