=======
Plugins
=======

Das Grundsystem von SmartHomeNG kann durch den Einsatz von Plugins erweitert werden. Ein Plugin
ist ein Zusatzmodul in einem Unterverzeichnis unterhalb des Verzeichnisses **../plugins**.
Um ein Plugin in SmartHomeNG zu verwenden (eine Instanz des Plugins zu laden) muss eine Sektion
für das gewünschte Plugin in der Datei **etc/plugin.yaml** erstellt werden.

Für das oft benutzte KNX-Plugin sieht das z.B. so aus:

.. code:: yaml

   # etc/plugin.yaml
   knx:
       plugin_name: knx
   #    instance: knx_1
   #    host: 127.0.0.1
   #    port: 6720
   #    webif_pagelength: 0
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
   #   webif_pagelength = 0
      send_time = 600 # update date/time every 600 seconds, default none
      time_ga = 8/0/0
      date_ga = 8/0/1


Dabei kann der Name der **Plugin-Instanz** (Name des Abschnitts) frei gewählt werden. Es muss
nur darauf geachtet werden, dass er eindeutig ist, also nur einmal vorkommt. Der Name der Instanz
sollte auch so gewählt werden, dass es zu keiner Namensgleichheit mit Top-Level Items kommt.

Es gibt folgende allgemeine Parameter im Abschnitt eines Plugins:

+------------------+-------------------------------------------------------------------------------------+
| Parameter        | Bedeutung                                                                           |
+==================+=====================================================================================+
| plugin_name      | Der Kurzname des Plugins, das eingebunden werden soll (Name des Verzeichnisses      |
|                  | im **../plugins** Verzeichnis). Statt des Parameters **plugin_name** konnten bisher |
|                  | auch die Parameter **class_name** und **class_path** angegeben werden.              |
|                  |                                                                                     |
|                  | **WICHTIG**: Bitte darauf achten, dass der Plugin Name Case-sensitive ist und der   |
|                  | Schreibweise des Verzeichnisnamens des Plugin entsprechen muss.                     |
+------------------+-------------------------------------------------------------------------------------+
| plugin_enabled   | Optional: Wenn dieser Parameter auf **False** gesetzt wird, wird das Plugin nicht   |
|                  | geladen, die Konfiguration bleibt jedoch erhalten und die Verwendung von Item-      |
|                  | Attributen dieses Plugins in den Itemkonfigurationen erzeugt keine Warnungen im Log.|
+------------------+-------------------------------------------------------------------------------------+
| class_name       | **DEPRECATED**: Name der Klasse in der Plugin Datei. Was hier einzutragen ist,      |
|                  | steht in der Dokumentation zum jeweiligen Plugin. Stattdessen ist die               |
|                  | Konfiguration über den Parameter **plugin_name** vorzunehmen.                       |
+------------------+-------------------------------------------------------------------------------------+
| class_path       | **DEPRECATED**: Pfad zur Plugin Datei. Was hier einzutragen ist, steht in der       |
|                  | Dokumentation zum jeweiligen Plugin. Stattdessen ist die Konfiguration  über den    |
|                  | Parameter **plugin_name** vorzunehmen.                                              |
+------------------+-------------------------------------------------------------------------------------+
| plugin_version   | Optional: Wenn im Plugin Repository mehrere Versionen eines Plugins zur Verfügung   |
|                  | stehen, kann über diesen Parameter eine andere als die neueste Version des Plugins  |
|                  | geladen werden. Dazu muss die Versionsnummer des Plugins angegeben werden.          |
|                  | (z.B.  **plugin_version: 1.4.9**)                                                   |
+------------------+-------------------------------------------------------------------------------------+
| instance         | Optional: Dieser Parameter muss nur verwendet werden, wenn mehrere Instanzen des    |
|                  | selben Plugins geladen werden sollen. Das Plugin selbst muss dazu **Multiinstance** |
|                  | fähig sein. Damit die Items der richtigen Plugin-Instanz zugeordnet werden, muss    |
|                  | in der jeweiligen Item Definition der Name des Plugin-spezifische Attributes um     |
|                  | die Angabe der Instanz ergänzt werden. Also z.B.: Statt **avm_data_type: uptime**   |
|                  | muss **avm_data_type@<instance>: uptime** geschrieben werden.                       |
+------------------+-------------------------------------------------------------------------------------+
| webif_pagelength | Optional: Anzahl an Tabellenreihen, die im Plugin Webinterface standardmäßig        |
|                  | pro Seite angezeigt werden sollen. Bei **-1** werden alle Einträge auf einer Seite  |
|                  | gezeigt, bei **0** so viele, dass sie genau auf die Seite ohne Scrolling passen.    |
|                  | Weitere mögliche Werte sind 25, 50, 100. Der hier angegebene Wert überschreibt den  |
|                  | für das **http Modul** im /etc/module.yaml File über den gleichnamigen Parameter    |                                                                            |
|                  | definierten globalen Wert.                                                          |
+------------------+-------------------------------------------------------------------------------------+


Die weiteren Einträge sind Plugin spezifisch. Welche Parameter ein Plugin kennt ist auch der
plugin.yaml Datei bzw. Doku des Plugins zu entnehmen. Je nach Plugin können sie verpflichtend oder
optional sein. Im obigen Beispiel sind sie alle (außer plugin_name) optional. Diese Parameter werden
beim Start von SmartHomeNG an das Plugin übergeben.

Ein **#** wirkt wie auch bei den Konfigurationsdateien der Items als Beginn eines Kommentars.



Multi-Instance Fähigkeit
========================

Es gibt Plugins, die so geschrieben sind, dass von ihnen mehrere Instanzen parallel geladen werden
können.

Wenn von solchen Plugins nur eine Instanz konfiguriert wird, ist nichts besonderes zu
beachten. Dann wird ein solches Plugin konfiguriert wie alle andern Plugins auch.

Wenn mehrere Instanzen eines Plugins konfiguriert werden, muss in der Konfiguration der Items
eine Information hinterlegt werden, auf welche Instanz des Plugins sich das Item bezieht. Dazu
**muss** jeder Instanz ein eindeutiger Name gegeben werden. Das erfolgt in der **../etc/plugin.yaml**
dadurch, dass jeder Instanz ein Parameter **instance** hinzugefügt wird:

.. code:: yaml

   fritzbox_1:
       plugin_name: avm
       instance: fb6360
       ...

   fritzbox_2:
       plugin_name: avm
       instance: fb7490
       ...


Außerdem muss jedem Item die Information mitgegeben werden, auf welche Instanz sich das Item bezieht:

.. code:: yaml

   wan:
       connection_status:
           type: str
           avm_data_type@fb7490: wan_connection_status


Wenn ein Item mehrere Attribute nutzt, die das Plugin zur Verfügung stellt, ist als Grundregel
jedes Attribut mit der **@<instance>** zu ergänzen.

Es kann sein, dass die Ergänzung eines einzelnen Attributes reicht. Das ist dann in der Doku
des jeweiligen Plugins beschrieben.



Liste der verfügbaren Plugins
=============================

Details zu den :doc:`existierenden Plugins <../../plugins_all>` finden sich :doc:`hier <../../plugins_all>` .
