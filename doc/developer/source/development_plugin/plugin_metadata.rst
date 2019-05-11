
.. index:: Metadata
.. index:: Plugin Metadata

.. role:: redsup
.. role:: bluesup

Plugin Metadata :bluesup:`update`
=================================

Plugins are configured in ``etc/plugin.yaml``. The parameters are described in the README.md
files of the plugins.


A plugin is made up of three files:

- The program code: __init__.py
- The metadata: plugin.yaml
- A short documentation: README.md

All three files reside in a folder within the ``/plugins`` folder. The name of the folder reflects
the name of the plugin.


The **metadata** file is named ``/plugins/<name of the plugin>/plugin.yaml``. It has three main sections:

- ``plugin:`` - Global metadata of the plugin
  The data defined in this section is used to check if the plugin works with the running version of SmartHomeNG, and defines
  how the plugin is loaded.

  The ``description:`` data is used to generate the plugin documentation pages within this documentation. Since this
  documentation is in english, the english description is read. If no english description is found, the german description
  is used.


- ``parameters:`` - Definition of the parameters that can bei used in ``/etc/plugin.yaml`` to configure the plugin
  The data defined in this section is used to check if configured parameters are valid.
  The data is going to be used:

  - for generating documentation pages (that way the parameter descriptions will not be needed in the README.md file)
  - for guiding users in a graphical configuration utility


- ``item_attributes:`` - Definition of the additional attributes for items, defined by this plugin
  The data defined in this section is used to check if configured item attributes are valid.
  The data is going to be used:

  - for generating documentation pages (that way the item attribute descriptions will not be needed in the README.md file)
  - for guiding users in a graphical configuration utility


- ``logic_parameters:`` - Definition of logic parameters that can bei used in ``/etc/logic.yaml`` to configure a logic.

  - for generating documentation pages (that way the parameter descriptions will not be needed in the README.md file)
  - for guiding users in a graphical configuration utility


- ``plugin_functions:`` - Definition of public functions, defined by this plugin
  The data defined in this section is used to check if configured item attributes are valid.
  The data is going to be used:

  - for generating documentation pages (that way the function descriptions will not be needed in the README.md file)
  - **in the future** for guiding users in a graphical configuration utility (e.g. code completion in the logic editor)




:Note: After the completion of the implementation of metadata for plugins, the following variables in the Python code of SmartPlugins need not be set anymore. They are read from the global metadata and are automatically set in the instance of the plugin:

    - ALLOW_MULTIINSTANCE
    - PLUGIN_VERSION

    The variable PLUGIN_VERSION should be set (even if it is not needed).
    If it is set, the version numbers defined in __init__.py and plugin.yaml are
    compared to ensure they match. If they don't match, an error is logged and the plugin is not loaded.


.. hint::

    To test the metadata in plugin.yaml use the tool ../tools/plugin_metadata_checker.py. This tool can check if the
    metadata is complete and free of errors.



If writing a core module, the metadata file has a section ``module:`` instead of the section ``plugin:``

The metadata file has the following sections:

.. toctree::
   :maxdepth: 3
   :titlesonly:

   /metadata/plugin_global
   /metadata/parameters
   /metadata/item_attributes
   /metadata/item_structs
   /metadata/logic_parameters
   /metadata/plugin_functions
   /metadata/module_global

