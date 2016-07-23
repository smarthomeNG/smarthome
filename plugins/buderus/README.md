# smarthome-buderus

Plugin to control Buderus boilers using an additional Logamatic web KM200 module. Logamatic web KM50 and KM300 modules should also be supported.


## Notes
This plugin is still __under development__! I use this plugin to lower heating when no presence is detected for longer period or when the alarm system is activated.

## Prerequisite
The following python packages need to be installed on your system:
- urllib
- crypto

You need to generate a key from your a) device password, printed on a sticker and b) from your user defined password used to access EasyControl App for example.


## Installation
<pre>
cd smarthome.py directory
cd plugins
git clone https://github.com/rthill/buderus.git
</pre>

### plugin.conf
```
[buderus]
class_name = Buderus
class_path = plugins.buderus
host = <ip_address>
key = <key generated from https://ssl-account.com/km200.andreashahn.info/>
cycle = 900 # default every 15 minutes
```

### items.conf

```
[buderus]
    [[info]]
        [[[datetime]]]
             type = str
             km_id = "/gateway/DateTime"
        [[[firmware]]]
             type = str
             km_id = "/gateway/versionFirmware"
        [[[hardware]]]
             type = str
             km_id = "/gateway/versionHardware"
        [[[brand]]]
             type = str
             km_id = "/system/brand"
        [[[health]]]
             type = str
             km_id = "/system/healthStatus"        
    [[sensors]]
        [[[outside]]]
            type = num
            km_id = "/system/sensors/temperatures/outdoor_t1"
            Influx = true
        [[[supply]]]
            type = num
            km_id = "/system/sensors/temperatures/supply_t1"
            Influx = true
        [[[hotwater]]]
            type = num
            km_id = "/system/sensors/temperatures/hotWater_t2"
            Influx = true
    [[boiler]]
        [[[flame]]]
            type = str
            km_id = "/heatSources/flameStatus"
        [[[starts]]]
            type = num
            km_id = "/heatSources/hs1/numberOfStarts"
    # Heating circuit 1
    [[hc1]]
        [[[room_set]]]
            type = num
            km_id = "/heatingCircuits/hc1/currentRoomSetpoint"
            Influx = true
        [[[manual_set]]]
            type = num
            km_id = "/heatingCircuits/hc1/manualRoomSetpoint"
        [[[temporary_set]]]
            type = num
            km_id = "/heatingCircuits/hc1/temporaryRoomSetpoint"
        [[[temp_eco]]]
            type = num
            km_id = "/heatingCircuits/hc1/temperatureLevels/eco"
            Influx = true
        [[[temp_comfort]]]
            type = num
            km_id = "/heatingCircuits/hc1/temperatureLevels/comfort2"
            Influx = true
        [[[active_program]]]
            type = str
            km_id = "/heatingCircuits/hc1/activeSwitchProgram"
        [[[mode]]]
            type = str
            km_id = "/heatingCircuits/hc1/operationMode"
    # Hot water circuit 1
    [[hw1]]
        [[[temp]]]
            type = num
            km_id = "/dhwCircuits/dhw1/actualTemp"
            Influx = true          
        [[[set]]]
            type = num
            km_id = "/dhwCircuits/dhw1/currentSetpoint"
            Influx = true          
        [[[flow]]]
            type = num
            km_id = "/dhwCircuits/dhw1/waterFlow"
            Influx = true          
        [[[time]]]
            type = num
            km_id = "/dhwCircuits/dhw1/workingTime"
            Influx = true          
```

See [URLs](URLs.md) for more valid km_id's. 