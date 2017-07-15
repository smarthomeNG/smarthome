Items
=====

Overview
--------

Items can be defined with a ``.conf`` file. Starting with SmartHomeNG 1.3 items may also be defined
within one or more ``.yaml``-files. If there are filenames with the same base name then the ``.yaml`` file
will be read instead of the ``.conf`` file.

The following still describes the old-fashioned way with a ``.conf`` file. Indentation may be used
for legibility purposes but is neither necessary nor mandatory.

For any item name only the characters ``A-Z`` and ``a-z`` should be used.
An underscore ``_`` or a digit ``0-9`` may be used within the item name but not as a first character.
Item names like ``[1w_Bus]``, ``[42]`` or ``[_Bus]`` should not be used.
Any Python reserved names like e.g. ``get`` or ``set`` also should be avoided.

Items can be build up in a hierarchical manner. An item can have children that may have children as well and so on.
The level of an item is shown by the number of square parentheses used. The more parentheses around the item name,
the lower in the hierarchy.

.. code-block:: text
   :caption: myitem.conf

   [grandfather]
      [[daddy]]
         [[[kid]]]

It is advised to use nested items to build a tree representing your environment:

.. code-block:: text
   :caption: /usr/local/smarthome/items/living.conf

   [living]
       [[light]]
           type = bool
           name = Livingroom main light
       [[tv]]
           type = bool

           [[[current]]]
               type = num
   [kitchen]
       [[light]]
           type = bool
           name = kitchen table light
       [[temp]]
           type = num
       [[presence]]
           type = bool



Item Attributes
~~~~~~~~~~~~~~~

Any item can have several attributes. In the above code there is defined the item ``living.light`` and it has the
attributes ``type`` and ``name``. The following table shows the attributes that will be understood by the core
of SmartHomeNG.

However plugins may introduce many more attributes that will mostly be specific by the plugin itself.

======================= ================================================================================================
attribute               description
======================= ================================================================================================
``type``                for storing values and/or triggering actions you have to
                        specify this attribute. (If you do not specify this attribute the
                        item is only useful for structuring your item tree).

                        **Supported types**:

                        ``bool`` boolean type (on, 1, True or off, 0, False).
                        True or False are internally used. Use e.g. ``if sh.item(): ...``.

                        ``num``  any number (integer or float).

                        ``str``  regular string or unicode string.

                        ``list``  list/array of values. Useful e.g. for some KNX dpts.

                        ``dict``  python dictionary for generic purposes.

                        ``foo``   special purposes. No validation is done.

                        ``scene`` special keyword to support scenes

``value``               initial value of that item.
``name``                name which would be the str representation of the item (optional).
``cache``               if set to On, the value of the item will be cached in a
                        local file (in /usr/local/smarthome/var/cache/).
``enforce_updates``     If set to On, every call of the item will trigger depending logics and item evaluations.
``threshold``           specify values to trigger depending logics only if the value transit the threshold.

                        ``low:high`` to set a value for the lower and upper threshold,
                        e.g. ``21.4:25.0`` which triggers the logic if the value exceeds 25.0 or fall below 21.4.
                        Or simply a single value.
``eval``                if the value of the item is to be changed and this attribute presents a formula then
                        the new value will be calculated using this formula
``eval_trigger``        trigger to initiate the evaluation of the formula given with eval
``crontab``             see logic.conf for possible options to set the value of an item at the specified times / cycles.
``cycle``               see logic.conf for possible options to set the value of an item at the specified times / cycles.
``autotimer``           sets the items value after some time delay
======================= ================================================================================================


Scenes
^^^^^^

For using scenes a config file into the scenes directory for every scene item is necessary.
The scene config file consists of lines with 3 space separated values in the format ``ItemValue ItemPath | LogicName
Value``

