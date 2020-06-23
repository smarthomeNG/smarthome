Tools
=====

This gives an overview to the script collection in directory ``tools`` of SmartHomeNG

.. list-table::
   :header-rows: 1

   * - Tool
     - Purpose
   * - backup_restore.py
     - Backup and restore of your configuration (items, logics, etc) but not the databases or other directories
   * - build_requirements.py
     - Walking the core and plugins directories to collect all requirements.txt content into a base.txt and all.txt
   * - conf_to_yaml_converter.py
     - Convert the config files in old ``*.conf`` format into ``*.yaml`` equivalents


The following are marked as deprecated and if no working solution is found we will remove them. For the time being
they have been moved to ``/deprecated/tools``

.. list-table::
   :header-rows: 1

   * - Tool
     - Purpose
   * - conf2-1.0.sh
     - Update old ``+.conf`` files to new attributes (deprecated, only for informational purpose)
   * - ets4parser.py
     - Takes xml file from ETS4 export and creates a ``*.conf`` config file (origin 2012 Niko Will)
       See at `knx user forum - halbautomatischer ETS4 import <https://knx-user-forum.de/forum/supportforen/smarthome-py/22688-halbautomatischer-ets4-import>`_
       This tool is the older one but seems to need conversion to Python 3.x
   * - ga2conf.py
     - Takes xml file from ETS4 export and convert group addresses to a ``*.conf`` file
       See at `knx user forum - vollautomatischer ETS import <https://knx-user-forum.de/forum/supportforen/smarthome-py/28374-vollautomatischer-ets-import>`_
       This tool is the newer one but seems to need conversion to Python 3.x
   * - owmonitor.py
     - Monitors the uncached sensors of an installed owserver
   * - owsensors2items.py
     - Takes a list with Sensors and gives back a dict with items
   * - print_lib_versions.py
     - gives a list of installed modules with pip (This list can be looked at in the backend plugin)
   * - visu.manifest.sh
     - Seems to be used for a former visu approach (will be deleted)


.. toctree::
   :maxdepth: 2
   :titlesonly:

   /tools/backup_restore
   /tools/build_requirements 
   /tools/conf_to_yaml_converter
