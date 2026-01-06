
Metadaten für Plugins
=====================

Plugins werden in der Datei ``../etc/plugin.yaml`` bzw. über die Admit GUI konfiguriert. Die Parameter sind in
der Dokumentation des Plugins beschrieben.


Ein Plugin besteht im minimum aus drei Dateien:

- Der Plugin Code: ``__init__.py``
- Die Metadaten: ``plugin.yaml``
- und optional: Eine kurze Dokumentation: ``user_doc.rst``

Eine genaue Beschreibung welche weiteren Dateien und Unterverzeichnisse ein Plugin haben kann, ist im Abschnitt
:doc:`Entwicklung </entwicklung/plugins/plugins>` beschrieben.

Alle drei Dateien sind in einem Verzeichnis unterhalb von ``../plugins`` gespeichert, welches den Namen des
Plugins trägt (nur in Kleinbuchstaben).


Die **Metadaten** Datei eines Plugins heißt ``/plugins/<name of the plugin>/plugin.yaml``. Die bis zu sieben
Abschnitte, die im folgenden beschrieben sind.

- ``plugin:`` - Globale Metadaten des Plugins
- ``parameters:`` - Definition der Parameter, welche zur Konfiguration des Plugins in der Datei ``../etc/plugin.yaml``
  benutzt werden können
- ``item_attributes:`` - Definition der Item Attribute, die durch das Plugin genutzt/unterstützt werden
- ``item_structs:`` - Definition von Item Strukturen, welche im Zusammenhang mit dem Plugin genutzt werden können
- ``item_attribute_prefixes:`` - Definition von Item Attributen elche nur einen genmeinsamen Namens-Beginn haben
- ``logic_parameters:`` - Definition von Parameters welche steuern wie Logiken durch das Plugin genutzt/getriggert
  werden können
- ``plugin_functions:`` - Beschreibung öffentlicher Funktionen des Plugins, die durch Logiken oder andere Plugins
  genutzt werden können

|

Für Plugins werden die folgenden Abschnitte in der Metadaten Datei ``plugin.yaml`` des jeweiligen Plugins genutzt:

.. toctree::
   :maxdepth: 4
   :titlesonly:

   /referenz/metadata/plugin_global
   /referenz/metadata/parameters
   /referenz/metadata/item_attributes
   /referenz/metadata/item_structs
   /referenz/metadata/item_attribute_prefixes
   /referenz/metadata/logic_parameters
   /referenz/metadata/plugin_functions

|


