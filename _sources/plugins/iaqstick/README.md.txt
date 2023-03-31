# iaqstick

## Requirements

* pyusb
* udev rule

install by
```bash
apt-get install python3-setuptools
pip3 install "pyusb>=1.0.2"
```

```
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="03eb", ATTR{idProduct}=="2013", MODE="666"' > /etc/udev/rules.d/99-iaqstick.rules
udevadm trigger
```

## Supported Hardware

* Applied Sensor iAQ Stick
* Voltcraft CO-20 (by Conrad)
* others using the same reference design

## Configuration

### plugin.yaml

```yaml
iaqstick:
    plugin_name: iaqstick
#    update_cycle: 10
```

Description of the attributes:

* __update_cycle__: interval in seconds how often the data is read from the stick (default 10)

### items.yaml

Attributes:
* __iaqstick_id__: used to distinguish multiple sticks
* __iaqstick_info__: used to get data from the stick

To get the Stick-ID, start sh.py and check the log saying: "iaqstick: Vendor: AppliedSensor / Product: iAQ Stick / Stick-ID: <this-is-your-stick-id>".
Don't bother if you are going to use a single stick anyway.

Fields:
* __ppm__: get the air quality measured in part-per-million (ppm)

```yaml
iAQ_Stick:
  PPM:
    type: num
    iaqstick_id: H02004-266272
    iaqstick_info: ppm
```
