
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
Datei *etc/module.yaml*
--------------------------

.. code-block:: yaml
   :caption: etc/module.yaml

   # etc/module.yaml
   admin:
       module_name: admin
       # login_expiration: 48
       # login_autorenew: True
       # itemtree_fullpath: True
       # itemtree_searchstart: 2
       # websocket_host: smarthomeng.local
       # websocket_port: 2424
       # log_chunksize: 1000
       # developer_mode: False
       # rest_dispatch_force_exception: False
       # click_dropdown_header: False
       # dark_mode: False
       # resource_graph_period: '24h'
       # start_page: dashboard


.. note::

    Die Konfigurationsparameter des admin Modules, die in dieser Datei konfiguriert werden, können auch über das graphische
    Administrations-Interface geändert werden.


+-------------------------------+------------------------------------------------------------------------------------------------+
| Parameter                     | Bemerkung                                                                                      |
+===============================+================================================================================================+
| login_expiration              | **Optional**: Gültigkeitsdauer des Tokens nach einem Login in Stunden (Nachkommastellen        |
|                               | können angegeben werden). Standard ist 48 -> zwei Tage                                         |
+-------------------------------+------------------------------------------------------------------------------------------------+
| login_autorenew               | **Optional**: Bestehendes Login-Token automatisch verlängern.                                  |
+-------------------------------+------------------------------------------------------------------------------------------------+
| itemtree_fullpath             | **Optional**: Falls dieser Parameter auf **True** gesetzt wird, werden auf der Item Seite im   |
|                               | Tree Items mit vollem Pfad angezeigt, fallse der Wert auf **False** gesetzt wird, wird die     |
|                               | Kurzform verwendet.                                                                            |
+-------------------------------+------------------------------------------------------------------------------------------------+
| itemtree_searchstart          | **Optional**: Anzahl Zeichen die eingegeben sein muss, damit die Suche im Itemtree startet.    |
|                               | Standardmäßig wird nach der Eingabe des zweiten Zeichens mit der Suche begonnen.               |
+-------------------------------+------------------------------------------------------------------------------------------------+
| websocket_host                | **VERALTET**: IP Adresse für den websocket Zugriff - bitte im Websocket-Modul konfigurieren.   |
+-------------------------------+------------------------------------------------------------------------------------------------+
| websocket_port                | **VERALTET**: Port der für den Websocket Zugriff verwendet wird - bitte im Websocket-Modul     |
|                               | konfigurieren.                                                                                 |
+-------------------------------+------------------------------------------------------------------------------------------------+
| log_chunksize                 | **Optional**: Größe der gelesenen Blöcke bei der Anzeige großer Logdateien.                    |
+-------------------------------+------------------------------------------------------------------------------------------------+
| developer_mode                | **Optional**: Entwickler Modus aktivieren (Ist für das Core Entwickler Team gedacht).          |
+-------------------------------+------------------------------------------------------------------------------------------------+
| rest_dispatch_force_exception | **Optional**: Sollen WARNINGs aus REST_dispatch_execute als EXECPTION geloggt werden?          |
+-------------------------------+------------------------------------------------------------------------------------------------+
| click_dropdown_header         | **Optional**: Click auf Kopfeintrag von Dropdown Menüs erlauben.                               |
+-------------------------------+------------------------------------------------------------------------------------------------+
| dark_mode                     | **Optional**: Dark Mode als Standard für das Administrations-Interface aktivieren (kann pro    |
|                               | Browser über den Schalter in der Navigationsleiste übersteuert werden). Standard ist **False**.|
+-------------------------------+------------------------------------------------------------------------------------------------+
| resource_graph_period         | **Optional**: Zeitraum, den die Ressourcen-Graphen (Systemeigenschaften) initial anzeigen, z.B.|
|                               | ``1h``, ``6h``, ``24h``. Standard ist **24h**.                                                 |
+-------------------------------+------------------------------------------------------------------------------------------------+
| start_page                    | **Optional**: Seite, die nach dem Login im Administrations-Interface angezeigt wird. Standard  |
|                               | ist **dashboard**.                                                                             |
+-------------------------------+------------------------------------------------------------------------------------------------+

