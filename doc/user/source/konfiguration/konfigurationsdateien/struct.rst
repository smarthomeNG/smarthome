
.. role:: bluesup
.. role:: redsup

.. index:: structs; struct.yaml

struct.yaml und struct_*.yaml
=============================

In dieser Konfigurationsdatei können eigene Item-Strukturen angelegt werden, die über das **struct** Attribut als
Template verwendet werden können.

Ab SmartHomeNG v1.9 können eigene Item-Strukturen auf mehrere Dateien verteilt werden.

Außer der Datei **struct.yaml** im Verzeichnis ../etc können weitere Dateien angelegt werden. Deren
Name muss mit **struct_** beginnen. Der danach folgende Teil des Dateinamens wird dabei dem struct Namen
als Prefix vorangestellt, um Namensdopplungen vorzubeugen.

.. note::

    Weitergehende Informationen zu structs sind unter :doc:`Konfiguration/struct </konfiguration/item_structs>` und in
    der Entwicklerdokumentation unter **Development of Plugins** / **Plugin Metadata** zu finden.


