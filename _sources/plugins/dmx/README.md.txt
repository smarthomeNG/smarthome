# DMX

## Requirements

This plugin needs one of the supported DMX interfaces:

   * [NanoDMX](http://www.dmx4all.de/)
   * [DMXking](http://www.dmxking.com) it should work with other Enttec Pro compatible as well.

The communication with the interface is handled via serial interface. Thus Python serial driver is need as well.
A requirements file is provided to easy the installation.

## Configuration

### plugin.yaml

```yaml
dmx:
    plugin_name: dmx
    serialport: /dev/usbtty...
    # interface = nanodmx
```

With ``interface``  it can be chosen between ``nanodmx`` and ``enttec``. By default nanodmx is used.

The serialport must match the real interface. On Linux it might be necessary to create a udev rule.
For a NanoDMX device provided via ``/dev/usbtty-1-2.4`` the following udev rule could match:

```bash
# /etc/udev/rules.d/80-smarthome.rules
SUBSYSTEMS=="usb",KERNEL=="ttyACM*",ATTRS{product}=="NanoDMX Interface",SYMLINK+="usbtty-%b"
```

Please consult the online help for Linux on how to properly create udev rules.

### items.yaml

#### dmx_ch

With this attribute one or more DMX channels given as integer can be specified

### Example

```yaml
living_room:

    dimlight:
        type: num
        dmx_ch:
          - 10
          - 11

    dimlight_reading:
        type: num
        dmx_ch: 23
```

In a logic an expression like  ``sh.living_room.dimlight(80)`` will send ``80`` to channels ``10`` and ``11`` to dim the living room light
as ``sh.living_room.dimlightreading(50)`` will send ``50`` to channel ``23`` to dim the living room reading light.


## Methods

### send(channel, value)

Sends the value to the given dmx channel. The value may be in range from ``0`` to ``255``.

Example: ``sh.dmx.send(12, 255)`` will send the value ``255`` to channel ``12``

