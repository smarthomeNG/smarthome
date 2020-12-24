
.. index:: Metadata
.. index:: Plugin Metadata

.. role:: redsup
.. role:: bluesup

Plugin-Metadata :bluesup:`update`
=================================

Plugins werden in ``etc/plugin.yaml`` konfiguriert. Die Parameter sind in der ``plugin.yaml`` des jeweiligen Plugins
beschrieben.

Ein Plugin besteht aus mindestens zwei Dateien:

- dem Programmcode: __init__.py
- den Metadaten: plugin.yaml

.. hint::

   Das in früheren Versionen verwendete **README**-Format für die Dokumentation von Plugins ist veraltet. Ein Großteil der Dokumentation ist in die Metadaten-Dokumentation in **plugin.yaml** übergegangen. Die restliche Dokumentation sollte nur noch im **user_doc**-Format erfolgen.

   Soweit möglich, sollten bestehende **README** im Rahmen von Aktualisierungen in entsprechende **user_doc** überführt werden.


Diese Dateien befinden sich in einem Unterordner des ``/plugins``-Ordners. Der Name des Unterordners entspricht dem
Namen des Plugins.

Die **Metadaten**-Datei heißt ``/plugins/<Name des Plugins>/plugin.yaml``. Sie besteht aus sechs Abschnitten:

- ``plugin:`` - Gobale Metadaten des Plugins
  Die Daten dieses Abschnitts werden verwendet, um die Kompatibilität des Plugins mit der laufenden Version von
  SmartHomeNG zu prüfen und definieren, wie das Plugin geladen wird

  Die Angaben unter ``description:`` werden genutzt, um die Plugin-Seite in der SmartHomeNG-Dokumentation zu erzeugen.
  Standardmäßig wird die deutsche Sprachversion verwendet, wenn diese nicht vorhanden ist, wird die englische genutzt.


- ``parameters:`` - Parameter, mit denen das Plugin in ``/etc/plugin.yaml`` konfiguriert wird.
  Die Daten dieses Abschnitts werden verwendet, um die Gültigkeit der Plugin-Konfiguration zu prüfen.


- ``item_attributes`` - Item-Attribute, die durch das Plugin definiert werden
  Die Daten dieses Abschnitts werden verwendet, um die Attribute der Item-Konfiguration auf Gültigkeit zu prüfen.


- ``item_structs:`` - Item-Strukturen, die vorgefertigte Item-Pakete des Plugins bereitstellen


- ``logic_parameters:`` - Logik-Parameter, die in ``/etc/logic.yaml`` zur Konfiguration von Logiken genutzt werden


- ``plugin_functions:`` - Funktionsaufrufe, die das Plugin bereitstellt


Die Metadaten werden weiterhin vorgesehen

  - für die automatisierte Erstellung der SmartHomeNG-Dokumentation
  - für die Nutzung in einer grafischen Konfigurationsoberfläche


:Note: Wenn die Implementation der Metadaten-Systematik abgeschlossen ist, werden die folgenden Variablen im Python code von SmartPlugins nicht mehr benötigt. Sie werden aus den globalen Metadaten ausgelesen und im Plugin automatisch bereitgestellt:

    - ALLOW_MULTIINSTANCE
    - PLUGIN_VERSION

    Es wird empfohlen, die Variable PLUGIN_VERSION trotzdem zu setzen. Dann kann durch den Vergleich der Angaben
    in __init__.py und plugin.yaml sichergestellt werden, dass die Dateiversionen zueinander passen. Wenn das nicht 
    der Fall ist, wird ein Fehler ausgegeben und das Laden des Plugins verhindert.


.. hint::

    Zum Validieren der Metadaten in plugin.yaml kann das Tool /tools/plugin_metadata_checker.py genutzt werden. Dies
    prüft die Metadaten auf Vollständigkeit und Fehlerfreiheit.


:Note: Bei Modulen heißt der Abschnitt entsprechend ``module:`` statt ``plugin:``


Detaillierte Beschreibung
-------------------------

Die einzelnen Abschnitte sind im Folgenden detailliert beschrieben:

.. include:: /referenz/metadata/plugin_global.rst
.. include:: /referenz/metadata/parameters.rst
.. include:: /referenz/metadata/item_attributes.rst
.. include:: /referenz/metadata/item_structs.rst
.. include:: /referenz/metadata/logic_parameters.rst
.. include:: /referenz/metadata/plugin_functions.rst

