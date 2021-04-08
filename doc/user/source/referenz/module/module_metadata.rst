
Metadaten für Module
====================

Module werden in der Datei ``../etc/module.yaml`` bzw. über die Admit GUI konfiguriert. Die Parameter sind in
der Dokumentation des Moduls beschrieben.


Ein Modul besteht im minimum aus zwei Dateien:

- Der Modul Code: ``__init__.py``
- Die Metadaten: ``module.yaml``

Eine genaue Beschreibung welche weiteren Dateien und Unterverzeichnisse ein Modul haben kann, ist im Abschnitt
:doc:`Entwicklung </entwicklung/module/module>` beschrieben.

Alle Dateien sind in einem Verzeichnis unterhalb von ``../modules`` gespeichert, welches den Namen des
Moduls trägt (nur in Kleinbuchstaben).


Die **Metadaten** Datei eines Moduls heißt ``/modules/<name of the module>/module.yaml``. Die bis zu sieben
Abschnitte, die im folgenden beschrieben sind.

- ``module:`` - Globale Metadaten des Moduls
- ``parameters:`` - Definition der Parameter, welche zur Konfiguration des Moduls in der Datei ``../etc/module.yaml``
  benutzt werden können

|

Für Module werden die folgenden Abschnitte in der Metadaten Datei ``module.yaml`` des jeweiligen Moduls genutzt:

.. toctree::
   :maxdepth: 4
   :titlesonly:

   /referenz/metadata/module_global
   /referenz/metadata/parameters

|
