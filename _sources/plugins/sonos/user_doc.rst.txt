.. index:: Plugins; sonos
.. index:: Sonos

========
sonos
========

Sonos plugin, mit Unterstützung für Sonos Lautsprecher

Das Plugin basiert auf dem Sonos SoCo github projekt:
https://github.com/SoCo/SoCo

Official Sonos Seite:
https://www.sonos.com/


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/sonos` beschrieben.


Web Interface
=============

Das sonos Plugin verfügt über ein Webinterface, auf dem die aktive SoCo version angezeigt wird.

.. important::

   Das Webinterface des Plugins kann mit SmartHomeNG v1.4.2 und davor **nicht** genutzt werden.
   Es wird dann nicht geladen. Diese Einschränkung gilt nur für das Webinterface. Ansonsten gilt
   für das Plugin die in den Metadaten angegebene minimale SmartHomeNG Version.


Aufruf des Webinterfaces
------------------------

Das Plugin kann aus dem Admin Interface aufgerufen werden. Dazu auf der Seite Plugins in der entsprechenden
Zeile das Icon in der Spalte **Web Interface** anklicken.

Außerdem kann das Webinterface direkt über ``http://smarthome.local:8383/sonos`` aufgerufen werden.


Beispiele
---------

Folgende Informationen können im Webinterface angezeigt werden:

Oben rechts werden allgemeine Parameter zum Plugin wie die aktuelle SoCo Version angezeigt.

