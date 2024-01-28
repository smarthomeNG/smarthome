.. index:: shelly
.. index:: Plugins; shelly
.. index:: mqtt; shelly Plugin

======
shelly
======

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 90px
   :scale: 50 %
   :align: left

Das Plugin dienst zur Steuerung von Shelly Devices über MQTT. Zur Aktivierung von MQTT für die Shelly Devices bitte
die Dokumentation des jeweiligen Devices zu Rate ziehen.

|

Konfiguration
=============

Zurzeit werden eine Reihe von Shelly Devices mit Gen1 API im **Backward-Co^mpatibility Mode** unterstützt. Dabei handelt
es sich um die Devices, die bereits in der v1.2.0 des Plugins unterstützt wurden. Diese Devices werden konfiguriert,
wie es bis zur v1.2.0 des shally Plugins üblich war.


Es werden alle Relays eines Shelly Devices (bis zu 4) unterstützt. Weiterhin werden die folgenden
Attribute/Parameter der Devices unterstützt, soweit die Devices selbst diese unterstützen:

- humidity
- state
- tilt
- vibration
- lux
- illumination
- flood
- battery
- power
- energy
- temperature
- temperature_f

sowie der online-Status.


Weitergehende Informationen speziell zur Konfiguration dieses Plugins sind unter
:doc:`/plugins/shelly/user_doc/plugin_configuration` zu finden.

Allgemeine Informationen zur Konfiguration und die vollständige Beschreibung der Item-Attribute sind
unter :doc:`/plugins_doc/config/shelly` zu finden.

.. attention::

    Das Plugin kommuniziert über MQTT und benötigt das mqtt Modul, welches die Kommunikation mit dem MQTT Broker
    durchführt. Dieses Modul muß geladen und konfiguriert sein, damit das Plugin funktioniert.

|

.. toctree::
  :hidden:

  user_doc/device_installation.rst
  user_doc/plugin_configuration.rst


Web Interface
=============

Shelly Items
------------

Das Webinterface zeigt die Items an, für die ein Shelly Device konfiguriert ist.

.. image:: user_doc/assets/shelly-webif-items.jpg
   :class: screenshot

Der Item Wert, sowie die Zeitangaben zu letzten Update und zum letzten Change werden periodisch aktualisiert.


Shelly Devices
--------------

Das Webinterface zeigt Informationen zu den konfigurierten Shelly Devices an, sowie etwa hinzugekommen Devices die
in SmartHomeNG noch nicht konfiguriert (mit einem Item vebunden) sind.

.. image:: user_doc/assets/shelly-webif-devices.jpg
   :class: screenshot

Ein Klick auf die Shelly ID öffnet die Shelly Konfigurationsseite des Devices.


Broker Information
------------------

Das Webinterface zeigt Informationen zum genutzten MQTT Broker an.

.. image:: user_doc/assets/shelly-webif-brokerinfo.jpg
   :class: screenshot

