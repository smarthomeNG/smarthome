# Amazon Dashbutton Plugin

## Setup your Amazon Dashbutton

 Configure your Amazon Dashbutton. After this, you have to make sure that the Button cannot access the internet.
 Within the popular AVM Fritzbox you have to activate the "Parental Lock" / "No Internet Policy" for your Dashbutton.

 [How-To in German language](https://blog.thesen.eu/aktuellen-dash-button-oder-ariel-etc-von-amazon-jk29lp-mit-dem-raspberry-pi-nutzen-hacken/)

## Requirements

### 1. Install scapy

 ```shell
 sudo pip3 install scapy
 ```

### 2. Install tcpdump

 ```shell
 sudo apt-get install tcpdump
 ```

### 3. Give unprivileged user access to sniff packets

 ```shell
 sudo setcap cap_net_raw=eip /usr/bin/python3.4
 sudo setcap cap_net_raw=eip /usr/sbin/tcpdump
 ```
 Change the python and/or the path to the tcpdump binary to your needs. If you're using the pre-configured
 [Smarthome-NG image from Onkelandy](https://knx-user-forum.de/forum/supportforen/smarthome-py/979095-smarthomeng-image-file#post979095)
 the correct command should be

 ```shell
 sudo setcap cap_net_raw=eip /usr/local/bin/python3.5
 ```


## Item setup

### Activate plugin

Activate plugin via plugin.yaml:

```yaml
dashbutton:
    class_name: Dashbutton
    class_path: plugins.dashbutton
```

### Item attributes

 **dashbutton_mac**     [required]<p>
    The mac address of the dash button. You can add as many mac addresses you want to your item, separated by '|'.  

 **dashbutton_mode**    [required]<p>
    The value can be 'flip' or 'value. If 'flip' mode is chosen, the item type has to be 'bool' and the attribute
 'dashbutton_value' will be ignored. If the configured button was pressed in this mode, the current item value is
 flipped. (0->1 or 1->0)

 **dashbutton_value**   [optional]<p>
 If 'dashbutton_mode' is set to 'value', the attribute 'dashbutton_value' has to be set. It can be a single value or
 a list af values. If the attribute value is a list, the values will be processed in the given order. After the last
 element of the list is reached, the next button press triggers the first element of the list.
 If a item value is changed by another action than a button press and the new item value is not in the configured list,
 the next dashbutton press triggers the first element.

 **dashbutton_reset**   [optional]<p>
    It is possible to configure a reset timer (in seconds). If there is no item value change after the configured time in
 seconds (neither a button press nor another action), the first element of the list is taken when the item is triggered
 the next time. This attribute will be ignored, if no list is passed to the attribute 'dashbutton_value'.

### Examples

**'flip' mode**

```yaml
Room:

   Dining_Room:
       name: Light DiningRoom
       type: bool
       knx_dpt: 1
       knx_send: 1/1/1
       knx_listen: 1/1/1
       dashbutton_mac:
         - cc:66:de:dd:55:11
         - xx:xx:xx:xx:xx:01
         - xx:xx:xx:xx:xx:02
       dashbutton_mode: flip
```

**'value' mode**

```yaml
Room:

    Dining_Room:
        name: Light Dimm DiningRoom
        type: num
        knx_dpt: 5
        knx_send: 1/2/1
        knx_listen: 1/2/1
        dashbutton_mac: cc:66:de:dd:55:11
        dashbutton_mode: value
        dashbutton_value: 30

    Kitchen:
        name: Light Dimm Kitchen
        type: num
        knx_dpt: 5
        knx_send: 1/2/1
        knx_listen: 1/2/1
        dashbutton_mac:
          - dd:11:12:55:55:22
          - cc:66:de:dd:55:11
        dashbutton_mode: value
        dashbutton_value:
          - '30'
          - '10'
          - '20'
          - '0'
        dashbutton_reset: 240
```
