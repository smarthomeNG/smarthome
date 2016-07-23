# SMA-WebBox (smawb)

# Description

You can use this Plugin to receive data of a single (or multiple) SMA-Sunny-WebBox(es).
i. e. http://www.sma-america.com/en_US/products/monitoring-systems/sunny-webbox.html.

This PlugIn is based on the ```SunnyWebBox.py``` Python-Script (https://github.com/jraedler/SunnyWebBox).

# Requirements

  * one (or more) active and configured SMA-Sunny-WebBox(es)
  * the IP(s) of the SMA-Sunny-WebBox(es)
  * all signal-names you want to track*

*you can run the SunnyWebBox.py to get those names. Execute the script by changing into the ```smarthome/plugins/smawb``` directory and executing ```python SunnyWebBox.py [IP-Address]```. You will get a list of all inverters wich are managed by the given SMA-Sunny-WebBox and their available signal-names.

# Configuration
## plugin.conf

You have to just simply copy the following into your plugin.conf file. The ip-address/hostname the SMA-Sunny-WebBox(es) has to be setup later in the items.conf!

<pre>
[smawb]
    class_name = SMAWB
    class_path = plugins.smawb
#    smawb_polling_cycle = 10
</pre>

Description of the optional attribute:

* __smawb_polling_cycle__: the number of seconds between polling data from all configured SMA-Sunny-WebBoxes (default: 10 sec)

## items.conf

The most item-fields of this plugin are mandatory. So you should always use all of the fields showed in the following example.

### Example

<pre>
# items/sma_sunny_webboxes.conf
[SMA_WebBox]
    type = str
    smawb_host = 192.168.0.123
#    smawb_password = ''
    [[Overview]]
        type = str
        smawb_key = OVERVIEW
        [[[GriPwr]]]
            type = str
            smawb_data = GriPwr
        [[[GriEgyTdy]]]
            type = num
            smawb_data = GriEgyTdy
    [[INV1]]
        type = str
        smawb_key = WRTL1ECD:2123456223
        [[[A_Ms_Watt]]]
            type = str
            smawb_data = A.Ms.Watt
        [[[B_Ms_Watt]]]
            type = num
            smawb_data = B.Ms.Watt
        ...
</pre>

Description of the attributes:

* __smawb_host__: the ip-address/hostname of the SMA-Sunny-WebBox (mandatory)
* __smawb_password__: the password of the given SMA-Sunny-WebBox (if any)
* __smawb_key__: the target-inverter-name or ```OVERVIEW``` for overview-data of the SMA-Sunny-WebBox
* __smawb_data__: the signal-name of the given target-inverter or overview-data (mandatory)

Hints:
* __You have to setup the items as showed in a tree structure with the `smawb_host` as its root, `smawb_key` as root-childs and `smawb_data` as childs of `smawb_key`!__ (The whole tree can be a subtree of a greater tree but always has to be `smawb_host` as a attribute of the root item!)

### Example for multiple SMA-Sunny-WebBoxes

<pre>
# items/sma_sunny_webboxes.conf
[SMA_WebBox_1]
    type = str
    smawb_host = 192.168.0.123
#    smawb_password = ''
    [[Overview]]
        type = str
        smawb_key = OVERVIEW
        [[[GriPwr]]]
            type = str
            smawb_data = GriPwr
        ...
    [[INV1]]
        type = str
        smawb_key = WRTL1ECD:2123456223
        [[[A_Ms_Watt]]]
            type = str
            smawb_data = A.Ms.Watt
        ...
[SMA_WebBox_2]
    type = str
    smawb_host = 192.168.0.124
#    smawb_password = ''
    [[Overview]]
        type = str
        smawb_key = OVERVIEW
        [[[GriPwr]]]
            type = str
            smawb_data = GriPwr
        ...
    [[INV1]]
        type = str
        smawb_key = WRTL1ECD:2522222222
        [[[A_Ms_Watt]]]
            type = str
            smawb_data = A.Ms.Watt
        ...
</pre>

## SmartVisu

You can get the data of a SMA-Sunny-WebBox by selecting the right leaves of the tree. For Example, you can setup a "tank" wich will show you how much power of the maximum power of the inverter is generated at the current moment:

If your Inverter can generate 5kW at its max you can setup for example

```html
{{ basic.tank('powerOfMaxPower', 'SMA_WebBox.Inverter.Power', 0, 5000, 100) }}
```
