# WakeOnLan - Plugin

Requirements
============
none


Configuration
=============

## plugin.conf

<pre>
 [wakeonlan]

     class_name = WakeOnLan
     class_path = plugins.wol
</pre>

## items.conf
<pre>
 [wakeonlan_item]
      
     type = bool

     wol_mac = 01:02:03:04:05:06
</pre>

### wol_mac
This attribute is mandatory. You have to provide the mac address for the host to wake up. Type of separators are unimportant. you can use:
    wol_mac = 01:02:03:04:05:06
or
    wol_mac = 01-02-03-04-05-06
or don't use any separators:

    wol_mac = 010203040506
#