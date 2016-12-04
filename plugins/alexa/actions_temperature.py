from .action import alexa

DEFAULT_RANGE = (16, 26)

def clamp_temp(temp, range):
    _min, _max = range
    return min(_max, max(_min, temp))

@alexa('setTargetTemperature', 'SetTargetTemperatureRequest', 'SetTargetTemperatureConfirmation')
def set_target_temp(self, payload):
    device_id = payload['appliance']['applianceId']
    items = self.items(device_id)

    target_temp = float( payload['targetTemperature']['value'] )
    previous_temp = items[0]() if items else 0

    for item in items:
        item_range = self.item_range(item, DEFAULT_RANGE)
        item_new = clamp_temp(target_temp, item_range)
        self.logger.info("Alexa: setTargetTemperature({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    new_temp = items[0]() if items else 0

    return self.respond({
        'targetTemperature': {
             'value': new_temp
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
        item_range = self.item_range(item, DEFAULT_RANGE)
        item_now = item()
        item_new = clamp_temp(item_now + delta_temp, item_range)
        self.logger.info("Alexa: incrementTargetTemperature({}, {:.1f})".format(item.id(), item_new))
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
        item_range = self.item_range(item, DEFAULT_RANGE)
        item_now = item()
        item_new = clamp_temp(item_now - delta_temp, item_range)
        self.logger.info("Alexa: decrementTargetTemperature({}, {:.1f})".format(item.id(), item_new))
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
