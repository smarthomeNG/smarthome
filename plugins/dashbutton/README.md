# Amazon Dashbutton Plugin

## Setup your Amazon Dashbutton

 Configure your Amazon Dashbutton. After this, you have to make sure that the Button cannot access the internet.
 Within the popular AVM Fritzbox you have to activate the "Parental Lock" / "No Internet Policy" for your Dashbutton.
 
 [How-To in German language](https://blog.thesen.eu/aktuellen-dash-button-oder-ariel-etc-von-amazon-jk29lp-mit-dem-raspberry-pi-nutzen-hacken/)
 
## Requirements

### 1. Install scapy

```shell
sudo pip3 install scapy-python3
```

### 2. Install tcpdump

```shell
sudo apt-get install tcpdump
```

### 3. Give unprivileged user access to sniff packets

```shell
setcap cap_net_raw=eip /usr/bin/python3.4
setcap cap_net_raw=eip /usr/sbin/tcpdump
```
Change the python and/or the path to the tcpdump binary to your needs.


## Item setup

### Activate plugin

 Activate plugin via plugin.con:
 
    [dashbutton]
        class_name = Dashbutton
        class_path = plugins.dashbutton
 

### Item attributes

 **dashbutton_mac**  
 The mac address of the dash button. You can add as many mac addresses you want to your item, separated by '|'.  
 
 **dashbutton_mode**  
 The value can be 'flip' or 'value. If 'flip' mode is chosen, the item type has to be 'bool' and the attribute
 'dashbutton_value' will be ignored. If the configured button was pressed in this mode, the current item value is 
 flipped. (0->1 or 1->0) 
 
 **dashbutton_value**  
 If 'dashbutton_mode' is set to 'value', the attribute 'dashbutton_value' has to be set.
 
### Examples
 
 **'flip mode'**
 
    [Room]
        [[Dining_Room]]
            name = "Light DiningRoom"knx_dpt = 1
            type = bool
            knx_send = 1/1/1
            knx_listen = 1/1/1
            knx_init = 1/1/3
            dashbutton_mac = "cc:66:de:dd:55:11 | xx:xx:xx:xx:xx:01 | xx:xx:xx:xx:xx:02"
            dashbutton_mode = 'flip'
            
  **'value' mode**

    [Room]
        [[Dining_Room]]
            name = "Light Dimm DiningRoom"
            type = num
            knx_dpt = 5
            knx_send = 1/2/1
            knx_listen = 1/2/1
            knx_init = 1/2/3
            dashbutton_mac = "cc:66:de:dd:55:11"
            dashbutton_mode = 'value'
            dashbutton_value = 30