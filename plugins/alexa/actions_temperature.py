from .action import alexa

TEMP_MIN = 0
TEMP_MAX = 100

@alexa('setTargetTemperature', 'SetTargetTemperatureRequest', 'SetTargetTemperatureConfirmation')
def set_target_temp(self, payload):
    device_id = payload['appliance']['applianceId']
    items = self.items(device_id)

    target_temp = float( payload['targetTemperature']['value'] )
    previous_temp = items[0]() if items else 0

    for item in items:
        self.logger.debug("Alexa: setTargetTemperature({}, {:.1f})".format(item.id(), targetTemp))
        item( targetTemp )

    return self.respond({
        'targetTemperature': {
             'value': target_temp
        },
        'temperatureMode': {
            'value':'AUTO'
        },
        'previousState':{
            'targetTemperature': {
                'value': previous_temp
            },
            'mode': {
                'value':'AUTO'
            }
        }
    })

@alexa('incrementTargetTemperature', 'IncrementTargetTemperatureRequest', 'IncrementTargetTemperatureConfirmation')
def incr_target_temp(self, payload):
    device_id = payload['appliance']['applianceId']
    items = self.items(device_id)

    delta_temp = float( payload['deltaTemperature']['value'] )
    previous_temp = items[0]() if items else 0

    for item in items:
        item_now = item()
        item_new_raw = item_now + delta_temp
        item_new = min(TEMP_MAX, max(TEMP_MIN, item_new_raw))
        self.logger.debug("Alexa: incrementTargetTemperature({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    new_temp = items[0]() if items else 0

    return self.respond({
        'targetTemperature': {
             'value': new_temp
        },
        'temperatureMode':{
            'value':'AUTO'
        },
        'previousState':{
            'targetTemperature': {
                'value': previous_temp
            },
            'mode': {
                'value':'AUTO'
            }
        }
    })

@alexa('decrementTargetTemperature', 'DecrementTargetTemperatureRequest', 'DecrementTargetTemperatureConfirmation')
def decr_target_temp(self, payload):
    device_id = payload['appliance']['applianceId']
    items = self.items(device_id)

    delta_temp = float( payload['deltaTemperature']['value'] )
    previous_temp = items[0]() if items else 0

    for item in items:
        item_now = item()
        item_new_raw = item_now - delta_temp
        item_new = min(TEMP_MAX, max(TEMP_MIN, item_new_raw))
        self.logger.debug("Alexa: decrementTargetTemperature({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    new_temp = items[0]() if items else 0

    return self.respond({
        'targetTemperature': {
             'value': new_temp
        },
        'temperatureMode':{
            'value':'AUTO'
        },
        'previousState':{
            'targetTemperature': {
                'value': previous_temp
            },
            'mode': {
                'value':'AUTO'
            }
        }
    })
