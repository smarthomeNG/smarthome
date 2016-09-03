
=============
Configuration
=============


Directories
===========

In general the home directory of SmartHomeNG will be ``/usr/local/smarthome/``. 
There are several subdirectories which are explaned below

==========    ==========
directory     description
==========    ==========
bin           contains the core smarthome.py                                          
dev           development files
doc           some documentation files reside here (the pages just are just reading) 
etc           contains the main configuration files 
              (`smarthome.conf`_, `plugin.conf`_, `logic.conf`_ and `logging.yaml`_)

examples      contains some example files for the configuration and the visu plugin
items         should contain one or more `item configuration files`_ (ending with \*.conf)
lib           contains the core libraries of SmartHomeNG
logics        should contain the logic scripts (ends with \*.py)
plugins       contains the available plugins, one subdirectory for each plugin
scenes        scene files
tests         files to test the modules and its functions
tools         contains little programms helping to maintain and setup SmartHomeNG
var           contains subdirectories with remanent data, e.g.

              - cache/: contains cached item values
              - db/: contains the SQLite3 Database
              - log/: contains the logfiles
              - rrd/: contains the Round Robin Databases
==========    ==========



Config files in etc
===================

.. _`smarthome.conf`:

etc/smarthome.conf
------------------

To calculate sunrise and sunset, position of the sun you will need to tell where the installation is located.
Following attributes are supported in smarthome.conf

.. raw:: html

   <pre># /usr/local/smarthome/etc/smarthome.conf

   lat = 51.1633        # latitude
   lon = 10.4476        # longitude
   elev = 500           # elevation

   tz = 'Europe/Berlin' # timezone, the example will be fine for most parts of central Europe
   </pre>

.. _`logic.conf`:

etc/logic.conf
--------------

Logics within SmartHomeNG are just python scripts like the core, too. These scripts will be
placed in `/usr/local/smarthome/logics/`. To let SmartHomeNG know about when to start a script and which script to use then
it is needed to configure every logic in `logic.conf`:

.. raw:: html

   <pre># /usr/local/smarthome/etc/logic.conf
   [MyLogic]
       filename = logic.py
       crontab = init</pre>

With the examply above SmartHomeNG would look in /usr/local/smarthome/logics/ for the file
logic.py. The logic would be started - once - when the system starts.


.. _`plugin.conf`:

etc/plugin.conf
---------------

Plugins extend the core functionality of SmartHomeNG. The config files tells SmartHomeNG 
which plugin to use and which parameters to pass for the execution.

The ``plugins`` directory contains a subdirectory for every available plugin.
Plugins are configured in the ``plugin.conf`` file. 

This example there is a plugin for the knx bus to send and receive telegrams from eibd or knxd
and may be part plugin.conf:

.. raw:: html

   <pre># /usr/local/smarthome/etc/plugin.conf
      [knx]
         class_name = KNX
         class_path = plugins.knx
         host = 127.0.0.1
         port = 6720
      #   send_time = 600 # update date/time every 600 seconds, default none
      #   time_ga = 1/1/1 # default none
      #   date_ga = 1/1/2 # default none
   </pre>

The object name, class name and class path are mandatory. Other attributes 
needs to be specified as needed. There is a Readme for every plugin that gives the necessary
information. To continue reading follow the `plugin <plugin.html>`_ page.


.. _`logging.yaml`:

etc/logging.yaml
----------------

Logging was improved after the last release, see details at `logging <logging>`_.

.. _`item configuration files`:

items/\*.conf
-------------

The items represent the heart of the configuration. An item can be accessed from any logic, plugin or eval.
Any number of item configuration files may be used and any number of items may be defined (depends on your memory)

To find out more details about items and as well scenes continue reading the `items <items.html>`_ page.


SmartHomeNG start options
=========================

SmartHomeNG can be executed with the following options:

.. raw:: html

   <pre>
   <code>
   usage: smarthome.py [-h] [-v | -d | -i | -l | -s | -q | -V | --start]
   optional arguments:
     -h, --help         show this help message and exit
     -v, --verbose      DEPRECATED use logging.config (verbose (debug output)
                        logging to the logfile)
     -d, --debug        stay in the foreground with verbose output
     -i, --interactive  open an interactive shell with tab completion and with
                        verbose logging to the logfile
     -l, --logics       reload all logics
     -s, --stop         stop SmartHome.py
     -q, --quiet        DEPRECATED use logging config (reduce logging to the
                        logfile)
     -V, --version      show SmartHome.py version
     --start            start SmartHome.py and detach from console (default)
   </code>
   </pre>

Please be noted that due to the changed nature of logging the -v and -q options are deprecated and will be removed 
in a later release.