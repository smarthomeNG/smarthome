# kostal

### Version: 1.3.1.2

## Requirements
Kostal Inverter

This plugin is designed to retrieve data from a [KOSTAL](http://www.kostal-solar-electric.com/) inverter module (e.g. PIKO inverters).
Since UI-version (communication-board) 6 json-format is supported.

Forum thread to the plugin: https://knx-user-forum.de/forum/supportforen/smarthome-py/1109697-kostal-plugin-piko-wechselrichter

## Supported Hardware

Is currently working with the following KOSTAL inverter modules:

  * KOSTAL PIKO 3.0 UI-Version 06.20 (datastructure=json)
  * KOSTAL PIKO 5.5 UI-Version 05.xx (datastructure=html)

  (should work with all KOSTAL PIKO inverters)
  <add more successfull testet Kostal Inverters with UI-Version and used datastructure>


### Hint
  If communication board (Kommunikationsboard II) firmware has a version 5.x,
  then the inverter generates an html - page.
  The default datastructure=html configuration of this plugin, trys to read
  the current inverter values from this status page.

  If communication board (Kommunikationsboard II) firmware has a version 6.x,
  then the inverter generates ajax - style status page.
  The datastructure=json configuration of this plugin, reads the current
  inverter values from an json-comminication string.

  So the datastructure - configuration depends on the firmwareversion of your
  communication board.

  New inverters:
  http://kostal-solar-electric.com/de-DE/Produkte_Service/PIKO-Wechselrichter_neue_Generation
  My Kostal Piko 3.0 was shipped with a communication board with a firmware version 5.x.
  After a firmware-upgrade my inverter doesn't ship a html-page. Now i could user the
  JSON-communication.
  Firmware Updates http://www.kostal-solar-electric.com/de-DE/Download/Updates

  Old inverters:
  http://kostal-solar-electric.com/de-DE/Produkte_Service/PIKO-Wechselrichter_bewaehrte_Generation,
  I'll don't know if the communication board of old inverters could also be updated to version 6.x.

## Configuration


### plugin.yaml

The plugin can be configured like this:

```yaml
Kostal_PV:
    plugin_name: kostal
    ip: 192.168.1.21
    user: pvserver
    passwd: pvwr
    cycle: 300
    datastructure: html
    # use
    # datastructure: json
    # for UI-Version >6
```

This plugin retrieves data from a KOSTAL inverter module of a solar energy
plant.

The data retrieval is done by establishing a network connection to the
inverter module and retrieving the status via a HTTP/JSON request.

You need to configure the IP address of the inverter module.
If datastructure=html is used the user and password attributes (user, passwd)
can be overwritten, but defaults to the standard credentials.

If datasructure=json is used, no credentials are requred.

The cycle parameter defines the update interval and defaults to 300 seconds.

### items.yaml

#### Description of all possible items (depending on inverter features)

Hint: PIKO 3.0 is a single phase inverter with a single dc-line (dc-string).
  all DC2, DC3, AC2 and AC3 values would reply a None-value.

* operation_status: status of the Kostal inverter (On,Off,Feed in,starting)
* dcpower: total dc power (all dc inputs); unit: Watt
* dc1_v ... dc3_v: DC-voltage input 1 ... 3; unit: Voltage
* dc1_a ... dc3_a: DC-current input 1 ... 3; unit: Ampere
* dc1_w ... dc3_w: DC-power input 1 ... 3; unit: Watt [1]
* actot_w : total ac power (all ac phases); unit: Watt
* actot_cos: total ac Cos φ [1]
* actot_limitation: total ac limitation; unit % [1]
* ac1_v ... ac3_v: AC phase 1 ... 3 voltage; unit: Voltage
* ac1_a ... ac3_a: AC phase 1 ... 3 current; unit: Ampere [1]
* ac1_w ... ac3_w: AC phase 1 ... 3 power; unit: Watt
* yield_day_kwh: Yield today; unit kWh [2]
* yield_tot_kwh: Yield total; unit kWh
* operationtime_h: Inverter operation time; unit hours [1]

[1] If your communication board has a firmwareversion 5 (datastructure=html), these values are not displayed in the html-status page and are also not available for the plugin.

[2] The json communication returns Yield_today in Wh. The plugin divide the value by 1000. So we get in both communication ways the same units.

Hint:
Item names have changed from the previous version of the plugin, so that both
types of communication can be configured the same way.


#### Example

```yaml
# not all possible items are used

Kostal_PV:

    status:
        name: inverter status
        type: str
        kostal: operation_status

    dcpower:
        name: total dc power
        type: num
        kostal: dctot_w

    dc1_v:
        name: DC-input 1 voltage
        type: num
        kostal: dc1_v

    dc1_a:
        name: DC-input 1 current
        type: num
        kostal: dc1_a

    dc1_w:
        name: DC-input 1 power
        type: num
        kostal: dc1_w

    dc2_v:
        name: DC-input 2 voltage
        type: num
        kostal: dc2_v

    dc2_a:
        name: DC-input 2 current
        type: num
        kostal: dc2_a

    dc2_w:
        name: DC-input 2 power
        type: num
        kostal: dc2_w

    actot_w:
        name: total ac-output power
        type: num
        kostal: actot_w

    actot_cos:
        name: Cos phi
        type: num
        kostal: actot_cos

    actot_limitation:
        name: Limitation on percent
        type: num
        kostal: actot_limitation

    ac1_v:
        name: Phase 1 voltage
        type: num
        kostal: ac1_v

    ac1_a:
        name: Phase 1 current
        type: num
        kostal: ac1_a

    ac1_w:
        name: Phase 1 power
        type: num
        kostal: ac1_w

    ac2_v:
        name: Phase 2 voltage
        type: num
        kostal: ac2_v

    ac2_a:
        name: Phase 2 current
        type: num
        kostal: ac2_a

    ac2_w:
        name: Phase 2 power
        type: num
        kostal: ac2_w

    ac3_v:
        name: Phase 3 voltage
        type: num
        kostal: ac3_v

    ac3_a:
        name: Phase 3 current
        type: num
        kostal: ac3_a

    ac3_w:
        name: Phase 3 power
        type: num
        kostal: ac3_w

    yield_day_kwh:
        name: Yield today
        type: num
        kostal: yield_day_kwh

    yield_tot_kwh:
        name: Yield total
        type: num
        kostal: yield_tot_kwh

    operationtime_h:
        name: Operation time
        type: num
        kostal: operationtime_h
```

### logic.yaml

No logic related stuff implemented.

## Methods

No methods provided currently.
