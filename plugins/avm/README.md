# AVM

# Requirements
This plugin requires lib requests. You can install this lib with: 
<pre>
sudo pip3 install requests --upgrade
</pre>

It is completely based on the TR-064 interface from AVM (http://avm.de/service/schnittstellen/)

Forum thread to the plugin: https://knx-user-forum.de/forum/supportforen/smarthome-py/934835-avm-plugin

Version 1.1.2 tested with a FRITZ!Box 7490 (FRITZ!OS 06.51), a FRITZ! WLAN Repeater 1750E (FRITZ!OS 06.32) and a
WLAN Repeater 300E (FRITZ!OS 06.30). It was also tested with a FRITZ!Box 7390 with FW 84.06.36 and a Fritz!Box 7390
with v6.30 und v6.51.

The avm_data_types listed in the example items under "devices" only work correctly with firmware <= v6.30, if the
FRITZ!Box does not handle more than 16 devices in parallel (under "Heimnetz/Netzwerk"). Otherwise some of the devices
won't work.

The MonitoringService currently does not support multiple parallel incoming or outgoing calls. For being able to
connect to the FritzDevice's CallMonitor, you have to activate it, by typing `#96*5*` on a directly connected phone.

The version is tested with new multi-instance functionality of SmartHomeNG.

# Configuration

## plugin.conf
<pre>
[fb1]
    class_name = AVM
    class_path = plugins.avm
    username = ... # optional
    password = ...
    host = fritz.box
    port = 49443
    cycle = 300
    ssl = True     # use https or not
    verify = False # verify ssl certificate
    call_monitor = True
    call_monitor_incoming_filter = ... #optional, don't set if you don't want to watch only one specific number with your call monitor
    instance = fritzbox_7490
[fb2]
    class_name = AVM
    class_path = plugins.avm
    username = ... # optional
    password = ...
    host = ...
    port = 49443
    cycle = 300
    ssl = True     # use https or not
    verify = False # verify ssl certificate
    call_monitor = True
    instance = wlan_repeater_1750
[...]    
</pre>

Note: Depending on the FritzDevice a shorter cycle time can result in problems with CPU rating and, in consequence with the accessibility of the webservices on the device.
If cycle time is reduced, please carefully watch your device and your sh.log. In the development process, 120 Seconds also worked worked fine on the used devices.

### Attributes
  * `username`: Optional login information
  * `password`: Required login information
  * `host`: Hostname or ip address of the FritzDevice.
  * `port`: Port of the FritzDevice, typically 49433 for https or 49000 for http
  * `cycle`: timeperiod between two update cycles. Default is 240 seconds.
  * `ssl`: True or False => True will add "https", False "http" to the URLs in the plugin
  * `verify`: True or False => Turns certificate verification on or off. Typically False
  * `call_monitor`: True or False => Activates or deactivates the MonitoringService, which connects to the FritzDevice's call monitor
  * `instance`: Unique identifier for each FritzDevice / each instance of the plugin

## items.conf

### avm_data_type
This attribute defines supported functions that can be set for an item. Full set see example below.
For most items, the avm_data_type can be bound to an instance via @... . Only in some points the items
are parsed as child items. In the example below there is a comment in the respective spots.

### Example:
<pre>
[avm]
	[[uptime_7490]]
        type = num
        visu_acl = ro
        avm_data_type@fritzbox_7490 = uptime
    [[uptime_1750]]
        type = num
        visu_acl = ro
        avm_data_type@wlan_repeater_1750 = uptime
    [[serial_number_7490]]
        type = str
        visu_acl = ro
        avm_data_type@fritzbox_7490 = serial_number
    [[serial_number_1750]]
        type = str
        visu_acl = ro
        avm_data_type@wlan_repeater_1750 = serial_number
    [[firmware_7490]]
        type = str
        visu_acl = ro
        avm_data_type@fritzbox_7490 = software_version
    [[firmware_1750]]
        type = str
        visu_acl = ro
        avm_data_type@wlan_repeater_1750 = software_version
    [[hardware_version_7490]]
        type = str
        visu_acl = ro
        avm_data_type@fritzbox_7490 = hardware_version
    [[hardware_version_1750]]
        type = str
        visu_acl = ro
        avm_data_type@wlan_repeater_1750 = hardware_version
    [[myfritz]]
    	type = bool
        avm_data_type@fritzbox_7490 = myfritz_status
	[[monitor]]
	    [[[trigger]]]
            type = bool
            avm_data_type@fritzbox_7490 = monitor_trigger
            avm_incoming_allowed = xxxxxxxx
            avm_target_number = xxxxxxxx
            enforce_updates = yes
        [[[trigger2]]]
            type = bool
            avm_data_type@fritzbox_7490 = monitor_trigger
            avm_incoming_allowed = xxxxxxxx
            avm_target_number = xxxxxxxx
            enforce_updates = yes
        [[[trigger3]]]
            type = bool
            avm_data_type@fritzbox_7490 = monitor_trigger
            avm_incoming_allowed = xxxxxxxx
            avm_target_number = xxxxxxxx
            enforce_updates = yes
        [[[trigger4]]]
            type = bool
            avm_data_type@fritzbox_7490 = monitor_trigger
            avm_incoming_allowed = xxxxxxxx
            avm_target_number = xxxxxxxx
            enforce_updates = yes
	    [[[incoming]]]
            [[[[is_call_incoming]]]]
                type = bool
                avm_data_type@fritzbox_7490 = is_call_incoming
            [[[[duration]]]]
                type = num
                avm_data_type@fritzbox_7490 = call_duration_incoming
            [[[[last_caller]]]]
                type = str
                avm_data_type@fritzbox_7490 = last_caller_incoming
            [[[[last_calling_number]]]]
                type = str
                avm_data_type@fritzbox_7490 = last_number_incoming
            [[[[last_called_number]]]]
                type = str
                avm_data_type@fritzbox_7490 = last_called_number_incoming
            [[[[last_call_date]]]]
                type = str
                avm_data_type@fritzbox_7490 = last_call_date_incoming
            [[[[event]]]]
                type = str
                avm_data_type@fritzbox_7490 = call_event_incoming
	    [[[outgoing]]]
	        [[[[is_call_outgoing]]]]
                type = bool
                avm_data_type@fritzbox_7490 = is_call_outgoing
            [[[[duration]]]]
                type = num
                avm_data_type@fritzbox_7490 = call_duration_outgoing
            [[[[last_caller]]]]
                type = str
                avm_data_type@fritzbox_7490 = last_caller_outgoing
            [[[[last_calling_number]]]]
                type = str
                avm_data_type@fritzbox_7490 = last_number_outgoing
            [[[[last_called_number]]]]
                type = str
                avm_data_type@fritzbox_7490 = last_called_number_outgoing
            [[[[last_call_date]]]]
                type = str
                avm_data_type@fritzbox_7490 = last_call_date_outgoing
            [[[[event]]]]
                type = str
                avm_data_type@fritzbox_7490 = call_event_outgoing
        [[[newest]]]
            [[[[direction]]]]
                type = str
                avm_data_type@fritzbox_7490 = call_direction
                cache = yes
            [[[[event]]]]
                type = str
                avm_data_type@fritzbox_7490 = call_event
                cache = yes
    [[tam]]
        index = 1
        type = bool
        visu_acl = rw
        avm_data_type@fritzbox_7490 = tam
        [[[name]]]
            type = str
            visu_acl = ro
            avm_data_type@fritzbox_7490 = tam_name
        [[[message_number_old]]]
            type = num
            visu_acl = ro
            avm_data_type@fritzbox_7490 = tam_old_message_number
            eval = (sh.avm.tam.message_number_total()-sh.avm.tam.message_number_new())
            eval_trigger = avm.tam.message_number_total | avm.tam.message_number_new
        [[[message_number_new]]]
            type = num
            visu_acl = ro
            avm_data_type@fritzbox_7490 = tam_new_message_number
        [[[message_number_total]]]
            type = num
            visu_acl = ro
            avm_data_type@fritzbox_7490 = tam_total_message_number
    [[wan]]
        [[[connection_status]]]
           	type = str
           	visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_connection_status
        [[[connection_error]]]
           	type = str
           	visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_connection_error
        [[[is_connected]]]
            type = bool
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_is_connected
        [[[uptime]]]
            type = num
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_uptime
        [[[ip]]]
            type = str
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_ip
        [[[upstream]]]
            type = num
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_upstream
        [[[downstream]]]
            type = num
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_downstream
        [[[total_packets_sent]]]
            type = num
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_total_packets_sent
        [[[total_packets_received]]]
            type = num
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_total_packets_received
        [[[total_bytes_sent]]]
            type = num
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_total_bytes_sent
        [[[total_bytes_received]]]
            type = num
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_total_bytes_received
        [[[link]]]
            type = bool
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wan_link
    [[wlan]]
        [[[gf_wlan_1]]]
            type = bool
            visu_acl = rw
            avm_data_type@fritzbox_7490 = wlanconfig #2,4ghz
            avm_wlan_index = 1
        [[[gf_wlan_1_ssid]]]
            type = str
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wlanconfig_ssid #2,4ghz
            avm_wlan_index = 1
        [[[gf_wlan_2]]]
            type = bool
            visu_acl = rw
            avm_data_type@fritzbox_7490 = wlanconfig #5 GHz
            avm_wlan_index = 2
        [[[gf_wlan_3]]]
            type = bool
            visu_acl = rw
            avm_data_type@fritzbox_7490 = wlanconfig # Guest
            avm_wlan_index = 3
        [[[gf_wlan_3_ssid]]]
            type = str
            visu_acl = ro
            avm_data_type@fritzbox_7490 = wlanconfig_ssid #2,4ghz
            avm_wlan_index = 3
        [[[gf_wlan_3_tr]]]
            type = num
            visu_acl = rw
            avm_data_type@fritzbox_7490 = wlan_guest_time_remaining # Guest
            avm_wlan_index = 3
        [[[uf_wlan_1]]]
            type = bool
            visu_acl = rw
            avm_data_type@wlan_repeater_1750 = wlanconfig #2,4ghz
            avm_wlan_index = 1
        [[[uf_wlan_1_ssid]]]
            type = str
            visu_acl = ro
            avm_data_type@wlan_repeater_1750 = wlanconfig_ssid #2,4ghz
            avm_wlan_index = 1
        [[[uf_wlan_2]]]
            type = bool
            visu_acl = rw
            avm_data_type@wlan_repeater_1750 = wlanconfig #5 GHz
            avm_wlan_index = 2
        [[[uf_wlan_3]]]
            type = bool
            visu_acl = rw
            avm_data_type@wlan_repeater_1750 = wlanconfig # Guest
            avm_wlan_index = 3
    [[devices]]
    	[[[wlan_repeater_1750]]]
	        [[[[GalaxyS5]]]]
	            mac = xx:xx:xx:xx:xx:xx
	            avm_data_type@wlan_repeater_1750 = network_device
	            type = bool
	            cache = yes
	            visu_acl = ro
	            [[[[[ip]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_ip
	                visu_acl = ro
	            [[[[[connection_type]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_connection_type
	                visu_acl = ro
	            [[[[[hostname]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_hostname
	                visu_acl = ro
	        [[[[iPhone]]]]
	            mac = xx:xx:xx:xx:xx:xx
	            avm_data_type@wlan_repeater_1750 = network_device
	            type = bool
	            cache = yes
	            visu_acl = ro
	            [[[[[ip]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_ip
	                visu_acl = ro
	            [[[[[connection_type]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_connection_type
	                visu_acl = ro
	            [[[[[hostname]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_hostname
	                visu_acl = ro
        [[[fritzbox_7490]]]
	        [[[[iPad]]]]
	            mac = xx:xx:xx:xx:xx:xx
	            avm_data_type@fritzbox_7490 = network_device
	            type = bool
	            visu_acl = ro
	            [[[[[ip]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_ip
	                visu_acl = ro
	            [[[[[connection_type]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_connection_type
	                visu_acl = ro
	            [[[[[hostname]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_hostname
	                visu_acl = ro
	        [[[[hauptrechner]]]]
	            mac = xx:xx:xx:xx:xx:xx
	            avm_data_type@fritzbox_7490 = network_device
	            type = bool
	            visu_acl = ro
	            [[[[[ip]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_ip
	                visu_acl = ro
	            [[[[[connection_type]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_connection_type
	                visu_acl = ro
	            [[[[[hostname]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_hostname
	                visu_acl = ro
	        [[[[GalaxyS5]]]]
	            mac = xx:xx:xx:xx:xx:xx
	            avm_data_type@fritzbox_7490 = network_device
	            type = bool
	            cache = yes
	            visu_acl = ro
	            [[[[[ip]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_ip
	                visu_acl = ro
	            [[[[[connection_type]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_connection_type
	                visu_acl = ro
	            [[[[[hostname]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_hostname
	                visu_acl = ro
	        [[[[GalaxyTabS2]]]]
	            mac = xx:xx:xx:xx:xx:xx
	            avm_data_type@fritzbox_7490 = network_device
	            type = bool
	            visu_acl = ro
	            [[[[[ip]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_ip
	                visu_acl = ro
	            [[[[[connection_type]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_connection_type
	                visu_acl = ro
	            [[[[[hostname]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_hostname
	                visu_acl = ro
	        [[[[iPhone]]]]
	            mac = xx:xx:xx:xx:xx:xx
	            avm_data_type@fritzbox_7490 = network_device
	            type = bool
	            cache = yes
	            visu_acl = ro
	            [[[[[ip]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_ip
	                visu_acl = ro
	            [[[[[connection_type]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_connection_type
	                visu_acl = ro
	            [[[[[hostname]]]]] # these items need to be child items from network_device, an @... must not be set
	                type = str
	                avm_data_type = device_hostname
	                visu_acl = ro
    [[dect]]
        [[[socket_living]]]
            type = bool
            avm_data_type@fritzbox_7490 = aha_device
            ain = 14324 0432601 # has to be identical to id in fritzbox (also with spaces!)
            visu_acl = rw
            [[[[energy]]]] # these items need to be child items from aha_device, an @... must not be set
                avm_data_type = energy
                type = num
                visu_acl = ro
            [[[[power]]]] # these items need to be child items from aha_device, an @... must not be set
                avm_data_type = power
                type = num
                sqlite = yes
                enforce_updates=true
                visu_acl = ro
                eval = value / 100
            [[[[temperature]]]] # these items need to be child items from aha_device, an @... must not be set
                avm_data_type = temperature
                type = num
                visu_acl = ro
        [[[socket_office]]]
            type = bool
            avm_data_type@fritzbox_7490 = aha_device
            ain = 03456 0221393 # has to be identical to id in fritzbox (also with spaces!)
            visu_acl = rw
            [[[[energy]]]] # these items need to be child items from aha_device, an @... must not be set
                avm_data_type = energy
                type = num
                visu_acl = ro
            [[[[power]]]] # these items need to be child items from aha_device, an @... must not be set
                avm_data_type = power
                type = num
                sqlite = yes
                enforce_updates=true
                visu_acl = ro
                eval = value / 100
            [[[[temperature]]]] # these items need to be child items from aha_device, an @... must not be set
                avm_data_type = temperature
                type = num
                visu_acl = ro
</pre>

# Functions

## get_phone_name
Get the phone name at a specific index. The returend value can be used as phone_name for set_call_origin. Parameter is an INT, starting from 1. In case an index does not exist, an error is logged.
The used function X_AVM-DE_GetPhonePort() does not deliver analog connections like FON 1 and FON 2 (BUG in AVM Software).
<pre>
phone_name = sh.fb1.get_phone_name(1)
</pre>
CURL for this function:
<pre>
curl --anyauth -u user:password "https://fritz.box:49443/upnp/control/x_voip" -H "Content-Type: text/xml; charset="utf-8"" -H "SoapAction:urn:dslforum-org:service:X_VoIP:1#X_AVM-DE_GetPhonePort" -d "<?xml version='1.0' encoding='utf-8'?><s:Envelope s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/' xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'><s:Body><u:X_AVM-DE_GetPhonePort xmlns:u='urn:dslforum-org:service:X_VoIP:1'><s:NewIndex>1</s:NewIndex></u:X_AVM-DE_GetPhonePort></s:Body></s:Envelope>" -s -k
</pre>

##get_call_origin
Gets the phone name, currently set as call_origin.
<pre>
phone_name = sh.fritzbox_7490.get_call_origin()
</pre>
CURL for this function:
<pre>
curl --anyauth -u user:password "https://fritz.box:49443/upnp/control/x_voip" -H "Content-Type: text/xml; charset="utf-8"" -H "SoapAction:urn:dslforum-org:service:X_VoIP:1#X_AVM-DE_DialGetConfig" -d "<?xml version='1.0' encoding='utf-8'?><s:Envelope s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/' xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'><s:Body><u:X_AVM-DE_DialGetConfig xmlns:u='urn:dslforum-org:service:X_VoIP:1' /></s:Body></s:Envelope>" -s -k
</pre>

## set_call_origin(phone_name)
Sets the origin of a call. E.g. a DECT phone. Typically set before using "start_call".
You can also set the origin on your FritzDevice via "Telefonie -> Anrufe -> Wählhilfe verwenden -> Verbindung mit dem Telefon".
The used function X_AVM-DE_SetDialConfig() does not allow the configuration of analog connections (BUG in AVM Software).
<pre>
sh.fb1.set_call_origin("<phone_name>")
</pre>

## start_call(phone_number)
This function starts a call. Parameter can be an external or internal number.
<pre>
sh.fb1.start_call('0891234567')
sh.fb1.start_call('**9')
</pre>

## cancel_call()
This function cancels a running call.

## wol(mac_address)
This function executes a wake on lan command to the specified MAC address

## reconnect()
This function reconnects the WAN (=internet) connection.

## reboot()
This function reboots the FritzDevice.

## get_contact_name_by_phone_number(phone_number)
This is a function to search for telephone numbers in the contacts stored on the devices phone book

## get_calllist()
Returns an array with calllist entries

## is_host_active(mac_address)
This function checks, if a device running on a given mac address is active on the FritzDevice. Can be used for presence detection.
