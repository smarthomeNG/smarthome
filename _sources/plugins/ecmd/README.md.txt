# ecmd

## Requirements

The ECMD plugin connects to an AVR microcontroller board with ethersex firmware via network.
The ECMD protocoll provides access to attached 1wire temperature sensors DS1820.

## Supported Hardware

* 8-bit AVR microcontroller boards with network support, like NetIO (Pollin), Etherrape (lochraster.org), etc.
* 1-wire temperature and other sensors
* - DS1820 (temperature sensor)
* - DS18B20 (temperature sensor)
* - DS1822 (temperature sensor)
* - DS2502 (EEPROM)
* - DS2450 (4 channel ADC)

## Configuration

### plugin.yaml

You can specify the host ip of your ethersex device.

```yaml
ecmd:
    plugin_name: ecmd
    host: 10.10.10.10
    # port: 2701
```

This plugin needs an host attribute and you could specify a port attribute which differs from the default '1010'.

### items.yaml

The item needs to define the 1-wire address of the sensor.

#### ecmd1wire_addr

```yaml
mysensor:
    ecmd1wire_addr: 10f01929020800dc
    type: num
```

#### Example

Please provide an item configuration with every attribute and usefull settings.

```yaml
someroom:

    temperature:
        name: Raumtemperatur
        ecmd1wire_addr: 10f01929020800dc
        type: num
        sqlite: 'yes'
        history: 'yes'
        visu: 'yes'
        sv_widget: "\"{{ basic.float('item', 'item', '°') }}\" , \"{{ plot.period('item-plot', 'item') }}\""
```
