
.. index:: Admin GUI; Übersicht
.. index:: Dashboard; Admin GUI

=========
Übersicht
=========

Die Seite **Übersicht** (Dashboard) ist die Startseite des Administrations-Interface (siehe Parameter ``start_page``
des :doc:`admin Moduls </konfiguration/module/module_admin>`). Sie fasst den Zustand der SmartHomeNG Installation
auf einen Blick zusammen:

* **Systemstatus**: Hostname, Betriebssystem, SmartHomeNG Version und Laufzeit, Python Version, sowie die Anzahl
  der Items und Logiken
* **Gestoppte Plugins**: Plugins, die nicht laufen, z.B. weil sie beim Start einen Fehler hatten
* **Aktuelle Warnungen und Fehler**: die neuesten Log-Einträge mit dem Level WARNING oder höher
* **Überfällige Scheduler**: Scheduler, deren geplante Ausführung überfällig ist
* **Datenbank**: Falls das database Plugin konfiguriert ist, Treiber, Datenbankname, Host, Status der
  Verbindung, Version der Datenbank-Engine und der Abfrage-Timeout (Parameter ``db_query_timeout`` der
  :doc:`smarthome.yaml </konfiguration/konfigurationsdateien/smarthome>`). Bei SQLite wird zusätzlich der
  Journal-Modus angezeigt, bei TimescaleDB, ob Hypertables, native Continuous Aggregates und native Retention
  genutzt werden.

Die Daten werden regelmäßig aktualisiert. Konnten sie eine Zeit lang nicht abgerufen werden, wird angezeigt, wann sie
zuletzt aktualisiert wurden.
