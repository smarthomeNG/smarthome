Core modules
============

There are loadable modules (SmartHomeNG modules) that can be used when developing plugins.
They implement additional functionality that is not implemented in the core itself.

Modules are configured in ``etc/modules.yaml``. The parameters are described in the README.md
files of the modules.

At the moment, the following modules exist:


.. toctree::
   :maxdepth: 3
   :titlesonly:

   /modules_doc/modules_readmes


A module is made up of two files:

- The program code: __init__.py
- The metadata: module.yaml

Both files reside in a folder within the ``/modules`` folder. The name of the folder reflects
the name of the module.

The **metadata** file is named ``/modules/<name of the module>/module.yaml``. It has two main sections:


- ``module:`` - Global metadata of the module
- ``parameters:`` - Definition of the parameters that can bei used in ``/etc/module.yaml`` to configure the module

.. include:: metadata/module_global.rst

.. include:: metadata/parameters.rst


If a module has requirements for a Python package that is not met by the standard Python installation, it has to be added
to the **requirements.txt** file in the modules' directory.
