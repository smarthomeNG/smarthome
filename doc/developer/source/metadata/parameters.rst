
.. role:: redsup
.. role:: bluesup

.. index:: parameters; Plugin Metadata
.. index:: Plugin Metadata; parameters

Section `parameters`
====================

Parameter metadata is used to check if the configured parameters in ``/etc`` are valid.
If the configured data is not valid, warnings are logged in the logfile of SmartHomeNG.

If the configuration is valid, the parameters are handed over to the plugin/module through
a dict, that contains a value for each parameter (defined in the metadata file). The datatype
of those values correspond to the type-definitions in the metadata.

Metadata is supported in SmartHomeNG v1.4 and up.

The ``parameters:`` section has a section for each parameter that is implemented. The name of that
section is the name of the parameter.

The definitions in the ``parameters:`` section are used for validity checking of the plugin/module configuration.
In the future the definitions will be used for a configuration tool for SmartHomeNG.

.. code:: yaml

    parameters:
        param1:
            type: int
            default: 1234
            description:
                de: 'Deutsche Beschreibung'
                en: 'English description'
            valid_list:
              - 1234
              - 2222
              - 4321

        param2:
            type: ...


.. include:: /metadata/parameter_keys.rst

if a plugin has no parameters, this is signaled by the following entry in the plugin.yaml file:

.. code:: yaml

    parameters: NONE

.. hint::

    Please note, that NONE has to be written in upper case.

