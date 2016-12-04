from .action import alexa

DEFAULT_RANGE = (0, 100)

def what_percentage(value, range):
    _min, _max = range
    return ( (value - _min) / (_max - _min) ) * 100

def calc_percentage(percent, range):
    _min, _max = range
    return (_max - _min) * (percent / 100) + _min

def clamp_percentage(percent, range):
    _min, _max = range
    return min(_max, max(_min, percent))

@alexa('setPercentage', 'SetPercentageRequest', 'SetPercentageConfirmation')
def set_percentage(self, payload):
    device_id = payload['appliance']['applianceId']
    items = self.items(device_id)
    new_percentage = float( payload['percentageState']['value'] )

    for item in items:
        item_range = self.item_range(item, DEFAULT_RANGE)
        item_new = calc_percentage(new_percentage, item_range)
        self.logger.info("Alexa: setPercentage({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    return self.respond()

@alexa('incrementPercentage', 'IncrementPercentageRequest', 'IncrementPercentageConfirmation')
def incr_percentage(self, payload):
    device_id = payload['appliance']['applianceId']
    items = self.items(device_id)
    percentage_delta = float( payload['deltaPercentage']['value'] )

    for item in items:
        item_range = self.item_range(item, DEFAULT_RANGE)
        item_now = item()
        percentage_now = what_percentage(item_now, item_range)
        percentage_new = clamp_percentage(percentage_now + percentage_delta, item_range)
        item_new = calc_percentage(percentage_new, item_range)
        self.logger.info("Alexa: incrementPercentage({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    return self.respond()

@alexa('decrementPercentage', 'DecrementPercentageRequest', 'DecrementPercentageConfirmation')
def decr_percentage(self, payload):
    device_id = payload['appliance']['applianceId']
    items = self.items(device_id)
    percentage_delta = float( payload['deltaPercentage']['value'] )

    for item in items:
        item_range = self.item_range(item, DEFAULT_RANGE)
        item_now = item()
        percentage_now = what_percentage(item_now, item_range)
        percentage_new = clamp_percentage(percentage_now - percentage_delta, item_range)
        item_new = calc_percentage(percentage_new, item_range)
        self.logger.info("Alexa: decrementPercentage({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    return self.respond()
