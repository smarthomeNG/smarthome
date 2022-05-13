# ETA Pellet Unit PU

## Requirements

## Supported Hardware

* ETA Pellet Unit PU (http://www.eta.co.at) with remote access enabled (there are 3 modes available: none, readonly, read/write)

## Configuration

### plugin.yaml

```yaml
eta_pu:
    class_name: ETA_PU
    class_path: plugins.eta_pu
    address: 192.168.179.15
    port: 8080
    setpath: /user/vars
    setname: smarthome
```

Description of the attributes:

* __address__: ip address of the ETA pellet unit
* __port__: port of the ETA webserver (usally 8080)
* __setpath__: path to the presaved sets of CAN-bus-uri
* __setname__: the name of the set, used by this plugin

### items.yaml

The ETA pellet unit organises the data with so calles "uri" (unified ressource identifier). Every uri is readable, some are also writable.
Every uri represents a CAN-bus-id of all internal parts of the pellet unit.
The ETA pellet unit replies to an uri-request e.g. with the following answer:

```
<value uri="/user/var/112/10021/0/0/12162" strValue="26" unit="°C" decPlaces="0" scaleFactor="10" advTextOffset="0">262</value>
```

The plugin can read every part of the answer into an extra subitem depending of the requested type. There is an additional type "calc", that calculates the reply with:

```
data = value * scale_factor + adv_text_offset
```

For writing operations, the "calc" type must be used. The plugin calculates the correct value to write down. Not every uri is writable. Generally, every data, changeable by the ETA touch display (user mode), can be written with the display.

The following item entries are available for reading and writing uri data:

* __eta_pu_uri__: Contains the CAN-bus-id. The pellet unit shows all ids with discription by requesting http://ip/user/menu

* __eta_pu_type__: Represents the field of the data line. Must be one of: strValue, unit, decPlaces, scaleFactor, advTextOffset or calc

There is a second item type available for reading error messages from the pellet unit.

* __eta_pu_error__: The error message from the ETA pellet unit will be read.


#### Example

The __visu__ elements are optional.


```yaml
eta_unit:

    boiler:

        emission_temperature:
            eta_pu_uri: 112/10021/0/0/12162
            type: str

            Value:
                eta_pu_type: calc
                type: num

            unit:
                eta_pu_type: unit
                type: str

    warmwater:

        state:
            eta_pu_uri: 112/10111/0/0/12129

            text:
                visu_acl: ro
                type: str
                eta_pu_type: strValue

        extra_loading_button:
            eta_pu_uri: 112/10111/0/0/12134

            number:
                visu_acl: rw
                type: num
                eta_pu_type: calc

    error:
        eta_pu_error: 'yes'
        type: str
```

### logic.yaml

No special logic functions available in the moment
