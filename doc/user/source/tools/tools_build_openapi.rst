
.. index:: build_openapi
.. index:: Tools; build_openapi

build_openapi.py
================

Dieses Skript für Entwickler erzeugt die Beschreibung der REST API des Administrations-Interface
(``modules/admin/openapi.yaml``, OpenAPI 3.0). Die Beschreibung jeder Route steht als ``ApiDoc`` Metadaten direkt an
der Methode in ``modules/admin/api_*.py``, die die Route bedient. ``modules/admin/openapi.yaml`` wird nicht von Hand
bearbeitet, sondern nach einer Änderung der Routen neu erzeugt:

.. code::

   smarthome$ python3 tools/build_openapi.py
   File .../modules/admin/openapi.yaml created (77 operations across 64 paths).
