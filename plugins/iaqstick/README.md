# iAQ Stick

# Requirements

* pyusb
* udev rule

install by
<pre>
apt-get install python3-setuptools
easy_install3 pyusb
</pre>

<pre>
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="03eb", ATTR{idProduct}=="2013", MODE="666"' > /etc/udev/rules.d/99-iaqstick.rules
udevadm trigger
</pre>

## Supported Hardware

* Applied Sensor iAQ Stick
* Voltcraft CO-20 (by Conrad)
* others using the same reference design

# Configuration

## plugin.conf

<pre>
[iaqstick]
    class_name = iAQ_Stick
    class_path = plugins.iaqstick
#    update_cycle = 10
</pre>

Description of the attributes:

* __update_cycle__: interval in seconds how often the data is read from the stick (default 10)

## items.conf

Attributes:
* __iaqstick_id__: used to distinguish multiple sticks
* __iaqstick_info__: used to get data from the stick
 
To get the Stick-ID, start sh.py and check the log saying: "iaqstick: Vendor: AppliedSensor / Product: iAQ Stick / Stick-ID: <this-is-your-stick-id>".
Don't bother if you are going to use a single stick anyway.
 
Fields:
* __ppm__: get the air quality measured in part-per-million (ppm)

<pre>
[iAQ_Stick]
  [[PPM]]
    type = num
    iaqstick_id = H02004-266272
    iaqstick_info = ppm
</pre>
