
.. index:: Module; Konfiguration

.. role:: redsup
.. role:: bluesup

======
Module
======

Module stellen Core Funktionalitäten von SmartHomeNG zur Verfügung. Da diese Funktionalitäten
einen größeren Ressourcen Bedarf haben, sind sie als ladbare Module ausgeführt. Dadurch ist
es möglich auf leistungsschwachen Systemen SmartHomeNG einzusetzen. Man muss nur auf den Einsatz
der ladbaren Module verzichten.

Einige Plugins benötigen die Features von Modulen. Diese Plugins können ohne die benötigten
Module nicht genutzt werden oder stellen nur einen eingeschränkten Funktionsumfang zur Verfügung.
So ist zum Beispiel der Einsatz des Plugins **Backend** ohne das geladene Modul **http** nicht
möglich.


.. note::

    Die Konfigurationsparameter der Module **http**, **admin** und **mqtt**, die in der Datei **../etc/module.yaml**
    konfiguriert werden, können auch über das graphische Administrations-Interface geändert werden.



.. toctree::
   :maxdepth: 4
   :hidden:

   module_http
   module_websocket
   module_admin
   module_mqtt

