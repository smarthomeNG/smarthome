=========================
Ideen für das Release 1.9
=========================

Core
====


Weitere Loglevel einführen
--------------------------

* SYSINFO (bzw. SHNGINFO)   -   Für allgemeine Informationen, die bisher als WARNING geloggt werden
* INFO_L2   -   um einen höheren INFO Level zu haben, damit man nur "wichtigere" INFOs loggen kann
* INFO_L3   -   evtl. um einen höheren INFO Level zu haben, damit man nur "wichtige" INFOs loggen kann

Evtl. auch weitere DEBUG Level (DEBUG_L2, DEBUG_L3)?

|


Web Interfaces
--------------

* Sortiere Tabellen in die Globals aufnehmen
* Login per JWT (wie bei shngadmin) implementieren, zusätzlich zu basic auth um das doppelte Login zu vermeiden.

|


Update Routinen für die Konfiguration bei neuen Releases implementieren
-----------------------------------------------------------------------

* Python Routine, die nach der Installation der Requirements gestartet wird
* Nach erfolgtem Lauf ein Flag in eine Datei speichern (dass die Daten dem Release … entsprechen)
* Mehrere Routinen nacheinander aufrufen, falls jemand beim Update Versionen überspringt
* Neustart nach jeder Routine notwendig?
* Routinen könnten in ../lib/update abgelegt werden
* Wo sollten die Flags gespeichert werden?

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

Plugins
=======

rtr2
----

* PID Regler implementieren
* Korrektur Faktoren (Kp, Ki, Kd) über Items setzbar machen

