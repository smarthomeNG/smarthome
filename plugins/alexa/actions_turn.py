from .action import alexa

@alexa('turnOn', 'TurnOnRequest', 'TurnOnConfirmation')
def turn_on(self, payload):
    items = self.items( payload['appliance']['applianceId'] )

    for item in items:
        item( True )

    return self.respond()

@alexa('turnOff', 'TurnOffRequest', 'TurnOffConfirmation')
def turn_off(self, payload):
    items = self.items( payload['appliance']['applianceId'] )

    for item in items:
        item( False )

    return self.respond()
