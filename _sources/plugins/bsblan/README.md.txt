
![BSB-LAN Logo](assets/BSB-LAN-Logo_SmartHomeNG.png)

# Plugin for BSB-Lan-Adapter

#### Version 1.0.2

This plugin connects your BSB-LAN-Adapter (https://github.com/fredlcore/BSB-LAN) with SmarthomeNG.
BSB-LAN is a LAN Interface for Boiler-System-Bus (BSB) that enables you to control heating systems from Elco or 
Brötje and similar Systems. 
- read out all available boiler parameters.
- write all accessible boiler parameters

## Change history
- 1.0.2 revised README. Compatibility check for BSB-LAN Version 2.x
- 1.0.1 added support for writing parameters

### Requirements needed software

* Python > 3.7
* SmarthomeNG >= 1.7.2


## Configuration

### 1) /smarthome/etc/plugin.yaml

Enable the plugin in plugin.yaml and type in the adapters IP address.

```yaml
bsblan:
    plugin_name: bsblan
    bsblan_ip: 192.168.xxx.xxx
```

### 2) /smarthome/items/bsblan.yaml

Create an item and add the parameters you want to get from BSB-LAN.
A full list of supported parameters you can get from the BSB-LAN-Adapter Web interface (http://192.168.xxx.xxx/K)

```yaml
bsblan:
    Komfortsollwert_HK1:
        type: num
        bsb_lan: 710
        visu_acl: rw
        descr:
            type: str
    Vorlauftemperatur_HK1:
        type: num
        bsb_lan: 8743
        visu_acl: ro
        descr:
            type: str
    Trinkwassertemperatur:
        type: num
        bsb_lan: 8830
        visu_acl: ro
        descr:
            type: str
    Vorlauftemperatur_HK2:
        type: num
        bsb_lan: 8773
        visu_acl: ro
        descr:
            type: str
    Heizkreispumpe_HK2_Status:
        type: num
        bsb_lan: 8760
        visu_acl: ro
        descr:
            type: str
    Status_Brenner:
        type: num
        bsb_lan: 8009
        visu_acl: ro
        descr:
            type: str
    Kesseltemperatur:
        type: num
        bsb_lan: 8310
        visu_acl: ro
        descr:
            type: str
    Kesselruecklauftemperatur:
        type: num
        bsb_lan: 8314
        visu_acl: ro
        descr:
            type: str
    Wasserdruck:
        type: num
        bsb_lan: 8327
        visu_acl: ro
        descr:
            type: str
    Status_Trinkwasser:
        type: num
        bsb_lan: 8003
        visu_acl: ro
        descr:
            type: str
    Status_Kessel:
        type: num
        bsb_lan: 8005
        visu_acl: ro
        descr:
            type: str
```








