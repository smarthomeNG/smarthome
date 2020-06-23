Logics
======


Introduction
------------

Logics itself are just scripts written in Python and they reside in subdirectory ``logics/``.
All logics will be defined in ``etc/logic.yaml``.
The configuration file tells SmartHomeNG when to execute a certain logic script.

The following sample configuration file defines four logic scripts for use by SmartHomeNG.

* The first logic script is named ``InitSmartHomeNG`` and its source code
  is configured to be found in ``logics/InitSmartHomeNG.py``.
  The attribute ``crontab: init`` tells SmartHomeNG to start the script just after
  SmartHomeNG has started.
* The second logic script named ``Hourly`` resides in ``logics/time.py``
  and the attribute ``cycle: 3600`` tells SmartHomeNG to call (execute) the script every 3600 seconds (one hour).
* The third logic script named ``Gate`` resides in ``logics/gate.py`` and the attribute
  ``watch_item: gate.alarm`` tells SmartHomeNG to call the script when item
  value of gate.alarm changed.
* The fourth logic thus is named ``disks`` and it's source code ``logics/disks.py``
  will be executed every 5 minutes.

.. code-block:: yaml
   :caption:  etc/logic.yaml

   InitSmarthomeNG:
       filename: InitSmartHomeNG.py
       crontab: init

   Hourly:
       filename: time.py
       cycle: 3600

   Gate:
       filename: gate.py
       watch_item: gate.alarm    # monitor for changes

   disks:
       filename: disks.py
       # 'crontab: run at start and every 5 minutes'
       crontab:
         - init
         - '0,5,10,15,20,25,30,35,40,45,50,55 * * *'
       usage_warning: 500

Configuration parameters
------------------------

The following parameters can be used in `etc/logic.yaml` to configure the logic and it's behavior.

watch_item
~~~~~~~~~~

The list of items will be monitored for changes.

.. code-block:: yaml
   :caption:  etc/logic.yaml

   logicnamehere:
      watch_item:
       - house.alarm
       - garage.alarm


Any change of the item **house.alarm** and **garage.alarm** triggers the execution of the given logic.
It is possible to use an asterisk * for any path part (like a regular expression):

.. code-block:: yaml
   :caption:  Configuration in YAML syntax

   watch_item: '*.door'

this will trigger **garage.door** and also **house.door** but *not* **house.hallway.door**

cycle
~~~~~

This will trigger the given logic in a recurring way

.. code-block:: yaml
   :caption:  Configuration in YAML syntax

   cycle: 60


Optional use a parameter

.. code-block:: yaml
   :caption:  Configuration in YAML syntax

   cycle: 60 = 100


This triggers the logic every 60 seconds and passes the value 100 to the logic.
The object ``trigger['value']`` can be queried and will here result in '100'

**Since SmartHomeNG v1.3** there are extended configuration options.

The value for the ``cycle duration`` can be provided as follows:

1. a number defining the duration in seconds, can be optionally followed by an ``s``
2. a number follows by an ``m`` to define the duration in minutes

crontab
~~~~~~~

Like Unix crontab with the following options:

* ``crontab: init``
   Run the logic during the start of SmartHomeNG.

* ``crontab: minute hour day wday``
   See description of Unix crontab and some online generators for details.
   -  minute: single value from 0 to 59, or comma separated list, or * (every minute)
   -  hour: single value from 0 to 23, or comma separated list, or * (every hour)
   -  day: single value from 0 to 28, or comma separated list, or * (every day)
   Please note: dont use days greater than 28 in the moment.
   -  wday: weekday, single value from 0 to 6 (0 = Monday), or comma separated list, or * (every day)

``crontab: sunrise``
   Runs the logic at every sunrise. Use ``sunset`` to run
   at sunset. For sunset / sunrise you could provide:

   -  an horizon offset in degrees e.g. crontab: sunset-6 You have to
      specify your latitude/longitude in smarthome.conf.
   -  an offset in minutes specified by a 'm' e.g. crontab = sunset-10m
   -  a boundary for the execution

.. code-block:: yaml
   :caption:  Configuration in YAML syntax

    crontab: '17:00<sunset'        # sunset, but not bevor 17:00 (locale time)
    crontab: sunset<20:00          # sunset, but not after 20:00 (locale time)
    crontab: '17:00<sunset<20:00'  # sunset, beetween 17:00 and 20:00
    crontab: '15 * * * = 50'       # Calls the logic with trigger['value'] # == 50

