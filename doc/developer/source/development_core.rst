==================
Development - Core
==================

The core which resides in ``bin/smarthome.py`` is the heart of the system. The core needs
a couple of libraries which are located in ``lib``. Part of them is for exclusive use by ``bin/smarthome.py``,
why they are considered core libraries.

The main object which is in instance of the class defined in ``bin/smarthome.py``,
is accessible and named  ``sh`` in most contexts. From time to time it is referred to as
``_sh`` or ``smarthome``.

The functionality of the core can be extended by the use of loadable modules. a description of the
module system follows below.

The libraries listed here provide the extra functionality for the core.
More info upon the functions and their parameters can be found here.

.. toctree::
   :maxdepth: 5
   :titlesonly:
   :hidden:

   core
   core_libraries
   core_modules 


