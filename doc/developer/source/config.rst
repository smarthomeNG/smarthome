
=============
Configuration
=============

------------------------
Structure of SmartHomeNG
------------------------

After the base system is installed a closer look at the SmartHomeNG directory
(e.g. ``/usr/local/smarthome/``) is advised to learn something about its content:

.. code-block:: bash
   :emphasize-lines: 6,8,10

   # directories
   bin            contains smarthome.py, the main application
   deprecated     contains deprecated tools, which will be removed in an upcoming release of SmartHomeNG
   dev            development files like a sample plugin
   doc            the documentation of the project resides here
   etc            should contain the basic configuration files (smarthome.yaml, plugin.yaml, logic.yaml)
   examples       contains some example files for the configuration and the visu plugin
   items          should contain one or more item configuration files.
   lib            contains the core libraries of SmartHomeNG
   logics         should contain the logic scripts
   media          contains logos of SmartHomeNG
   modules        loadable core modules. These modules extend the functionality of the core
   plugins        contains the available plugins
   requirements   you will find the requirements file here for the core and all plugins
   scenes         scene files
   tests          contains the test environment with tests and test data
   tools          contains little programs helping to maintain SmartHomeNG
   var            its subdirectories contain various collected data
   var/cache      contains cached item values
   var/db         may contain a SQLite3 database
   var/log        contains the logfiles
   var/rrd        may contain a Round Robin Databases if rrd plugin is used (deprecated)

   # files
   CHANGELOG.md   changes of this project. (deprecated, should be documented in doc)
   LICENSE        GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007)
   README.md      a general information
   setup.py       not functional right now
   tox.ini        used for software testing

Important for configuration are the directories ``etc``, ``items`` and ``logics``.
Those are the locations were configuration is stored and maintained.
The following discusses how these directories are populated.


---------------------------------
Config files in directory **etc**
---------------------------------

The configuration is done by the widespread `yaml <https://en.wikipedia.org/wiki/YAML>`_ format.
Older versions used `configobj <http://www.voidspace.org.uk/python/articles/configobj.shtml>`_ file format 
which is like a well-known `ini-file <https://en.wikipedia.org/wiki/INI_file>`_ but with the ability to create multilevel sub-sections.
It is still supported in SmartHomeNG but it is deprecated
for a while and was removed from documentation.

If the backend-plugin is configured then a service can be used to
convert old ``*.conf`` configuration snippets into ``*.yaml`` format.

There is furthermore a service tool located at ``tools/conf_to_yaml_converter.py``
that can be used to convert your whole configuration.
Please have a look at :doc:`tools`.


.. _`smarthome.yaml`:

smarthome.yaml
==============

To calculate sunrise, sunset, azimuth and elevation of the sun for a given time the coordinates of the physical location
of the SmartHomeNG installation is needed.

Create a new ``smarthome.yaml`` within ``etc/`` or copy the given ``smarthome.yaml.default``
to ``smarthome.yaml`` and edit it to your needs. It should look like the following:

.. code-block:: yaml
   :caption: smarthome.yaml

   lat: 51.1633         # latitude
   lon: 10.4476         # longitude
   elev: 500            # elevation
   tz: Europe/Berlin    # timezone, the example will be fine for most parts of central Europe
   default_language: de # default language for use with the backend plugin and multi-language entries in metadata