Combine several options with ``|``:

.. code-block:: yaml
   :caption:  Configuration in YAML syntax

   crontab:
     - init = start
     - sunrise-2
     - '0 5 * *'

enabled
~~~~~~~

``enabled`` can be set to False to disable the execution of the logic after loading. The status
of the logic (enabled/disabled) can be controlled via the plugins ``backend`` or ``cli``

prio
~~~~

Sets the priority of the logic script within the execution context of the scheduler.
Any value between 1 to 10 is allowed where 1 has the highest priority and 10 the lowest.
Usually you don't need to specify a priority. The default priority is 5.

Other parameters
~~~~~~~~~~~~~~~~

Other parameters could be accessed from the the logic with self.parameter_name.
Like in the first example script for the fourth logic the attribute ``usage_warning: 500``


Basic Structure of a logic script
---------------------------------

The most important object is the smarthome object ``sh``.
Using this object all items, plugins and basic functions of SmartHomeNG can be accessed.
To query an item's value call: ``sh.area.item()``
To set a new value just specify it as argument sh.area.item(new\_value).

.. code-block:: python

   #!/usr/bin/env python
   # put on the light in the living room, if it is not on
   if not sh.living_room.light():
       sh.living_room.light('on')

Items need to be accessed with parentheses, otherwise an exception will be raised

``sh`` can be used to iterate over the item objects:

.. code-block:: python

   for item in sh:
       print item
       for child_item in item:
           print child_item


Loaded Python modules
---------------------

In the logic environment are several python modules already loaded:

-  sys
-  os
-  time
-  datetime
-  ephem
-  random
-  Queue
-  subprocess

you could however import more modules as needed with the import statement.


Available Objects/Methods
-------------------------

Beside the 'sh' object other important predefined objects are available.

logic
~~~~~

This object provides access to the current logic object. It is possible
to change logic attributes (crontab, cycle, ...) during runtime. They
will be lost after restarting SmartHomeNG. ``while logic.alive:``
creates an endless loop. This way SmartHomeNG could stop the loop at
shutdown. Next section (trigger) describes the special function
``logic.trigger()``. Predefined attributs of the logic object:

-  logic.name: with the name of the logic as specified in logic.conf
-  logic.last\_time(): this function provides the last run of this logic
   (before the recent one)
-  logic.prio: read and set of the current priority of this logic.

logic.trigger()
~~~~~~~~~~~~~~~

Equal to ``sh.trigger()``, but it triggers only the current logic. This
function is useful to run the logic (again) at a specified time.

trigger
~~~~~~~

``trigger`` is a runtime environment for the logic, which provides some
information about the event that triggered the logic.

It is a dictionary which can be used by: ``trigger['by']``,
``trigger['source']``, ``trigger['dest']`` and ``trigger['value']``.

logger and sh.log
-----------------

This object is useful to generate log messages. It provides five
different log levels: debug, info, warning, error, critical.
logger.level(str) e.g. logger.info('42'). The log messages are stored in
the log file and the latest 50 entries are also in 'sh.log' available.
So its possible to access the messages by plugins (visu) and logics.
Attention: the datetime in every log entry is the timezone aware
localtime.

.. code-block:: python

   # a simple loop over the log messages
   for entry in sh.log:
       print(entry) # remark: if SmartHomeNG is run in daemon mode output by 'print' is not visible.


SmartHomeNG methods to use
--------------------------

sh.now and sh.utcnow
~~~~~~~~~~~~~~~~~~~~

These two functions return a timezone-aware datetime object. Its
possible to compute with different timezones. sh.tzinfo() and
sh.utcinfo() address a local and the UTC timezone.

sh.sun
~~~~~~

This module provides access to parameters of the sun. In order to use
this module, it is required to specify the latitude (e.g. lat = 51.1633)
and longitude (e.g. lon = 10.4476) in the smarthome.conf file!

.. code-block:: python

   # sh.sun.pos([offset], [degree=False]) specifies an optional minute offset and if the return values should be degrees instead of the default radians.
   azimut, altitude = sh.sun.pos() # return the current sun position
   azimut, altitude = sh.sun.pos(degree=True) # return the current sun position in degrees
   azimut, altitude = sh.sun.pos(30) # return the sun position 30 minutes
                                     # in the future.

   # sh.sun.set([offset]) specifies a degree offset.
   sunset = sh.sun.set() # Returns a utc! based datetime object with the next
                         # sunset.
   sunset_tw = sh.sun.set(-6) # Would return the end of the twilight.

   # sh.sun.rise([offset]) specifies a degree offset.
   sunrise = sh.sun.rise() # Returns a utc! based datetime object with the next
                           # sunrise.
   sunrise_tw = sh.sun.rise(-6) # Would return the start of the twilight.

