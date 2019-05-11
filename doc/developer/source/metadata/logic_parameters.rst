Section `logic_parameters:`
---------------------------

Logic-parameter metadata is at the moment only used for generation of user documentation.
If the configured data is not valid, warnings are logged in the logfile of SmartHomeNG.

The ``logic_parameters:`` section has a section for each parameter for logics that is implemented. The name of that
section is the name of the logic-parameter.

The definitions in the ``logic_parameters:`` section are used for documentation generation.
In the future the definitions will be used for a configuration tool for SmartHomeNG.

.. code:: yaml

    logic_parameters:
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

if a plugin has no logic_parameters, this is signaled by the following entry in the plugin.yaml file:

.. code:: yaml

    logic_parameters: NONE

.. hint::

    Please note, that NONE has to be written in Uppercase.

