Libraries
=========

Aside from the main program which resides in ``bin/smarthome.py`` there are libraries supporting SmartHomeNG. If a library
has requirements for a Python package that is not met by the standard Python installation, it has to be added to the
**requirements.txt** file in the ../lib directory.

The description of the libraries' functions is shown here:


.. toctree::
   :maxdepth: 2
   :titlesonly:

   /lib/config
   /lib/constants
   /lib/daemon
   /lib/item_conversion
   /lib/log
   /lib/metadata
   /lib/module
   /lib/scene
   /lib/shyaml


The following libraries are more public. They can be used for plugin development too.


.. toctree::
   :maxdepth: 5
   :titlesonly:

   /lib/connection
   /lib/db
   /lib/logutils
   /lib/network
   /lib/orb
   /lib/tools
   /lib/utils
