Section `item_attributes:`
--------------------------

The ``item_attributes:`` section has a section for each attribute that is additionally implemented for am item.
The name of that section is the name of the attribute.

For the configuration of SmartHomeNG these attributes are configured in the item configuration files in the ``/items`` folder.

The definitions in the ``item_attributes:`` section are used in the future for a configuration tool for SmartHomeNG.

.. code:: yaml

    item_attributes:
        attribute1:
            type: int
            default: 1234
            description:
                de: 'Deutsche Beschreibung des Attributes'
                en: 'English description of the attribute'
            valid_list:
              - 1234
              - 2222
              - 4321

        attribute2:
            type: ...


.. include:: /metadata/parameter_keys.rst

if a plugin has no item attributes, this is signaled by the following entry in the plugin.yaml file:

.. code:: yaml

    item_attributes: NONE

.. hint::

    Please note, that NONE has to be written in Uppercase.

