======
Logics
======

Introduction
============

Logic items within SmartHome.py are simple python scripts. SmartHome.py
expects the logic scripts in /usr/local/smarthome/logics/.

Basic Structure
===============

The most important object is 'sh'. This is the smarthome object. It
contains every detail about the smarthome. With this object it is
possible to access all items, plugins and basic functions of
SmartHome.py. To get the value of an item call the name of it:
sh.area.item(). To set a new value just specify it as argument:
sh.area.item(new\_value).

.. raw:: html

   <pre>#!/usr/bin/env python
   # put on the light in the living room, if it is not on
   if not sh.living_room.light():
       sh.living_room.light('on')
   </pre>

It is very important to access the items always with parantheses ()!
Otherwise an error could occur.

It is possible to iterate over ``sh`` and the item objects.

.. raw:: html

   <pre>
   for item in sh:
       print item
       for child_item in item:
           print child_item
   </pre>

Available Objects/Methods
=========================

Beside the 'sh' object other important predefined objects are available.

logic
-----

This object provides access to the current logic object. It is possible
to change logic attributes (crontab, cycle, ...) during runtime. They
will be lost after restarting SmartHome.py. ``while logic.alive:``
creates an endless loop. This way SmartHome.py could stop the loop at
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
-------

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

.. raw:: html

   <pre># a simple loop over the log messages
   for entry in sh.log:
       print(entry) # remark: if SmartHome.py is run in daemon mode output by 'print' is not visible.
   </pre>

sh.now and sh.utcnow
--------------------

These two functions return a timezone-aware datetime object. Its
possible to compute with different timezones. sh.tzinfo() and
sh.utcinfo() address a local and the UTC timezone.

sh.sun
------

This module provides access to parameters of the sun. In order to use
this module, it is required to specify the latitude (e.g. lat = 51.1633)
and longitude (e.g. lon = 10.4476) in the smarthome.conf file!

.. raw:: html

   <pre># sh.sun.pos([offset], [degree=False]) specifies an optional minute offset and if the return values should be degrees instead of the default radians.
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
   </pre>

sh.moon
-------

Besides the three functions (pos, set, rise) it provides two more.
``sh.moon.light(offset)`` provides a value from 0 - 100 of the
illuminated surface at the current time + offset.
``sh.moon.phase(offset)`` returns the lunar phase as an integer [0-7]: 0
= new moon, 4 = full moon, 7 = waning crescent moon

sh item methods
---------------

sh.return\_item(path)
~~~~~~~~~~~~~~~~~~~~~

Returns an item object for the specified path. E.g.
``sh.return_item('first_floor.bath')``

sh.return\_items()
~~~~~~~~~~~~~~~~~~

Returns all item objects.
``for item in sh.return_items():     logger.info(item.id())``

sh.match\_items(regex)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns all items matching a regular expression path and optional attribute.
``for item in sh.match_items('*.lights'):     # selects all items ending with 'lights'     logger.info(item.id())``
``for item in sh.match_items('*.lights:special'):     # selects all items ending with 'lights' and attribute 'special'     logger.info(item.id())``

sh.find\_items(configattribute)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns all items with the specified config attribute
``for item in sh.find_items('my_special_attribute'):     logger.info(item.id())``

find\_children(parentitem, configattribute):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Returns all children items with the specified config attribute.

sh.scheduler
------------

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

sh.tools
--------

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



Loaded modules
==============

In the logic environment are several python modules already loaded:

-  sys
-  os
-  time
-  datetime
-  ephem
-  random
-  Queue
-  subprocess

