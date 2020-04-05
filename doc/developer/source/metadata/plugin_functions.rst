
.. role:: redsup
.. role:: bluesup

.. index:: plugin_functions; Plugin Metadata
.. index:: Plugin Metadata; plugin_functions

Section `plugin_functions`
==========================

This sections describes the public functions that are defined by the plugin.

The ``plugin_functions:`` section has a section for each function that is implemented. The name of that section
is the name of the function. Each function has a section ``parameters:`` which describes each parameter in detail.


The definitions in the ``plugin_functions:`` section are used for generating the documentation.
In the future the definitions will be used for a configuration tool for SmartHomeNG.

.. code:: yaml

    plugin_functions:
        example_function:
            type: str
            description:
                de: 'Deutsche Beschreibung der Funktion'
                en: 'English description of the function'
            parameters:
                param1:
                    type: int
                    default: 1234
                    description:
                        de: 'Deutsche Beschreibung des Funktionsparameters'
                        en: 'English description of the function's parameter'
                    valid_list:
                      - 1234
                      - 2222
                      - 4321

                param2:
                    type: ...


.. include:: /metadata/parameter_keys.rst


Plugins without plugin-functions
================================

if a plugin has no public functions, this is signaled by the following entry in the plugin.yaml file:

.. code:: yaml

    plugin_functions: NONE

.. hint::

    Please note, that NONE has to be written in Uppercase.

