+-------------------+
| title: Overview   |
+-------------------+
| layout: default   |
+-------------------+
| summary:          |
+-------------------+
| uid: index        |
+-------------------+

SmartHome.py is a modular framework to automate your (smart) home.

See the `install <install>`_ and `config <config>`_ section to start
your SmartHome.

You would like to support SmartHome.py?

.. raw:: html

   <form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">

.. raw:: html

   </form>

2013-06-13: New Release `0.9 <https://github.com/mknx/smarthome/tags>`_
-----------------------------------------------------------------------

with code contributions and help from: Alexander Rieger, Matthias Lemke
and Niko Will!

New Plugins
~~~~~~~~~~~

-  `Fritzbox Plugin <plugins/fritzbox>`_: control anything a FritzBox
   offers with the web interface.
-  `Luxtronic2 Plugin <plugins/luxtronic2>`_: get state information and
   control Luxtronic 2.0 heating controllers.
-  `MPD Plugin <plugins/mpd>`_: to control Music Player Daemons.
-  `Samsung Smart TV Plugin <plugins/smarttv>`_: send commands to a
   SmartTV device.
-  `Solarlog Plugin <plugins/solarlog>`_: to retrieve information from
   SolarLog devices.
-  `SQLite Plugin <plugins/sqlite>`_: to store the item history in a
   SQLite database.
-  `XBMC Plugin <plugins/xbmc>`_: to control and monitor your XBMC.

Features
~~~~~~~~

-  `Item <config>`_: setting values with the crontab and cycle attribute
-  `Logic <logic>`_: Logic: calling with values by crontab and cycle
-  `Logic <logic>`_: trigger supports destinations in
   ``trigger['dest']``
-  `Logic <logic>`_: de-/activate logics. e.g.
   ``sh.scheduler.change('alarmclock', active=False)``
-  `Logic <logic>`_: new basic methods: sh.return\_item,
   sh.return\_items, sh.match\_items, sh.find\_items, find\_children
-  `Scene support <config>`_: to set multiple item values at the same
   time
-  `1-Wire Plugin <plugins/onewire>`_: rewritten to support many
   different sensors.
-  `Asterisk <plugins/asterisk>`_: adding destination support for
   Userevents
-  `CLI plugin <plugins/cli>`_: new command 'cl' to clean the memory log
   of sh.py
-  `DWD Plugin <plugins/dwd>`_: adding support for Pollen forecast
-  `KNX Plugin <plugins/knx>`_:

   -  change encoding of dpt10 to use a datetime object and send the
      isoweekday
   -  DPT 17 support
   -  adding support to log all packets (busmonitor)

-  `Mail Plugin <plugins/mail>`_: enable sending UTF-8 mails
-  `Visu Plugin <plugins/visu>`_:

   -  change url
   -  smartVISU support multiple widgets with one item

Bug Fixes
~~~~~~~~~

-  KNX Plugin: fix broken knx\_cache, with support from
   Robert@knx-user-forum

2013-02-11: Big Picture SmartHome.py with KNX, 1-Wire and smartVISU
-------------------------------------------------------------------

`Martin <http://knx-user-forum.de/members/sipple.html>`_ has created an
`overview </_static/img/big_picture.pdf>`_ how SmartHome.py interacts
with KNX, 1-Wire and the smartVISU.

2013-02-02: `Release of an Raspberry Pi image with SmartHome.py and smartVISU <https://github.com/mknx/smarthome/wiki/SmartHome.pi>`_
-------------------------------------------------------------------------------------------------------------------------------------

2013-01-31 New Release `0.8 <https://github.com/mknx/smarthome/tags>`_
----------------------------------------------------------------------

with contributions from: Niko Will and Alexander Rieger. Thank you.

I am happy to announce a new cooperation with
`smartVISU <http://code.google.com/p/smartvisu/>`_ to give you the best
user interface experience.

New Plugins
~~~~~~~~~~~

-  `DWD Plugin <plugins/dwd>`_: fetch weather warnings and forecasts
   from Deutscher Wetterrdienst (DWD).
-  `Mail Plugin <plugins/mail>`_: sending (SMTP) and receiving (IMAP)
   mail.
-  `RRD Plugin <plugins/rrd>`_: build round robin databases.
-  `Russound Plugin <plugins/russound>`_: control a Russound audio
   device with RIO over TCP.
-  `Snom Plugin <plugins/snom>`_: to handle snom VOIP phones.

Features
~~~~~~~~

-  Base

   -  sh.tools.fetch\_url()
   -  item.conf: new types list, dict
   -  sh.moon() with set(), rise(), pos(), light(), phase()
   -  sh.find\_items('config\_string'), sh.find\_children(self, parent,
      'config\_string')

-  Asterisk plugin: Call Log and mailbox count
-  CLI plugin: adding 'rl' to reload and 'rr' to reload and run logic
-  KNX plugin: DPT 16 support
-  Network plugin: adding a simple http interface
-  Visu plugin:

   -  `smartVISU <http://code.google.com/p/smartvisu/>`_ support: to
      generate pages for and communicate with this visualisation
      framework.
   -  plot rrd with flot
   -  list view
   -  dpt3 push buttons
   -  TITLE header template
   -  adding 'unit' attribute to item.conf
   -  JQuery: 1.8.3, JQuery Mobile 1.2
   -  Log view SmartHome.py, Asterisk

Bug Fixes
~~~~~~~~~

-  KNX plugin: knx\_init/knx\_cache could not work if first connection
   attempt failed

   -  dpt 10, 11, 16 handling fix

