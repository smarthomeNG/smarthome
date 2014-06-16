# Sml

# Requirements

To use this plugin for reading data from your smart power meter hardware
you need to have a serial or network interface connected to your hardware.

Most smart power meter hardware have an optical interface on the front of
the casis. These are two IR LEDs which can be used to read data from the
power meter hardware (e.g. by using a [optical reader](http://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf)
connected to an USB port).

## Hardware

The plugin was tested with the following hardware:

   * Hager EHZ363Z5
   * Hager EHZ363W5

# Configuration

## plugin.conf

<pre>
[sml]
  class_name = Sml
  class_path = plugins.sml
  serialport = /dev/ttyUSB0
  # host = 192.168.2.1
  # port = 1234

</pre>

The plugin reads data from smart power meter hardware by using a serial
interface (e.g. /dev/ttyUSB0) or by connecting to a host/port. It reads
messages using the SML (Smart Message Language) protocol. If you
want to know more about the protocol see [here](http://wiki.volkszaehler.org/software/sml).

Usually the smart power meter hardware is sending status information
every few seconds via the interface which is read by the plugin. This
status information, consisting of a SML_PublicOpen and SML_GetList message,
provides the current power status and details (e.g. total power consumed,
current power).

All status values retrieved by these messages have a unique identifier which
is called [OBIS](http://de.wikipedia.org/wiki/OBIS-Kennzahlen) code. This can
be used to identify the meaning of the value returned.

Description of the attributes:

   * `serialport` - defines the serial port to use to read data from
   * `host` - instead of serial port you can use a network connection
   * `port` - additionally to the host configuration you can specify a port

If you have more then one power meter device or serial device in use,
please configure this plugin multiple times and restrict the items to
the different plugin instances using the `plugin` setting:

<pre>
[sml1]
  class_name = Sml
  class_path = plugins.sml
  serialport = /dev/ttyUSB0

[sml2]
  class_name = Sml
  class_path = plugins.sml
  serialport = /dev/ttyUSB1
</pre>

<pre>
[power]
  [[home]]
    [[[total]]]
      type = num
      plugin = sml1
      sml_obis = 1-0:1.8.0*255
  [[pv]]
    [[[total]]]
      type = num
      plugin = sml2
      sml_obis = 1-0:1.8.0*255
</pre>


## items.conf

You can assign a value retrieved by the plugin to some of your items
using the OBIS identifier.

Here's a list of OBIS codes which may be useful:

   * 129-129:199.130.3*255 - Manufacturer
   * 1-0:0.0.9*255 - ServerId / serial number
   * 1-0:1.8.0*255 - Total kWh consumption (in)
   * 1-0:1.8.1*255 - Tariff 1 kWh consumption (in)
   * 1-0:1.8.2*255 - Tariff 2 kWh consumption (in)
   * 1-0:2.8.0*255 - Total kWh delivery (out)
   * 1-0:2.8.1*255 - Tariff 1 kWh delivery (out)
   * 1-0:2.8.2*255 - Tariff 2 kWh delivery (out)
   * 1-0:16.7.0*255 - Current Delivery Watt (out)

### sml_obis

This assigns the value for the given OBIS code to the item.

e.g. sml_obis = 1-0:1.8.0*255

### Example

Here you can find a sample configuration:

<pre>
[power]
  [[home]]
    [[[total]]]
      type = num
      sml_obis = 1-0:1.8.0*255
    [[[current]]]
      type = num
      sml_obis = 1-0:16.7.0*255
</pre>

## logic.conf
Currently there is no logic configuration for this plugin.


# Methodes
Currently there are no functions offered from this plugin.
