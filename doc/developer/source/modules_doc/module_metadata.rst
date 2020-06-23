Metadata for Modules
====================

Modules are configured in ``etc/module.yaml``. The parameters are described in the README.md
files of the modules.


A module is made up of three files:

- The program code: __init__.py
- The metadata: module.yaml
- A short documentation: README.md

All three files reside in a folder within the ``/modules`` folder. The name of the folder reflects
the name of the module.


The **metadata** file is named ``/modules/<name of the plugin>/module.yaml``. It has two main sections:

- ``module:`` - Global metadata of the plugin
- ``parameters:`` - Definition of the parameters that can bei used in ``/etc/plugin.yaml`` to configure the plugin

.. include:: /metadata/module_global.rst

.. include:: /metadata/parameters.rst

