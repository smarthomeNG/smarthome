.. index:: Class; MqttPlugin
.. index:: Plugin; Class MqttPlugin
.. index:: MQTT; Class MqttPlugin

.. role:: redsup
.. role:: bluesup

Class MqttPlugin
================


Die Klasse MqttPlugin implementiert die Basisklasse aller SmartPlugins die MQTT nutzen.
Die vorhandenen Methoden sind im Folgenden beschrieben


Zusätzlich werden die Methoden der Klasse ``lib.utils.Utils`` vererbt.


Teile eines JSON-Payloads an ein Item übergeben
-----------------------------------------------

Sendet ein Gerät mehrere Werte in einem JSON-Payload, kann ``add_subscription()`` mit dem Parameter ``select`` ein
`JMESPath <https://jmespath.org>`_ Ausdruck übergeben werden. Der Payload wird dann als dict ausgewertet
(``payload_type`` wird ignoriert) und das Item erhält nur den ausgewählten Teil. Passt der Ausdruck auf keinen Teil
des Payloads, wird das Item nicht verändert. Ein ungültiger Ausdruck wird als Fehler geloggt und das Topic nicht
abonniert.

.. code-block:: python

    # Payload: {"sensors": [{"temp": 21.5, "hum": 48}]}
    self.add_subscription('haus/klima', 'dict', item=item, select='sensors[0].temp')    # Item erhält 21.5

Für ``select`` wird das Python-Package ``jmespath`` benötigt; es ist in den Requirements des mqtt Moduls enthalten.

.. autoclass:: lib.model.mqttplugin.MqttPlugin
    :members:
    :noindex:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

