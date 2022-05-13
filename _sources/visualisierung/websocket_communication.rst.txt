
Websocket Kommunikation
=======================

Die Kommunikation zwischen SmartHomeNG und der smartVISU wird auf Seite von SmartHomeNG durch
das Modul **websocket** gesteuert. Auf Seite der smartVISU wird die Kommunikation über
den Treiber **io_smarthome.py.js** abgewickelt. Dieser Treiber is in Javascript geschrieben
und ermöglicht die Kommunikation des Browsers der die Visu anzeigt mit dem Websocket Plugin
von SmartHomeNG.

.. important::

   Die Kommunikation findet zwischen dem Browser und SmartHomeNG statt, NICHT zwischen dem
   Webserver und SmartHomeNG. Der Webserver liefert nur den statischen Kontent der Visu aus.

Das Modul **websocket** muss in **../etc/module.yaml** konfiguriert werden.

.. code-block:: yaml
   :caption: Ausschnitt aus **../etc/module.yaml**

   websocket:
       module_name: websocket
   #    ip: 0.0.0.0
   #    port: 2424
   #    tls_port: 2425
   #    use_tls: True
   #    tls_cert: shng.cer
   #    tls_key: shng.key
   #    sv_enabled: True
   #    sv_acl: ro
   #    sv_querydef: False


+-------------+-----------------------------------------------------------------------------------+
| Parameter   | Beschreibung                                                                      |
+=============+===================================================================================+
| module_name | Referenziert das gewählte Modul (hier **websocket**).                             |
+-------------+-----------------------------------------------------------------------------------+
| ip          | Muss normalerweise nicht angegeben werden. Hiermit wird für Computer mit mehreren |
|             | ip Adressen festgelegt, auf welcher Adresse das Modul hört. Wenn ip nicht         |
|             | angegeben ist, hört das Plugin auf allen ip Adressen des Computers.               |
+-------------+-----------------------------------------------------------------------------------+
| port        | Muss normalerweise nicht angegeben werden. Hiermit wird festgelegt auf welchem    |
|             | Port das Modul hört (ws://). Wenn der Parameter nicht angegeben wird, hört das    |
|             | Modul auf Port 2424.                                                              |
+-------------+-----------------------------------------------------------------------------------+
| tls_port    | Muss normalerweise nicht angegeben werden. Hiermit wird festgelegt auf welchem    |
|             | Port das Modul für verschlüsselte Kommunikation (wss://) hört. Wenn der Parameter |
|             | nicht angegeben wird, hört das Modul auf Port 2425.                               |
+-------------+-----------------------------------------------------------------------------------+
| use_tls     | Muss normalerweise nicht angegeben werden. Wenn use_tls auf True gesetzt wird,    |
|             | wird die verschlüsselte Kommunikation über **tls_port** aktiviert. Dazu müssen    |
|             | im Verzeichnis **../etc** gültige Zertifikatdateien **shng.cer** und **shng.key** |
|             | abgelegt werden.                                                                  |
+-------------+-----------------------------------------------------------------------------------+
| tls_cert    | Muss normalerweise nicht angegeben werden. Hiermit wird der Name der Zertifikat-  |
|             | Datei festgelegt. Wird kein Name angegeben, wird **shng.cer** verwendet.          |
+-------------+-----------------------------------------------------------------------------------+
| tls_key     | Muss normalerweise nicht angegeben werden. Hiermit wird der Name der Datei mit    |
|             | dem privaten Schlüssel festgelegt. Wird kein Name angegeben, wird **shng.key**    |
|             | verwendet.                                                                        |
+-------------+-----------------------------------------------------------------------------------+
| sv_enabled  | Muss normalerweise nicht angegeben werden. Hiermit wird festgelegt, ob das        |
|             | Nutzdaten Protokoll für die smartVISU aktiviert ist. Standardmäßig ist das        |
|             | smartVISU Nutzdaten-Protokoll aktiviert.                                          |
+-------------+-----------------------------------------------------------------------------------+
| sv_acl      | Mit dem Parameter **Accesscontrol list** kann eine generelle Voreinstellung für   |
|             | den Zugriff der smartVISU auf Items vorgenommen werden. Wenn im Item kein         |
|             | Attribut **acl:** gesetzt ist, wird die Einstellung dieses Parameters genutzt.    |
|             | Mögliche Werte sind **deny**, **ro** (Read Only) und **rw** (Read/Write).         |
|             | Wird dieser Parameter nicht angegeben, wird als Standardeinstellung **ro**        |
|             | verwendet.                                                                        |
+-------------+-----------------------------------------------------------------------------------+
| sv_querydef | Dieser Parameter ist für eine zukündftige Erweiterung der smartVISU gedacht und   |
|             | muss aktuell nicht angegeben werden. Wird der Parameter auf **True** gesetzt,     |
|             | ermöglicht dies die Abfrage der definierten Items (mit einem Teil ihrer           |
|             | Attribute) und die Abfrage der definierten Logiken.                               |
+-------------+-----------------------------------------------------------------------------------+

