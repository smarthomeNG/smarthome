======
Items
======

Overview
========

The easiest item consists just of a file with the item name:

.. raw:: html

   <pre># myitem.conf
       [One]</pre>


For any item name only the characters A-Z and a-z should be used. An underscor or a digit may be used within the item name
An item name like ``[1w_Bus]``, ``[42]`` or ``[_Bus]`` should not be used. (Any Python reserved name also should be avoided)

Items can be build up in a hierarchical manner. An item can have children that may have children as well and so on.
To express the level of an item square parentheses are used. The more the lower in the hierarchy.
Child item are always accessed with a full path:

.. raw:: html

    <pre># myitem.conf
    [grandfather]
       [[daddy]]
          [[[kid]]]
    </pre>

Here a simple item:

.. raw:: html

   <pre># e.g. items/kitchen.conf
   [kitchen]
       type = num
   </pre>

Use nested items to build a tree representing your environment.

.. raw:: html

   <pre># /usr/local/smarthome/items/living.conf
   [kitchen]
       [[fridge]]
           type = bool

       [[oven]]
           type = bool

           [[[L1]]]
               type = num
   </pre>

Item Attributes
~~~~~~~~~~~~~~~

-  ``type``: for storing values and/or triggering actions you have to
   specify this attribute. (If you do not specify this attribute the
   item is only useful for structuring your item tree). Supported
   types:
   -  bool: boolean type (on, 1, True or off, 0, False). True or False are
   internally used. Use e.g. ``if sh.item(): ...``.
   -  num: any number (integer or float).
   -  str: regular string or unicode string.
   -  list: list/array of values. Usefull e.g. for some KNX dpts.
   -  dict: python dictionary for generic purposes.
   -  foo: pecial purposes. No validation is done.
   -  scene: special keyword to support scenes

-  ``value``: initial value of that item.
-  ``name``: name which would be the str representation of the item
   (optional).
-  ``cache``: if set to On, the value of the item will be cached in a
   local file (in /usr/local/smarthome/var/cache/).
-  ``enforce_updates``: If set to On, every call of the item will
   trigger depending logics and item evaluations.
-  ``threshold``: specify values to trigger depending logics only if the
   value transit the threshold. low:high to set a value for the lower
   and upper threshold, e.g. 21.4:25.0 which triggers the logic if the
   value exceeds 25.0 or fall below 21.4. Or simply a single value.
-  ``eval`` and ``eval_trigger``: see next section for a description of
   these attributes.
-  ``crontab`` and ``cycle``: see logic.conf for possible options to set
   the value of an item at the specified times / cycles.
- ``autotimer`` see the item function below. e.g. ``autotimer = 10m = 42``

Scenes
^^^^^^

For using scenes a config file into the scenes directory for every
'scene item' is necessary. The scene config file consists of lines
with 3 space separated values in the format ItemValue ItemPath\|LogicName
Value:

-  ItemValue: the first column contains the item value to check for the configured action.
-  ItemPath or LogicName: the second column contains an item path, which is set to the given value, or a LogicName, which is triggered
-  Value: in case an ItemPath was specified the item will be set to the given value, in case a LogicName was specified the logic will be run (specify 'run' as value) or stop (specify 'stop' as value).

.. raw:: html

   <pre># items/example.conf
   [example]
       type = scene
   [otheritem]
       type = num
   </pre>

   <pre># scenes/example.conf
   0 otheritem 2
   1 otheritem 20
   1 LogicName run
   2 otheritem 55
   3 LogicName stop
   </pre>

eval
^^^^

This attribute is useful for small evaluations and corrections. The
input value is accesible with ``value``.

.. raw:: html

   <pre>
   # items/level.conf
   [level]
       type = num
       eval = value * 2 - 1  # if you call sh.level(3) sh.level will be evaluated and set to 5
   </pre>

Trigger the evaluation of an item with ``eval_trigger``:

.. raw:: html

   <pre>
   # items/room.conf
   [room]
       [[temp]]
           type = num
       [[hum]]
           type = num
       [[dew]]
           type = num
           eval = sh.tools.dewpoint(sh.room.temp(), sh.room.hum())
           eval_trigger = room.temp | room.hum  # every change of temp or hum would trigger the evaluation of dew.
   </pre>

Eval keywords to use with the eval\_trigger:

-  sum: compute the sum of all specified eval\_trigger items.
-  avg: compute the average of all specified eval\_trigger items.
-  and: set the item to True if all of the specified eval\_trigger items
   are True.
-  or: set the item to True if one of the specified eval\_trigger items
   is True.

.. raw:: html

   <pre>
   # items/rooms.conf
   [room_a]
       [[temp]]
           type = num
       [[presence]]
           type = bool
   [room_b]
       [[temp]]
           type = num
       [[presence]]
           type = bool
   [rooms]
       [[temp]]
           type = num
           name = average temperature
           eval = avg
           eval_trigger = room_a.temp | room_b.temp
       [[presence]]
           type = bool
           name = movement in on the rooms
           eval = or
           eval_trigger = room_a.presence | room_b.presence
   </pre>

Item Functions
~~~~~~~~~~~~~~

Every item provides the following methods:

id()
^^^^

Returns the item id (path).

return\_parent()
^^^^^^^^^^^^^^^^

Returns the parent item. ``sh.item.return_parent()``

return\_children()
^^^^^^^^^^^^^^^^^^

Returns the children of an item.
``for child in sh.item.return_children(): ...``


autotimer(time, value)
^^^^^^^^^^^^^^^^^^^^^^
Set a timer to run at every item change. Specify the time (in seconds), or use m to specify minutes. e.g. autotimer('10m', 42) to set the item after 10 minutes to 42.
If you call autotimer() without a timer or value, the functionality will be disabled.

timer(time, value)
^^^^^^^^^^^^^^^^^^
Same as autotimer, excepts it runs only once.

age()
^^^^^

Returns the age of the current item value as seconds.

prev\_age()
^^^^^^^^^^^

Returns the previous age of the item value as seconds.

last\_change()
^^^^^^^^^^^^^^

Returns a datetime object with the time of the last change.

prev\_change()
^^^^^^^^^^^^^^

Returns a datetime object with the time of the next to last change.


prev\_value()
^^^^^^^^^^^^^^

Returns the value of the next to last change.


last\_update()
^^^^^^^^^^^^^^

Returns a datetime object with the time of the last update.

changed\_by()
^^^^^^^^^^^^^

Returns the caller of the latest update.

fade()
^^^^^^

Fades the item to a specified value with the defined stepping (int or
float) and timedelta (int or float in seconds). E.g.
sh.living.light.fade(100, 1, 2.5) will in- or decrement the living room
light to 100 by a stepping of '1' and a timedelta of '2.5' seconds.

