import re

class AlexaDevice(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.description = ''
        self.action_items = {}

    @staticmethod
    def create_id_from_name(name):
        return re.sub('[a-z0-9]', '-', name.strip().lower())

    def add_action(self, name, item):
        if name in self.actions:
            self.action_items[name].append(item)
        else:
            self.action_items[name] = [item]

    def supports_action(self, name):
        return name in self.action_items

    def supported_actions():
        return self.action_items.keys()

    def get_items_for_action(self, action_name):
        return self.action_items[name]
