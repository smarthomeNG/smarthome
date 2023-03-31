# CO2Meter

## Description

The CO2Meter Plugin allows to access a Dostmann TFA Dostmann AirCO2ntrol device via its raw USB data.

## Requirements

There are no requirements for this plugin.

Forum thread to the plugin: https://knx-user-forum.de/forum/supportforen/smarthome-py/1165010-supportthread-f%C3%BCr-das-co2meter-plugin

The code was adapted from the CO2Meter project Copyright 2017 by Michael Heinemann under MIT License 
(https://github.com/heinemml/CO2Meter/).

## Configuration

### plugin.yaml
```yaml
co2meter:
    plugin_name: co2meter
    device: '/dev/hidraw0'
    time_sleep: 5
```
#### Attributes
  * `device`: Path to raw usb data (optional, default: /dev/hidraw0)
  * `time_sleep`: Seconds to wait after each request (optional, default: 5)
  
### items.yaml

#### co2meter_data_type
This attribute defines supported values of the co2 meter. Full set of tested values see example below.

#### Example
```yaml
co2:

    temperature:
        type: num
        co2meter_data_type: temperature
 
    co2:
        type: num
        co2meter_data_type: co2
```

