.. index:: Plugins; kostal
.. index:: kostal

======
kostal
======

Das Plugin liest Daten aus einem KOSTAL-Wechselrichter (z.B. PIKO) einer Photovoltaikanlage aus.
Die Kommunikation erfolgt über eine Netzwerkverbindung zum Wechselrichter, entweder per HTTP-Status-
seite oder per JSON-Request.

Voraussetzungen
================

Welche Kommunikationsart verwendet wird, hängt von der Firmware-Version des Kommunikationsboards
des Wechselrichters ab:

- Firmware-Version 5.x: Der Wechselrichter liefert eine HTML-Statusseite. Dafür wird
  **datastructure: html** verwendet (Standardeinstellung).
- Firmware-Version 6.x: Der Wechselrichter liefert die Werte im JSON-Format über eine
  Ajax-Statusseite. Dafür wird **datastructure: json** verwendet, es werden dann keine
  Zugangsdaten benötigt.

Das Plugin wurde erfolgreich mit einem KOSTAL PIKO 3.0 (UI-Version 06.20, JSON) und einem KOSTAL
PIKO 5.5 (UI-Version 05.xx, HTML) getestet, sollte aber mit allen KOSTAL PIKO Wechselrichtern
funktionieren.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/kostal` beschrieben.

Bei der PIKO 3.0 handelt es sich um einen einphasigen Wechselrichter mit einem einzelnen
DC-Eingang (DC-String). Alle Werte für DC2, DC3, AC2 und AC3 liefern dann **None**. Bei
HTML-Kommunikation (Firmware 5.x) stehen die Werte für AC-Strom, AC-Cos φ, AC-Limitierung sowie
die Betriebszeit nicht zur Verfügung, da sie in der HTML-Statusseite nicht enthalten sind. Bei
JSON-Kommunikation liefert der Wechselrichter den Tagesertrag in Wh, das Plugin rechnet den Wert
für das Item **yield_day_kwh** in kWh um.

Beispiel
========

::

    Kostal_PV:

        status:
            name: inverter status
            type: str
            kostal: operation_status

        dcpower:
            name: total dc power
            type: num
            kostal: dcpower

        yield_day_kwh:
            name: Yield today
            type: num
            kostal: yield_day_kwh

        yield_tot_kwh:
            name: Yield total
            type: num
            kostal: yield_tot_kwh