The coordinates can be found out by using GPS of a mobile or via an adequate website (e.g. http://www.mapcoordinates.net/)



.. _`plugin.yaml`:

plugin.yaml
===========

Plugins extend the core functionality of SmartHomeNG.
The ``plugins`` directory contains a subdirectory for every available plugin.
The file ``etc/plugin.yaml`` holds the configuration for every plugin to be used during runtime.

For each plugin at least the plugin object name is needed and the
attributes where to find the plugin and how to expect the classname to be.

The example below configures a plugin for the KNX bus to send and receive telegrams from and to eibd or knxd (both a software gateway to the KNX hardware bus).
In this case the object name is ``knx``, the place to look for the module is within subdirectory ``plugins/knx/`` and the class of the plugin is ``KNX``.
The object name can be any valid Python name, the class name and class path need to match those of the plugin.

.. code-block:: yaml
   :caption: plugin.yaml

   knx:
       plugin_name: knx
       # class_name: KNX           # old way of configuration
       # class_path: plugins.knx   # old way of configuration
       host: 127.0.0.1
       port: 6720
       # send_time; 600 # update date/time every 600 seconds, default none
       # time_ga: 1/1/1 # default none
       # date_ga: 1/1/2 # default none

There is a `README.md` for every plugin that gives the necessary configuration information.
To continue reading follow the :doc:`plugin <plugins_all>` page.


Referencing a plugin in the configuration
-----------------------------------------

Up to SmartHomeNG v1.3 a plugin had to be referenced by the parameters ``class_name`` and ``class_path``.
**Now it is possible** to reference it alone by specifying the parameter ``plugin_name``, where
the value would be the former class_path without the `plugins.` prefix. Since all plugins are
located in the ``/plugins`` folder, the `plugins.` is redundant information.

If the plugin comes with a metadata definition (what almost all plugins do), there is no need so specify
the ``class_name`` parameter. This information is retrieved from the metadata.

.. Note::

   As standard the parameter **plugin_name** should be used when configuring plugins.

   Only is the need arises to configure a plugin that is located outside the ``../plugins`` folder, **class_path** should be used.

   The parameter **class_name** shouldn't be used any more, since the name of the plugin's class is defined in the metadata file



Using an older version of a plugin
----------------------------------

If you are not using the newest version of the SmartHomeNG core, if may be necessary to use an
older version of a plugin. Some plugins come with embedded older versions. To load an older
version of the plugin, you have to specify the parameter `plugin_version` in the configuration
section of the plugin.

To find out, if a plugin comes with an older version (or versions), take a look at the plugin's
directory. if you find a subdirectory with the name starting with ``_pv_`` the plugin comes with
an older (previous) version. The rest of the folder name specifies the version number. If you
find a subfolder ``_pv_1_3_0``, it contains the v1.3.0 of the plugin. To load that version, just
add ``plugin_version: 1.3.0`` to the plugin configuration.



.. _`logic.yaml`:

logic.yaml
==========

Logics within SmartHomeNG are just Python scripts like the core, too. These scripts will be
placed in `/usr/local/smarthome/logics/`. To let SmartHomeNG know about when to start a script and which script to use then
it is needed to configure every logic script in `logic.yaml`:


.. code-block:: yaml
   :caption: logic.yaml

   MyLogic:
       filename: logic.py
       crontab: init

With the example above SmartHomeNG would look in ``/usr/local/smarthome/logics/`` for the file
``logic.py``. The logic would be started - once - when SmartHomeNG starts.



.. _`logging.yaml`:

logging.yaml
============

The core and also every module is able to output logging information.
The logging can be configured to be rich in detail for debugging purposes or rather smart with warning or general info.
There is a separate document to explain how to configure :doc:`logging <logging>`.
To get started, simply copy the given ``logging.yaml.default``
to ``logging.yaml`` and edit it to your needs. It should look like the following:

.. literalinclude:: ../../../etc/logging.yaml.default
   :caption: logging.yaml
   :language: yaml

See further details at :doc:`logging <logging>`.

.. _`item configuration files`:


---------------------------------------
Item definitions in directory **items**
---------------------------------------


The items represent the heart of the configuration. An item can be accessed from any logic, plugin or eval.
Any number of item configuration files may be used and any number of items may be defined (depends on your memory) in one of these files.

This directory contains yaml files with the definitions of the items SmartHomeNG can use. The yaml files can be named
the way you want.

To find out more details about items and scenes configuration continue reading the :doc:`items <items>` page.


-----------------------------------------
Logic definitions in directory **logics**
-----------------------------------------

This directory contains logics you write, which are used by SmartHomeNG. A logic is basically a file
of Python code. It has some additional conventions. When and how the logic is executed is configured
in the file `etc/logics.yaml`.

When using the Blockly Plugin to write a logic, the logic has two files. One is the Blockly code with the
extension `.blockly` and one file with the Python code. That file has the extension `.py`.

To find out more details about logics continue reading the :doc:`logics <logics>` page.


-------------------------
SmartHomeNG start options
-------------------------

SmartHomeNG can be executed with the following options:

.. code-block:: bash

   usage: smarthome.py [-h] [-v | -d | -i | -l | -s | -q | -V | --start]
   optional arguments:
     -h, --help         show this help message and exit
     -v, --verbose      DEPRECATED use logging.config (verbose (debug output)
                        logging to the logfile)
     -d, --debug        stay in the foreground with verbose output
     -i, --interactive  open an interactive shell with tab completion and with
                        verbose logging to the logfile
     -l, --logics       reload all logics
     -s, --stop         stop SmartHomeNG
     -q, --quiet        DEPRECATED use logging config (reduce logging to the
                        logfile)
     -V, --version      show SmartHomeNG version
     --start            start SmartHomeNG and detach from console (default)

If you start SmartHomeNG without any option, then SmartHomeNG will return the PID if already running.

Please be noted that due to the changed nature of logging
the -v and -q options are deprecated and will be removed
in a later release.
