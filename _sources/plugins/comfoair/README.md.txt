# ComfoAir

The ComfoAir plugin is designed to connect to a Zehnder ComfoAir KWL (heat-recovery ventilation) system and read out and write its parameters.
Primarly supported is the ComfoAir 350, which uses the following protocol: http://www.see-solutions.de/sonstiges/Protokollbeschreibung_ComfoAir.pdf
There exist identical systems from different manufactures which use the exact same protocol, known is the Wernig G90-380 and supposedly some types of Paul Lüftung Germany.

Additional support for the ComfoAir 500 was added but the protocol is not fully investigated yet:  http://matsab.de/images/comfoair/Protokoll_CA500_Avignon.pdf

The ComfoAir plugin uses a separate commands.py file which contains the different control- (control characters like start sequence, acknowledge etc.) and commandsets for the supported systems.

You can configure the plugin to connect by TCP (host and port) using a TCP to serial (RS232 for ComfoAir 350 or RS485 for ComfoAir 500) converter or provide a direct serial connection on the host system.

WARNING!
* Don't use the CC Ease command panel parallel with the plugin. They would both try to communicate with ComfoAir at the same time and create big troubles (corrupt the config in ComfoAir in worst case).

## Requirements

This plugin has no requirements or dependencies.

## Configuration

### plugin.yaml

```
comfoair:
    class_name: ComfoAir
    class_path: plugins.comfoair
    kwltype: comfoair350       # Currently supported: comfoair350 and comfoair500
    host: 192.168.123.6        # Provide host and port if you want to use TCP connection (for a TCP to serial converter)
    port: 5555                 # Port
    #serialport: /dev/ttyUSB0  # Enable this if you want to use a serial connection
```

### items.yaml

The plugin is completely flexible in which commands you use and when you want the read out which parameters.
Everything is configured by adding new items in a SmartHomeNG item configuration file.

The following item attributes are supported:

#### comfoair_send

Changes to this item result in sending the configured command to the KWL system.
The command is complemented by the item value in a pre-configured way (see commands.py).

```yaml
comfoair_send: WriteVentilationLevel
```

#### comfoair_read

The item value should be read by using the configured command.

```yaml
comfoair_read: ReadVentilationLevel
```

#### comfoair_read_afterwrite

A timespan (seconds) can be configured. If a value for this attribute is set, the plugin will wait the configured delay after the write command and then issue the configured read command to update the items value.
This attribute has no default value. If the attribute is not set, no read will be issued after write.

```yaml
comfoair_read_afterwrite: 1 # seconds
```

#### comfoair_read_cycle

With this attribute a read cycle for this item can be configured (timespan between cycles in seconds).

```yaml
comfoair_read_cycle: 3600 # every hour
```

#### comfoair_init

If this attribute is set to a value (e.g. 'true'), the plugin will use the read command at startup to get an initial value.

```yaml
comfoair_init: true
```

#### comfoair_trigger

This attribute can contain a list of commands, which will be issued if the item is updated.
Useful for instance: If the ventilation level is changed, get updated ventilator RPM values.

```yaml
comfoair_trigger:
   - ReadSupplyAirRPM
   - ReadExtractAirRPM
```

#### comfoair_trigger_afterwrite

A timespan (seconds) can be configured. After an update to this item, the commands configured in comfoair_trigger will be issued. Before triggering the here configured delay will be waited for.
Default value: 5 seconds.

```yaml
comfoair_trigger_afterwrite: 10 # seconds
```

#### Example

Here you can find a sample configuration using the ComfoAir 350 commands:

