KNX
===

This plugin send and receive messages to and from KNX bus.

Requirements
------------

This plugin needs a running eibd or knxd.

Configuration
-------------

plugin.conf
~~~~~~~~~~~

.. raw:: html

   <pre>
   [knx]
      class_name = KNX
      class_path = plugins.knx
   #   host = 127.0.0.1
   #   port = 6720
      send_time = 600 # update date/time every 600 seconds, default none
      time_ga = 1/1/1 # default none
      date_ga = 1/1/2 # default none
   #   busmonitor = False
   #   readonly = False
   </pre>

This plugins is looking by default for the eibd on 127.0.0.1 port 6720.
You could change this in your plugin.conf. If you specify a
``send_time`` intervall and a ``time_ga`` and/or ``date_ga`` the plugin
sends the time/date every cycle seconds on the bus.

If you set ``busmonitor`` to True, every KNX packet will be logged. If
you set ``readonly`` to True, the plugin only read the knx bus and send
no group message to the bus.

items.conf
~~~~~~~~~~

knx\_dpt
........

This attribute is mandatory. If you don't provide one the item will be
ignored. The DPT has to match the type of the item!

The following datapoint types are supported:

+-----------+------------+---------+-------------------------------------+
| DPT       | Data       | Type    | Values                              |
+===========+============+=========+=====================================+
| 1         | 1 bit      | bool    | True \| False                       |
+-----------+------------+---------+-------------------------------------+
| 2         | 2 bit      | list    | [0, 0] - [1, 1]                     |
+-----------+------------+---------+-------------------------------------+
| 3         | 4 bit      | list    | [0, 0] - [1, 7]                     |
+-----------+------------+---------+-------------------------------------+
| 4.002     | 8 bit      | str     | 1 character (8859\_1) e.g. 'c'      |
+-----------+------------+---------+-------------------------------------+
| 5         | 8 bit      | num     | 0 - 255                             |
+-----------+------------+---------+-------------------------------------+
| 5.001     | 8 bit      | num     | 0 - 100                             |
+-----------+------------+---------+-------------------------------------+
| 6         | 8 bit      | num     | -128 - 127                          |
+-----------+------------+---------+-------------------------------------+
| 7         | 2 byte     | num     | 0 - 65535                           |
+-----------+------------+---------+-------------------------------------+
| 8         | 2 byte     | num     | -32768 - 32767                      |
+-----------+------------+---------+-------------------------------------+
| 9         | 2 byte     | num     | -671088,64 - 670760,96              |
+-----------+------------+---------+-------------------------------------+
| 10        | 3 byte     | foo     | datetime.time                       |
+-----------+------------+---------+-------------------------------------+
| 11        | 3 byte     | foo     | datetime.date                       |
+-----------+------------+---------+-------------------------------------+
| 12        | 4 byte     | num     | 0 - 4294967295                      |
+-----------+------------+---------+-------------------------------------+
| 13        | 4 byte     | num     | -2147483648 - 2147483647            |
+-----------+------------+---------+-------------------------------------+
| 14        | 4 byte     | num     | 4-Octet Float Value IEEE 754        |
+-----------+------------+---------+-------------------------------------+
| 16        | 14 byte    | str     | 14 characters (ASCII)               |
+-----------+------------+---------+-------------------------------------+
| 16.001    | 14 byte    | str     | 14 characters (8859\_1)             |
+-----------+------------+---------+-------------------------------------+
| 17        | 8 bit      | num     | Scene: 0 - 63                       |
+-----------+------------+---------+-------------------------------------+
| 20        | 8 bit      | num     | HVAC: 0 - 255                       |
+-----------+------------+---------+-------------------------------------+
| 24        | var        | str     | ulimited string (8859\_1)           |
+-----------+------------+---------+-------------------------------------+
| 232       | 3 byte     | list    | RGB: [0, 0, 0] - [255, 255, 255]    |
+-----------+------------+---------+-------------------------------------+

If you are missing one, open a bug report or drop me a message in the
knx user forum.

knx\_send
.........

You could specify one or more group addresses to send updates to. Item
update will only be sent if the item is not changed via KNX.

knx\_status
...........

Similar to knx\_send but will send updates even for changes vie KNX if
the knx\_status GA differs from the destination GA.

knx\_listen
...........

You could specify one or more group addresses to monitor for changes.

knx\_init
.........

If you set this attribute, SmartHome.py sends a read request to
specified group address at startup and set the value of the item to the
response. It implies 'knx\_listen'.

knx\_cache
..........

If you set this attribute, SmartHome.py tries to read the cached value
for the group address. If it fails it sends a read request to specified
group address at startup and set the value of the item to the response.
It implies 'knx\_listen'.

knx\_reply
..........

Specify one or more group addresses to allow reading the item value.

logic.conf
~~~~~~~~~~

You could specify the ``knx_listen`` and ``knx_reply`` attribute to
every logic in your logic.conf. The argument could be a single group
address and dpt or a list of them.

.. raw:: html

   <pre>
   [logic1]
       knx_dpt = 9
       knx_listen = 1/1/7

   [logic2]
       knx_dpt = 9
       knx_reply = 1/1/8 | 1/1/8
   </pre>

If there is a packet directed to the according group address,
SmartHome.py would trigger the logic and will pass the payload (via the
trigger object) to the logic.

In the context of the KNX plugin the trigger dictionary consists of the
following elements:

-  trigger['by'] protocol ('KNX')
-  trigger['source'] PA (physical adress of the KNX packet source)
-  trigger['value'] payload

Example
-------

.. raw:: html

   <pre>
   [living_room]
       [[light]]
           type = bool
           knx_dpt = 1
           knx_send = 1/1/3
           knx_listen = 1/1/4 | 1/1/5
           knx_init = 1/1/4

       [[temperature]]
           type = num
           knx_dpt = 9
           knx_send = 1/1/6
           knx_reply = 1/1/6
           ow_id = 28.BBBBB20000 # see 1-Wire plugin
           ow_sensor = temperature # see 1-Wire plugin
   </pre>

..\u0020Functions
..\u0020=========

..\u0020encode(data, dpt)
..\u0020-----------------

..\u0020This function encodes your data according to the specified datapoint.

..\u0020.. raw:: html

..\u0020   <pre>data = sh.knx.encode(data, 9)</pre>

..\u0020groupwrite(ga, data, dpt)
..\u0020-------------------------

..\u0020With this function you could send the data to the specified group
..\u0020address.

..\u0020.. raw:: html

..\u0020   <pre>sh.knx.groupwrite('1/1/10', 10.3, '9')</pre>

..\u0020groupread(ga, cache=False)
..\u0020--------------------------

..\u0020This function triggers a read request on the specified group address. It
..\u0020doesn't return the received value!

..\u0020send\_time(time\_ga, date\_ga)
..\u0020------------------------------

..\u0020This funcion send the current time and or date to the specified group
..\u0020address.

..\u0020.. raw:: html

..\u0020   <pre>sh.knx.send_time('1/1/1', '1/1/2') # send the time to 1/1/1 and the date to 1/1/2
..\u0020   sh.knx.send_time('1/1/1') # only send the time to 1/1/1
..\u0020   sh.knx.send_time(data_ga='1/1/2') # only send the date to 1/1/2
..\u0020   </pre>

..\u0020Hint: instead of this function you could use the plugin attribute
..\u0020'send\_time' as described above.
