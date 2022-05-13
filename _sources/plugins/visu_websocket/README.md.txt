# Visualisation (Websocket Protocol)

```

Copyright 2012-2013 Marcus Popp                  marcus@popp.mx
Copyright 2016- Martin Sinn                      m.sinn@gmx.de
Copyright 2019 Bernd Meiners                     Bernd.Meiners@mail.de

This plugin is part of SmartHomeNG.

Visit:  https://github.com/smarthomeNG/
        https://knx-user-forum.de/forum/supportforen/smarthome-py

```

This plugin provides a WebSocket interface for the smartVISU visualisation framework.
Right now the WebSocket interface only supports unencrypted connections. 
Please use an internal network or VPN to connect to the service.

## Requirements
SmarthomeNG version above v1.4c.

## Configuration
The configuration of the plugin itself is done in the file ``etc/plugin.yaml``. 

The configuration of the visualization can be achieved by 
extending item description in any ``items/<your items>.yaml.
As other plugin some additional attributes are to be put to the item structure.

### plugin.yaml

```yaml
visu:
    plugin_name: visu_websocket
    # ip: '0.0.0.0'
    # port: 2424
    # tls: no
    # wsproto: 3
    # acl: ro
```

#### ip
This plugins listens by default on every IP address of the host.

#### port
This plugins listens by default on the TCP port 2424.

#### tls
Encryption can be turned on by this parameter.

--> Details are documented later

#### wsproto
The version of the web socket protocol can be specified. By default the plugin uses version 3. 
For smartVISU version > v2.7 the web socket protocol has to be set to 0 or 4 
(depending on the time the v2.8 pre-release of smartVISU was checked out of github).

#### acl
The plugin provides by default read only (**`ro`**) access to every item. 
By changing the **`acl`** attribute to **`rw`** you could modify this default behaviour
to gain write access to the items in smarthomeNG.

#### querydef
If set to True, the plugin can be queried by a websocket client (a visu) for the item- and logic-definitions.



### items.yaml

The plugin only knows a single attribute for an item: 

#### visu_acl
Simply set the **`visu_acl`** attribute to **`rw`** to allow read/write access to the specific item.
Other valid values are **`ro`** for readonly access and **`deny`** to disallow access to that item.

#### Example

An example item definition is given below:

```yaml
second:

    sleeping:
        name: Sleeping Room

        light:
            name: Light
            type: bool
            visu_acl: rw
            knx_dpt: 1
            knx_listen: 3/2/12
            knx_send: 3/2/12

            level:
                type: num
                visu_acl: rw
                knx_dpt: 5
                knx_listen: 3/2/14
                knx_send: 3/2/14
```

Starting with SmartHomeNG 1.6 the way attributes can be accessed changed. Instead of using the attributes directly 
it was extended to accept attributes with ``.property.``. 
Thus item attribute access changed e.g. from ``sh.second.sleeping.light.prev_value`` to ``sh.second.sleeping.light.property.prev_value()``.
The philosophy is now to have a getter and a setter if possible.

For this plugin it means that SmartVISU now can access the attributes values, too as shown in the following example (valid for SmartVISU >= 2.9):

```html
{{ basic.print( '', 'second.sleeping.light.property.prev_value') }} 
{{ basic.print( '', 'second.sleeping.light.property.last_change') }} 
```

The properties aka attributes will only be updated when the items value is updated, thus changes can only propagated to SmartVISU in case the 
items value was changed.

### logic.yaml
The **`visu_acl`** attribute can be set to every logic in ``logic.yaml``. 
This way a logic can be triggered via the SmartVISU.

```yaml
dialog:
    filename: dialog.py
    visu_acl: 'true'
```

## Functions

### url(url)

--> This command works with **smartVISU 2.9** and up, for **smartVISU 2.8** a modified driver **`io_smarthome.py`** is needed.

This function instructs the smartVISU clients to change to the specified url (visu page).

Example:

```python
sh.visu.url('index.php')
```

This function call expects the visu_websocket plugin to be configured in a section 
named **`visu`** in the configuration file **`etc/plugin.yaml`**.

It instructs **all** running visu clients to change to the main page.


### url(url, ip)

--> This command works with **smartVISU 2.9** and up, for **smartVISU 2.8** a modified driver **`io_smarthome.py`** is needed.

Function is the same as above, but only clients (browsers) running on a host with the specified ip address are instructed to change the page.

Example:

```
	sh.visu.url('index.php?page=apartement.living', '10.0.0.23')
```

This command expects the visu_websocket plugin to be configured in a section 
named **`visu`** in the configuration file **`etc/plugin.yaml`**.
