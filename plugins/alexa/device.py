import re

class AlexaDevice(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.description = ''
        self.action_items = {}

    @classmethod
    def create_id_from_name(cls, name):
        return re.sub('[a-z0-9]', '-', name.strip().lower())

    def add_action(self, action_name, item):
        if action_name in self.actions:
            self.action_items[action_name].append(item)
        else:
            self.action_items[action_name] = [item]

    def supported_actions(self):
        return self.action_items.keys()

    def supports_action(self, action_name):
        return action_name in self.action_items

    def backed_items(self):
        item_set = { item for item in self.action_items.itervalues() }
        return list(item_set)

    def items_for_action(self, action_name):
        return self.action_items[action_name] if action_name in self.action_items else []
