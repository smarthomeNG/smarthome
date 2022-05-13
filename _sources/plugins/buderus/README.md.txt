# Buderus Plugin

Plugin to control [Buderus heating systems](https://www.buderus.de/de) using an additional Logamatic web KM200 module. See section 'supported hardware' for more specific information.

__Disclaimer__

This plugin is still *under development*! The original author used this plugin
to lower heating when no presence is detected for longer period or
when the alarm system is activated.

__Limitations__
- Holiday modes are not available yet
- Heating circuits switch program modification is not possible

## Requirements

### Needed software

* SmartHomeNG V1.6 or later
* Python modules: see **requirements.txt** in the plugin directory

### Supported Hardware

* Buderus Gateway KM200 (see https://www.buderus.com/ch/de/ocs/wohngebaeude/gateway-km200-632270-p/)
* Logamatic web KM50 and KM300 modules should also be supported. (NOT TESTED)

## Change history

### Changes Since version 1.0.2

- Improved the documentation
- Introduced structs in `plugin.yaml` to ease the integration

## Configuration 

### plugin.yaml

The plugin can be configured with the following parameters:

| Parameter  | Description | Required
| ------------- | ------------- | ------------- |
| class_name  | Must be set to `Buderus`  | Yes  |
| class_path  | Must be set to `plugins.buderus`  | Yes  |
| host  | IP address of the KM200 gateway. e.g. `192.168.2.28`  | Yes  |
| key  | Security key which must be created beforehand from your device password (printed on the KM200) and your user defined password (set in the EasyControl App): https://ssl-account.com/km200.andreashahn.info/  | Yes  |
| cycle_time  | Information will be fetched from KM200 every X seconds. Defaults to 900, meaning an update will be pulled every 15 minutes.  | - |

The following example can be used to setup a device:

```yaml
buderus:
    class_name: Buderus
    class_path: plugins.buderus
    host: 192.168.2.28
    key: 90ad52660ce1234551234579d89e25b70b5331ce0e82c5fd1254a317574ec807
```

### items.yaml

The plugin provides ready to use structs for easy integration into your item configuration.

| Item  | Description |
| ------------- | ------------- |
| gateway  | Information about the KM200 gateway itself.  |
| heating_system  | Information about the connected heating system (e.g. current power, temperatures, ...)  |
| heating_circuit_01  | Information about the heating circuit 01.   |
| hot_water_circuit_01  | Information about the hot water circuit 01.   |

Please see the following example:

```yaml
Buderus:
  gateway:
    struct: buderus.gateway
  heating_system:
    struct: buderus.heating_system
  heating_circuit_01:
    struct: buderus.heating_circuit_01
  hot_water_circuit_01:
    struct: buderus.hot_water_circuit_01
```

See [URLs](URLs.md) for additional km_id's. 

# Appendix
- [ioBroker Modul for KM200](https://github.com/frankjoke/ioBroker.km200)