sh.moon
~~~~~~~

Besides the three functions (pos, set, rise) it provides two more.
``sh.moon.light(offset)`` provides a value from 0 - 100 of the
illuminated surface at the current time + offset.
``sh.moon.phase(offset)`` returns the lunar phase as an integer [0-7]: 0
= new moon, 4 = full moon, 7 = waning crescent moon

Scheduling
----------

sh.scheduler.trigger() / sh.trigger()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This global function triggers any specified logic by its name.
``sh.trigger(name [, by] [, source] [, value] [, dt])`` ``name``
(mandatory) defines the logic to trigger. ``by`` a name of the calling
logic. By default its set to 'Logic'. ``source`` the reason for
triggering. ``value`` a variable. ``dt`` timezone aware datetime object,
which specifies the triggering time.

sh.scheduler.change()
~~~~~~~~~~~~~~~~~~~~~

This method changes some runtime options of the logics.
``sh.scheduler.change('alarmclock', active=False)`` disables the logic
'alarmclock'. Besides the ``active`` flag, it is possible to change:
``cron`` and ``cycle``.

sh.tools object
---------------

The ``sh.tools`` object provide some useful functions:

sh.tools.ping()
~~~~~~~~~~~~~~~

Pings a computer and returns True if the computer responds, otherwise
False. ``sh.office.laptop(sh.tools.ping('hostname'))``

sh.tools.dewpoint()
~~~~~~~~~~~~~~~~~~~

Calculate the dewpoint for the provided temperature and humidity.
``sh.office.dew(sh.tools.dewpoint(sh.office.temp(), sh.office.hum())``

sh.tools.fetch\_url()
~~~~~~~~~~~~~~~~~~~~~

Return a website as a String or 'False' if it fails.
``sh.tools.fetch_url('https://www.regular.com')`` Its possible to use
'username' and 'password' to authenticate against a website.
``sh.tools.fetch_url('https://www.special.com', 'username', 'password')``
Or change the default 'timeout' of two seconds.
``sh.tools.fetch_url('https://www.regular.com', timeout=4)``

sh.tools.dt2ts(dt)
~~~~~~~~~~~~~~~~~~

Converts an datetime object to a unix timestamp.

sh.tools.dt2js(dt)
~~~~~~~~~~~~~~~~~~

Converts an datetime object to a json timestamp.


sh.tools.rel2abs(temp, hum)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Converts the relative humidity to the absolute humidity.


Accessing items
---------------

Usage of Object ``sh`` for items is deprecated, it's better to use the Item API:

.. code:: python

   from lib.item import Items
   items = Items.get_instance()

With ``items`` Object in place the following functions can be called:

items.return_item(path)
~~~~~~~~~~~~~~~~~~~~~~~

Returns an item object for the specified path. E.g.
``items.return_item('first_floor.bath')``

items.return_items()
~~~~~~~~~~~~~~~~~~~~

Returns all item objects.

.. code-block:: python

   for item in items.return_items():
      logger.info(item.id())

items.match_items(regex)
~~~~~~~~~~~~~~~~~~~~~~~~

Returns all items matching a regular expression path and optional attribute.

.. code-block:: python

   for item in items.match_items('*.lights'):     # selects all items ending with 'lights'
       logger.info(item.id())

   for item in items.match_items('*.lights:special'):     # selects all items ending with 'lights' and attribute 'special'
       logger.info(item.id())

items.find_items(configattribute)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Depending on ``configattribute`` the following items will be returned:

.. table::

   ======================  ====================================================
   attribute               Ergebnis
   ======================  ====================================================
   ``attribute``           Only items having no instance id
   ``attribute@``          Items with or without instance id
   ``attribute@instance``  Items with exact match of attribute and instance id
   ``@instance``           Items having this instance id
   ======================  ====================================================


.. code:: python

   for item in items.find_items('my_special_attribute'):
       logger.info(item.id())

find\_children(parentitem, configattribute):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns all child items with the specified config attribute. The search for ``configattribute``
will be exactly conducted as described in ``find_items(configattribute)`` above.