```yaml
kwl:
    level:
        type: num
        comfoair_send: WriteVentilationLevel
        comfoair_read: ReadCurrentVentilationLevel
        comfoair_read_afterwrite: 1 # seconds
        comfoair_trigger: ReadSupplyAirRPM
        comfoair_trigger_afterwrite: 6 # seconds
        comfoair_init: true
        sqlite: yes
    extractair:
        rpm:
            type: num
            comfoair_read: ReadExtractAirRPM
            comfoair_read_cycle: 60 # seconds
            comfoair_init: true
        level:
            type: num
            comfoair_read: ReadExtractAirPercentage
            comfoair_read_cycle: 60 # seconds
            comfoair_init: true
    supplyair:
        rpm:
            type: num
            comfoair_read: ReadSupplyAirRPM
            comfoair_read_cycle: 60 # seconds
            comfoair_init: true
        level:
            type: num
            comfoair_read: ReadSupplyAirPercentage
            comfoair_read_cycle: 60 # seconds
            comfoair_init: true
    filter:
        reset:
            type: bool
            comfoair_send: WriteFilterReset
    temp:
        comfort:
            type: num
            comfoair_send: WriteComfortTemperature
            comfoair_read: ReadComfortTemperature
            comfoair_read_cycle: 60 # seconds
            comfoair_init: true
        freshair:
            type: num
            comfoair_read: ReadFreshAirTemperature
            comfoair_read_cycle: 60 # seconds
            comfoair_init: true
            sqlite: yes
        supplyair:
            type: num
            comfoair_read: ReadSupplyAirTemperature
            comfoair_read_cycle: 60 # seconds
            comfoair_init: true
            sqlite: yes
        extractair:
            type: num
            comfoair_read: ReadExtractAirTemperature
            comfoair_read_cycle: 60 # seconds
            comfoair_init: true
            sqlite: yes
        exhaustair:
            type: num
            comfoair_read: ReadExhaustAirTemperature
            comfoair_read_cycle: 60 # seconds
            comfoair_init: true
            sqlite: yes
        preheater:
            type: num
            comfoair_read: ReadPreHeatingTemperature
            comfoair_read_cycle: 60 # seconds
            comfoair_init: true
        groundheat:
            type: num
            comfoair_read: ReadGroundHeatTemperature
            comfoair_read_cycle: 60 # seconds
            comfoair_init: true
    bypass:
        type: num
        comfoair_read: ReadBypassPercentage
        comfoair_read_cycle: 600 # seconds
        comfoair_init: true
    preheater:
        type: num
        comfoair_read: ReadPreHeatingStatus
        comfoair_read_cycle: 600 # seconds
        comfoair_init: true
    operatinghours:
        away:
            type: num
            comfoair_read: ReadOperatingHoursAway
            comfoair_read_cycle: 3600 # seconds
            comfoair_init: true
        low:
            type: num
            comfoair_read: ReadOperatingHoursLow
            comfoair_read_cycle: 3600 # seconds
            comfoair_init: true
        medium:
            type: num
            comfoair_read: ReadOperatingHoursMedium
            comfoair_read_cycle: 3600 # seconds
            comfoair_init: true
        high:
            type: num
            comfoair_read: ReadOperatingHoursHigh
            comfoair_read_cycle: 3600 # seconds
            comfoair_init: true
        antifreeze:
            type: num
            comfoair_read: ReadOperatingHoursAntiFreeze
            comfoair_read_cycle: 3600 # seconds
            comfoair_init: true
        preheater:
            type: num
            comfoair_read: ReadOperatingHoursPreHeating
            comfoair_read_cycle: 3600 # seconds
            comfoair_init: true
        bypass:
            type: num
            comfoair_read: ReadOperatingHoursBypass
            comfoair_read_cycle: 3600 # seconds
            comfoair_init: true
        filter:
            type: num
            comfoair_read: ReadOperatingHoursFilter
            comfoair_read_cycle: 3600 # seconds
            comfoair_init: true
    heatpreparationratio:
        type: num
        eval: (sh.kwl.temp.supplyair() - sh.kwl.temp.freshair()) / (sh.kwl.temp.extractair() - sh.kwl.temp.exhaustair()) * 100
        eval_trigger:
          - kwl.temp.supplyair
          - kwl.temp.freshair
          - kwl.temp.extractair
          - kwl.temp.exhaustair
```


### logic.yaml
Currently there is no logic configuration for this plugin.


## Methods
Currently there are no functions offered from this plugin.
