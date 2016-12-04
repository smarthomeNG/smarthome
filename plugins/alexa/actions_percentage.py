from .action import alexa

def what_percentage(value, range):
    min, max = range
    return ( (value - min) / (max - min) ) * 100

def calc_percentage(percent, range):
    min, max = range
    return (max - min) * (percent / 100) + min

def clamp_percentage(percent):
    return min(100, max(0, percent))

@alexa('setPercentage', 'SetPercentageRequest', 'SetPercentageConfirmation')
def set_percentage(self, payload):
    items = self.items( payload['appliance']['applianceId'] )
    new_percentage = float( payload['percentageState']['value'] )

    for item in items:
        item_range = self.range(item, (0,100))
        item_new = calc_percentage(new_percentage, item_range)
        self.logger.info("Alexa: setPercentage({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    return self.respond()

@alexa('incrementPercentage', 'IncrementPercentageRequest', 'IncrementPercentageConfirmation')
def incr_percentage(self, payload):
    items = self.items( payload['appliance']['applianceId'] )
    percentage_delta = float( payload['deltaPercentage']['value'] )

    for item in items:
        item_range = self.range(item, (0,100))
        item_now = item()
        percentage_now = what_percentage(item_now, item_range)
        percentage_new = clamp_percentage( percentage_now + percentage_delta )
        item_new = calc_percentage(percentage_new, item_range)
        self.logger.info("Alexa: incrementPercentage({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    return self.respond()

@alexa('decrementPercentage', 'DecrementPercentageRequest', 'DecrementPercentageConfirmation')
def decr_percentage(self, payload):
    items = self.items( payload['appliance']['applianceId'] )
    percentage_delta = float( payload['deltaPercentage']['value'] )

    for item in items:
        item_range = self.range(item, (0,100))
        item_now = item()
        percentage_now = what_percentage(item_now, item_range)
        percentage_new = clamp_percentage( percentage_now - percentage_delta )
        item_new = calc_percentage(percentage_new, item_range)
        self.logger.info("Alexa: decrementPercentage({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    return self.respond()
