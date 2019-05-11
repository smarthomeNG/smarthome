.. index:: items; properties
.. index:: properties; items

.. role:: bluesup
.. role:: redsup


Properties of an item :redsup:`new`
===================================

Each defined item offers the following properties, which may be used in **eval** expressions.
All properties are at least readable (r/o). Some properties can also written to (r/w).

Properties are available **in SmartHomeNG v1.6** and up.


Properties are accessed in logics and eval expressions as follows:

.. code::

    var = sh.<item-path>.property.<property-name>

    # Example how to retrieve the name of an item:
    var = sh.wohnung.testitem.property.name


Values for properties that can also be written (for example, in logics) are set as follows:

.. code::

    sh.<item-path>.property.<property-name> = value

    # Example how to ser the name of an item:
    sh.wohnung.testitem.property.name = 'New Name'


+----------------------+------------+----------+------------------------------------------------------------------------------+
| **Property**         | **Access** | **Type** | **Description**                                                              |
+======================+============+==========+==============================================================================+
| defined_in           | r/o        | str      | Returns the file name in which the item was defined                          |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| enforce_updates      | r/w        | bool     | Sets or clears the **enforce_updates** status                                |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| eval                 | r/w        | str      | Allows querying or setting the eval expression                               |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| eval_unexpanded      | r/w        | str      | Allows querying or setting the eval expression. When describing the property,|
|                      |            |          | any contained relative item references are expanded (analogous to loading    |
|                      |            |          | from item configuration files).                                              |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_change          | r/o        | datetime | Returns a *datetime* object with the time of the last change of the item.    |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_change_age      | r/o        | float    | Returns the age of the item since the last change of the value in seconds.   |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_change_by       | r/o        | str      | Returns a string indicating the object that last changed the item.           |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_update          | r/o        | datetime | Returns a *datetime* object with the time of the last update of the item.    |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_update_age      | r/o        | float    | Returns the age of the item since the last update of the value in seconds.   |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_update_by       | r/o        | str      | Returns a string indicating the object that last updated the item.           |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_value           | r/o        | str      | Returns the value of the item it had before the last change.                 |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| name                 | r/w        | str      | Allows querying or setting the name of the item.                             |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| on_change            | r/o        | list     | Returns the list of **on_change** expressions of the item.                   |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| on_change_unexpanded | r/w        | list     | Returns the list of **on_change** expressions of the item in which relative  |
|                      |            |          | item references are not expanded. When assigning the property, any contained |
|                      |            |          | relative item references are expanded (analogous to loading from item        |
|                      |            |          | configuration files).                                                        |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| on_update            | r/o        | list     | Returns the list of **on_update** expressions of the item.                   |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| on_update_unexpanded | r/w        | list     | Returns the list of **on_update** expressions of the item in which relative  |
|                      |            |          | item references are not expanded. When assigning the property, any contained |
|                      |            |          | relative item references are expanded (analogous to loading from item        |
|                      |            |          | configuration files).                                                        |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| path                 | r/o        | str      | Returns the path of the item.                                                |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_change          | r/o        | datetime | Returns a *datetime* object with the time of the penultimate change of the   |
|                      |            |          | item.                                                                        |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_change_age      | r/o        | float    | Returns the age of the item since the penultimate change of the value in     |
|                      |            |          | seconds.                                                                     |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_change_by       | r/o        | str      | Returns a string indicating the object that penultimately changed the item.  |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_update          | r/o        | datetime | Returns a *datetime* object with the time of the penultimate update of the   |
|                      |            |          | item.                                                                        |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_change_age      | r/o        | float    | Returns the age of the item since the penultimate update of the value in     |
|                      |            |          | seconds.                                                                     |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_update_by       | r/o        | str      | Returns a string indicating the object that penultimately updated the item.  |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_value           | r/o        | str      | Returns the value the item had before the penultimate change.                |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| trigger              | r/w        | list     | Allows querying or setting the list of triggers (eval_trigger) of the item.  |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| trigger_unexpanded   | r/w        | list     | Allows querying or setting the list of unexpanded triggers (eval_trigger) of |
|                      |            |          | the item. When describing the property, any contained relative item          |
|                      |            |          | references for use are expanded (analogous to loading from item configuration|
|                      |            |          | files).                                                                      |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| type                 | r/o        | str      | Returns the type of the item.                                                |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| value                | r/w        | str      | The value property represents an alternative to query/assignment by          |
|                      |            |          | var = **item()** / **item(** value **)** .                                   |
+----------------------+------------+----------+------------------------------------------------------------------------------+

