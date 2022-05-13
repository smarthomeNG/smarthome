# Sml

## Requirements

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
   * EHM eHZ-GW8 E2A 500 AL1
   * EHM eHZ-ED300L

## Configuration

### plugin.yaml

```
sml:
  class_name: Sml
  class_path: plugins.sml
  serialport: /dev/ttyUSB0
  # host: 192.168.2.1
  # port: 1234
  # device: raw | hex | <known-device>
```

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
   * `device` - specifies connected device to indicate pre-processing

The `device` attribute can be used to specify the connected device and the
kind of data delivery. Since different devices (e.g. when connecting the
power meter device via a LAN gateway) the data can be differently. Usually
when connecting a serial device directly to the power meter device the
raw data can be directly used with this plugin. Some other devices needs
to be configured.

The following kinds of device types are supported:
   * `raw` - this is the default and means the raw SML binary data is
     send to the plugin
   * `hex` - can be used in case the SML data is encoded as hex string
   * or a known device name

In case you have a known device you can also specify this and the plugin
knows which data pre-processing is required. The following known devices
are supported:
   * `smart-meter-gateway-com-1` - The Smart Meter Gateway COM-1
     http://shop.co-met.info/artikeldetails/kategorie/Smart-Metering/artikel/smart-meter-gateway-com-1.html

### items.yaml

You can assign a value retrieved by the plugin to some of your items by
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

Instead of assigning the value for a given OBIS code, you can also assign meta
information for an OBIS code which is included in the data packet sent from
the power meter device.

For the complete list of properties for an OBIS code see below. They can be
assigned to items using the `sml_prop` attribute. In case one property is not
available or explicitely unset it's value will be set to None.

The following properties are available:
   * `objName` - this is the OBIS code as string / binary data
   * `status` - a status value
   * `valTime` - the time of value (as seconds of unit start or as timestamp)
   * `unit` - identifies the value's unit (e.g. W, kWh, V, A, ...)
   * `scaler` - the scaler (10-factor shift) used to calculate the real value
   * `value` - the value
   * `signature` - the signature to protect the payload

Additionally the following attributes will be calculated and also be provided:
   * `obis` - the OBIS code as string
   * `valueReal` - the real value when including the scaler calculation
   * `unitName` - the name of the unit



#### sml_obis

This assigns the value for the given OBIS code to the item.

```yaml
sml_obis: 1-0:1.8.0*255
```

#### sml_prop

Use this to assign other information for an OBIS code to the item. When not
explicitely specified it defaults to `valueReal`.

```yaml
sml_prop: unitName
```

#### Example

Here you can find a sample configuration:

```yaml
power:

    home:

        total:
            type: num
            sml_obis: 1-0:1.8.0*255

        current:
            type: num
            sml_obis: 1-0:16.7.0*255

        unit:
            type: num
            sml_obis: 1-0:16.7.0*255
            sml_prop: unitName
```

### logic.yaml
Currently there is no logic configuration for this plugin.


## Methodes
Currently there are no functions offered from this plugin.
