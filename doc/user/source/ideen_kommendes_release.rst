=========================
Ideen für das Release 1.9
=========================


.. contents:: Inhaltsübersicht
    :depth: 3

|

Core
====

Ideen für neue Funktionalitäten im Core

|

Struct Nesting
--------------

Möglichkeiten des Nesting von structs erweitern.

|

Logiken: Zusätzlichen Trigger „shutdown“
----------------------------------------

Zusätzlichen Trigger, um Logiken beim herunterfahren von SmartHomeNG triggern zu können.

|

Items: User Attribute implementieren
------------------------------------

Attribute, die User nutzen wollen, die aber in keinem Plugin definiert sind.

|

Weitere Loglevel einführen
--------------------------

Siehe auch https://github.com/smarthomeNG/smarthome/issues/384

* SYSINFO (bzw. SHNGINFO)   -   Für allgemeine Informationen, die bisher als WARNING geloggt werden
* INFO_L2   -   um einen höheren INFO Level zu haben, damit man nur "wichtigere" INFOs loggen kann
* INFO_L3   -   evtl. um einen höheren INFO Level zu haben, damit man nur "wichtige" INFOs loggen kann

Evtl. auch weitere DEBUG Level (DEBUG_L2, DEBUG_L3)?

Diese Loglevel sollten auch in Plugins und Logiken zur Verfügung stehen. Evtl. mit der Ausnahme von SHNGINFO, welcher
evtl. dem Core vorbehalten sein solle. Dafür könnte man noch einen Level wie PLGINFO o.ä. einführen, der unterhalb
von SHNGINFO liegt.

Evtl in folgender Abstufung:

* 50 - CRITICAL
* 40 - ERROR
* 30 - WARNING
* 27 - SHNGINFO  (für den Core)
* 25 - SYSINFO   (für Plugins und Logiken)
* (23 - INFO_L3)
* (22 - INFO_L2)
* 20 - INFO
* 12 - USER_DEBUG
* 10 - DEBUG
* 8  - DEBUG_LOW

|

lib.color
---------

Library zur Umrechnung zwischen Farbräumen. Zur Nutzung in Logiken und evals z.B.
bei Nutzung von Hue.

|

Web Interfaces
--------------

* Sortiere Tabellen in die Globals aufnehmen
* Login per JWT (wie bei shngadmin) implementieren, zusätzlich zu basic auth um das doppelte Login zu vermeiden.

|


Update Routinen für die Konfiguration bei neuen Releases implementieren
-----------------------------------------------------------------------

Automatische Updates Umgebung der Anwender Installation erlauben, wenn eine
neue Version von SmartHomeNG installiert wird.

* Python Routine, die nach der Installation der Requirements gestartet wird
* Nach erfolgtem Lauf ein Flag in eine Datei speichern (dass die Daten dem Release … entsprechen)
* Mehrere Routinen nacheinander aufrufen, falls jemand beim Update Versionen überspringt
* Neustart nach jeder Routine notwendig?
* Routinen könnten in ../lib/update abgelegt werden
* Wo sollten die Flags gespeichert werden?

|

MQTT Modul Erweiterungen
------------------------

* MQTT v5 Protokoll implementieren.
* Verhalten bei Broker Neustart verbessern.

|

Admin GUI
=========

Ideen für neue Funktionalitäten in der Admin GUI

|

Websocket Nutzdaten Protokoll für shngadmin
-------------------------------------------

* Item Details: Werte automatisch aktualisieren

  * Wert
  * letzter Wert
  * Vorletzter Wert
  * Changed_by / Change Time
  * Updated_by / Update Time
  * Previous change_by / Change Time
  * Previous updated_by / Update Time

* Implementieren der Seite "Items monitoren"

* Graphen auf das neue Nutzdaten Protokoll umstellen

|

Nach Core Neustart die Server infos neu lesen
---------------------------------------------

|

Admin GUI shngadmin: Dark Mode?
-------------------------------

|


Plugins
=======

Ideen für neue Plugins oder die Erweiterung bestehender Plugins

|

hue2
----

discoverhue Package ersetzen

|

rtr2
----

* PID Regler implementieren
* Korrektur Faktoren (Kp, Ki, Kd) über Items setzbar machen

|

smartvisu
---------

* Weitere Möglichkeiten für generierte Seiten implementieren

  * weitere Blöcke (z.B.: Doppelte Breite, feste Höhe, nicht zuklappbar, maximierbar, ...)
  * Seiten ohne Navigation ermöglichen

* Navigation mit zwei gleichnamigen Räumen
* Widget Handling verbessern

|

tasmota
-------

Bisher darf ein MQTT Topic (für MQTT-In) nur einmal vorkommen. Bei Verwendung in mehreren Items, wird nur eines berücksichtigt (aktualisiert).

|

Tools
=====

Ideen für neue Funktionalitäten in den Tools

|

Tool zur formalen Prüfung von Plugins
-------------------------------------

Formale Prüfung des Codes, nicht nur der Metadaten

|
