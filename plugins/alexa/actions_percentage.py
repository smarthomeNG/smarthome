from .action import alexa

@alexa('setPercentage', 'SetPercentageRequest', 'SetPercentageConfirmation')
def set_percentage(self, payload):
    items = self.items( payload['appliance']['applianceId'] )
    new_percentage = float( payload['percentageState']['value'] )

    for item in items:
        item_now = item()
        item_max = 100 # any idea?
        item_new = item_max * (new_percentage / 100)
        self.logger.debug("Alexa: setPercentage({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    return self.respond()

@alexa('incrementPercentage', 'IncrementPercentageRequest', 'IncrementPercentageConfirmation')
def incr_percentage(self, payload):
    items = self.items( payload['appliance']['applianceId'] )
    percentage_delta = float( payload['deltaPercentage']['value'] )

    for item in items:
        item_now = item()
        item_max = 100 # any idea?
        percentage_now = item_now / item_max
        percentage_new_raw = (percentage_now * 100) + percentage_delta
        percentage_new = min(100, max(0, percentage_new_raw))
        item_new = item_max * (percentage_new / 100)
        self.logger.debug("Alexa: incrementPercentage({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    return self.respond()

@alexa('decrementPercentage', 'DecrementPercentageRequest', 'DecrementPercentageConfirmation')
def decr_percentage(self, payload):
    items = self.items( payload['appliance']['applianceId'] )
    percentage_delta = float( payload['deltaPercentage']['value'] )

    for item in items:
        item_now = item()
        item_max = 100 # any idea?
        percentage_now = item_now / item_max
        percentage_new_raw = (percentage_now * 100) - percentage_delta
        percentage_new = min(100, max(0, percentage_new_raw))
        item_new = item_max * (percentage_new / 100)
        self.logger.debug("Alexa: decrementPercentage({}, {:.1f})".format(item.id(), item_new))
        item( item_new )

    return self.respond()
