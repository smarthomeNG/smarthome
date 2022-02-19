
.. index:: Entwicklung; Plugins

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup


=====================================
Plugins :bluesup:`under construction`
=====================================

Informationen über das Schreiben von Plugins und wie sie in SmartHomeNG eingebunden werden, können in diesem
Abschnitt und den links in der Navigation verlinkten Seiten gefunden werden.

.. toctree::
   :maxdepth: 1
   :hidden:

   vorueberlegungen.rst
   /dev/README.md

Kurzanleitung
=============

Weitere Informationen über die zu erstellenden Methoden und ihre Parameter können in der folgenden Kurzanleitung
gefunden werden. Die Libraries im Verzeichnis ``/lib`` stellen den Kern der Funktionalitäten von smarthomeng bereit.

.. toctree::
   :maxdepth: 1
   :titlesonly:
   :hidden:

   plugin_in5minutes.rst


Alle Dateien eines Plugins befinden sich in einem Unterverzeichnis des Verzeichnisses ``/plugins``, welches den Namen des Plugins trägt (nur Kleinbuchstaben). Ein Plugin besteht mindestens den folgenden zwei Dateien:

+--------------------------+---------------------------------------------------------------------------------+
| File                     | Description                                                                     |
+==========================+=================================================================================+
| ``__init__.py``          | Der Programmcode des Plugins                                                    |
+--------------------------+---------------------------------------------------------------------------------+
| ``plugin.yaml``          | Die (mehrsprachige) Beschreibung der Metadaten für das Plugin                   |
+--------------------------+---------------------------------------------------------------------------------+


Je nach Umfang und Erfordernissen sind folgende optionale Dateien hinzuzufügen:

+--------------------------+---------------------------------------------------------------------------------+
| File                     | Description                                                                     |
+==========================+=================================================================================+
| ``locale.yaml``          | Enthält die Übersetzungen für die mehrsprachige Implementierung des Web         |
|                          | Interfaces                                                                      |
+--------------------------+---------------------------------------------------------------------------------+
| ``requirements.txt``     | Falls ein Plugin ein Python Package nutzt, welches nicht in der                 |
|                          | Standardinstallation von Python enthalten ist, muss diese Anforderung in der    |
|                          | Datei ``requirements.txt`` dokumentiert werden. (Für eine Beschreibung der      |
|                          | Dateiformats bitte in der Dokumentation des ``pip`` Kommandos nachlesen:        |
|                          | (https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format) |
+--------------------------+---------------------------------------------------------------------------------+
| ``user_doc.rst``         | Weitergehende Dokumentation des Plugins, die in die Anwender-Dokumentation      |
|                          | integriert wird. Falls die Dokumentation in ``user_doc.rst`` Bilder oder andere |
|                          | Assets enthalten soll, ist im Plugin Verzeichnis ein Verzeichnis ``assets``     |
|                          | anzulegen, welches diese Dateien aufnimmt.                                      |
|                          |                                                                                 |
|                          | Die Dokumentationsdatei ``user_doc.rst`` muss nicht in den Metadaten            |
|                          | (``plugin.yaml``) referenziert werden. Sie wird automatisch bei der Generierung |
|                          | der Anwender Dokumentation von SmartHomeNG integriert.                          |
+--------------------------+---------------------------------------------------------------------------------+
| ``developer_doc.rst``    | Weitergehende Entwickler-Dokumentation des Plugins.                             |
+--------------------------+---------------------------------------------------------------------------------+
| ``README.md``?           | Das in früheren Versionen verwendete ``README``-Format für die Dokumentation    |
|                          | von Plugins ist veraltet. Ein Großteil der Dokumentation ist in die Metadaten-  |
|                          | Dokumentation in ``plugin.yaml`` übergegangen. Die restliche Dokumentation      |
|                          | sollte nur noch im ``user_doc``-Format erfolgen.                                |
|                          | Soweit möglich, sollten bestehende ``README`` im Rahmen von Aktualisierungen    |
|                          | in entsprechende ``user_doc`` überführt werden.                                 |
+--------------------------+---------------------------------------------------------------------------------+


.. important::

   Die erste Überschrift in der Datei ``user_doc.rst`` MUSS dem Short-Name des Plugins in Kleinbuchstaben
   entsprechen (identisch zum Namen des Verzeichnisses in dem die Plugin Dateien gespeichert sind.

   Diese Überschrift wird als Eintrag in der Navigation der Dokumentation verwendet. Wenn eine andere Überschrift
   gewählt würde, würde die Navigation der Dokumentation inkonsistent werden.


Ein Plugin Verzeichnis kann die folgenden Unterverzeichnisse haben:

+--------------------------+-----------------------------------------------------------------------+
| Directory                | Description                                                           |
+==========================+=======================================================================+
| ``_pv_<version>``        | Ein Verzeichnis, welches eine vorangegangene Version des Plugins      |
|                          | enthält (bei größeren Überarbeitungen des Plugins). Die ``<version>`` |
|                          | muss der Versionsnummer des Plugins entsprechen, wobei die Punkte     |
|                          | durch Unterstriche ersetzt werden. (z.B.: 1.3.5 -> 1_3_5)             |
+--------------------------+-----------------------------------------------------------------------+
| ``assets``               | Verzeichnis für Bilder und Assets der Doku (``user_doc``)             |
+--------------------------+-----------------------------------------------------------------------+
| ``webif``                | Enthält die Dateien eines Webinterfaces, falls das Plugin eines       |
|                          | implementiert. (Es sollte die Unterverzeichnisse ``static`` und       |
|                          | ``templates`` enthalten.)                                             |
+--------------------------+-----------------------------------------------------------------------+
| ``webif/static``         | Enthält die eigentlichen Dateien des Webinterfaces                    |
+--------------------------+-----------------------------------------------------------------------+
| ``webif/static/css``     | Optional, falls cascading style sheets genutzt werden.                |
+--------------------------+-----------------------------------------------------------------------+
| ``webif/static/img``     | Optional, falls das Webinterface Bilder enthält                       |
+--------------------------+-----------------------------------------------------------------------+
| ``webif/templates``      | Dieses Verzeichnis enthält die Jinja2 Templates des Webinterfaces und |
|                          | sollte mindestens ``index.html`` enthalten.                           |
+--------------------------+-----------------------------------------------------------------------+


Ein Plugin implementiert im Code eine Klasse, welche von der ``class SmartPlugin`` abgeleitet ist. Die Methoden
von ``SmartPlugin`` sind hier dokumentiert:

.. toctree::
   :maxdepth: 5
   :titlesonly:

   smartplugin

Plugins welche MQTT nutzen, sollten stattdessen von ``class MqttPlugin`` abgeleitet werden. ``MqttPlugin`` ist
eine Unterklasse von ``SmartPlugin``, die um Methoden zur MQTT-Nutzung erweitert ist. Die Methoden von
``MqttPlugin`` sind hier dokumentiert:

.. toctree::
   :maxdepth: 5
   :titlesonly:

   mqttplugin


.. toctree::
   :maxdepth: 5
   :titlesonly:
   :hidden:

   plugin_metadata
   plugin_documentation_files
   webinterface
   multilanguage
   sampleplugin
   samplemqttplugin
   libraries_plugins



Weitergehende und sehr spezifische Informationen über einzelne Plugins sind hier verfügbar:

.. toctree::
   :maxdepth: 1
   :titlesonly:

   /plugins/visu_smartvisu/developer_doc
   /plugins/visu_websocket/developer_doc