======================= ================================================================================================
Column                  description
======================= ================================================================================================
ItemValue:              the first column contains the item value to check for the configured action.
ItemPath or LogicName:  the second column contains an item path, which is set to the given value,
                        or a LogicName, which is triggered
Value:                  in case an ItemPath was specified the item will be set to the given value, in case a
                        LogicName was specified the logic will be run (specify 'run' as value)
                        or stop (specify 'stop' as value).
======================= ================================================================================================

.. code-block:: text
   :caption: items/example.conf

   [example]
       type = scene
   [otheritem]
       type = num

.. code-block:: text
   :caption: scenes/example.conf

   0 otheritem 2
   1 otheritem 20
   1 LogicName run
   2 otheritem 55
   3 LogicName stop

eval
^^^^

This attribute is useful for small evaluations and corrections. The
input value is accessible with ``value``.

.. code-block:: text
   :caption: items/level.conf

   [level]
       type = num
       eval = value * 2 - 1  # if you call sh.level(3) sh.level will be evaluated and set to 5

Trigger the evaluation of an item with ``eval_trigger``:

.. code-block:: text
   :caption: items/room.conf

   [room]
       [[temp]]
           type = num
       [[hum]]
           type = num
       [[dew]]
           type = num
           eval = sh.tools.dewpoint(sh.room.temp(), sh.room.hum())
           eval_trigger = room.temp | room.hum  # every change of temp or hum would trigger the evaluation of dew.

Eval keywords to use with the ``eval_trigger``:

======= =============================================================================
``sum`` compute the sum of all specified ``eval_trigger`` items.
``avg`` compute the average of all specified ``eval_trigger`` items.
``and`` set the item to True if all of the specified ``eval_trigger`` items are True.
``or``  set the item to True if one of the specified ``eval_trigger`` items  is True.
======= =============================================================================

.. code-block:: text
   :caption:  items/rooms.conf

   [living]
       [[temp]]
           type = num
       [[presence]]
           type = bool
   [kitchen]
       [[temp]]
           type = num
       [[presence]]
           type = bool
   [rooms]
       [[temp]]
           type = num
           name = average temperature
           eval = avg
           eval_trigger = living.temp | kitchen.temp
       [[presence]]
           type = bool
           name = movement in on the rooms
           eval = or
           eval_trigger = living.presence | kitchen.presence

Item functions
~~~~~~~~~~~~~~

Every item provides the following methods:

================================ ==================================================================================
function                         description
================================ ==================================================================================
``id()``                         Returns the item id (path).
``return_parent()``              Returns the parent item.
``return_children()``            Returns the children of an item.
``autotimer(time, value)``       Set a timer to run at every item change. Specify the time (in seconds),
                                 or use m to specify minutes.

``timer(time, value)``           Same as ``autotimer()``, except that it runs only once.
``age()``                        Returns the age of the current item value as seconds.
``prev_age()``                   Returns the previous age of the item value as seconds.
``last_change()``                Returns a datetime object with the time of the last change.
``prev_change()``                Returns a datetime object with the time of the next to last change.
``prev_value()``                 Returns the value of the next to last change.
``last_update()``                Returns a datetime object with the time of the last update.
``changed_by()``                 Returns the caller of the latest update.
``fade(tovalue,step,timedelta)`` Fades the item to a specified value with the defined stepping
                                 (int or float) and timedelta (int or float in seconds).

================================ ==================================================================================


Example logic with uses of above functions
------------------------------------------

.. code-block:: python
   :caption:  logics/sample.py

   # getting the parent of item
   sh.item.return_parent()

   # get all children for item and log them
   for child in sh.item.return_children():
      logger.debug( ... )

   # set the item after 10 minutes to 42
   sh.item.autotimer('10m', 42)``

   # disable autotimer for item
   sh.item.autotimer()

   # will in- or decrement the living room light to 100 by a stepping of ``1`` and a timedelta of ``2.5`` seconds.
   sh.living.light.fade(100, 1, 2.5)``