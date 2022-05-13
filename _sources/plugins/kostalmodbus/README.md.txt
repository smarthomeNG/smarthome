# Modbus Plugin for Kostal inverters

#### Version 1.0.0

This plugin connects your Kostal inverter (https://www.kostal-solar-electric.com/) via ModBus with SmarthomeNG.
- read out all inverter data

## Change history

### Changes Since version 1.x.x

- No Changes so far


### Requirements needed software

* Python > 3.5
* pip install pymodbus
* SmarthomeNG >= 1.6.0


### Supported Inverters

| Inverter            | Supported    | Tested  |
| --------------------|:------------:| -------:|
| PLENTICORE plus 4.2 | yes          | no      |
| PLENTICORE plus 5.5 | yes          | no      |
| PLENTICORE plus 7.0 | yes          | yes     |
| PLENTICORE plus 8.5 | yes          | yes     |
| PLENTICORE plus 10  | yes          | no      |
| PIKO IQ 4.2         | yes          | no      |
| PIKO IQ 5.5         | yes          | no      |
| PIKO IQ 7.0         | yes          | no      |
| PIKO IQ 8.5         | yes          | no      |
| PIKO IQ 10          | yes          | no      |

## Configuration

### 1) /smarthome/etc/plugin.yaml

Enable the plugin in plugin.yaml, type in the inverters IP address and configure the ModBus Port and update cycle(seconds).

```yaml
Kostalmodbus:
    plugin_name: kostalmodbus
    inverter_ip: 'XXX.XXX.XXX.XXX'
    modbus_port: '1502'
    update_cycle: '20'
```

### 2) /smarthome/items/kostal.yaml

Create an item based on the template /files/kostal_item_template.yaml


## Examples

Thats it! Now you can start using the plugin within SmartVisu.
For example:

#### Get data from inverter:
```html
<p>Daily yield: {{ basic.value('DailyYield', 'Kostal.Inverter.kostal_322') }} Wh</p>
/** Get the daily yield (num)*/

<p>Total DC power: {{ basic.value('TotalDCPower', 'Kostal.Inverter.kostal_100') }} W</p>
/** Get the current total DC power (num)*/

```


#### The following data are stored in the respective items:

| Addr (dec)        | Description                                       | Format | Unit    |
|-------------------|---------------------------------------------------|--------|---------|
| kostal_30         | Number of bidirectional converter                 | U16    | -       |
| kostal_32         | Number of AC phases                               | U16    | -       |
| kostal_34         | Number of PV strings                              | U16    | -       |
| kostal_36         | Hardware-Version                                  | U16    | -       |
| kostal_54         | Power-ID                                          | U16    | -       |
| kostal_56         | Inverter state2                                   | U16    | -       |
| kostal_100        | Total DC power W                                  | Float  | W       |
| kostal_104        | State of energy manager3                          | U32    | -       |
| kostal_106        | Home own consumption from battery                 | Float  | W       |
| kostal_108        | Home own consumption from grid                    | Float  | W       |
| kostal_110        | Total home consumption Battery                    | Float  | Wh      |
| kostal_112        | Total home consumption Grid                       | Float  | Wh      |
| kostal_114        | Total home consumption PV                         | Float  | Wh      |
| kostal_116        | Home own consumption from PV                      | Float  | W       |
| kostal_118        | Total home consumption                            | Float  | Wh      |
| kostal_120        | Isolation resistance                              | Float  | Ohm     |
| kostal_122        | Power limit from EVU                              | Float  | %       |
| kostal_124        | Total home consumption rate                       | Float  | %       |
| kostal_144        | Worktime s Float                                  | Float  | Seconds |
| kostal_150        | Actual cos                                        | Float  | cos     |
| kostal_152        | Grid frequency                                    | Float  | Hz      |
| kostal_154        | Current Phase 1                                   | Float  | A       |
| kostal_156        | Active power Phase 1                              | Float  | W       |
| kostal_158        | Voltage Phase 1                                   | Float  | V       |
| kostal_160        | Current Phase 2                                   | Float  | A       |
| kostal_162        | Active power Phase 2                              | Float  | W       |
| kostal_164        | Voltage Phase 2                                   | Float  | V       |
| kostal_166        | Current Phase 3                                   | Float  | A       |
| kostal_168        | Active power Phase 3                              | Float  | W       |
| kostal_170        | Voltage Phase 3                                   | Float  | V       |
| kostal_172        | Total AC active power                             | Float  | W       |
| kostal_174        | Total AC reactive power                           | Float  | Var     |
| kostal_178        | Total AC apparent power                           | Float  | VA      |
| kostal_190        | Battery charge current                            | Float  | A       |
| kostal_194        | Number of battery cycles                          | Float  | -       |
| kostal_200        | Actual battery charge (-) / discharge (+) current | Float  | A       |
| kostal_202        | PSSB fuse state5                                  | Float  | -       |
| kostal_208        | Battery ready flag                                | Float  | -       |
| kostal_210        | Act. state of charge                              | Float  | %       |
| kostal_214        | Battery temperature                               | Float  | °C      |
| kostal_216        | Battery voltage                                   | Float  | V       |
| kostal_218        | Cos φ (powermeter)                                | Float  | cos     |
| kostal_220        | Frequency (powermeter)                            | Float  | Hz      |
| kostal_222        | Current phase 1 (powermeter)                      | Float  | A       |
| kostal_224        | Active power phase 1 (powermeter)                 | Float  | W       |
| kostal_226        | Reactive power phase 1 (powermeter)               | Float  | Var     |
| kostal_228        | Apparent power phase 1 (powermeter)               | Float  | VA      |
| kostal_230        | Voltage phase 1 (powermeter)                      | Float  | V       |
| kostal_232        | Current phase 2 (powermeter)                      | Float  | A       |
| kostal_234        | Active power phase 2 (powermeter)                 | Float  | W       |
| kostal_236        | Reactive power phase 2 (powermeter)               | Float  | Var     |
| kostal_238        | Apparent power phase 2 (powermeter)               | Float  | VA      |
| kostal_240        | Voltage phase 2 (powermeter)                      | Float  | V       |
| kostal_242        | Current phase 3 (powermeter)                      | Float  | A       |
| kostal_244        | Active power phase 3 (powermeter)                 | Float  | W       |
| kostal_246        | Reactive power phase 3 (powermeter)               | Float  | Var     |
| kostal_248        | Apparent power phase 3 (powermeter)               | Float  | VA      |
| kostal_250        | Voltage phase 3 (powermeter)                      | Float  | V       |
| kostal_252        | Total active power (powermeter)                   | Float  | W       |
| kostal_254        | Total reactive power  (powermeter)                | Float  | Var     |
| kostal_256        | Total apparent power (powermeter)                 | Float  | VA      |
| kostal_258        | Current DC1                                       | Float  | A       |
| kostal_260        | Power DC1                                         | Float  | W       |
| kostal_266        | Voltage DC1                                       | Float  | V       |
| kostal_268        | Current DC2                                       | Float  | A       |
| kostal_270        | Power DC2                                         | Float  | W       |
| kostal_276        | Voltage DC2                                       | Float  | V       |
| kostal_278        | Current DC3                                       | Float  | A       |
| kostal_280        | Power DC3                                         | Float  | W       |
| kostal_286        | Voltage DC3                                       | Float  | V       |
| kostal_320        | Total yield                                       | Float  | Wh      |
| kostal_322        | Daily yield                                       | Float  | Wh      |
| kostal_324        | Yearly yield                                      | Float  | Wh      |
| kostal_326        | Monthly yield                                     | Float  | Wh      |
| kostal_512        | Battery gross capacity                            | U32    | Ah      |
| kostal_514        | Battery actual SOC                                | U16    | %       |
| kostal_515        | Firmware Maincontroller (MC)                      | U32    | -       |
| kostal_525        | Battery Model ID                                  | U32    | -       |
| kostal_529        | Work Capacity                                     | U32    | Wh      |
| kostal_531        | Inverter Max Power                                | U16    | W       |
| kostal_575        | Inverter Generation Power (actual)                | S16    | W       |
| kostal_577        | Generation Energy                                 | U32    | Wh      |
| kostal_582        | Actual battery charge/discharge power             | S16    | W       |
| kostal_586        | Battery Firmware                                  | U32    | -       |
| kostal_588        | Battery Type6                                     | U16    | -       |





