# NUT - Network UPS Tools plugin

This plugin is connecting to NUT daemon and can be used to read ups variables.

The primary goal of the Network UPS Tools (NUT) project is to provide support for Power Devices,
such as Uninterruptible Power Supplies, Power Distribution Units, Automatic Transfer Switch, Power Supply Units and Solar Controllers.

The plugin can be used standalone to list available variables using command `upsc your_ups_name`.
More about NUT: http://networkupstools.org/


## Requirements

Configured & running upsd - NUT daemon


## Configuration

### plugin.yaml

```yaml
nut:
    class_name: NUT
    class_path: plugins.nut
    ups: your_ups_name
    cycle: read cycle, optional, default 60
    host: upsd host, optional, default 'localhost'
    port: upsd port, optional, default 3493
    timeout: telnet read timeout, optional, default 5
```

## items.yaml

```yaml
ups_item:
    ...
    nut_var: variable_name_from_upsc
```

## Example

The most important variable: `ups.status` is returned from ups as string containing `OL` - OnLine, `OB` - On Battery or `LB` - LowBattery. Easy way to parse to boolean:

```yaml
ups:  
    status:
        name: Status
        type: str
        nut_var: ups.status
        online:
            type: bool
            eval_trigger: ups.status
            eval: 1 if 'OL' in sh.ups.status() else 0
        on_battery:
            type: bool
            eval_trigger: ups.status
            eval: 1 if 'OB' in sh.ups.status() else 0
        low_battery:
            type: bool
            eval_trigger: ups.status
            eval: 1 if 'LB' in sh.ups.status() else 0
    battery:
        percent:
            type: num
            sqlite: 'yes'
            nut_var: battery.charge
        voltage:
            type: num
            sqlite: 'yes'
            nut_var: battery.voltage
```

Other ups variables, like `battery.charge`, can be directly parsed to num by sh.

## Synology Example
This plugin can be used with a Synology diskstation as NUT Server. In this configuration, the UPS is connected to the Synology diskstation via USB. The Synology then can distribute
the UPS status as a NUT server. For this configuration

1) Enable the NUT option in the Synology under "Hardware and engery"->UPS->"active network UPS server"
2) Klick on "Authenticated Diskstation devices" and set the IP of the smarthomeNG computer
3) Use the following Synology default settings for configuration of the plugin:

### plugin.yaml

```yaml

    nut:
        plugin_name: nut
        ups: ups
        host: <IP of smarthomeNG system>
        port: 3493
```

