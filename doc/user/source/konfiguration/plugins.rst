=======
Plugins
=======

Das Grundsystem von SmartHomeNG kann durch den Einsatz von Plugins erweitert werden. Ein Plugin
ist ein Zusatzmodul in einem Unterverzeichnis unterhalb des Verzeichnisses ``plugins``.
Um ein Plugin in SmartHomeNG zu verwenden (eine Instanz des Plugins zu laden) muss eine Sektion
für das gewünschte Plugin in der Datei ``etc/plugin.yaml`` erstellt werden.

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


Dabei kann der Name der **Plugin-Instanz** (Name des Abschnitts) frei gewählt werden. Es muss
nur darauf geachtet werden, dass er eindeutig ist, also nur einmal vorkommt. Der Name der Instanz
sollte auch so gewählt werden, dass es zu keiner Namensgleichheit mit Top-Level Items kommt.

Es gibt folgende allgemeine Parameter im Abschnitt eines Plugins:

+------------------+-------------------------------------------------------------------------------------+
| Parameter        | Bedeutung                                                                           |
+==================+=====================================================================================+
| plugin_name      | Der Kurzname des Plugins, das eingebunden werden soll (Name des Verzeichnisses      |
|                  | im ``../plugins`` Verzeichnis).                                                     |
|                  |                                                                                     |
|                  | **WICHTIG**: Bitte darauf achten, dass der Plugin Name Case-sensitive ist und der   |
|                  | Schreibweise des Verzeichnisnamens des Plugin entsprechen muss.                     |
+------------------+-------------------------------------------------------------------------------------+
| plugin_enabled   | Optional: Wenn dieser Parameter auf **False** gesetzt wird, wird das Plugin nicht   |
|                  | geladen, die Konfiguration bleibt jedoch erhalten und die Verwendung von Item-      |
|                  | Attributen dieses Plugins in den Itemkonfigurationen erzeugt keine Warnungen im Log.|
+------------------+-------------------------------------------------------------------------------------+
| plugin_version   | Optional: Wenn im Plugin Repository mehrere Versionen eines Plugins zur Verfügung   |
|                  | stehen, kann über diesen Parameter eine andere als die neueste Version des Plugins  |
|                  | geladen werden. Dazu muss die Versionsnummer des Plugins angegeben werden.          |
|                  | (z.B.  **plugin_version: 1.4.9**)                                                   |
+------------------+-------------------------------------------------------------------------------------+
| instance         | Optional: Nur der Wert **default** wird ausgewertet. Er legt fest, dass diese       |
|                  | Instanz den leeren Instanzbezeichner erhält (für Item-Attribute ohne                |
|                  | Instanzangabe).                                                                     |
+------------------+-------------------------------------------------------------------------------------+
| default_instance | Optional: Legt fest, welche Instanz von mehreren den leeren Instanzbezeichner       |
|                  | erhält (für Item-Attribute ohne Instanzangabe). Die Angabe des Parameters genügt,   |
|                  | z.B. **default_instance: true**.                                                    |
+------------------+-------------------------------------------------------------------------------------+
| webif_pagelength | Optional: Anzahl an Tabellenreihen, die im Plugin Webinterface standardmäßig        |
|                  | pro Seite angezeigt werden sollen. Bei **-1** werden alle Einträge auf einer Seite  |
|                  | gezeigt, bei **0** so viele, dass sie genau auf die Seite ohne Scrolling passen.    |
|                  | Weitere mögliche Werte sind 25, 50, 100. Der hier angegebene Wert überschreibt den  |
|                  | für das **http Modul** im ``/etc/module.yaml`` File über den gleichnamigen Parameter|
|                  | definierten globalen Wert.                                                          |
+------------------+-------------------------------------------------------------------------------------+


.. note::

    Wird dasselbe Plugin mehrfach eingebunden, ist der Name des jeweiligen Abschnitts in der ``plugin.yaml``
    der Instanzbezeichner. Item-Attribute werden dann um diesen Bezeichner ergänzt, also z.B.
    **avm_data_type@<abschnittsname>: uptime**. Mit **legacy_instances: true** in der ``etc/smarthome.yaml``
    gilt wieder das bis SmartHomeNG 1.12 übliche Verfahren, bei dem der Instanzname aus dem Parameter
    **instance** gelesen wird.


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
**muss** jeder Instanz ein eindeutiger Name gegeben werden. Das ist der Name des Abschnitts in der
``etc/plugin.yaml``:

.. code:: yaml

   fb6360:
       plugin_name: avm
       ...

   fb7490:
       plugin_name: avm
       ...


Außerdem muss jedem Item die Information mitgegeben werden, auf welche Instanz sich das Item bezieht:

.. code:: yaml

   wan:
       connection_status:
           type: str
           avm_data_type@fb7490: wan_connection_status

Items ohne Instanzangabe gehören zu der Instanz, die den leeren Instanzbezeichner hat. Welche das ist,
wird mit dem Parameter **default_instance** (oder **instance: default**) festgelegt.


Wenn ein Item mehrere Attribute nutzt, die das Plugin zur Verfügung stellt, ist als Grundregel
jedes Attribut mit der **@<instance>** zu ergänzen.

Es kann sein, dass die Ergänzung eines einzelnen Attributes reicht. Das ist dann in der Doku
des jeweiligen Plugins beschrieben.



Liste der verfügbaren Plugins
=============================

Details zu den :doc:`existierenden Plugins <../../plugins_all>` finden sich :doc:`hier <../../plugins_all>` .
