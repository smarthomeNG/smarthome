############
Installation
############

The steps described here will work for a fresh installation of Debian Linux (8.x aka Jessie).
Other packages might be needed another Linux flavour like Ubuntu, Arch Linux, etc. is installed.

First, please update the system to the latest fixes. Then install the following packages from the distribution:

.. code-block:: bash

   sudo apt-get -y install dialog python3 python3-dev python3-setuptools unzip build-essential
   sudo apt-get install python3-pip

For security reasons it is **strongly recommended** to create a **dedicated user account** for SmartHomeNG.
On most Linux Distributions this can be done via:

.. code-block:: bash

   sudo adduser smarthome

In the following it is expected that SmartHomeNG **is not installed and run as user root** but instead uses
the dedicated user *smarthome*


Download SmartHomeNG from GitHub
================================

Everything is extracted to ``/usr/local/smarthome/``. It is possible however to use another path.
``sudo`` is needed to access ``/usr/local/`` as well as setting the ownership to user **smarthome**

For development, the latest development version is about to installed. This is done with the option **-b develop** in the **git clone** command.

.. code-block:: bash

   cd /usr/local
   sudo mkdir smarthome
   sudo chown -R smarthome:smarthome /usr/local/smarthome

   cd smarthome
   git clone -b develop https://github.com/smarthomeNG/smarthome.git .

   mkdir plugins
   cd plugins
   git clone -b develop https://github.com/smarthomeNG/plugins.git .

Please notice the dot at the end of the **git** commands!


Required Python modules
=======================

For many plugins there are some further Python modules needed. There are two ways of providing access
for the application to these modules. The first method is to install any module system wide.
You will need to run pip with ``sudo`` prefix then.

If you decide to run more than SmartHomeNG on your system
you might encounter situations were SmartHomeNG needs a module with a special version but another program
needs another version of this module. You might not be able to solve this conflict.
One idea is to use a virtual environment for python for a specific program.

Both methods are described below:

System wide installation
------------------------

It is a good idea to first upgrade the Python package manager pip:

.. code-block:: bash

   sudo python3 -m pip install --upgrade pip

Then enter the SmartHomeNG directory and start pip with

.. code-block:: bash

   cd /usr/local/smarthome                      # change if necessary
   sudo pip3 install -r requirements/base.txt

Now the dependencies for the core should be met. Some plugins however require further Python modules.
Since every plugin supplies a requirement file, the missing modules can be installed with

.. code-block:: bash

   cd /usr/local/smarthome                                      # change if necessary
   sudo pip install -r plugins/pluginname/requirements.txt      # Install requirements of given plugin.

It is also possible to install all requirements of **all** plugins at once:

.. code-block:: bash

   cd /usr/local/smarthome                      # change if necessary
   sudo pip3 install -r requirements/all.txt

Keep in mind that some Python modules require additional system packages for a working installation. Just
take a look at ``plugins/<pluginname>/README.md`` file.


Virtualenv / Pyenv
------------------

If other software is running on the same system then a better choice might be to isolate the needed Python
modules for SmartHomeNG using a virtual environment.
With Python >= 3.5 this is provided with the pyvenv tool, before virtualenv will do this job.
First the home directory of SmartHomeNG is entered and then
a subdirectory ``shpy-virtualenv`` will be created within the home directory of user **smarthome**.
Next the Python package manager is updated to the most recent version and finally the modules are
installed according to requirements in base.txt

.. code-block:: bash

   cd /usr/local/smarthome                   # Change this if needed
   ~/shpy-virtualenv                         # Or "pyenv" of Python >= 3.5
   ~/shpy-virtualenv/bin/activate            # Activates the virtual environment for this shell
   pip install --upgrade pip                 # Update the Python Package Installer inside the virtualenv
   pip install -r requirements/base.txt      # Install base requirements for smarthome.py

Now the dependencies for the core should be met. Some plugins however require further Python modules.
Since every plugin supplies a requirement file, the missing modules can be installed with

.. code-block:: bash

   cd /usr/local/smarthome                            # Change this if needed
   . ~/shpy-virtualenv/bin/activate                   # Activate the virtual environment for this shell
   pip install -r plugins/pluginname/requirements.txt # Install requirements of pluginname.

Keep in mind that some Python modules require additional apt packages for a working installation. Just
take a look at plugins/pluginname/README.md.

Every time you want to use SmartHomeNG with an virtualenv, you must activate it in the current shell:

.. code-block:: bash

   cd /usr/local/smarthome                    # Change this if needed
   . ~/shpy-virtualenv/bin/activate           # Activate the Virtual Environment for this shell

Virtualenv can be deactivated by entering ``deactivate`` in the current shell.
