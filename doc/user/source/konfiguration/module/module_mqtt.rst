
.. index:: mqtt; Modul
.. index:: Module; mqtt
.. index:: mqtt; Konfiguration

.. role:: redsup
.. role:: bluesup

===========
Module mqtt
===========

Dieses Modul erlaubt es SmartHomeNG über das MQTT Protokoll zu kommunizieren. Es stellt ein einfach zu nutzendes
Interface für Logiken und Plugins zur Verfügung. Dabei kann das mqtt Modul von mehreren Logiken und/oder Plugins
gleichzeitig genutzt werden.

- Informationen zur Nutzung in Logiken sind im Abschnitt **Logiken** der Anwender Dokumentation zu finden.
- Informationen zur Nutzung in Plugins sind im Abschnitt **Development of Plugins** der Entwickler Dokumentation zu finden.

Aktuell unterstützt das Modul MQTT bis zur Protokoll Version 3.1.1. Sobald das verwendete Python Package des Eclipse
Projektes auch die Version MQTT v5.0 unterstützt, wird das SmartHomeNG Modul entsprechend erweitert.

.. index:: Konfigurationsdateien; /etc/module.yaml (mqtt)

Konfiguration
=============

--------------------------
Datei *../etc/module.yaml*
--------------------------

.. code-block:: yaml
   :caption: ../etc/module.yaml

   # etc/module.yaml
   mqtt:
       module_name: mqtt
       # broker_host: 127.0.0.1
       # broker_port: 1883
       # broker_monitoring: False
       # qos: 1
       # last_will_topic: devices/shng-module/$online
       # last_will_payload: 'False'
       # birth_topic: devices/shng-module/$online
       # birth_payload: 'True'
       # bool_values: ['Falsch', 'Wahr']
       # user: Benutzer
       # password: Geheim


.. note::

    Die Konfigurationsparameter des mqtt Modules die in dieser Datei konfiguriert werden, können auch über das graphische
    Administrations-Interface geändert werden.


+-------------------------+------------------------------------------------------------------------------------------------------+
| Parameter               | Bemerkung                                                                                            |
+=========================+======================================================================================================+
| broker_host             | **Optional**: DNS Name oder IP Adresse des MQTT Brokers. Wird **broker_host** nicht angegeben, wird  |
|                         | angenommen, dass der Broker auf dem selben Rechner läuft wie SmartHomeNG und es wird **127.0.0.1**   |
|                         | (localhost) genutzt.                                                                                 |
+-------------------------+------------------------------------------------------------------------------------------------------+
| broker_port             | **Optional**: Port auf dem der MQTT Broker hört. Wird **broker_port** nicht angegeben, wird der      |
|                         | Standard Port **1883** genutzt.                                                                      |
+-------------------------+------------------------------------------------------------------------------------------------------+
| broker_monitoring       | **Optional**: Wenn dieser Parameter auf **True** gesetzt wird, werden Informationen des Brokers zum  |
|                         | Message Durchsatz abgefragt und können im Admin-Interface angezeigt werden.                          |
+-------------------------+------------------------------------------------------------------------------------------------------+
| qos                     | **Optional**: Legt fest, welche Quality-of-Service Anforderungen MQTT Messages beim Publish          |
|                         | mitgegeben werden soll. Wird der Parameter nicht angegeben, wird als Standardwert **1** verwendet.   |
+-------------------------+------------------------------------------------------------------------------------------------------+
| last_will_topic         | **Optional**: Legt den Topic der MQTT last_will Message fest. Wird der Parameter nicht angegeben,    |
|                         | wird beim Verbindungsaufbau keine last_will Message festgelegt.                                      |
+-------------------------+------------------------------------------------------------------------------------------------------+
| last_will_payload       | **Optional**: Legt die Payload der MQTT last_will Message fest. Wird der Parameter nicht angegeben,  |
|                         | wird beim Verbindungsaufbau eine last_will Message ohne Payload festgelegt.                          |
+-------------------------+------------------------------------------------------------------------------------------------------+
| birth_topic             | **Optional**: Analog zur MQTT last_will Message implementiert das SmartHomeNG mqtt Modul eine        |
|                         | birth Message, die beim Aufbau der Verbindung zum MQTT Broker versendet wird. Wird dieser Parameter  |
|                         | nicht angegeben, wird beim Verbindungsaufbau keine birth Message versendet.                          |
+-------------------------+------------------------------------------------------------------------------------------------------+
| birth_payload           | **Optional**: Legt die Payload der birth Message fest. Wird der Parameter nicht angegeben, wird beim |
|                         | Verbindungsaufbau eine birth Message ohne Payload versendet.                                         |
+-------------------------+------------------------------------------------------------------------------------------------------+
| bool_values             | **Optional**: Legt fest, welche Werte als Payload für Topics verwendet werden sollen, wenn Werte vom |
|                         | Typ **bool** versendet werden sollen. Außerdem werden diese Werte auch auf eingehende MQTT Messages  |
|                         | angewendet, die in Variablen des Typ **bool** eingelesen werden sollen. Für den Parameter            |
|                         | **bool_values** muss eine Liste mit **zwei** Werten angegeben werden, wobei der erste Wert für       |
|                         | **False** steht und der zweiter Wert für **True**                                                    |
+-------------------------+------------------------------------------------------------------------------------------------------+
| user                    | **Optional**: Benutzername des MQTT Brokers, falls dieser ein Login erfordert.                       |
+-------------------------+------------------------------------------------------------------------------------------------------+
| password                | **Optional**: Password des MQTT Brokers, falls dieser ein Login erfordert.                           |
+-------------------------+------------------------------------------------------------------------------------------------------+

