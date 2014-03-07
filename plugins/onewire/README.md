# 1-Wire

Requirements
============
This plugin needs an running owserver from owfs. I have tested owfs-2.7p34 and owfs-2.8p15.

Hint: to run the owserver as non root. You have to add a udev rule for the usb busmasters.
<pre># /etc/udev/rules.d/80-smarthome.rules
SUBSYSTEM=="usb",ENV{DEVTYPE}=="usb_device",ATTR{idVendor}=="04fa", ATTR{idProduct}=="2490",GROUP="smarthome",MODE="0660"
</pre>

Hint2: You can also use a running owserver on another host.

Configuration
=============

plugin.conf
-----------
<pre>
[ow]
    class_name = OneWire
    class_path = plugins.onewire
#    host = 127.0.0.1
#    port = 4304
</pre>

This plugins is looking by default for the owserver on 127.0.0.1 port 4304. You could change this in your plugin.conf.

Advanced options in plugin.conf. Please be careful.

* 'cycle' = timeperiod between two sensor cycles. Default 300 seconds. If you decrease the cycle to much you could destabilise the bus, because of the increased power consumption.
* 'io_wait' = timeperiod between two requests of 1-wire I/O chip. Default 5 seconds.
* 'button_wait' = timeperiod between two requests of ibutton-busmaster. Default 0.5 seconds.



items.conf
--------------

### name
This is a name for the defined sensor information.

### type
This is the type of the sensor data. Currently 'num' and 'bool' are supported.

### ow_addr
'ow_addr' defines the 1wire adress of the sensor (formerly 'ow_id'). If 'ow_addr' is specified, the 1wire plugin monitors this sensor.

### ow_sensor
'ow_sensor' defines the particular data of the sensor. Currently are supported:

* 'T' - temperature - could be T, T9, T10, T11, T12 (depends on accuracy, but more accuracy needs more time!)
* 'H' - humidity
* 'L' - light intensity (lux)
* 'V' - voltage
* 'Ix' - input - could be IA or IB (depends on the choosen input)
* 'Ox' - output - could be OA or OB (depends on the choosen output)
* 'VDD' - voltage of sensor powering (most DS2438 based sensors)

For ibuttons:

* 'BM' - ibutton master
* 'B' - ibutton

If an ibutton master ('BM') is specified, the 1-wire plugin will monitor this bus with a higher frequency for changes.
The ibutton sensor ('B') returns 'true', if the ibutton is present or 'false', if not.
If I/O sensors (2406) are specified they will be monitored within a shorter timeframe.

Currently the following 1wire devices are tested by users:

* DS9490 busmaster
* DS18B20 (temperature)
* Elabnet BMS v1.3  (MS-THS-13)
* Elabnet BMS v2.11 (MS-THS-21) (incl. additional lightsensor modul) 
* Elabnet AMS v2.11 (MS-THS-21) (additional '+ DS2406 dual I/O + DS2438 0-10V' are untested)
* DATANAB DS2438 (rugged temp/hum)
* D2PC (dual I/O DS2406)

<pre>
[test-1wire]
    [[bm-ibutton]]
        name = ibutton busmaster to identify ibutton buses
        type = bool
        ow_addr = 81.75172D000000
        ow_sensor = BM
    [[ib-guest]]
        name = ibutton guest
        type = bool
        ow_addr = 01.787D58130000
        ow_sensor = B
    [[temp_outside]]
        name = temperature outside
        type = num
        ow_addr = 28.8DEAAA030000
        # could be T, T9, T10, T11, T12
        ow_sensor = T
    [[lux_outside]]
        name = lux / lightintensity outside
        type = num
        ow_addr = 26.8DD76B010000
        ow_sensor = L
    [[humidity_outside]]
        name = humidity outside
        type = num
        ow_addr = 26.8DD76B010000
        ow_sensor = H
    [[input_water_leak]]
        name = input water leak detection
        type = bool
        ow_addr = 3A.C6CC07000000
        # could be IA, IB
        ow_sensor = IA
    [[output_led1]]
        name = output led1 keys
        type = bool
        ow_addr = 3A.C6CC07000000
        # could be OA, OB
        ow_sensor = OB
    [[voltage_sensor]]
        name = voltage of the sensor input (0-10V)
        type = num
        ow_addr = 26.A9D76B010000
        ow_sensor = V
</pre>

Functions
=========

ibutton_hook(ibutton, item)
--------------------------------

This is a special function which is called if an unknown ibutton is attached to the bus.
If the unknown ibutton is already seen, the id will be cached and the function is not called again. The cache will be reset every ten minutes.
The function must take two arguments. The first will be the id of the ibutton and the second is the item of the ibutton busmaster (e.g. `sh.home.key_hanger`).

To use it you have to assign a (useful) function. For this you could do something like this:

<pre># my startup.py logic which is called at startup with crontab = init
def intruder_alert(ibutton_id, item):
    sh.notify("iButton-Alert","Someone uses an unknown iButton ({0}) at {1}".format(ibutton_id, item))
    # sh.take_picuture()
    # ...

sh.ow.ibutton_hook = intruder_alert</pre>

