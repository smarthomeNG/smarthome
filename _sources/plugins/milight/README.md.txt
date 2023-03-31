# milight

#### Version 1.6.0

This Plugin sends changes in items value to a miLight gateway to control light settings.

Some parameters have changed and are improved a little:

* bri --> bricontrol, changed from Bool to String
* off --> cutoff

The best way to configure it is by using the Admin Interface. It should also be possible
to use multiple instances of the plugin although not tested so far.

#### Todo:

* The webinterface needs to be populated
* A better check for Broadcast IP should be implemented
* A user_doc.rst needs to be written

## Requirements

### Supported Hardware

MiLight 2,4 GHz controlled Light Bulbs or LED RGB-W Strip Controller with WLAN Interface / WiFi Bridge receiver V3.0
(V2.0 interfaces should be backward compatible but using different default UDP port)
User also reported it works with the ESP8266 based replacement hub (https://github.com/sidoh/esp8266_milight_hub) which is
based on this works here https://hackaday.io/project/5888-reverse-engineering-the-milight-on-air-protocol

Lamps are sold under different brands MiLight, Easybulb, LimitlessLED
The plugin was tested with recently released RGB-W Lamps
API description was posted at http://www.limitlessled.com/dev/ formerly but it was taken 
offline and excluded from internet archvie as well. So at https://github.com/BKrajancic/LimitlessLED-DevAPI something is saved
for reference but last entries are from 2017.

## Configuration

### plugin.yaml

Typical configuration

```yaml
milight:
  plugin_name: milight
  #udp_ip:  192.168.123.147
  #udp_port: 8899
  #bri: yes
  #off: 10    
  #hue_calibrate: 0
```

#### udp_ip

Specifies IP adress of miLight gateway - if not specified broadcast to 255.255.255.255 (all miLight gateways)

#### udp_port

Specifies communication port - V3 is using 8899 by default

#### bricontrol

Specifies if RGB settings should only impact HUE or HUE and LUM (brightness)
on will change color and brightness  - off only color
values: on/off

#### cutoff

If bricontrol is enabled, this value specifies threshold level for turn off the light (e.g. below brightness 10 turn off)
Needed to give a numeric value here.

#### hue_calibrate

Fine calibrating of color (HUE) to match with different color wheels / tables as input
value: 0 to 1   eg. 0.005 to adjust 0,5% clockwise or  -0.005 to adjust 0,05% counter-clockwise


### items.yaml

#### milight_sw

Specifies channel that should be SWITCHED(on/off)
 0 = all   1-4 like on remote      1 | 2   controls group 1 and 2
Item type must be bool


#### milight_dim

Specifies channel that should be DIMMED  (0...255)
remark: miLight supports only 32 values - will be recalculated for KNX DPT5 compliance
Item type must be num  (integer 0 .. 255)
   1-4 like on remote   multiple input :   1 | 3   controls group 1 and 3

#### milight_col

Specifies channel to change HUE COLOR ring (0...255)
change will switch from white to RGB color
Item type must be num  (integer 0 .. 255)

#### milight_rgb

Specifies channel that should be switched to defined RGB value. Calculated Luminanz (Brightness)
0 = all   1-4 like on remote      1 | 2   controls group 1 and 2
Item type must be list with 3 objects (integer 0 .. 255) like  [255;128;0]


#### milight_white

Specifies channel that should be switched to WHITE (on/off )
 0 = all   1-4 like on remote      1 | 2   controls group 1 and 2
type must be bool

#### milight_disco

Activates and toggles DISCO modes (toggle )
  1-4 like on remote      1 | 2   controls group 1 and 2
type must be bool
enforce_updates = yes     recommended

#### milight_disco_up / milight_disco_down

Controls SPEED of DISCO mode (increase/ decrease)
  1-4 like on remote      1 | 2   controls group 1 and 2
Item type must be bool
enforce_updates: yes     recommended

#### Example

```yaml
mylight:

    all:
        type: bool
        milight_sw: 0

    wohnen:
        type: bool
        milight_sw: 1
        knx_dpt: 1
        knx_send: 1/0/107
        knx_listen: 1/0/65

        dimmen:
            type: num
            milight_dim: 1
            knx_dpt: 5
            knx_listen: 1/0/66
            knx_send: 1/0/67

        farbe:
            type: num
            milight_col: 1

        white:
            type: bool
            milight_white: 1

        disco:
            type: bool
            milight_disco: 1
            enforce_updates: 'on'

        discospeedup:
            type: bool
            milight_disco_up: 1
            enforce_updates: 'yes'

        discospeeddown:
            type: bool
            milight_disco_down: 1
            enforce_updates: 'yes'

    flur:
        type: bool
        milight_sw: 2

        dimmen:
            type: num
            milight_dim: 2

        farbe:
            type: num
            milight_col: 2

        white:
            type: bool
            milight_white: 2

        disco:
            type: bool
            milight_disco: 2
            enforce_updates: 'on'

        discospeedup:
            type: bool
            milight_disco_up: 2
            enforce_updates: 'yes'

        discospeeddown:
            type: bool
            milight_disco_down: 2
            enforce_updates: 'yes'

        rgb:
            type: list
            knx_dpt: 232
            milight_rgb: 1
            knx_sent: 1/1/1

    eg:
        type: bool
        milight_sw:
          - '1'
          - '2'

        dimmen:
            type: num
            milight_dim:
              - '1'
              - '2'

        farbe:
            type: num
            milight_col:
              - '1'
              - '2'

        white:
            type: bool
            milight_white:
              - '1'
              - '2'
```

Hint: On and bricontrol are coupled, like a typical KNX dimmer.

### Example for RGB

Since SmartVISU does not support table input for RGB selection, following item construction
could be useful to calculate RGB table out of 3 separate input for R, G and B values

```yaml
living_room:
    rgb:
        name: RGB
        type: list
        milight_rgb: 1
        cache: yes
        eval: "[sh..r(), sh..g(), sh..b()]"
        eval_trigger:
          - .r
          - .g
          - .b
        
        r:
            name: value for red
            type: num
            cache: yes
            visu_acl: rw

        g:
            name: value for green
            type: num
            cache: yes
            visu_acl: rw

        b:
            name: value for blue
            type: num
            cache: yes
            visu_acl: rw
```

If autogeneration plugin for SmartVISU is used, on ecan take the following code snippet as basis:

```html
{{ basic.color('', 'living_room.rgb', '', '', [0,0,0], [255,255,255], '', '', 'rect', 'rgb') }}
```