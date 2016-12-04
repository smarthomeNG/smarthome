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
    def __init__(self, id):
        self.id = id
        self.name = None
        self.description = None
        self.action_items = {}

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

    def item_range(self, item):
        return self.item_ranges[item] if item in self.item_ranges else None

    def validate(self, logger):
        logger.debug("Alexa: validating device {}".format(self.id))

        if not self.id:
            msg = "Alexa-Device {}: empty identifier".format(self.id)
            logger.error(msg)
            return False
        elif len(self.id) > 128:
            msg = "Alexa-Device: {}: identifier '{}' too long >128".format(self.id, self.id)
            logger.error(msg)
            return False

        if not self.name:
            msg = "Alexa-Device {}: empty name".format(self.id)
            logger.error(msg)
            return False
        elif len(self.name) > 128:
            msg = "Alexa-Device: {}: name '{}' too long >128".format(self.id, self.name)
            logger.error(msg)
            return False

        if not self.description:
            logger.warning("Alexa-Device {}: empty description, fallback to name '{}' - please set `alexa_description`".format(self.id, self.name))
            self.description = self.name
        elif len(self.description) > 128:
            msg = "Alexa-Device {}: description '{}' too long >128".format(self.id, self.description)
            logger.error(msg)
            return False

        if not self.action_items:
            logger.warning("Alexa-Device {}: no actions/items registered - please set `alexa_actions`".format(self.id))

        return True
