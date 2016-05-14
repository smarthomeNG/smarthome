# Easymeter

# Requirements
## Supported Hardware

* Easymeter Q3D with ir-reader from volkszaehler.org

# Configuration
## plugin.conf

<pre>
[easymeter]
    class_name = easymeter
    class_path = plugins.easymeter
</pre>

Parameter for serial device are currently set to fix 9600/7E1.

Description of the attributes:

* none

## items.conf

* __easymeter_code__: obis protocol code

* __device__: USB device for ir-reader from volkszaehler.org

### Example

<pre>
# items/easymeter.conf

[output]
  easymeter_code = 1-0:21.7.0*255
  device = /dev/ttyUSB0
  type = num
</pre>


Please take care, there are different obis codes for different versions of Easymeter Q3D.
For example Version 3.02 reports obis code 1-0:21.7.0*255, version 3.04 
reports 1-0:21.7.255*255.
