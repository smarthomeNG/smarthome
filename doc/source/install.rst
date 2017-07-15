############
Installation
############

*****************************
Operating System Requirements
*****************************

-  OS: Any Linux or Unix System should be fine. SmartHomeNG is tested on Debian Jessie (amd64).
   So the specific installation commands may differ from this guide.
-  NTP: A running NTP daemon is recommended:
   ``# apt-get install openntpd``
-  Shell Access to install requirements and smarthome.py

************
Installation
************

The steps described here will work for a fresh install of Debian Jessie. You might need other packages if you
are using another Linux flavour like Ubuntu.

First, please update your system to the latest fixes. Then we need to install some packages from the distribution:

.. code-block:: bash

   sudo apt-get -y install dialog python3 python3-dev python3-setuptools unzip build-essential
   sudo apt-get install python3-pip

It is a good idea to upgrade the Python package manager:

.. code-block:: bash

   sudo python3 -m pip install --upgrade pip

For security reasons it is recommended to create an dedicated user account for smarthome.py. On
most Linux Distributions this can be done via:

.. code-block:: bash

   $ sudo adduser smarthome


Get the latest master from Github:

.. code-block:: bash

   cd /usr/local
   sudo git clone --recursive git://github.com/smarthomeNG/smarthome.git
   sudo chown -R smarthome:smarthome /usr/local/smarthome
   cd /usr/local/smarthome/etc
   touch logic.conf

Everything is extracted to ``/usr/local/smarthome/``. It is possible to use another path.
If you want to use the latest development version just enter the base directory and checkout ``develop`` from git.

Required Python modules
=======================

For many plugins there are some further Python modules needed. There are two ways of providing access 
for the application to these modules:

Systemwide Installation
-----------------------

It is  possible to install SmartHomeNG requirements system wide. If no other software is running or if the system
is installed in a virtual machine then the needed modules can be installed for the whole system.

.. code-block:: bash

   cd /usr/local/smarthome
   sudo pip3 install -r requirements/base.txt

Installing Python Modules system wide requires no further actions for starting and running SmartHomeNG.

Virtualenv / Pyenv
------------------

If other software is running on the same system then a better choice might be to isolate the needed Python 
modules for SmartHomeNG using a virtual environment.
With Python >3.5 this is provided with the pyvenv tool, before virtualenv will do this job.

.. code-block:: bash

   cd /usr/local/smarthome                   # Change this if needed
   pyvenv ~/shpy-virtualenv                  # Or "virtualenv" of Python <= 3.4, like on Debian Wheezy
   . ~/shpy-virtualenv/bin/activate          # Activates the Virtual Environment for this shell
   pip install --upgrade pip                 # Update the Python Package Installer inside the virtualenv
   pip install -r requirements/base.txt      # Install base requirements for smarthome.py

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

Folder Structure
================

Structure of the smarthome.py directory, e.g. /usr/local/smarthome/:

.. code-block:: bash

   bin/           contains smarthome.py
   dev/           development files
   etc/           should contain the basic configuration files (smarthome.conf, plugin.conf, logic.conf)
   examples/      contains some example files for the configuration and the visu plugin
   items/         should contain one or more item configuration files.
   lib/           contains the core libraries of SmartHomeNG
   logics/        should contain the logic scripts
   plugins/       contains the available plugins
   scenes/        scene files
   tools/         contains little programms helping to maintain SmartHomeNG
   var/           its subdirs contain various collected data
   var/cache/     contains cached item values
   var/db/        contains the SQLite3 Database
   var/log/       contains the logfiles
   var/rrd/       contains the Round Robin Databases

Configuration
================

`There is a dedicated page for the configuration. <config.html>`_

Plugins
================

Every `plugin <allplugins.html>`_ has it's own installation section.

*******************
Running SmartHomeNG
*******************

Arguments for running SmartHomeNG

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

If you start without any option, then SmartHomeNG will return the PID if already running.
