import alexa from alexa.actions

@alexa('turnOn', 'TurnOnRequest', 'TurnOnConfirmation')
def turn_on(self, payload):
    for item in self.items( payload['appliance']['applianceId'] )
        item( False )
    return self.respond()

@alexa('turnOff', 'TurnOffRequest', 'TurnOffConfirmation')
def turn_off(self, payload):
    for item in self.items( payload['appliance']['applianceId'] )
        item( False )
    return self.respond()
