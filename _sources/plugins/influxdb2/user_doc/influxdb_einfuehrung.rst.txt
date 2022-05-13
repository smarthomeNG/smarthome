
InfluxDB Einführung
===================

Was ist InfluxDB?
-----------------

Bei InfluxDB handelt es sich um eine spezialisierte Datenbank des Unternehmens InfluxData, die ihre Priorität anders
als relationale Datenbanken wie MySQL und MariaDB oder strukturierte Datenbanken wie Redis auf eine maximale Effizienz
bei begrenzter Komplexität setzt. Die Software steht unter einer Open Source Lizenz.

Zu den Merkmalen von InfluxDB zählen unter anderem:

- Spezialisierung auf Zeitreihen
- Kombination mehrerer Quellen in einer zentralen Instanz
- Sehr hohe Effizienz bei der Verarbeitung
- Erfassung von Daten aus unterschiedlichen Quellen etwa über die API von Drittanbietern

Eine vollständige Übersicht und Beschreibung der Daten Elemente von InfluxDB sind auf der Website von Influxdata
beschrieben. Im folgenden werden die wichtigsten Elemente kurz erläutert.


Was ist eine Organisation?
--------------------------

Eine InfluxDB-Organisation ist ein Arbeitsbereich für eine Gruppe von Benutzern. Alle Dashboards, Aufgaben,
Buckets und Benutzer gehören zu einer Organisation.


Was ist ein Bucket?
-------------------

Ein Bucket ist ein benannter Speicherort innerhalb von InfluxDB. Alle InfluxDB-Daten werden in einem Bucket
gespeichert. Ein Bucket kombiniert das Konzept einer Datenbank und einer Aufbewahrungsfrist (die Dauer, die jeder
Datenpunkt bestehen bleibt). Ein Bucket gehört zu einer Organisation.


Was ist ein Point?
------------------

Ein Point enthält den Serienschlüssel, einen Feldwert und einen Zeitstempel.


Serienschlüssel und Serien
--------------------------

Ein Serienschlüssel ist eine Sammlung von Punkten, die eine Messung, einen Tag-Satz und einen Feldschlüssel
gemeinsam haben.

Eine Serie enthält Zeitstempel und Feldwerte für einen bestimmten Serienschlüssel.


Fields und Tags
---------------

Ein Field enthält einen in der Spalte _field gespeicherten Feldschlüssel und einen in der Spalte _value
gespeicherten Feldwert. Eine Messung erfordert mindestens ein Feld.

Tags stellen Metadaten für einen Point bereit. Tags umfassen Tag-Schlüssel und Tag-Werte, die als Zeichenfolgen
gespeichert werden.


