===========
zigbee2mqtt
===========

Das Plugin dienst zur Steuerung von Zigbee Devices via Zigbee2MQTT über MQTT. Notwendige Voraussetzung ist eine
funktionsfähige und laufende Installation von Zigbee2Mqtt. Die Installation, Konfiguration und der Betrieb ist hier
beschrieben: https://www.zigbee2mqtt.io/
Dort findet man ebenfalls die unterstützten Zigbee Geräte.

.. attention::

    Das Plugin kommuniziert über MQTT und benötigt das mqtt Modul, welches die Kommunikation mit dem MQTT Broker
    durchführt. Dieses Modul muß geladen und konfiguriert sein, damit das Plugin funktioniert.

Getestet ist das Plugin mit folgenden Zigbee-Geräten:

- SONOFF SNZB-02
- IKEA TRADFRI E1766
- Aqara DJT11LM
- TuYa TS0210
- Aqara Opple 3fach Taster


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/zigbee2mqtt` beschrieben.

Nachfolgend noch einige Zusatzinformationen.

Konfiguration des Plugins
-------------------------

Die Konfigruation des Plugins erfolgt über das Admin-Interface. Dafür stehen die folgenden Einstellungen zur Verfügung:

- `base_topic`: MQTT TopicLevel_1, um mit dem ZigBee2MQTT Gateway zu kommunizieren (%topic%)
- `poll_period`: Zeitabstand in Sekunden in dem das Gateway Infos liefer soll


Konfiguration von Items
-----------------------

Für die Nutzung eines Zigbee Devices müssen in dem entsprechenden Item die zwei Attribute ``zigbee2mqtt_topic`` und
``zigbee2mqtt_attr`` konfiguriert werden, wie im folgenden Beispiel gezeigt:

.. code-block:: yaml

    sensor:
        temp:
            type: num
            zigbee2mqtt_topic: SNZB02_01
            zigbee2mqtt_attr: temperature
        hum:
            type: num
            zigbee2mqtt_topic: SNZB02_01
            zigbee2mqtt_attr: humidity


Dabei entspricht das Attribute ``zigbee2mqtt_topic`` dem Zigbee ``Friendly Name`` des Device bzw. dem MQTT Topic Level_2, um mit dem ZigBee2MQTT Gateway zu kommunizieren.

Das Attribut ``zigbee2mqtt_attr`` entspricht dem jeweiligen Tag aus der Payload, der verwendet werden soll. Welche Tags beim jeweiligen Device verfügbar sind, kann man im WebIF des Pluigns sehen.

Die folgenden Tags des Attributes ``zigbee2mqtt_attr`` sind definiert und werden vom Plugin unterstützt:

- online
- bridge_permit_join
- bridge_health_check
- bridge_restart
- bridge_networkmap_raw
- device_remove
- device_configure
- device_options
- device_rename
- device_configure_reporting
- temperature
- humidity
- battery
- battery_low
- linkquality
- action
- vibration
- action_group
- voltage
- angle
- angle_x
- angle_x_absolute
- angle_y
- angle_y_absolute
- angle_z
- strength
- last_seen
- tamper
- sensitivity
- contact


Web Interface des Plugins
=========================

Zigbee2Mqtt Items
-----------------

Das Webinterface zeigt die Items an, für die ein Zigbee2Mqtt Device konfiguriert ist.

.. image:: user_doc/assets/webif_tab1.jpg
   :class: screenshot


Zigbee2Mqtt Devices
-------------------

Das Webinterface zeigt Informationen zu den konfigurierten Zigbee2Mqtt Devices an, sowie etwa hinzugekommen Devices die
in SmartHomeNG noch nicht konfiguriert (mit einem Item vebunden) sind.

.. image:: user_doc/assets/webif_tab2.jpg
   :class: screenshot


Zigbee2Mqtt Bridge Info
-----------------------

Das Webinterface zeigt detaillierte Informationen der Zigbee2Mqtt Bridge zu jedem verbundenen Device an.

.. image:: user_doc/assets/webif_tab3.jpg
   :class: screenshot


Broker Information
------------------

Das Webinterface zeigt Informationen zum genutzten MQTT Broker an.

.. image:: user_doc/assets/webif_tab6.jpg
   :class: screenshot