-  Onewire plugin: improve error handling
-  Workaround for urllib2 memory leakage

2012-09-27 New Release `0.7 <https://github.com/mknx/smarthome/tags>`_
----------------------------------------------------------------------

Features
~~~~~~~~

-  Items

   -  Trees: You could now build unlimited item trees.
   -  id(): function to return the item id (path).
   -  eval: see the item configuration page for an explanation for
      'eval' and 'eval\_trigger'.

-  `Asterisk plugin <plugins/asterisk>`_: new function hangup(channel)
-  `iCal plugin <plugins/ical>`_: to parse iCal files
-  `Visu Plugin <plugins/visu>`_:

   -  autogenerate visu pages
   -  new input type 'time'

-  SmartHome.py:

   -  sh.scheduler.change
   -  directory structure cleanup: logic => logics
   -  items directory: to put multiple item configuration files in
   -  sh.tools.dewpoint(): new function to calculate the dewpoint
   -  sh.tools.ping(): moved ping to the tools object.
   -  sh.tz => sh.tzinfo(): new function tzinfo().

Bug Fixes
~~~~~~~~~

-  CLI Plugin: update attribute negated

2012-06-21 New Release `0.6 <http://sourceforge.net/projects/smarthome/files/>`_
--------------------------------------------------------------------------------

Nonfunctional changes
~~~~~~~~~~~~~~~~~~~~~

-  Redesign of the underlying framework to reduce the number of
   necessary threads and system footprint.

Features
~~~~~~~~

-  `Network plugin <plugins/network>`_ to receive TCP/UDP and send UDP
   messages and to trigger logics.
-  `DMX plugin <plugins/dmx>`_ accepts now a channel list to bound
   several channel to one item (value)
-  `KNX plugin <plugins/knx>`_ changed class options to ``host`` and
   ``port``. Adding support for more DPTs. Sending the date/time on the
   bus.
-  `Asterisk plugin <plugins/asterisk>`_ changed class options to
   ``host`` and ``port``. New functions: db\_write, db\_read and
   mailbox\_count.
-  `1-Wire plugin <plugins/onewire>`_ changed class options to ``host``
   and ``port``. Supporting the current owfs version (2.8p15). New
   function `ibutton\_hook <plugins/onewire/#ibuttonhookibutton-item>`_
   to monitor intrusion attempts.
-  `Visu <plugins/visu>`_ three new interactive image elements added:
   switch, push and set. See the example.html file. JQuery mobile
   updated to 1.1.0. Websocket default ``port`` changed to 2121.
-  New `item types </config#item-attributes>`_ list and foo.
-  New start option ``-d`` to set the log level to debug.
-  UDP plugin is no longer supported. Please use the generic network
   plugin instead.

Bug Fixes
~~~~~~~~~

-  Due to the redesign several bugs are fixed. I hope it will not
   intruduce the same amount of new bugs ;-)

2012-04-12 New Release `0.5 <http://sourceforge.net/projects/smarthome/files/>`_
--------------------------------------------------------------------------------

Features
~~~~~~~~

-  `Visu <plugins/visu>`_ with JQuery mobile
-  ping: sh.ping(host), return True if up, False if down.

Bug Fixes
~~~~~~~~~

-  using the enviroment timezone (TZ) - if provided

2011-10-29 New Release `0.4 <http://sourceforge.net/projects/smarthome/files/>`_
--------------------------------------------------------------------------------

Feature
~~~~~~~

-  KNX Reply with `KNX plugin <plugins/knx>`_

2011-08-14 New Release `0.3 <http://sourceforge.net/projects/smarthome/files/>`_
--------------------------------------------------------------------------------

Features
~~~~~~~~

-  `Asterisk plugin <plugins/asterisk>`_ to monitor channels and listen
   for UserEvents
-  `item.fade() <config#fade>`_: fade the item to a specified value
-  `item.area <config#item-attributes>`_: provides access to the area
   object
-  `logic.alive <logic/config#logic>`_: safe loop expression for a clean
   shutdown
-  `logig crontab <logic/config#crontab>`_: new keyword 'init'
-  `CLI plugin <plugins/cli/#usage>`_: new function 'tr' to trigger
   logics

Nonfunctional changes
~~~~~~~~~~~~~~~~~~~~~

-  New Logic handling. Logics share worker threads and multiple
   instances of one logic could run at the same time.
-  Two new functions to call/trigger a logic: logic.trigger() and
   sh.trigger().
-  Every logic provides an 'trigger' object with the reason of the call.

Bug Fixes
~~~~~~~~~

-  sh.sun.set() and rise provides a timezone aware datetime. :-) And a
   small fix in computing the dates.

2011-06-21 New Release `0.2 <http://sourceforge.net/projects/smarthome/files/>`_
--------------------------------------------------------------------------------

Features
~~~~~~~~

-  Two new `item attributes <config#item-attributes>`_: threshold and
   offset
-  `CLI plugin <plugins/cli/>`_ for a simple telnet interface
-  `DMX plugin <plugins/dmx/>`_ to interact with the DMX bus

Bug Fixes
~~~~~~~~~

-  sh.sun.set() provided a timezone aware datetime which results in a
   internal conflict with a third party function.
-  knx\_ga is splitted into two attributes: knx\_send, knx\_listen. See
   the `KNX plugin <plugins/knx/>`_ for more information.

2011-04-09 Initial Release
--------------------------

You could find the initial release 0.1 in the
`download <http://sourceforge.net/projects/smarthome/files/>`_ section.
