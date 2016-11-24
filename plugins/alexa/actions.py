# https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#skill-adapter-directives
import functools
import uuid

class AlexaActions(object):
    def __init__(self, sh, logger):
        self.sh = sh
        self.logger = logger
        self.methods_by_action_name = {}
        self.methods_by_request_type = {}
        self.response_types_by_method = {}

    @staticmethod
    def register(func):


    def by_name(self, name):
        try:
            return getattr(self, self.methods_by_action_name[name])
        except (AttributeError):
            return None

    def by_request_type(self, request_type):
        try:
            return getattr(self, self.methods_by_request_type[request_type])
        except (AttributeError):
            return None

    # https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#error-messages
    def create_response(self, response_type, payload = {}):
        return {
            "header": {
                "namespace": "Alexa.ConnectedHome.Control",
                "name": response_type,
                "payloadVersion": "2",
                "messageId": uuid.uuid4()
            },
            "payload": payload
        }

def alexa(action_name, request_type, response_type):
    def apply_metadata(func):
        func.alexa_action = action_name
        func.alexa_request = request_type
        func.alexa_response = response_type
        AlexaActions.register(func)
        return func
    return apply_metadata

# -------------------------------------------------------------------------
# supported alexa actions/directives, exactly as defined here:
# https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#skill-adapter-directives

@alexa('setTargetTemperature', 'SetTargetTemperatureRequest', 'SetTargetTemperatureConfirmation')
def setTargetTemp(payload, get_items_by_device_id, logger):

    targetTemp = float( payload['targetTemperature']['value'] )

    for item in get_items_by_device_id( payload['appliance']['applianceId'] ):
        item( targetTemp )

    return {

    }

     {
         "payload":{
             "targetTemperature":{
                 "value":25.0
             },
         "temperatureMode":{
             "value":"AUTO"
         },
         "previousState":{
             "targetTemperature":{
                 "value":21.0
              },
             "mode":{
                 "value":"AUTO"
             }
           }
         }
     }


@alexa('incrementTargetTemperature', 'TurnOffRequest', 'TurnOffConfirmation')
def incrTargetTemp(payload, get_items_by_device_id, respond, logger):
    pass

@alexa('decrementTargetTemperature', 'TurnOffRequest', 'TurnOffConfirmation')
def decrTargetTemp(payload, get_items_by_device_id, respond, logger):
    pass

@alexa('setPercentage', 'TurnOffRequest', 'TurnOffConfirmation')
def setPercent(payload, get_items_by_device_id, respond, logger):
    pass

@alexa('incrementPercentage', 'TurnOffRequest', 'TurnOffConfirmation')
def incrPercent(payload, get_items_by_device_id, respond, logger):
    pass

@alexa('decrementPercentage', 'TurnOffRequest', 'TurnOffConfirmation')
def decrPercent(payload, get_items_by_device_id, respond, logger):
    pass

@alexa('turnOff', 'TurnOffRequest', 'TurnOffConfirmation')
def turnOff(payload, get_items_by_device_id, respond, logger):
    pass

@alexa('turnOn', 'TurnOnRequest', 'TurnOffConfirmation')
def turnOn(payload, get_items_by_device_id, respond, logger):
    pass
