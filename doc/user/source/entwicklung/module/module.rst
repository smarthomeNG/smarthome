
.. index:: Entwicklung; Module

.. role:: bluesup
.. role:: redsup


======
Module
======

Ladbare Code Module (SmartHomeNG Module) stellen zusätzliche Funktionalitäten zur Verfügung, die zur Programmierung
von Plugins und Logiken genutzt werden können. Sie implementieren Funktionalitäten, die nicht unbedingt benötigt
werden und deshalb nicht direkt im Core implementiert und zwangsweise geladen werden.

Module werden in der Datei ``../etc/modules.yaml`` oder in der Admin GUI konfiguriert. Die Parameter sind in
der jeweiligen README.md beschrieben.

Bisher existieren die folgenden Module:

.. toctree::
   :maxdepth: 3
   :titlesonly:

   module_http
   module_admin
   module_mqtt
   ../../referenz/module/module_websocket


Ein Modul besteht aus mindestens zwei Dateien:

- dem Programm Code: __init__.py
- den Metadaten: module.yaml

Beide Dateien lliegen in einem Unterordnet des Ordners ``../modules`` und dieser Unterordnet trägt den Namen des
Mooduls.

Metadaten
=========

Die **Metadaten** Datei trägt den Namen ``../modules/<name of the module>/module.yaml``. Sie hat zwei
Haupt Abschnitte:


- ``module:`` - Globale Metadaten des Moduls
- ``parameters:`` - Definition der Parameter welche in ``../etc/module.yaml`` zur Konfiguration des Moduls
  genutzt werden können.

.. include:: /referenz/metadata/module_global.rst

.. include:: /referenz/metadata/parameters.rst


Falls ein Modul ein Python Package nutzt, welches nicht in der Standardinstallation von Python enthalten ist,
muss diese Anforderung in der Datei ``../modules/<name of the module>/requirements.txt`` dokumentiert werden.

