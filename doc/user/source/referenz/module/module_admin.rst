.. index:: Module; admin
.. index:: Administration Interface; admin Modul

.. role:: redsup
.. role:: bluesup

Modul admin
===========

Dieses Modul implementiert ein graphisches Administrations-Interface für SmartHomeNG. Das ermöglicht die
vollständige Konfiguration von SmartHomeNG.


API des Moduls
--------------

Im folgenden werden die einzelnen APIs beschrieben.


API des Moduls admin.rest
-------------------------

.. autoclass:: modules.admin.rest::RESTResource
    :noindex:

|

API des Moduls (WebApi)
-----------------------

.. autoclass:: modules.admin::WebApi
    :noindex:
    :show-inheritance:

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

