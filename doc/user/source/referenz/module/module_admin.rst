.. index:: Module; admin
.. index:: Administration Interface; admin Modul

.. role:: redsup
.. role:: bluesup

Modul admin
===========

Dieses Modul implementiert ein graphisches Administrations-Interface für SmartHomeNG. Das ermöglicht die
vollständige Konfiguration von SmartHomeNG.

Das Modul implementiert eine Reihe von REST Interfaces, die vom "Web Interface", einer Angular Applikation genutzt
werden um die Daten im Browser anzuzeigen bzw. zu manipulieren. Das Web Interface wird über das http Modul bereit
gestellt, wie es auch bei den Web Interfaces der Plugins der Fall ist.


API des Moduls
--------------

Im folgenden werden die einzelnen APIs des Moduls beschrieben.


API des Moduls admin.rest
-------------------------

RESTResource ist die Grundlegende Klasse um REST Interfaces über das im http Modul verwendete CherryPy zur
Verfügung zu stellen.

.. autoclass:: modules.admin.rest::RESTResource
    :noindex:

|

API des Moduls api_plugins
--------------------------

.. automodule:: modules.admin.api_plugins
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

|

API des Moduls api_plugin
-------------------------

.. automodule:: modules.admin.api_plugin
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

|

API des Moduls (WebApi)
-----------------------

.. autoclass:: modules.admin::WebApi
    :noindex:
    :show-inheritance:

|

README
------

.. literalinclude:: /modules/admin/README.md
    :caption: README


Metadaten
---------

Auskommentierte Parameter in den Metadaten sind noch nicht implementiert. Die Implementierung dieser Parameter
wird im Rahmen der Weiterentwicklung von SmartHomeNG erfolgen:

.. literalinclude:: /modules/admin/module.yaml
    :caption: module.yaml

