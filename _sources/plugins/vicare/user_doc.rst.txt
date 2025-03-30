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
das Plugin bei jedem Neustart einen neuen accessToken. Der refresh Token ist 180 Tage gültig, d.h. die manuelle Authentifizierung muss alle 180 Tage einmal durchgeführt werden. Dies ist eine Vorgabe der Viessmann API.

Requirements
=============
- authlib

Supported Hardware
==================
z.B.
Vitodens 200-W

Vitocal 200S


Web Interface
=============


Aufruf des Webinterfaces
------------------------

Das Plugin kann aus dem Admin Interface aufgerufen werden. Dazu auf der Seite Plugins in der entsprechenden
Zeile das Icon in der Spalte **Web Interface** anklicken.

Außerdem kann das Webinterface direkt über ``http://smarthome.local:8383/vicare`` aufgerufen werden.

Allgemein
---------
In der Kopfzeile werden der Onlinestatus, die Anzahl der gefundenen Geräte, die ClientID und das Gerätemodell angezeigt. Aktuell unterstützt das Gerät nur das Auslesen eines
Heizgeräts. Werden mehrere Geräte gefunden, wird aktuell das erste gültige Heizgerät ausgewählt.


Reiter
------

Unter dem Reiter **Mit Vicare verbinden** wird unter Anleitung der OAutch2 Authentifizierungsvorgang durchgeführt, damit das Plugin Zugang zur Viessmann API bekommt. 

Unter dem Reiter **Geräteliste** werden alle mit dem Konto verknüpften Viessmann Geräte aufgelistet.

Unter dem Reiter **Featureliste** werden alle vom Gerät unterstützen Features angezeigt. Wenn ein Feature in der Spalte **Commands** einen Eintrag hat, kann das Feature schreibend verändert werden.
Wenn das Feature nur einen Eintrag in der Spalte **Properties** hat, kann das Feature nur ausgelesen werden. 
Die Spalte *Feature* gibt den Featurenamen an, der im Item Attribut ``vicare_rx_key`` (fürs Auslesen) oder `vicare_tx_key` (fürs Steuern) angegeben werden muss.

Aus den unter **Properties** und **Commands** angezeigten Jsons werden die nötigen Item Attribute (`vicare_rx_key`, `vicare_path`) generisch abgeleitet.

Beispiele:

+------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------+
| Art        | JSON                                                                                                                                    | vicare_path / vicare_tx_path                    |
+============+=========================================================================================================================================+=================================================+
| Temperatur | Properties: {'value': {'type': 'number', 'value': 54.9, 'unit': 'celsius'}, 'status': {'type': 'string', 'value': 'connected'}}         | ['value','value']                               |
+------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------+
| Status     | Properties: {'value': {'type': 'number', 'value': 54.9, 'unit': 'celsius'}, 'status': {'type': 'string', 'value': 'connected'}}         | ['status','value']                              |
+------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------+
| Modus      | Commands:   {'setTargetTemperature': {'uri': 'https:...setTargetTemperature', 'params': {'temperature': {'type': 'number',.}}}}         | ['setTargetTemperature','params','temperature'] |
+------------+-----------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------+
