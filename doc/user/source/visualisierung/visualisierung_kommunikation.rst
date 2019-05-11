##########################
Kommunikation mit der Visu
##########################

Die Kommunikation zwischen SmartHomeNG und der smartVISU wird auf Seite von SmartHomeNG durch 
das Plugin **visu_websocket** gesteuert. Auf Seite der smartVISU wird die Kommunikation über 
den Treiber **io_smarthome.py.js** abgewickelt. Dieser Treiber is in Javascript geschrieben 
und ermöglicht die Kommunikation des Browsers der die Visu anzeigt mit dem Websocket Plugin
von SmartHomeNG.

.. important::

   Die Kommunikation findet zwischen dem Browser und SmartHomeNG statt, NICHT zwischen dem
   Webserver und SmartHomeNG. Der Webserver liefert nur den statischen Kontent der Visu aus. 

Das Plugin **visu_websocket** muss in **../etc/plugin.yaml** konfiguriert werden.

.. code-block:: yaml
   :caption: Ausschnitt aus **../etc/plugin.yaml**

   websocket:
       class_name: WebSocket
       class_path: plugins.visu_websocket
   #    plugin_name: visu_websocket
   #    ip: 0.0.0.0
   #    port: 2424
   #    tls: no
   #    wsproto: 4
       acl: rw

+-------------+-----------------------------------------------------------------------------------+
| Parameter   | Beschreibung                                                                      |
+=============+===================================================================================+
| class_name  | class_name muss wie im obigen Beispiel angegeben werden. Kann ab SmartHomeNG v1.4 |
|             | durch den Parameter plugin_name ersetzt werden.                                   |
+-------------+-----------------------------------------------------------------------------------+
| class_path  | class_path muss wie im obigen Beispiel angegeben werden. Kann ab SmartHomeNG v1.4 |
|             | durch den Parameter plugin_name ersetzt werden.                                   |
+-------------+-----------------------------------------------------------------------------------+
| ip          | Muss normalerweise nicht angegeben werden. Hiermit wird für Computer mit mehreren |
|             | ip Adressen festgelegt, auf welcher Adresse das Plugin hört. Wenn ip nicht        |
|             | angegeben ist, hört das Plugin auf allen ip Adressen des Computers.               |
+-------------+-----------------------------------------------------------------------------------+
| port        | Muss normalerweise nicht angegeben werden. Hiermit wird festgelegt auf welchem    |
|             | Port das Plugin hört. Wenn der Parameter nicht angegeben wird, hört das Plugin    |
|             | auf Port 2424.                                                                    |
+-------------+-----------------------------------------------------------------------------------+
| tls         | Muss normalerweise nicht angegeben werden. Wenn tls auf yes gesetzt wird,         |
|             | kommuniziert das Plugin verschlüsselt. Dazu müssen im Verzeichnis **../etc**      |
|             | gültige Zertifikatdateien **home.crt**, **home.key** und **ca.crt** abgelegt      |
|             | werden.                                                                           |
+-------------+-----------------------------------------------------------------------------------+
| wsproto     | Spezifiziert die Protokoll Version der Websocket Kommunikation zwischen smartVISU |
|             | und SmartHomeNG. Wird der Parameter nicht angegeben, wird **wsproto: 4** genutzt. |
|             | Es ist nur notwendig diesen Parameter anzugeben, wenn man noch smartVISU v2.7     |
|             | nutzt. Dann muss **wsproto: 3** angegeben werden.                                 |
+-------------+-----------------------------------------------------------------------------------+
| acl         | Mit dem Parameter **Accesscontrol list** kann eine generelle Voreinstellung für   |
|             | den Zugriff der Visu auf Items vorgenommen werden. Wenn im Item kein Attribut     |
|             | **acl:** gesetzt ist, wird die Einstellung dieses Parameters genutzt. Mögliche    |
|             | Werte sind **ro** (Read Only) und **rw** (Read/Write)                             |
+-------------+-----------------------------------------------------------------------------------+


.. toctree::
   :maxdepth: 4
   :hidden:
   :titlesonly:

   reverse_proxy
