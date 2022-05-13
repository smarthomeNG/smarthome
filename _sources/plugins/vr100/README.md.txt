# VR100

## Requirements

bluez

install by
```bash
$ apt-get install bluez
$ hcitool scan
Scanning ...
        <bt-addr>       <name of your bluetooth-module, e.g. 'HC-05' or custom>
$ simple-agent hci0 <bt-addr>
RequestPinCode (/org/bluez/3070/hci0/dev_bt_addr_underscores)
Enter PIN Code: <pin-code>
Release
New device (/org/bluez/3070/hci0/dev_bt_addr_underscores)
$ bluez-test-device trusted <bt-addr> yes
$ bluez-test-device list
```

## Supported Hardware

A Vorwerk Kobold VR100 robotic vacuum cleaner with a retrofitted bluetooth module.

## Configuration

### plugin.yaml

```
vr100:
    class_name: VR100
    class_path: plugins.vr100
    bt_addr: 07:12:07:xx:xx:xx
    # update_cycle: 60
```

Description of the attributes:

* __bt_addr__: MAC-address of the robot (find out with 'hcitool scan')
* __update_cycle__: interval in seconds how often the data is read from the robot (default 60)

### items.yaml

You can use all commands available by the serial interface.

For a explanation of all available commands type 'help' when connected to robot

Attributes:
* __vr100_cmd__: used to set a comand string
* __vr100_info__: used to get data from the robot - all but the last strings are send as a comand, the last string is read to get the value

Fields:
* __{}__: the value of the item is written to this placeholder (don't use if a fixed/no value is required)

You should verify all your commands manually by using the serial interface.

```yaml
VR100:

    Reinigung:
        type: bool
        vr100_cmd: Clean

        Spot:
            type: bool
            vr100_cmd: Clean Spot

    Batterie:

        Fuellstand:
            type: num
            sqlite: 'true'
            vr100_info: GetCharger FuelPercent

        Ladung_aktiv:
            type: bool
            vr100_info: GetCharger ChargingActive

        leer:
            type: bool
            vr100_info: GetCharger EmptyFuel

        Spannung:
            type: num
            sqlite: 'true'
            vr100_info: GetCharger VBattV
```
