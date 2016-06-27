Installation
============

Requirements
------------

Operating System
~~~~~~~~~~~~~~~~

-  OS: Any Linux or Unix System should be fine. This Guide assumes
   any recent Debian oder Ubuntu based Distribution.
-  Time Syncronisation via NTP or systemd-timesyncd is recommended

Python
~~~~~~

We require Python >= 3.2 and some typical development Tools
for successfull deployment:

- Python with Development Headers
- pip, the Python Package Manager
- virtualenv, the Python Virtual Environment

On any Debian/Ubuntu based Distribution this means at least this Packages:

.. code-block:: bash

   $ sudo apt-get install python3 python3-dev python3-pip python-virtualenv


Installation
------------

For security reasons it is recommended to create an dedicated user account for smarthome.py. On
most Linux Distributions this can be done via:

.. code-block:: bash

   $ sudo adduser smarthome

Stable Release
~~~~~~~~~~~~~~

At
`https://github.com/smarthomeng/smarthome/releases <https://github.com/smarthomeng/smarthome/releases>`_
you find the latest release.

.. code-block:: bash

   $ cd /usr/local
   $ sudo tar --owner=smarthome xvzf path-to-tgz/smarthome-X.X.tgz

Everything is extracted to /usr/local/smarthome/. It is possible to use
another path.

Development
~~~~~~~~~~~

To install the recent developer version of SmartHome.py for user **smarthome**:

.. code-block:: bash

   $ sudo mkdir -p /usr/local/smarthome/
   $ sudo chown -R smarthome /usr/local/smarthome/
   $ cd /usr/local
   $ git clone git://github.com/smarthomeng/smarthome.git

To get the latest updates:

.. code-block:: bash

   $ cd /usr/local/smarthome
   $ git pull

Folder Structure
----------------

Structure of the smarthome.py directory, e.g. /usr/local/smarthome/:

-  bin/: contains smarthome.py
-  dev/ development files
-  etc/: should contain the basic configuration files (smarthome.conf,
   plugin.conf, logic.conf)
-  examples/: contains some example files for the configaration and the
   visu plugin
-  items/: should contain one or more item configuration files.
-  lib/: contains the core libraries of SmartHome.py
-  logics/: should contain the logic scripts
-  plugins/: contains the available plugins
-  scenes/: scene files
-  tools/: contains little programms helping to maintain SmartHome.py
-  var/cache/: contains cached item values
-  var/db/: contains the SQLite3 Database
-  var/log/: contains the logfiles
-  var/rrd/: contains the Round Robin Databases

Configuration
-------------

`There is a dedicated page for the configuration. <config.html>`_

Plugins
-------

Every `plugin <plugin.html>`_ has it's own installation section.


Running SmartHome.py
--------------------

Arguments for running SmartHome.py

.. raw:: html

   <pre>
   <code>
   $ /usr/local/smarthome/bin/smarthome.py -h
   --help show this help message and exit 
   -v, --verbose verbose (debug output) logging to the logfile
   -d, --debug stay in the foreground with verbose output
   -i, --interactive open an interactive shell with tab completion and with verbose logging to the logfile
   -l, --logics reload all logics
   -s, --stop stop SmartHome.py
   -q, --quiet reduce logging to the logfile
   -V, --version show SmartHome.py version
   --start start SmartHome.py and detach from console (default)
   </code>
   </pre>

