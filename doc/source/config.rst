
=============
Configuration
=============

The configuration of SmartHome.py is split up in four areas:

-  Basic Configuration: etc/smarthome.conf
-  Logic Configuration: etc/logic.conf
-  Plugin Configuration: etc/plugin.conf
-  Item Configuration: items/\*.conf

etc/smarthome.conf [optional]
-----------------------------

Following attributes are supported in smarthome.conf:

-  ``lat``, ``lon``, ``elev``: geographic coordinates of your home
   (latitude, longitude, elevation). lat and lon are necessary for
   sunrise/sunset calculation, dealing with the position of the sun.
-  ``tz``: timezone
-  ``item_change_log``: log item changes with loglevel info
-  ``loglevel``: specify the loglevel. Levels could be debug, info, warning or error.


Sample Configuration
~~~~~~~~~~~~~~~~~~~~

.. raw:: html

   <pre># /usr/local/smarthome/etc/smarthome.conf

   lat = 51.1633
   lon = 10.4476
   elev = 500

   tz = 'Europe/Berlin'
   </pre>

etc/logic.conf [mandatory]
--------------------------

It is possible to use a blank file (touch logic.conf) for the first
steps.

Logic items within SmartHome.py are simple python scripts, which are
placed in /usr/local/smarthome/logics/. See the `logic
introduction </smarthome/logic>`_ for howto write logics.

An example of a very simple logic.conf:

.. raw:: html

   <pre># /usr/local/smarthome/etc/logic.conf
   [MyLogic]
       filename = logic.py
       crontab = init</pre>

SmartHome.py would look in /usr/local/smarthome/logics/ for the file
logic.py. The logic would be started - once - when the system starts.

Following attributes are supported control the behavior of the logics:

watch\_item
~~~~~~~~~~~

The list of items will be monitored for changes.

.. raw:: html

   <pre>watch_item = house.door | terrace.door</pre>

Every change of these two items triggers (run) the logic.
Or you could use a regular expression:

.. raw:: html

   <pre>watch_item = *.door</pre>

cycle
~~~~~

Defines the time interval for repeating the logic (in seconds).

.. raw:: html

   <pre>cycle = 60</pre>

Special use:

.. raw:: html

   <pre>cycle = 15 = 42</pre>

Calls the logic with trigger['value'] # == '42'

crontab
~~~~~~~

Like Unix crontab with the following options:

crontab = init Run the logic during the start of SmartHome.py.

crontab = minute hour day wday

-  minute: single value from 0 to 59, or comma separated list, or \*
   (every minute)
-  hour: single value from 0 to 23, or comma separated list, or \*
   (every hour)
-  day: single value from 0 to 28, or comma separated list, or \* (every
   day) Please note: dont use days greater than 28 in the moment.
-  wday: weekday, single value from 0 to 6 (0 = Monday), or comma
   separated list, or \* (every day)

crontab = sunrise Runs the logic at every sunrise. Use ``sunset`` to run
at sunset. For sunset / sunrise you could provide:

-  an horizon offset in degrees e.g. crontab = sunset-6 You have to
   specify your latitude/longitude in smarthome.conf.
-  an offset in minutes specified by a 'm' e.g. crontab = sunset-10m
-  a boundary for the execution

   .. raw:: html

      <pre>crontab = 17:00&lt;sunset  # sunset, but not bevor 17:00 (locale time)
      crontab = sunset&lt;20:00  # sunset, but not after 20:00 (locale time)
      crontab = 17:00&lt;sunset&lt;20:00  # sunset, beetween 17:00 and 20:00</pre>

crontab = 15 \* \* \* = 50 Calls the logic with trigger['value'] # == 50

Combine several options with '\|':

.. raw:: html

   <pre>crontab = init = 'start' | sunrise-2 | 0 5 * *</pre>

prio
~~~~

Priority of the logic used by the internal scheduling table. By default
every logic has the the priority of '3'. You could assign [0-10] as a
value. You could change it to '1' to prefer or to '4' to penalise the
logic in comparison to other logics.

Other attributes
~~~~~~~~~~~~~~~~

Other attributes could be accessed from the the logic with
self.attribute\_name.

Sample logic.conf
~~~~~~~~~~~~~~~~~

.. raw:: html

   <pre># /usr/local/smarthome/etc/logic.conf
   [Time]
       filename = time.py
       cyle = 60

   [DoorBell]
       filename = bell.py
       watch_item = dorr.bell # monitor for changes

   [Blind Living]
       filename = blind.py
       crontab = 10,25,40,55 * * * # run every 15 minutes
       # cycle = 900 # could be used instead
       sunshine = no # accessed by self.sunshine

   [BlindKitchen]
       filename = blind.py  # you could run the same logic file several times
       crontab = 10,25,40,55 * * * # run every 15 minutes
       sunshine = yes
   </pre>

etc/plugin.conf (mandatory)
---------------------------

It is possible to use a blank file (touch plugin.conf) for the first
steps.

Plugins extend the core functionality of SmartHome.py. You could access
these plugins from every logic script. For example there is a plugin for
the prowl notification service to send small push messages to your
iPhone/iPad. Plugins are placed in /usr/local/smarthome/plugins/.

Configuration
~~~~~~~~~~~~~

Plugins are configured in the plugin.conf file. A simple plugin.conf:

.. raw:: html

   <pre># /usr/local/smarthome/etc/plugin.conf
   [notify] # object instance name e.g. sh.notify
       class_name = Prowl # class name of the python class
       class_path = plugins.prowl # path to the plugin
       apikey = abc123abc123 # attribute for the plugin e.g. secret key for prowl
   </pre>

The object name, class name and class path must be provided. The other
attributes depend on the individual plugin. See the corresponding plugin
page for more information.

The example above would generate the following statement
``sh.notify = plugins.prowl.Prowl(apikey='abc123abc123')``. From now on
there is the object ``sh.notify`` and you could access the function of
this object with ``sh.notify.function()``.

items/\*.conf (optional)
------------------------

Items could be specified in one or several conf files placed in the
``items`` directory of SmartHome.py Valid characters for the item name
are: a-z, A-Z and '\_'!

A simple item configuration:

.. raw:: html

   <pre># /usr/local/smarthome/items/living.conf
   [living_room_temp]
       type = num
   </pre>

Use nested items to build a tree representing your environment.

.. raw:: html

   <pre># /usr/local/smarthome/items/living.conf
   [living_room]
       [[temperature]]
           type = num

       [[tv]]
           type = bool

           [[[channel]]]
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
