class AlexaDevices(object):
    def __init__(self):
        self.devices = {}

    def exists(self, id):
        return id in self.devices

    def get(self, id):
        return self.devices[id]

    def put(self, device):
        self.devices[device.id] = device

    def all(self):
        return list( self.devices.values() )

class AlexaDevice(object):
    def __init__(self, id, name):
        if len(id) > 256:
            raise ValueError("identifier '{}' of device {} longer than 256 characters!".format(id, self.id))
        self.id = id
        self.action_items = {}
        self.set_name(name)
        self.set_description(name) # XXX preset description with name

    def set_name(self, name):
        if len(name) > 128:
            raise ValueError("name '{}' of device {} longer than 128 characters!".format(name, self.id))
        self.name = name

    def set_description(self, descr):
        if len(descr) > 128:
            raise ValueError("description '{}' of device {} longer than 128 characters!".format(descr, self.id))
        self.description = descr

    @classmethod
    def create_id_from_name(cls, name):
        import unicodedata
        import re
        id = name.strip()
        id = unicodedata.normalize('NFKD', id).encode('ascii', 'ignore').decode('ascii')
        id = id.lower()
        return re.sub('[^a-z0-9_-]', '-', id)

    def register(self, action_name, item):
        if action_name in self.action_items:
            self.action_items[action_name].append(item)
        else:
            self.action_items[action_name] = [item]

    def supported_actions(self):
        return list( self.action_items.keys() )

    def supports_action(self, action_name):
        return action_name in self.action_items

    def backed_items(self):
        item_set = set()
        for items in self.action_items.values():
            for item in items:
                item_set.add( item )
        return list( item_set )

    def items_for_action(self, action_name):
        return self.action_items[action_name] if action_name in self.action_items else []
