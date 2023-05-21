

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup


============
Plugin Typen
============

Durch Plugins kann die Funktionalität von SmartHomeNG erweitert werden und SmartHomeNG kann mit zu steuernden
Komponenten bzw. Systemen verbunden werden.

Es gibt bereits eine große Zahl von Plugins, die im Abschnitt :doc:`Plugins </plugins_all>`
dokumentiert sind. Die Dokumentation wird aus dem Metadaten des jeweiligen Plugins generiert und kann durch
eine Datei im restructured-Text Format (user_doc.rst) ergänzt werden.


Classic Plugin
==============

Das klassische Plugin aus smarthome.py wird zwar noch unterstützt, neue Plugins sollten jedoch aufgrund der geringeren
Funktionalität des des Classic Plugins nicht auf seiner Basis erstellt werden. Plugins, die nicht von der Klasse
``SmartPlugin`` abgeleitet sind, werden nicht mehr in das Plugin Repo von SmartHomeNG aufgenommen.

|

.. index:: Referenz; SmartPlugin
.. Index:: SmartPlugin Referenz

SmartPlugin
===========

Ein Plugin implementiert im Code eine Klasse, welche von der ``class SmartPlugin`` abgeleitet ist. ``SmartPlugin``
stellt alle grundsätzlichen Funktionalitäten bereit, die benötigt werden, um ein Plugin zu implementieren.

Die Methoden von ``SmartPlugin`` sind hier dokumentiert:

.. toctree::
   :maxdepth: 5
   :titlesonly:

   smartplugin_class


|

.. index:: Referenz; MqttPlugin
.. Index:: MqttPlugin Referenz

MqttPlugin
==========

Plugins welche MQTT nutzen, sollten stattdessen von ``class MqttPlugin`` abgeleitet werden. ``MqttPlugin`` ist
eine Unterklasse von ``SmartPlugin``, die um Methoden zur MQTT-Nutzung erweitert ist.

Dabei handelt es sich um die Methoden

    - add_subscription(topic, payload_type, bool_values=None, item=None, callback=None)
    - start_subscriptions()
    - stop_subscription()
    - publish_topic(topic, payload, item=None, qos=None, retain=False, bool_values=None)
    - get_broker_info()
    - broker_uptime()

Die Methoden von ``MqttPlugin`` sind hier dokumentiert:

.. toctree::
   :maxdepth: 5
   :titlesonly:

   mqttplugin_class

|


.. index:: Referenz; SmartDevicePlugin
.. index:: Referenz; SDP
.. Index:: SmartDevicePlugin Referenz
.. Index:: SDP Referenz

.. comment SmartDevicePlugin
.. comment =================

.. include:: smartdeviceplugin.rst

Die Methoden von ``SmartDevicePlugin`` sind hier dokumentiert:

.. toctree::
   :maxdepth: 5
   :titlesonly:

   smartdeviceplugin
   smartdeviceplugin_class

