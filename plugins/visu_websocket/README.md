# Visualisation plugin (Websocket Protocol)

```
 
Copyright 2012-2013 Marcus Popp                  marcus@popp.mx
Copyright 2016- Martin Sinn                      m.sinn@gmx.de

This plugin is part of SmartHome.py.
  
Visit:  https://github.com/smarthomeNG/
        https://knx-user-forum.de/forum/supportforen/smarthome-py

```

This plugin provides an WebSocket interface for the smartVISU visualisation framework.
Right now the WebSocket interface only supports unencrypted connections. Please use a internal network or VPN to connect to the service.

# Requirements
smarthomeNG version above v1.1.

# Configuration
The configuration of the plugin itself is done in the file **`etc/plugin.conf`**. The configuration of the visualization of the items is done by defining additional attributes of the item in the file **`items/*.conf`**.

## plugin.conf
<pre>
[visu]
    class_name = WebSocket
    class_path = plugins.visu_websocket
#    ip='0.0.0.0'
#    port=2424
#    tls = no
#    wsproto = 3
#    acl = ro

</pre>

### ip
This plugins listens by default on every IP address of the host.

### port
This plugins listens by default  on the TCP port 2424.

### tls
Encryption can be turned on by this parameter. 

--> Details are documented later

### wsproto
The version of the web socket protocol can be specified. By default the plugin uses version 3. For smartVISU version > v2.7 the web socket protocol has to be set to 0 or 4 (depending on the time the v2.8 pre-release of smartVISU was checked out of github).

### acl
The plugin provides by default read only (**`ro`**) access to every item. By changing the **`acl`** attribute to **`rw`** you could modify this default behaviour to gain write access to the items in smarthomeNG.


## items.conf

### visu_acl
Simply set the **`visu_acl`** attribute to **`rw`** to allow read/write access to the specific item.
Other valid values are **`ro`** for readonly access and **`deny`** to disallow access to that item.

### Example
<pre>
[second]
    [[sleeping]]
        name = Sleeping Room
        [[[light]]]
            name = Light
            type = bool
            visu_acl = rw
            knx_dpt = 1
            knx_listen = 3/2/12
            knx_send = 3/2/12
            [[[[level]]]]
                type = num
                visu_acl = rw
                knx_dpt = 5
                knx_listen = 3/2/14
                knx_send = 3/2/14
</pre>


## logic.conf
You could specify the **`visu_acl`** attribute to every logic in your logic.conf. This way you could trigger the logic via the interface.

<pre>
[dialog]
    filename = 'dialog.py'
    visu_acl = true
</pre>


