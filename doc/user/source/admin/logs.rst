
.. index:: Logs
.. index:: Logging
.. index:: Logging; Logs anzeige
.. index:: Admin GUI; Logs anzeigen
.. index:: Logs; Admin GUI

====
Logs
====

Logs anzeigen
=============

Unter **Logs** können die in SmartHomeNG erzeugten Logeinträge angezeigt werden. Das anzuzeigende Log wird in der
ersten Drop-Down Liste angezeigt. Daneben können unter Zeitrahmen die Logs vergangener Tage ausgewählt werden, falls
ein für ein Log ein **TimedRotatingFileHandler** genutzt wurde. Mit dem Button **Log aktualisieren** wird das Log
aktuell vom SmartHomeNG Server angefordert.


.. image:: assets/log-display.jpg
   :class: screenshot

In der zweiten Zeile können die Logeinträge gefiltert werden. Dazu steht ein Freitextfilter zur Verfügung. Dieser Filter
ist Case-Sensitive. Zusätzlich können die Logeinträge nach Log-Level gefiltert werden.


-----------------
Große Log Dateien
-----------------

Große Log Dateien werden nicht als ganzes, sondern in Stücken (Chunks) eingelesen. Standardmäßig ist ein Chunk 1000
Log-Einträge (Zeilen) lang. Die gewünschte Größe der Chunks kann in der Konfiguration (unter System/Konfiguration im
Tab 'Admin Modul') konfiguriert werden.

.. note::

   Log-Einträge mit einem Traceback werden hierbei zusammen mit dem Traceback als ein Eintrag gezählt.


Wenn ein Log länger als die gewählte Chunk Größe ist, kann mit den Navigations-Buttons ein Chunk weiter oder zurück
navigiert werden. Außerdem kann zum ersten Chunk zurück gesprungen werden oder zum letzten Chunk vor gesprungen werden.
Je nach Größe des Logs kann das einen Moment dauern, da dazu im Hintergrund das gesamte Log gelesen wird.



.. index:: Logging; Liste der Logger

Liste der Logger
================

Unter **Liste der Logger** können die von SmartHomeNG verwendeten Logger angezeigt werden. Die Logger sind der
Übersichtlichkeit halber auf vier Tabs verteilt.

Der Log-Level eines Loggers kann hier zur Laufzeit verändert werden (ohne dass SmartHomeNG neu gestartet werden muss).
Über die Links in der Spalte **Logfile(s)** kann zur Anzeige des entsprechenden Logs verzweigt werden.


.. image:: assets/logs-logger-list.jpg
   :class: screenshot


Aus der Liste geht hervor, über welchen Log-Handler die Einträge in welches Log geschrieben werden (siehe auch Abschnitt
Konfiguration/Logging).

Auf dem Screenshot ist zu sehen, wie das Logging einzelner Logiken unterschiedlich konfiguriert ist. Es gibt einen
Logger **logics**, der WARNINGS (oder höher) aus allen Logiken in das Logfile **smarthome-details.log** schreibt.
Abweichend davon, ist ein Logger für die Logik **a_testlogic2** definiert, der INFOs (oder höher) loggt und zwar über
den Standardhandler für Logiken (es ist in der Konfiguration kein Handler angegeben).

Für Logik **a_testlogic3** ist außer dem Loglevel auch ein Handler definiert. Das sorgt dafür, dass die Logeinträge
in das im Handler definierte Log geschrieben werden (hier das gleiche Log, welches auch für den Standard Logger für
Logiken verwendet wird).


.. index:: Logging; Konfiguration

Logging Konfiguration
=====================

Unter **Konfiguration** kann das Logging vollständig konfiguriert werden. Hierzu wird die Konfigurationsdatei
**logging.yaml** direkt editiert. Änderungen an der Konfiguration werden erst wirksam, wenn SmartHomeNG neu gestartet
wird.


.. image:: assets/logs-configuration.jpg
   :class: screenshot


