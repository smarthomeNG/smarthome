===========
zigbee2mqtt
===========

Das Plugin dienst zur Steuerung von Zigbee Devices via Zigbee2MQTT über MQTT.
Notwendige Voraussetzung ist eine funktionsfähige und laufende Installation von
Zigbee2Mqtt. Dessen Installation, Konfiguration und der Betrieb ist hier
beschrieben: https://www.zigbee2mqtt.io/ Dort findet man ebenfalls die
unterstützten Zigbee Geräte.

.. attention::

    Das Plugin kommuniziert über MQTT und benötigt das mqtt-Modul, welches die
    Kommunikation mit dem MQTT Broker durchführt. Dieses Modul muss geladen und
    konfiguriert sein, damit das Plugin funktioniert.

Getestet ist das Plugin mit folgenden Zigbee-Geräten:

- Philips Hue white ambiance E27 800lm with Bluetooth
- Philips Hue white ambiance E26/E27
- IKEA Tradfri LED1924G9
- IKEA Tradfri LED1949C5
- Philips Hue dimmer switch

Grundsätzlich kann jedes Gerät angebunden werden; für eine sinnvolle
Verarbeitung von Werten sollte ein entsprechendes struct erstellt werden,
ggfs. kann noch erweiterte Funktionalität mit zusätzlichem Code bereitgestellt
werden.

.. hint::

    Im Rahmen der Umstellung des Plugins auf Version 2 wurden die Attribute
    umbenannt, d.h. von "zigbee2mqtt_foo" in "z2m_foo" geändert.
    Das macht die Konfigurationsdateien übersichtlicher und einfacher zu
    schreiben. Bestehende Dateien müssen entsprechend angepasst werden.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/zigbee2mqtt` beschrieben.

Nachfolgend noch einige Zusatzinformationen.

Konfiguration von Items
-----------------------

Für die Nutzung eines Zigbee Devices können - sofern vorhanden - die
mitgelieferten structs verwendet werden:

.. code-block:: yaml

    lampe1:
        struct: zigbee2mqtt.light_white_ambient
        z2m_topic: friendlyname1

    lampe2:
        struct: zigbee2mqtt.light_rgb
        z2m_topic: friendlyname2


Sofern für das entsprechende Gerät kein struct vorhanden ist, können einzelne
Datenpunkte des Geräts auch direkt angesprochen werden:

.. code-block:: yaml

    sensor:
        temp:
            type: num
            z2m_topic: SNZB02_01
            z2m_attr: temperature
        hum:
            type: num
            z2m_topic: SNZB02_01
            z2m_attr: humidity


Dabei entspricht das Attribute ``z2m_topic`` dem Zigbee ``Friendly Name`` des
Device bzw. dem MQTT Topic Level_2, um mit dem ZigBee2MQTT Gateway zu
kommunizieren.

Das Attribut ``z2m_attr`` entspricht dem jeweiligen Tag aus der Payload, der
verwendet werden soll. Welche Tags beim jeweiligen Device verfügbar sind, kann
man im WebIF des Plugins sehen.

Die Informationen des Zigbee2MQTT-Gateways werden unter dem z2m_topic
(Gerätenamen) ``bridge`` bereitgestellt.

Die folgenden Tags des Attributes ``z2m_attr`` sind definiert und werden vom
Plugin unterstützt:

- online
- permit_join (bridge)
- health_check (bridge)
- restart (bridge)
- networkmap_raw (bridge)
- device_remove (bridge)
- device_configure (bridge)
- device_options (bridge)
- device_rename (bridge)
- device_configure_reporting (bridge)
- battery
- linkquality
- action
- last_seen

Weitere Tags werden abhängig vom Gerät unterstützt. In den meisten Fällen können
auch unbekannte Tags bei direkter Konfiguration verwendet werden.


