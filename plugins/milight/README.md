# miLight 

# Requirements

none

## Supported Hardware

miLight 2,4 GHz controlled Light Bulbs or LED RGB-W Strip Controller with WLAN Interface / WiFi Bridge receiver V3.0 
(V2.0 interfaces should be backward compatible but using different default UDP port)
Lamps are sold under different brands MiLight, Easybulb,LimitlessLED
plugin tested with recently released RGB-W Lamps
API decription could be found here:  http://www.limitlessled.com/dev/

# Configuration

## plugin.conf

Typical configuration
<pre>
[milight]
  class_name = milight
  class_path = plugins.milight
  #udp_ip =  192.168.123.147
  #udp_port = 8899
  #bri = yes
  #off = 10    
  #hue_calibrate = 0
  
</pre>

### udp_ip
specifies IP adress of miLight gateway - if not specified broadcast to 255.255.255.255 ( all miLight gateways)

### udp_port
specifies Communication port - V3 is using 8899 by default

### bri
specifies if RGB settings should only impact HUE or HUE and LUM (brightness)
on will change color and brightness  - off only color
values: on/off 

### off
if bri is enabled , this value specifies threashold level for turn off the light ( e.g. below brightness 10 turn off) 
values: on/off

### hue_calibrate 
fine calibrating of color (HUE) to match with different color wheels / tables as input
vaue: 0 to 1   eg. 0.005 to adjust 0,5% clockwise or  -0.005 to adjust 0,05% counter-clockwise


## items.conf

### milight_sw
specifies channel that should be SWITCHED(on/off ) 
 0 = all   1-4 like on remote      1 | 2   controls group 1 and 2
type must be bool


### milight_dim
specifies channel that should be DIMMED  ( 0...255)
remark: miLight supports only 32 values - will be recalculated for KNX DPT5 compliance
type must be num  (integer 0 .. 255)
   1-4 like on remote   multiple input :   1 | 3   controls group 1 and 3
 
### milight_col 
specifies channel to change HUE COLOR ring (0...255)
change will switch from white to RGB color
type must be num  (integer 0 .. 255)

### milight_rgb
specifies channel that should be switched to defined RGB value. Calculated Luminanz (Brightness) 
0 = all   1-4 like on remote      1 | 2   controls group 1 and 2
type must be list with 3 objects (integer 0 .. 255) like  [255;128;0]  
 

 

### milight_white 
specifies channel that should be switched to WHITE (on/off ) 
 0 = all   1-4 like on remote      1 | 2   controls group 1 and 2
type must be bool

### milight_disco
activates and toggles DISCO modes (toggle ) 
  1-4 like on remote      1 | 2   controls group 1 and 2
type must be bool
enforce_updates = yes   recommended

### milight_disco_up / milight_disco_down
controls SPEEDof DISCO mode (increase/ decrease) 
  1-4 like on remote      1 | 2   controls group 1 and 2
type must be bool
enforce_updates = yes   recommended

### Example

<pre>
[mylight]

     [[all]]
      type = bool
      milight_sw = 0 

      [[wohnen]]
       
       type = bool
       milight_sw = 1 
       knx_dpt = 1
       knx_send = 1/0/107
       knx_listen = 1/0/65
       
          
          [[[dimmen]]]       
           type = num
           milight_dim = 1 
           knx_dpt = 5
           knx_listen = 1/0/66
           knx_send = 1/0/67
         
          [[[farbe]]]
           type = num
           milight_col = 1 
          
          [[[white]]]
           type = bool
           milight_white = 1 
         
          [[[disco]]]
           type = bool
           milight_disco = 1 
           enforce_updates = on
          
          [[[discospeedup]]]
           type = bool
           milight_disco_up = 1 
           enforce_updates = yes
          
          [[[discospeeddown]]]
           type = bool
           milight_disco_down = 1 
           enforce_updates = yes
          
      [[flur]]
      
        type = bool
        milight_sw = 2
          
          [[[dimmen]]]       
           type = num
           milight_dim = 2
         
          [[[farbe]]]
           type = num
           milight_col = 2 
          
          [[[white]]]
           type = bool
           milight_white = 2 
         
          [[[disco]]]
           type = bool
          
           milight_disco = 2 
           enforce_updates = on
          
          [[[discospeedup]]]
           type = bool
           milight_disco_up = 2 
           enforce_updates = yes
          
          [[[discospeeddown]]]
           type = bool
           milight_disco_down = 2
           enforce_updates = yes
           
          [[[rgb]]]
            type = list
            knx_dpt = 232
            milight_rgb = 1
            knx_sent = 1/1/1
          
        [[eg]]
      
          type = bool
          milight_sw = 1 | 2
          
          [[[dimmen]]]       
           type = num
           milight_dim = 1 | 2
         
          [[[farbe]]]
           type = num
           milight_col = 1 | 2
          
          [[[white]]]
           type = bool
           milight_white = 1 | 2
</pre>

Hint: on and bri are  coupled, like a typical KNX dimmer.

## logic.conf
since SMARTVISU does not support table input for RGB selection, following logic could be useful to calculate RGB table out of 3 seperate input for R; G and B values

### Example
logic.conf
  [rgb_conversion]
  filename = rgb_conversion.py
  watch_item = r| g| b
  
rgb.conversion.py
  r=sh.r()
  g=sh.g()
  b=sh.b()
 sh.rgb ([r,g,b])
 
# Methodes

## authorizeuser()
No methods attributes.

