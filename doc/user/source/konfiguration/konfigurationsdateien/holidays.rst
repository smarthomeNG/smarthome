.. index:: Konfigurationsdateien; /etc/holidays.yaml
.. index:: holidays; Konfiguration
.. index:: Feiertage; Konfiguration

.. role:: bluesup
.. role:: redsup

=============
holidays.yaml
=============


.. _`holidays.yaml`:

Ab Version 1.7 unterstützt SmartHomeNG Feiertage. In Logiken und Plugins kann abgefragt werden, ob ein bestimmtes
Datum ein Feiertag ist und welcher.

Es werden zzt. die Feiertage von 50 Ländern unterstützt. Falls ein Land regional unterschiedliche Feiertage hat,
so wird dieses auch unterstützt. Um die richtigen Feiertage in der SmartHomeNG Umgebung zu erhalten, müssen das zu
verwendende Land und die Region/Provinz konfiguriert werden.

In der Konfigurationsdatei können auch noch zusätzlich benutzerdefinierte Feiertage konfiguriert werden.

Feiertage werden normalerweise im Reiter **Allgemein** der Systemkonfiguration konfiguriert. Hierzu stehen die Felder

- holidays_country
- holidays_province
- holidays_state

zur Verfügung.

Benutzerdefinierte Feiertage
============================

Des weiteren können benutzerdefinierte Feiertage deklariert werden. Hierzu stehen fünf Felder **holidays_custom**? zur
Verfügung in denen die entsprechenden Regeln hinterlegt werden können. Die Regeln werden in json formuliert (das Format
entspricht weitestgehend der Definition eines Python **dict**).

Die Definition darf folgende Keys enthalten:

+-------------------+-------------------------------------------------------------------------------------------------+
| Key               | Beschreibung                                                                                    |
+===================+=================================================================================================+
| day               | Tag des Feiertagsdatums                                                                         |
+-------------------+-------------------------------------------------------------------------------------------------+
| month             | Monat des Feiertagsdatums                                                                       |
+-------------------+-------------------------------------------------------------------------------------------------+
| year              | Jahr des Feiertagsdatums - Wird ein Jahr angegeben, wird der Feiertag nur für das entsprechende |
|                   | Jahr eingetragen. Wird das Jahr weggelassen, wird dieser Feiertag jährlich wiederholt.          |
+-------------------+-------------------------------------------------------------------------------------------------+
| name              | Name des Feiertages                                                                             |
+-------------------+-------------------------------------------------------------------------------------------------+
| dow               | Wochentag des Feiertagsdatums                                                                   |
+-------------------+-------------------------------------------------------------------------------------------------+
| dow_week          | Anzahl Wochen bis zur Wiederholung für einen Feiertag, der auf einem festen Wochentag liegt     |
+-------------------+-------------------------------------------------------------------------------------------------+
| dow_start_week    | Start-Kalenderwoche für einen Feiertag, der auf einem festen Wochentag liegt                    |
+-------------------+-------------------------------------------------------------------------------------------------+


Beispiele
---------

+---------------------------------------------------------------------------------------+------------------------------------------------+
| Definition                                                                            | Beschreibung                                   |
+=======================================================================================+================================================+
| {"day": 2, "month": 8, "name": "Jon Doe's birthday"}                                  | 2. August - Jon Doe's Geburtstag               |
+---------------------------------------------------------------------------------------+------------------------------------------------+
| {"day": 22, "month": 11, "name: "Jane Doe's birthday"}                                | 22. November - Jane Doe's Geburtstag           |
+---------------------------------------------------------------------------------------+------------------------------------------------+
| {"day": 2, "month": 8, "year": 2020, "name": "Jon Doe's 100th birthday"}              | 22. November 2020 - Jane Doe's 100. Geburtstag |
+---------------------------------------------------------------------------------------+------------------------------------------------+
| {"dow": 5, "dow_week": "last", "month": 7, "name": "Sysadmin day"}                    | Letzter Freitag im Juli - Sysadmin Day         |
+---------------------------------------------------------------------------------------+------------------------------------------------+
| {"dow": 2, "dow_week": 2, "month": 7, "name": "second tuesday in July"}               | 2. Dienstag im Juli                            |
+---------------------------------------------------------------------------------------+------------------------------------------------+
| {"dow": 2, "dow_week": 2, "month": 7, "year": 2019, "name": "2. tuesday in July '19"} | 2. Dienstag im Juli im Jahr 2019               |
+---------------------------------------------------------------------------------------+------------------------------------------------+
| {"dow": 3, "dow_week": 2, "year": 2021, "name": "Every second wednesday in 2021"}     | Jeder 2. Mittwoch in 2021                      |
+---------------------------------------------------------------------------------------+------------------------------------------------+
| {"dow": 3, "dow_week": 2, "dow_start_week": 1, "year": 2021,                          | Jeder 2. Mittwoch in 2021, beginnend           |
| "name": "Every second wednesday in 2021, starting on 1st wednesday"}                  | am 1. Mittwoch im Jahr                         |
+---------------------------------------------------------------------------------------+------------------------------------------------+


Konfigurationsdatei
===================

Statt in der Admin GUI kann die Konfiguration auch in der Konfigurationsdatei vorgenommen werden. Sie sollte in
etwa so aussehen:

.. literalinclude:: ../../../../../etc/holidays.yaml.default
   :caption: holidays.yaml
   :language: yaml


Im Abschnitt **Logiken** ist auf der Seite :doc:`Feiertage, Daten und Zeiten </logiken/objekteundmethoden_feiertage_datum_zeit>`
beschrieben, wie die hier konfigurierten Feiertage in Logiken und **eval** Attributen genutzt werden können.

