=======
Plugins
=======

.. toctree::
   :maxdepth: 5
   :hidden:
   :titlesonly:

   plugins_multiinstance


Das Grundsystem von SmartHomeNG kann durch den Einsatz von Plugins erweitert werden. Ein Plugin
ist ein Zusatzmodul in einem Unterverzeichnis unterhalb des Verzeichnisses **../plugins**.
Um ein Plugin in SmartHomeNG zu verwenden (eine Instanz des Plugins zu laden) muß eine Sektion
für das gewünschte Plugin in der Datei **etc/plugin.conf** erstellt werden.

Für das oft benutzte KNX-Plugin sieht das z.B. so aus:

.. code:: yaml

   # etc/plugin.yaml
   knx:
       plugin_name: knx
   #    instance: knx_1
   #    host: 127.0.0.1
   #    port: 6720
       send_time: 600    # update date/time every 600 seconds, default none
       time_ga: 8/0/0
       date_ga: 8/0/1


bzw. im alten Format:

.. code::

   # etc/plugin.conf
   [knx]
      plugin_name = knx
   #   instance = knx_1
   #   host = 127.0.0.1
   #   port = 6720
      send_time = 600 # update date/time every 600 seconds, default none
      time_ga = 8/0/0
      date_ga = 8/0/1


Dabei kann der Name der **Plugin-Instanz** (Name des Abschnitts) frei gewählt werden. Es muss
nur darauf geachtet werden, dass er eindeutig ist, also nur einmal vorkommt. Der name der Instanz
sollte auch so gewählt werden, dass es zu keiner Namensgleichheit mit Top-Level Items kommt.

Es gibt folgende allgemeine Parameter im Abschnitt eines Plugins:

+----------------+-------------------------------------------------------------------------------------+
| Parameter      | Bedeutung                                                                           |
+================+=====================================================================================+
| plugin_name    | Der Kurzname des Plugins, das eingebunden werden soll (Name des Verzeichnisses      |
|                | im **../plugins** Verzeichnis). Statt des Parameters **plugin_name** konnten bisher |
|                | auch die Parameter **class_name** und **class_path** angegeben werden.              |
+----------------+-------------------------------------------------------------------------------------+
| class_name     | **DEPRECATED**: Name der Klasse in der Plugin Datei. Was hier einzutragen ist,      |
|                | steht in der Dokumentation zum jeweiligen Plugin. Stattdessen ist die               |
|                | Konfiguration über den Parameter **plugin_name** vorzunehmen.                       |
+----------------+-------------------------------------------------------------------------------------+
| class_path     | **DEPRECATED**: Pfad zur Plugin Datei. Was hier einzutragen ist, steht in der       |
|                | Dokumentation zum jeweiligen Plugin. Stattdessen ist die Konfiguration  über den    |
|                | Parameter **plugin_name** vorzunehmen.                                              |
+----------------+-------------------------------------------------------------------------------------+
| instance       | Optional: Dieser Parameter muss nur verwendet werden, wenn mehrere Instanzen des    |
|                | selben Plugins geladen werden sollen. Das Plugin selbst muss dazu **Multiinstance** |
|                | fähig sein. Damit die Items der richtigen Plugin-Instanz zugeordnet werden, muss    |
|                | in der jeweiligen Item Definition der Name des Plugin-spezifische Attributes um     |
|                | die Angabe der Instanz ergänzt werden. Also z.B.: Statt **avm_data_type: uptime**   |
|                | muss **avm_data_type@<instance>: uptime** geschrieben werden.                       |
+----------------+-------------------------------------------------------------------------------------+
| plugin_version | Wenn im Plugin Repository mehrere Versionen eines Plugins zur Verfügung stehen,     |
|                | kann über diesen Parameter eine andere als die neueste Version des Plugins geladen  |
|                | werden. Dazu muss die Versionsnummer des Plugins angegeben werden.                  |
|                | (z.B.  **plugin_version: 1.4.9**)                                                   |
+----------------+-------------------------------------------------------------------------------------+

Die weiteren Einträge sind Plugin spezifisch. Welche Parameter ein Plugin kennt ist auch der
README.md des Plugins zu entnehmen. Je nach Plugin können sie verpflichtend oder optional sein.
Im obigen Beispiel sind sie alle optional. Diese Parameter werden  beim Start von SmartHomeNG an
das Plugin übergeben.

Ein **#** wirkt wie auch bei den Konfigurationsdateien der Items als Beginn eines Kommentars.


Liste der verfügbaren Plugins
-----------------------------

Details zu den :doc:`existierenden Plugins <../../plugins_all>` finden sich :doc:`hier <../../plugins_all>` .
