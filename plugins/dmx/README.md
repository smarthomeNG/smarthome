# DMX

Requirements
============
This plugin needs one of the supported DMX interfaces:

   * [NanoDMX](http://www.dmx4all.de/)
   * [DMXking](http://www.dmxking.com) it should work with other Enttec Pro compatible as well.

and pyserial.

<pre>apt-get install python-serial</pre>

Configuration
=============

plugin.conf
-----------
<pre>
[dmx]
   class_name = DMX
   class_path = plugins.dmx
   tty = /dev/usbtty...
#  interface = nanodmx
</pre>

You have to adapt the tty to your local enviroment. In my case it's <code>/dev/usbtty-1-2.4</code> because I have the following udev rule:

<pre># /etc/udev/rules.d/80-smarthome.rules
SUBSYSTEMS=="usb",KERNEL=="ttyACM*",ATTRS{product}=="NanoDMX Interface",SYMLINK+="usbtty-%b"</pre>

With 'interface'  you could choose between 'nanodmx' and 'enttec'. By default nanodmx is used.

items.conf
--------------

### dmx_ch
With this attribute you could specify one or more DMX channels.

# Example
<pre>
[living_room]
    [[dimlight]]
        type = num
        dmx_ch = 10 | 11
</pre>

Now you could simply use:
<pre>sh.living_room.dimlight(80)</pre> to dim the living room light.

Functions
=========

send(channel, value)
--------------------
This function sends the value to the dmx channel. The value could be 0 to 255.
<pre>sh.dmx.send(12, 255)</pre>
