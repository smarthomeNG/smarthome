Installation
============

Operating System Requirements
-----------------------------

-  OS: Any Linux or Unix System should be fine. SmartHomeNG is tested
   on Debian Jessie (amd64) and several flavors of Ubuntu.
   So the specific installation commands may differ from this guide.
-  NTP: A running NTP daemon is recommended:
   ``# apt-get install openntpd``
-  Shell Access to install requirements and smarthome.py

Smarthome.py is tested on Ubuntu 16.04, Debian Wheezy and Arch Linux.

Python 3.2 or higher is mandatory. Python 2.x is not supported
``$ sudo apt-get install python3 python3-dev python3-setuptools``

Ubuntu 16.04
~~~~~~~~~~~~

.. code-block:: bash

   $ sudo apt install build-essential git python3 python3-venv python3-dev python3-setuptools

Debian Wheezy
~~~~~~~~~~~~~

.. code-block:: bash


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

To install the recent development version of SmartHomeNG for user **smarthome**:

.. code-block:: bash

   $ sudo mkdir -p /usr/local/smarthome
   $ sudo chown -R smarthome /usr/local/smarthome/
   $ cd /usr/local
   $ git clone https://github.com/smarthomeNG/smarthome.git -b develop
   </code>
   </pre>

To get the latest updates:

.. code-block:: bash

   $ cd /usr/local/smarthome
   $ git pull

Virtualenv
~~~~~~~~~~

To avoid issues with the Distribution Python Package Versions we recommend the use of a
python virtual environment. With Python >3.5 this is provieded with the pyvenv tool, before
virtualenv will do this job.

.. code-block:: bash

   cd /usr/local/smarthome              # Change this if needed
   pyvenv ~/shpy-virtualenv             # Or "virtualenv" of Python <= 3.4, like on Debian Wheezy
   . ~/shpy-virtualenv/bin/activate     # Activates the Virtual Environment for this shell
   pip install --upgrade pip            # Update the Python Package Installer inside the virtualenv
   pip install -r requirements/base.txt # Install base requirements for smarthome.py

Some smarthome.py require some more Python Modules, you can simply install these, e.g.:

.. code-block:: bash

   cd /usr/local/smarthome                    # Change this if needed
   . ~/shpy-virtualenv/bin/activate           # Activate the Virtual Environment for this shell
   pip install -r requirements/pluginname.txt # Install Requirements of pluginname.

Keep in Mind that some Python Module require additional apt packages for a working installation. Just
take a look at plugins/pluginname/README.rst.

Every time you want to use smarthome.py with an virtualenv, you must activate it in your current shell:

.. code-block:: bash

   cd /usr/local/smarthome                    # Change this if needed
   . ~/shpy-virtualenv/bin/activate           # Activate the Virtual Environment for this shell

System Installation
~~~~~~~~~~~~~~~~~~~

It is also possible to install smarthome.py requirements system wide. We are not responsible for
side affects, and always recommend a virtualenv!

.. code-block:: bash

   cd /usr/local/smarthome
   sudo pip install -r requirements/base.txt

Installing Python Modules system wide requires no further actions for starting and running smarthome.py.

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

.. code-block:: none

   $ bin/smarthome.py -h
   --help show this help message and exit 
   -v, --verbose verbose (debug output) logging to the logfile
   -d, --debug stay in the foreground with verbose output
   -i, --interactive open an interactive shell with tab completion and with verbose logging to the logfile
   -l, --logics reload all logics
   -s, --stop stop SmartHome.py
   -q, --quiet reduce logging to the logfile
   -V, --version show SmartHome.py version
   --start start SmartHome.py and detach from console (default)

