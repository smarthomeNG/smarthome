"""
Test harness around the real mqtt module (modules/mqtt).

Message dispatch, subscription bookkeeping and payload casting run as in
production; only the broker connection is replaced.
"""

import logging
import threading


class BrokerClient:
    """Accepts subscriptions like paho's client; tests drive delivery themselves."""

    def subscribe(self, topic, qos=0):
        return 0, 1


class Message:
    """The members of paho's MQTTMessage the mqtt module reads."""

    def __init__(self, topic, payload, qos=0, retain=False):
        self.topic = topic
        self.payload = payload
        self.qos = qos
        self.retain = retain


def make_mqtt_module():
    """Return an initialized mqtt module without broker connection, ready to dispatch messages."""
    from modules.mqtt import Mqtt

    module = Mqtt.__new__(Mqtt)
    module.logger = logging.getLogger('tests.mqtt_harness')
    module.bool_values = None
    module.qos = 0
    module._client = BrokerClient()
    module._subscribed_topics = {}
    module._subscribed_topics_lock = threading.Lock()
    module.get_broker_config = lambda: {}
    return module
