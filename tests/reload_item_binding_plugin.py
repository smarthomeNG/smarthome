"""Test-only plugin that binds to every item.

Used by tests/test_plugin_reload.py to verify that reload_plugin() doesn't
register the freshly-reloaded instance's update_item twice on the same item:
item.remove_method_trigger() is a plain list.remove() (removes only the
first match), so a duplicate registration leaves one entry permanently
orphaned once cleanup removes only one match.
"""

from lib.model.smartplugin import SmartPlugin


class ItemBindingPlugin(SmartPlugin):
    PLUGIN_VERSION = (
        '1.2.0'  # matches plugins/wol/plugin.yaml's declared version, avoids an unrelated version-mismatch check
    )

    def __init__(self, sh, *args, **kwargs):
        super().__init__()

    def parse_item(self, item):
        self.add_item(item, updating=True)
        return self.update_item

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def update_item(self, item, caller=None, source=None, dest=None):
        pass
