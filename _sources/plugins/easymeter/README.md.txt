# Easymeter

## Requirements

* smartmeter using DLMS (Device Language Message Specification) IEC 62056-21
* USB IR-Reader e.g. from volkszaehler.org

install with
```
sudo python3 -m pip install pyserial
```

make sure the serial port can be used by the user executing smarthome.py

Example for a recent version of the Volkszaehler IR-Reader, please adapt the vendor- and product-id for your own readers:

```
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", ATTRS{serial}=="0092C9FE", MODE="0666", GROUP="dialout", SYMLINK+="dlms0"' > /etc/udev/rules.d/11-dlms.rules
udevadm trigger
```
If you like, you can also give the serial port a descriptive name with this.

## Supported Hardware

* Easymeter Q3D with ir-reader from volkszaehler.org

## Configuration

### plugin.yaml

```yaml
easymeter:
    class_name: easymeter
    class_path: plugins.easymeter
```

Parameter for serial device are currently set to fix 9600/7E1.

Description of the attributes:

* none

### items.yaml

* __easymeter_code__: obis protocol code

* __device__: USB device for ir-reader from volkszaehler.org

### Example

```yaml
output:
    easymeter_code: 1-0:21.7.0*255
    device: /dev/ttyUSB0
    type: num
```

Please take care, there are different obis codes for different versions of Easymeter Q3D.
For example Version 3.02 reports obis code 1-0:21.7.0*255, version 3.04
reports 1-0:21.7.255*255.
