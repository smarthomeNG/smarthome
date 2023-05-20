

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


.. index:: Referenz; SmartPlugin
.. Index:: SmartPlugin Referenz

SmartPlugin
===========

...

Ein Plugin implementiert im Code eine Klasse, welche von der ``class SmartPlugin`` abgeleitet ist. Die Methoden
von ``SmartPlugin`` sind hier dokumentiert:

.. toctree::
   :maxdepth: 5
   :titlesonly:

   smartplugin_class


|

.. index:: Referenz; MqttPlugin
.. Index:: MqttPlugin Referenz

MqttPlugin
==========

...

Plugins welche MQTT nutzen, sollten stattdessen von ``class MqttPlugin`` abgeleitet werden. ``MqttPlugin`` ist
eine Unterklasse von ``SmartPlugin``, die um Methoden zur MQTT-Nutzung erweitert ist. Die Methoden von
``MqttPlugin`` sind hier dokumentiert:

.. toctree::
   :maxdepth: 5
   :titlesonly:

   mqttplugin_class


|

.. index:: Referenz; SmartDevicePlugin
.. index:: Referenz; SDP
.. Index:: SmartDevicePlugin Referenz
.. Index:: SDP Referenz

SmartDevicePlugin
=================

...