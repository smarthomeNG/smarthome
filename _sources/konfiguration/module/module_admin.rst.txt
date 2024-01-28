
.. index:: admin; Modul
.. index:: Module; admin
.. index:: Admin Modul; Konfigurationsdatei

.. role:: redsup
.. role:: bluesup

============
Module admin
============

Dieses Modul erlaubt es SmartHomeNG über einen Webbrowser zu konfigurieren. Voraussetzung ist, dass auch das Modul
http geladen und konfiguriert ist.


.. index:: Konfigurationsdateien; /etc/module.yaml (admin)

Konfiguration
=============

--------------------------
Datei *../etc/module.yaml*
--------------------------

.. code-block:: yaml
   :caption: ../etc/module.yaml

   # etc/module.yaml
   admin:
       module_name: admin
       # login_expiration: 168
       # login_autorenew: True
       # pypi_timeout: 5
       # itemtree_fullpath: True
       # itemtree_searchstart: 3
       # websocket_host: smarthomeng.local
       # websocket_port: 2424
       # log_chunksize: 1000
       # developer_mode: False
       # rest_dispatch_force_exception: False
       # click_dropdown_header: False


.. note::

    Die Konfigurationsparameter des admin Modules, die in dieser Datei konfiguriert werden, können auch über das graphische
    Administrations-Interface geändert werden.


+-------------------------------+------------------------------------------------------------------------------------------------+
| Parameter                     | Bemerkung                                                                                      |
+===============================+================================================================================================+
| login_expiration              | **Optional**: Gültigkeitsdauer des Tokens nach einem Login in Stunden (Nachkommastellen        |
|                               | können angegeben werden). Standard ist 168 -> eine Woche                                       |
+-------------------------------+------------------------------------------------------------------------------------------------+
| login_autorenew               | **Optional**: Bestehendes Login-Token automatisch verlängern.                                  |
+-------------------------------+------------------------------------------------------------------------------------------------+
| pypi_timeout                  | **Optional**: Anzahl Sekunden die auf eine Antwort von pypi.org gewartet wird.                 |
+-------------------------------+------------------------------------------------------------------------------------------------+
| itemtree_fullpath             | **Optional**: Falls dieser Parameter auf **True** gesetzt wird, werden auf der Item Seite im   |
|                               | Tree Items mit vollem Pfad angezeigt, fallse der Wert auf **False** gesetzt wird, wird die     |
|                               | Kurzform verwendet.                                                                            |
+-------------------------------+------------------------------------------------------------------------------------------------+
| itemtree_searchstart          | **Optional**: Anzahl Zeichen die eingegeben sein muss, damit die Suche im Itemtree startet.    |
|                               | Standardmäßig wird nach der Eingabe des dritten Zeichens mit der Suche begonnen.               |
+-------------------------------+------------------------------------------------------------------------------------------------+
| websocket_host                | **Optional**: IP Adresse für den websocket Zugriff.                                            |
+-------------------------------+------------------------------------------------------------------------------------------------+
| websocket_port                | **Optional**: Port der für den Websocket Zugriff verwendet wird.                               |
+-------------------------------+------------------------------------------------------------------------------------------------+
| log_chunksize                 | **Optional**: Größe der gelesenen Blöcke bei der Anzeige großer Logdateien.                    |
+-------------------------------+------------------------------------------------------------------------------------------------+
| developer_mode                | **Optional**: Entwickler Modus aktivieren (Ist für das Core Entwickler Team gedacht).          |
+-------------------------------+------------------------------------------------------------------------------------------------+
| rest_dispatch_force_exception | **Optional**: Sollen WARNINGs aus REST_dispatch_execute als EXECPTION geloggt werden?          |
+-------------------------------+------------------------------------------------------------------------------------------------+
| click_dropdown_header         | **Optional**: Click auf Kopfeintrag von Dropdown Menüs erlauben.                               |
+-------------------------------+------------------------------------------------------------------------------------------------+

