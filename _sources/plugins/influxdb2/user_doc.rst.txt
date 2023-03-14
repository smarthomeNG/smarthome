
.. index:: Plugins; influxdb2
.. index:: influxdb2
.. index:: InfluxDB; influxdb2 Plugin

=========
influxdb2
=========

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

InfluxDB ist ein Open Source Datenbankmanagementsystem (DBMS), speziell für Zeitreihen (engl. time series).
Es wird von der Firma InfluxData entwickelt und vertrieben.

Das influxdb2 Plugin ist eine Neuentwicklung, die auf InfluxDB v2.x aufsetzt. Soll noch eine alte InfluxDB
Software (v1.8 und davor) eingesetzt werden, kann dieses Plugin nicht verwendet werden.


Einführung
==========

Dieses Plugin ermöglicht das Speichern von Daten in der Zeitreihen Datenbank InfluxDB. Es soll auch den Support
für serien (Plots) in smartVISU sicherstellen. Dadurch ist das InfluxDB Plugin in der Lage, als Ersatz für das database
Plugin zu fungieren. Um eine Migration zu erleichtern, kann das InfluxDB Plugin so konfiguriert werden, dass es alle
Werte, die durch das database Plugin in eine SQLite3 bzw. MySQL Datenbank geschrieben werden, zusätzlich in die InfluxDB
schreibt.


Anforderungen
=============

.. Anforderungen des Plugins auflisten. Werden spezielle Soft- oder Hardwarekomponenten benötigt?

Um das Plugin zu nutzen, muss eine InfluxDB Datenbank der Version 2.x installiert und zur Nutzung durch SmartHomeNG
konfiguriert sein.


.. Installation benötigter Software
.. ================================

Installation der InfluxDB Software
==================================

In der Navigation links sind Seiten mit weiteren Informationen zu InfluxDB, der Installation und zur Konfiguration
der InfluxDB Software zur Nutzung mit SmartHomeNG unter folgenden Topics verlinkt:

.. toctree::
  :titlesonly:

  user_doc/influxdb_einfuehrung.rst
  user_doc/influxdb_installation.rst
  user_doc/influxdb_konfiguration.rst


.. Unterstützte Geräte
.. -------------------
..
.. * die
.. * unterstütze
.. * Hardware
.. * auflisten


Gespeicherte Daten
==================

Mit jedem gespeicherten Wert wird unter **_measurement** der Name des Items abgelegt. Mit dem Item-Attribut
**influxdb2_name** kann für das Speichern in der InfluxDB ein Name explizit vergeben werden. Falls das Attribut
**influxdb2_name** nicht definiert wurde, wird der Inhalt des Item-Attributes **name** als Name für die Datenbank
verwendet. Falls **name** nicht spezifiziert ist, wird der Pfadname des Items verwendet.

- **_time** - Der Timestamp wird **nicht** von SmartHomeNG übermittelt, sondern von InfluxDB bei EMpfang der Daten
  bestimmt. Das erleichtert die Synchonisation von Zeitserien, die aus verschiedenen Systemen zusammen geführt werden.
- **_value** - zu speichernder Item Wert


Mit jedem Item Wert, der in einem InfluxDB Bucket abgelegt werden, werden folgende Tags als Metadaten gespeichert:

- **item** - Pfadname des Items
- **item_name** - Im Attribut **name** vergebener Name für das Item
- **caller** - Auslöser für die Änderung des Item Wertes (Plugin, Logik, eval, etc.)
- **source** - Quelle der Änderung: Item Instanz (mit Zusatzdaten), Item, etc.
- **dest** - Ziel der Änderung (z.B. eine GA im knx Plugin)
- **str_value** - enthält nicht numerische Werte, die in der Datenbank abgelegt werden sollen.




Konfiguration
=============

Die Konfiguration der InfluxDB Software ist weiter oben im Abschnitt **Installation der InfluxDB Software** beschrieben.

Die Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/influxdb2` nachzulesen.


Beispiele
---------

Hier können ausführlichere Beispiele und Anwendungsfälle beschrieben werden.

...

Web Interface
=============

...
