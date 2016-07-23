This plugin is design for TellStick and TellStick Duo RF Transmitter


1/ how to install   
=================


You must install telldus-core and configure it (http://developer.telldus.com/wiki/TellStickInstallationSource)

After install you must configure your devices in /etc/tellstick.conf (http://developer.telldus.com/wiki/TellStick_conf)   

2/ how to config   
================ 

Plugin activation `etc/plugin.conf`
 
        [tellstick]
          class_name = Tellstick
          class_path = plugins.tellstick
 
 
Items configuration :
 
- ts_id : id of the device in /etc/tellstick.conf
 
Example :
 
        [kitchen]
          [[light]]
            type = bool
            ts_id = 1
