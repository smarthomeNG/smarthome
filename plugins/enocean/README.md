EnOcean - under development !!!

Please do not remove any comments until stable.
  
Configure plugin.conf 
=
  
Add the following lines to your plugin.conf and just change the serialport to the portname of your enocean-adpater.
A udev-rules for the enocean-adapter is recommend.
  
<pre>
[enocean]
    class_name = EnOcean
    class_path = plugins.enocean
    serialport = /dev/ttyUSB0
</pre>
  
Configure items
=
  
According to the plugin-implementation of the enocean-devices you have to specify at least a enocean-id (enocean serial number in format 01:a2:f3:2d), the correct enocean-rorg-code and an enocean-value. 
   
The following example ist for a rocker/switch with two rocker and 6 available combinations.  
left rocker down = A1  
left rocker up = A0  
right rocker down = B1   
right rocker up = B0  
both rockers down = A1B1   
both rockers up = A0B0   

<pre>
[A1]
type = bool
enforce_updates = true
enocean_id = 00:22:60:37
enocean_rorg = F6_02_02
enocean_value = A1
</pre>
  
Add new enocean devices
=
  
You have to know about the EnOcean RORG of your device, so pleas ask Mr.Google or the vendor. Further the RORG must be declared in the plugin. At moment there is only the 2-Button-Rocker supportet.
  
