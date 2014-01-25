# DLMS

# Requirements

* smartmeter using DLMS (Device Language Message Specification) IEC 62056-21
* ir reader e.g. from volkszaehler.org
* serial port/USB-serial adapter
* python3-serial

install by
<pre>
$ apt-get install python3-serial
</pre>

make sure the serial port can be used by the user executing smarthome.py

Example (adapt the vendor- and product-id!):
<pre>
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6010", MODE="666"' > /etc/udev/rules.d/99-smartmeter.rules
udevadm trigger
</pre>

If you like, you can also give the serial port a descriptive name with this.

## Supported Hardware

* smart meters using using DLMS (Device Language Message Specification) IEC 62056-21
* e.g. Landis & Gyr ZMD120

# Configuration

## plugin.conf

<pre>
[dlms]
    class_name = DLMS
    class_path = plugins.dlms
    serialport = /dev/ttyO1
#    baudrate = 300
#    update_cycle = 20
#    use_checksum = no
#    reset_baudrate = no
#    no_waiting = yes
</pre>

Description of the attributes:

* __baudrate__: sets the baudrate used for reading from the meter - can be used to force specific baudrate (300,600,1200,2400,4800,9600,auto - default: 'auto')
* __update_cycle__: interval in seconds how often the data is read from the meter - be careful not to set a shorter interval than a read operation takes (default: 60)
* __use_checksum__: controls the checksum check of the received data - disable if you get continuous checksum errors/timeouts (yes/no - default: yes)
* __reset_baudrate__: determines if the baudrate is reset to 300 baud in every read cycle or left at full speed - disable to improve performance if your meter allows it (yes/no - default: yes)
* __no_waiting__: omit additional waiting times required for some meters - enable to improve performance if your meter allows it (yes/no - default: no)

Setup procedure:

1. Set only __serialport__ and start in debug-mode
 * not working: try to disable __use_checksum__ / use fixed __baudrate__ / cry for help
 * working: move on
2. Optimize for speed
 * disable __reset_baudrate__ - still works?
 * enable __no_waiting__ - still works?
3. Read the time a reading takes from the debug-output
 * set __update_cycle__ to a meaningfull value

## items.conf

You can use all obis codes available by the meter.

To get a list of all available OBIS codes of your reader, start smarthome.py in Debug-mode. All codes which can be obtained from the reader will be printer after the first successful read operation.

Attributes:
* __dlms_obis_code__: obis code such as 'x.y', 'x.y.z' or 'x.y.z*q'
 
<pre>
[Smartmeter]
  [[Import_Energy]]
    type = num
    dlms_obis_code = 1.8.1
  [[Export_Energy]]
    type = num
    dlms_obis_code = 2.8.1
</pre>
