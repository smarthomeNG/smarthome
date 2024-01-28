.. index:: Plugins; vicare
.. index:: vicare

======
vicare
======

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Allgemein
=========

SmarthomeNG plugin mit Unterstützung für Viessmann Heizungen via vicare backend mit OAuth2 Identifizierung.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/vicare` beschrieben.
Die Kopplung zwischen Plugin und Viessmann Backend erfolgt über das OAuth2 Verfahren. Das Webinterface führt Schritt für Schritt durch den Anmeldeprozess. Die Authentifizierung muss einmal via 
Webinterface durchgeführt werden. Nach Abschluss erhält man einen access Token und einen refresh Token. Beide werden persistent in der plugin.yaml gespeichert. Mit Hilfe des refresh Tokens generiert 
das Plugin bei jedem Neustart einen neuen accessToken. Der refresh Token ist 180 Tage gültig, d.g. die manuelle Authentifizierung muss alle 180 Tage einmal durchgeführt werden. Dies ist eine Vorgabe der Viessmann API.

Requirements
=============
- authlib

Supported Hardware
==================
z.B. Vitodens 200-W


Web Interface
=============


Aufruf des Webinterfaces
------------------------

Das Plugin kann aus dem Admin Interface aufgerufen werden. Dazu auf der Seite Plugins in der entsprechenden
Zeile das Icon in der Spalte **Web Interface** anklicken.

Außerdem kann das Webinterface direkt über ``http://smarthome.local:8383/vicare`` aufgerufen werden.


Beispiele
---------

Folgende Informationen können im Webinterface angezeigt werden:

