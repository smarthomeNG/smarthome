
Section `module`
================

The global metadata section ``module:`` has the following keys:

.. code:: yaml

    # Metadata for the module
    module:
        # Global module attributes
        classname: Http
        version: 1.4.3
    #    sh_minversion: 1.7          # minimum shNG version to use this module (leave empty if no special requirement)
    #    sh_maxversion:              # maximum shNG version to use this module (leave empty if latest)
    #    py_minversion: 3.6          # minimum Python version needed for this module (leave empty if no special requirement)
    #    py_maxversion:              # maximum Python version to use this module (leave empty if no special requirement)
        description:
            de: 'Modul zur Implementierung von Backend-Webinterfaces für Plugins'
            en: 'Module for implementing a backend-webinterface for plugins'

Description of the keys in the section ``module:``

    - **classname:** Name of the Python class to initialize
    - **version:** Version number of the module. It is checked against the version number defined in the Python source code
    - **sh_minversion:** Minimum SmartHomeNG version this module is compatible with. If *sh_minversion* is left empty, SmartHomeNG assumes that the module is compatible with every version of SmartHomeNG [Test not yet implemented]
    - **sh_maxversion:** Maximum SmartHomeNG version this module is compatible with (or empty, if compatible with the actual version of SmartHomeNG) [Test not yet implemented]
    - **py_minversion:** Minimum Python version this module is compatible with. If *py_minversion* is left empty, SmartHomeNG assumes that the module is compatible with every older Python version
    - **py_maxversion:** Maximum Python version this module is compatible with (or empty, if compatible with the actual version of Python)
    - **description:** Multilanguage Text describing what the module does. - The texts in the different languages are specified in sub-entries in the form <language>: <text>. Use the standard two letter codes for specifying the language (de, en, fr, pl, ..)
    - **classpath:** **Usually not specified.** Only needed, if the module resides outside the ``/modules`` folder

