# Unifi

#### Version 1.6.1

Plugin to read some data from UniFi Controllers and to control it

## Change history

### Changes Since version 1.6.0

- Fixed logging issues
- Extended Web-Interface

## Todo

* Add additional data as Itemtypes from the UniFi API, based on real-world demands.

## Requirements

This plugin requires a permanently available UniFi Controller or a UniFi cloud-key.

### Needed software

There is no additional requirement for software that is not bundled. Plugin was tested with Python 3.5 and the api was tested with Python 3.5 and 3.7

### Supported Hardware

As this plugin only communicates with the UniFi Controller basically all UniFi managed devices can be supported.

Tested with:
* UniFi Controller 5.10.23 in Docker Container on Synology
* UniFi UAP AC Lite
* UniFi UAP AC Mesh
* UniFi Switch US-8-60W

## Configuration

### plugin.yaml
Please refer to the documentation generated from plugin.yaml metadata.

Example:
```
unifi:
  plugin_name: unifi
  unifi_user: ubnt        # User Name
  unifi_password: ubnt    # Password
  unifi_controller_url: https://192.168.1.12:8443 # URL of YOUR controller / cloud-key
  poll_cycle_time: 60     # Cycle time for data retrieval in seconds 

```

### items.yaml

Please refer to the documentation generated from plugin.yaml metadata.

Example:
```
uni_items:
  type: foo

  switch:
    unifi_switch_mac: af:fe:af:fe:00:00
    
    ip:
      type: str
      unifi_type: device_ip

    sw_name:
      type: str
      unifi_type: device_name
    
    access_points:
      unifi_switch_port_profile_on: All
      unifi_switch_port_profile_off: Disabled
      
      ap_ac_lite1:
        unifi_ap_mac: af:fe:af:fe:00:01
        unifi_switch_port_no: 5

        ip:
          type: str
          unifi_type: device_ip

        ap_name:
          type: str
          unifi_type: device_name
        
        ap_enabled:
          type: bool
          unifi_type: ap_enabled

        port_enabled:
          type: bool
          unifi_type: switch_port_enabled

        jensIphoneHier:
          type: bool
          mac: a4:e9:00:00:af:fe
          unifi_type: client_present_at_ap
      
      ap_ac_lite2:
        unifi_ap_mac: af:fe:af:fe:00:02
        unifi_switch_port_no: 6

        ip:
          type: str
          unifi_type: device_ip

        ap_name:
          type: str
          unifi_type: device_name
        
        ap_enabled:
          type: bool
          unifi_type: ap_enabled

        port_enabled:
          type: bool
          unifi_type: switch_port_enabled

        jensIphoneHier:
          type: bool
          mac: a4:e9:00:00:af:fe
          unifi_type: client_present_at_ap


      ap_ac_mesh:
        unifi_ap_mac: af:fe:af:fe:af:fe
        unifi_switch_port_no: 8
        
        ap_enabled:
          type: bool
          unifi_type: ap_enabled

        port_enabled:
          type: bool
          unifi_type: switch_port_enabled
          unifi_switch_port_profile_on: WLAN AP
          unifi_switch_port_profile_off: Fully Off
            
        ip:
          type: str
          unifi_type: device_ip

        ap_name:
          type: str
          unifi_type: device_name
          
        myPhoneHere:
          type: bool
          mac: a4:e9:75:00:af:fe
          unifi_type: client_present_at_ap

  myPhonePresent:
    type: bool
    mac: a4:e9:75:00:af:fe
    unifi_type: client_present

    ip:
      type: str
      unifi_type: client_ip

  internetRadioDevicePresent:
    type: bool
    unifi_type: client_present
    mac: 00:00:00:00:af:fe
  
    ip:
      type: str
      unifi_type: client_ip

```



### logic.yaml
Please refer to the documentation generated from plugin.yaml metadata.


## Methods
Please refer to the documentation generated from plugin.yaml metadata.


## Examples

If you have extensive examples, you could describe them here.


## Web Interfaces

For building a web interface for a plugin, we deliver the following 3rd party components with the HTTP module:

   * JQuery 3.4.1: 
     * JS: &lt;script src="/gstatic/js/jquery-3.4.1.min.js"&gt;&lt;/script&gt;
   * Bootstrap : 
     * CSS: &lt;link rel="stylesheet" href="/gstatic/bootstrap/css/bootstrap.min.css" type="text/css"/&gt; 
     * JS: &lt;script src="/gstatic/bootstrap/js/bootstrap.min.js"&gt;&lt;/script&gt;     
   * Bootstrap Tree View: 
      * CSS: &lt;link rel="stylesheet" href="/gstatic/bootstrap-treeview/bootstrap-treeview.css" type="text/css"/&gt; 
      * JS: &lt;script src="/gstatic/bootstrap-treeview/bootstrap-treeview.min.js"&gt;&lt;/script&gt;
   * Bootstrap Datepicker v1.8.0:
      * CSS: &lt;link rel="stylesheet" href="/gstatic/bootstrap-datepicker/dist/css/bootstrap-datepicker.min.css" type="text/css"/&gt;
      * JS:
         * &lt;script src="/gstatic/bootstrap-datepicker/dist/js/bootstrap-datepicker.min.js"&gt;&lt;/script&gt;
         * &lt;script src="/gstatic/bootstrap-datepicker/dist/locales/bootstrap-datepicker.de.min.js"&gt;&lt;/script&gt;
   * popper.js: 
      * JS: &lt;script src="/gstatic/popper.js/popper.min.js"&gt;&lt;/script&gt;
   * CodeMirror 5.46.0: 
      * CSS: &lt;link rel="stylesheet" href="/gstatic/codemirror/lib/codemirror.css"/&gt;
      * JS: &lt;script src="/gstatic/codemirror/lib/codemirror.js"&gt;&lt;/script&gt;
   * Font Awesome 5.8.1:
      * CSS: &lt;link rel="stylesheet" href="/gstatic/fontawesome/css/all.css" type="text/css"/&gt;

 For addons, etc. that are delivered with the components, see /modules/http/webif/gstatic folder!
 
 If you are interested in new "global" components, contact us. Otherwise feel free to use them in your plugin, as long as
 the Open Source license is ok.
 
