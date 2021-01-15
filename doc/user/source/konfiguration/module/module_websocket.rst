
.. index:: websocket; Modul
.. index:: Module; websocket
.. index:: websocket; Konfiguration

.. role:: redsup
.. role:: bluesup

==============================
Module websocket :redsup:`Neu`
==============================

Dieses Modul erlaubt es SmartHomeNG über das Websocket Protokoll zu kommunizieren. Auf dem Websocket Protokoll
setzt z.B. das Nutzdaten Protokoll für die Kommunikation mit der smartVISU auf.

Es wird sowohl das unverschlüsselte (ws://) Protokoll unterstützt, als auch die verschlüsselte Variante (wss://). Beide
Varianten können parallel genutzt werden.


Anforderungen
=============

Dieses Modul läuft unter SmartHomeNG v1.8 und neuer und benötigt Python in der Version 3.6 oder neuer.


.. index:: Konfigurationsdateien; /etc/module.yaml (websocket)

Konfiguration
=============

--------------------------
Datei *../etc/module.yaml*
--------------------------

.. code-block:: yaml
   :caption: ../etc/module.yaml

   # etc/module.yaml
   websocket:
       module_name: websocket
       # tls_key: myprivate.key
       # use_tls: true
       # tls_cert: myprivate.pem
       # port: 2424
       # tls_port: 2425


.. note::

    Die Konfigurationsparameter des websocket Modules die in dieser Datei konfiguriert werden, können auch über das
    graphische Administrations-Interface geändert werden.


+-------------------------+------------------------------------------------------------------------------------------------------+
| Parameter               | Bemerkung                                                                                            |
+=========================+======================================================================================================+
| enabled                 | Websocket Unterstützung aktivieren (True) oder deaktivieren (False) - Standardwert ist True          |
+-------------------------+------------------------------------------------------------------------------------------------------+
| ip                      | IP Adresse auf der das websocket Modul aktiv sein soll - muss normalerweise nicht angegeben werden   |
+-------------------------+------------------------------------------------------------------------------------------------------+
| port                    | **Optional**: Der Port auf welchem SmartHomeNG unverschlüsselte Websocket Kommunikation erwartet     |
|                         | Standard Port ist **2424** .                                                                         |
+-------------------------+------------------------------------------------------------------------------------------------------+
| tls_port                | **Optional**: Der Port auf welchem SmartHomeNG verschlüsselte Websocket Kommunikation erwartet       |
|                         | Standard Port ist **2425** .                                                                         |
+-------------------------+------------------------------------------------------------------------------------------------------+
| use_tls                 | **Optional**: Muss auf True gesetzt werden, um verschüsselte Kommunikation zu aktivieren.            |
|                         | Für die verschlüsselte Kommunikation müssen die Zertifikats- und Schlüssel-Datei konfiguriert sein.  |
+-------------------------+------------------------------------------------------------------------------------------------------+
| tls_cert                | **Optional**: Name der Zertifikatsdatei mit der Endung '.cer' oder '.pem'. Die Datei muss im         |
|                         | Verzeichnis ../etc liegen. Dieser Parameter muss konfiguriert sein, damit eine verschlüsselte        |
|                         | Kommunikation möglich ist.                                                                           |
+-------------------------+------------------------------------------------------------------------------------------------------+
| tls_key                 | **Optional**: Name der Datei mit dem privaten Schlüssel und der Endung '.key'. Die Datei muss im     |
|                         | Verzeichnis ../etc liegen. Dieser Parameter muss konfiguriert sein, damit eine verschlüsselte        |
|                         | Kommunikation möglich ist.                                                                           |
+-------------------------+------------------------------------------------------------------------------------------------------+
