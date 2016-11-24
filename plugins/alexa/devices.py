class Devices(object):
    def __init__(self):
        self.devices = {}

    def exists(id):
        return id in self.devices

    def get(id):
        return self.devices[id]

    def put(device):
        self.devices[device.id] = device

    def all():
        return self.devices.values()
