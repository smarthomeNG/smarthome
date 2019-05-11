
.. role:: redsup
.. role:: bluesup

Section `item_structs:` :redsup:`new`
=====================================

The ``item_structs:`` allows to define templates of item-structures (sub-trees) which can be included in the item
definitions.


The definitions in the ``item_structs:`` have the following format:

.. code:: yaml

    item_structs:
        struct1:

            item1:
                type: int
            item2:
                item3:
                    name: 'my item 3'
                    type: str
                    plg_attr1: 'plugin specific'
                item4:
                    type: bool
                    initial_value: True

        struct2:

            ... (sub-tree with item definitions)


For the configuration of SmartHomeNG these structs are configured/included in the item configuration files in the
``/items`` folder:

.. code:: yaml

   item_name_of_struct:
       struct: <plugin name>.<struct name>



If **struct1** of the struct definitions above ist defined in a plugin named **example_plugin**, it is included in
the following form:

.. code:: yaml

   item_name_of_struct:
       struct: example_plugin.struct1


Definitions for multi-instance plugins
--------------------------------------

When writing a multi-instance plugin, it is likely that item-structs will have items with instance-specific attributes.
In item definitions, those attributes have `'@<instance-name> `` added to the attribute name.

To signal which attribute names will have the instance name added, in structs the attribute name have the constant string
``@instance`` added. This string will be replaced by the real instance name at load time.

.. code:: yaml

    item_structs:
        struct1:

            item1:
                type: int
            item2:
                item3:
                    name: 'my item 3'
                    type: str
                    plg_attr1@instance: 'plugin specific'
                item4:
                    type: bool
                    initial_value: True


The configuration in the item configuration files in the ``/items`` folder looks like this:

.. code:: yaml

   item_name_of_struct:
       struct: example_plugin.struct1
       instance: plg_instance


When looking at the loaded item (using the admin interface), **item3** will have an attribute called
**plg_attr1@plg_instance**.


Plugins without item-structs
----------------------------

if a plugin has no item struct, this is signaled by the following entry in the plugin.yaml file:

.. code:: yaml

    item_structs: NONE

.. hint::

    Please note, that NONE has to be written in Uppercase.

