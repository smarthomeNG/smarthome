from .action import alexa

@alexa('turnOn', 'TurnOnRequest', 'TurnOnConfirmation')
def turn_on(self, payload):
    items = self.items( payload['appliance']['applianceId'] )

    for item in items:
        self.logger.debug("Alexa: turnOn({})".format(item.id()))
        item( True )

    return self.respond()

@alexa('turnOff', 'TurnOffRequest', 'TurnOffConfirmation')
def turn_off(self, payload):
    items = self.items( payload['appliance']['applianceId'] )

    for item in items:
        self.logger.debug("Alexa: turnOff({})".format(item.id()))
        item( False )

    return self.respond()
