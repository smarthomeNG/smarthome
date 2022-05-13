# EnOcean

## Description
This plugin adds EnOcean support to SmarthomeNG.

## Support
If you have special hardware not supported yet, please feel free to improve and contribute!

## Version / Change History
Version: 1.3.6

Change History: currently not maintained.

## Hardware Requirements
For use of this plugin you need an EnOcean radio transceiver module like:
- Fam4Pi
- USB 300
- EnOcean PI 868 Funk Modul
- etc.

## Prerequisites
Make sure that the user 'smarthome' belongs to the user group dialout to be able to access the linux devices via:

sudo gpasswd --add smarthome dialout

## Configuration

### plugin.yaml

Add the following lines to your `plugin.yaml`:

#### Parameters

##### serialport

You have to specify the `serialport` to your port name of your EnOcean adapter.
UNder Linux, the creation of a specific **udev-rules** for the EnOcean adapter is recommended, when using different Uart devices.

##### tx_id
The specification of the EnOcean `tx_id` is optional **but** mandatory for sending control commands from smarthomeNG to EnOcean devices.
It is defined as a 8-digit hexadecimal value.

When controlling multiple devices, it is recommended to use the EnOcean adapter's Base-ID (not Unique-ID or Chip-ID) as transmitting ID.
For further information regarding the difference between Base-ID and Chip-ID, see
[Knowledge Base](https://www.enocean.com/en/knowledge-base-doku/enoceansystemspecification%3Aissue%3Awhat_is_a_base_id/)

With the specification of the Base-ID, 128 different transmit ID's are available, ranging between Base-ID and Base-ID + 127.

##### How-To Get the Base-ID of the EnOcean adapter
There are two different ways of reading the EnOcean adapter's Base ID:
a) Via the Enocean Plugin Webinterface
b) Via the logfiles created by the Enocean plugin.

For a) 
1. Configure Enocean plugin in plugin.yaml file with empty tx_id (or tx_id = 0).
2. Restart SmarthomeNG.
3. Open the plugin's webinterface under: http://localip:8383/enocean/
4. Read the Transceiver's BaseID, which is displayed on the upper right side.
5. Insert the Base-ID in the plugin.yaml file as tx_id parameter.

For b)
1. Configure Enocean plugin in plugin.yaml file with empty tx_id (or tx_id = 0).
2. Configure loglevel INFO in logger.yaml for enocean plugin.
3. Restart smarthomeNG
4. Wait until all plugins came up
5. Open the logfile (Enocean or general smarthomeNG logfile) and search for `enocean: Base ID = 0xYYYYZZZZ`
6. Insert the Base-ID in the plugin.yaml file as tx_id parameter..

#### Example plugin.yaml
```yaml
enocean:
    class_name: EnOcean
    class_path: plugins.enocean
    serialport: /dev/ttyUSB0
    tx_id: FFFF4680
```

### Items

#### enocean_rx_id, enocean_rx_eep and enocean_tx_id_offset
An EnOcean item (sensor or actor) must specify at minimum an `enocean_rx_id` (EnOcean Identification Number (hex code)) and an `enocean_rx_eep` (EnOcean Equipment Profile).
Transmitting items additionally need an `enocean_tx_id_offset`.

#### enocean_rx_eep
The EEP [EnOcean Equippment Profile] defines the message type that is broadcast by the Enocean device. EEPs are standardized by Enocean. More information can be found under http://www.enocean-alliance.org/eep/

#### enocean_rx_key
Generally, EnOcean devices broadcast more than just one information. These can be linked to different smarthomeNG items via so called shortcut key names (enocean_rx_key). See the list below for different examples of key names.


The following example outlines the available button shortcuts and their meaning for a rocker/switch with two rocker (EEP-Profile: F6_02_01 or F6_02_02).

```
AI = left rocker down
A0 = left rocker up
BI = right rocker down
B0 = right rocker up
```

The following example outlines the button shortcuts and its meaning for a rocker/switch with two rocker and 6 available combinations (EEP F6_02_03).

```
AI = left rocker down
A0 = left rocker up
BI = right rocker down
B0 = right rocker up
A = last state of left rocker
B = last state of right rocker
```
Example of a mechanical handle (F6_10_0):

```
STATUS = handle_status
```

### items.yaml

#### Attributes
For attributes have a look at the examples.

#### Example item.yaml
```
EnOcean_Item:
    Outside_Temperature:
        type: num
        enocean_rx_id: 0180924D
        enocean_rx_eep: A5_02_05
        enocean_rx_key: TMP

    Door:
        enocean_rx_id: 01234567
        enocean_rx_eep: D5_00_01
        status:
            type: bool
            enocean_rx_key: STATUS

    FT55switch:
        enocean_rx_id: 012345AA
        enocean_rx_eep: F6_02_03
            up:
                type: bool
                enocean_rx_key: BO
            down:
                type: bool
                enocean_rx_key: BI

    Brightness_Sensor:
        name: brightness_sensor_east
        remark: Eltako FAH60
        type: num
        enocean_rx_id: 01A51DE6
        enocean_rx_eep: A5_06_01
        enocean_rx_key: BRI
        visu_acl: rw
        sqlite: 'yes'

    dimmer1:
        remark: Eltako FDG14 - Dimmer
        enocean_rx_id: 00112233
        enocean_rx_eep: A5_11_04
        light:
        type: bool
        enocean_rx_key: STAT
        enocean_tx_eep: A5_38_08_02
        enocean_tx_id_offset: 1
        level:
            type: num
            enocean_rx_key: D
            enocean_tx_eep: A5_38_08_03
            enocean_tx_id_offset: 1
            ref_level: 80
            dim_speed: 100
            block_dim_value: 'False'

    handle:
        enocean_rx_id: 01234567
        enocean_rx_eep: F6_10_00
        status:
            type: num
            enocean_rx_key: STATUS

    actor1:
        enocean_rx_id: FFAABBCC
        enocean_rx_eep: A5_12_01
        power:
            type: num
            enocean_rx_key: VALUE

    actor1B:
        remark: Eltako FSR61, FSR61NP, FSR61G, FSR61LN, FLC61NP - Switch for Ligths
        enocean_rx_id: 1A794D3
        enocean_rx_eep: F6_02_03
        light:
            type: bool
            enocean_tx_eep: A5_38_08_01
            enocean_tx_id_offset: 1
            enocean_rx_key: B
            block_switch: 'False'
            cache: 'True'
            enforce_updates: 'True'
            visu_acl: rw

    actor_D2:
        remark: Actor with VLD Command
        enocean_rx_id: FFDB7381
        enocean_rx_eep: D2_01_07
        move:
            type: bool
            enocean_rx_key: STAT
            enocean_tx_eep: D2_01_07
            enocean_tx_id_offset: 1
            # pulsewith-attribute removed use autotimer functionality instead
            autotimer: 1 = 0  
            
    actorD2_01_12:
        enocean_rx_id: 050A2FF4
        enocean_rx_eep: D2_01_12
        switch:
            cache: 'on'
            type: bool
            enocean_rx_key: STAT_A
            enocean_channel: A
            enocean_tx_eep: D2_01_12
            enocean_tx_id_offset: 2

    awning:
        name: Eltako FSB14, FSB61, FSB71
        remark: actor for Shutter
        type: str
        enocean_rx_id: 1A869C3
        enocean_rx_eep: F6_0G_03
        enocean_rx_key: STATUS
        move:
            type: num
            enocean_tx_eep: A5_3F_7F
            enocean_tx_id_offset: 0
            enocean_rx_key: B
            enocean_rtime: 60
            block_switch: 'False'
            enforce_updates: 'True'
            cache: 'True'
            visu_acl: rw

    rocker:
        enocean_rx_id: 0029894A
        enocean_rx_eep: F6_02_01
        short_800ms_directly_to_knx:
            type: bool
            enocean_rx_key: AI
            enocean_rocker_action: **toggle**
            enocean_rocker_sequence: released **within** 0.8
            knx_dpt: 1
            knx_send: 3/0/60

        long_800ms_directly_to_knx:
            type: bool
            enocean_rx_key: AI
            enocean_rocker_action: toggle
            enocean_rocker_sequence: released **after** 0.8
            knx_dpt: 1
            knx_send: 3/0/61

        rocker_double_800ms_to_knx_send_1:
            type: bool
            enforce_updates: true
            enocean_rx_key: AI
            enocean_rocker_action: **set**
            enocean_rocker_sequence: **released within 0.4, pressed within 0.4**
            knx_dpt: 1
            knx_send: 3/0/62

    brightness_sensor:
        enocean_rx_id: 01234567
        enocean_rx_eep: A5_08_01
        lux:
            type: num
            enocean_rx_key: BRI

        movement:
            type: bool
            enocean_rx_key: MOV

    occupancy_sensor:
        enocean_rx_id: 01234567
        enocean_rx_eep: A5_07_03
        lux:
            type: num
            enocean_rx_key: ILL

        movement:
            type: bool
            enocean_rx_key: PIR

        voltage:
            type: bool
            enocean_rx_key: SVC

    temperature_sensor:
        enocean_rx_id: 01234567
        enocean_rx_eep: A5_04_02
        temperature:
            type: num
            enocean_rx_key: TMP

        humidity:
            type: num
            enocean_rx_key: HUM

        power_status:
            type: num
            enocean_rx_key: ENG

    sunblind:
        name: Eltako FSB14, FSB61, FSB71
        remark: actor for Shutter
        type: str
        enocean_rx_id: 1A869C3
        enocean_rx_eep: F6_0G_03
        enocean_rx_key: STATUS
        # runtime Range [0 - 255] s
        enocean_rtime: 80
        Tgt_Position:
            name: Eltako FSB14, FSB61, FSB71
            remark: Pos. 0...255
            type: num
            enocean_rx_id: ..:.
            enocean_rx_eep: ..:.
            enforce_updates: 'True'
            cache: 'True'
            visu_acl: rw
        Act_Position:
            name: Eltako FSB14, FSB61, FSB71
            remark: Ist-Pos. 0...255 berechnet aus (letzer Pos. + Fahrzeit * 255/rtime)
            type: num
            enocean_rx_id: ..:.
            enocean_rx_eep: ..:.
            enocean_rx_key: POSITION
            enforce_updates: 'True'
            cache: 'True'
            visu_acl: rw
            eval: min(max(value, 0), 255)
            on_update:
                - EnOcean_Item.sunblind = 'stopped'
        Run:
            name: Eltako FSB14, FSB61, FSB71
            remark: Ansteuerbefehl 0x00, 0x01, 0x02
            type: num
            enocean_rx_id: ..:.
            enocean_rx_eep: ..:.
            enocean_tx_eep: A5_3F_7F
            enocean_tx_id_offset: 0
            enocean_rx_key: B
            enocean_rtime: ..:.
            # block actuator
            block_switch: 'True'
            enforce_updates: 'True'
            cache: 'True'
            visu_acl: rw
            struct: uzsu.child
        Movement:
            name: Eltako FSB14, FSB61, FSB71
            remark: Wenn Rolladen gestoppt wurde steht hier die gefahrene Zeit in s und die Richtung
            type: num
            enocean_rx_id: ..:.
            enocean_rx_eep: A5_0G_03
            enocean_rx_key: MOVE
            cache: 'False'
            enforce_updates: 'True'
            eval: value * 255/int(sh.EnOcean_Item.sunblind.property.enocean_rtime)
            on_update:
                - EnOcean_Item.sunblind = 'stopped'
                - EnOcean_Item.sunblind.Act_Position = EnOcean_Item.sunblind.Act_Position() + value

    RGBdimmer:
        type: num
        remark: Eltako FRGBW71L - RGB Dimmer
        enocean_rx_id: 1A869C3
        enocean_rx_eep: A5_3F_7F
        enocean_rx_key: DI_0
        red:
            type: num
            enocean_tx_eep: 07_3F_7F
            enocean_tx_id_offset: 1
            enocean_rx_key: DI_0
            ref_level: 80
            dim_speed: 100
            color: red
        green:
            type: num
            enocean_tx_eep: 07_3F_7F
            enocean_tx_id_offset: 1
            enocean_rx_key: DI_1
            ref_level: 80
            dim_speed: 100
            color: green
        blue:
            type: num
            enocean_tx_eep: 07_3F_7F
            enocean_tx_id_offset: 1
            enocean_rx_key: DI_2
            ref_level: 80
            dim_speed: 100
            color: blue
        white:
            type: num
            enocean_tx_eep: 07_3F_7F
            enocean_tx_id_offset: 1
            enocean_rx_key: DI_3
            ref_level: 80
            dim_speed: 100
            color: white 
    water_sensor:
        enocean_rx_id: 00000000
        enocean_rx_eep: A5_30_03

        alarm:
            type: bool
            enocean_rx_key: ALARM
            visu_acl: ro

        temperature:
            type: num
            enocean_rx_key: TEMP
            visu_acl: ro
  
```

### Add new listening EnOcean devices

You have to know about the EnOcean RORG of your device (please search the internet or ask the vendor).

Further the RORG must be declared in the plugin.

The following status EEPs are supported:

```
* A5_02_01 - A5_02_0B	Temperature Sensors (40°C overall range, various starting offsets, 1/6°C resolution)
* A5_02_10 - A5_02_1B	Temperature Sensors (80°C overall range, various starting offsets, 1/3°C resolution)
* A5_02_20		High Precision Temperature Sensor (ranges -10*C to +41.2°C, 1/20°C resolution)
* A5_02_30		High Precision Temperature Sensor (ranges -40*C to +62.3°C, 1/10°C resolution)
* A5_04_02		Energy (optional), humidity and temperature sensor
* A5_07_03		Occupancy sensor, e.g. NodOn PIR-2-1-0x
* A5_08_01		Brightness and movement sensor
* A5_11_04		Dimmer status feedback
* A5_12_01		Power Measurement, e.g. Eltako FSVA-230V
* A5_0G_03		shutter feedback in s if actor is stopped before reaching his position (for calculation of new position)
* A5_30_01		Alarm sensor, e.g. Eltako FSM60B water leak sensor
* A5_30_03		Alarm sensor, e.g. Eltako FSM60B water leak sensor
* D2_01_07		Simple electronic switch
* D2_01_12		Simple electronic switch with 2 channels, like NodOn In-Wall module
* D5_00_01		Door/Window Contact, e.g. Eltako FTK, FTKB
* F6_02_01		2-Button-Rocker
* F6_02_02		2-Button-Rocker
* F6_02_03		2-Button-Rocker, Status feedback from manual buttons on different actors, e.g. Eltako FT55, FSUD-230, FSVA-230V, FSB61NP-230V or Gira switches.
* F6_10_00		Mechanical Handle (value: 0(closed), 1(open), 2(tilted)
* F6_0G_03		Feedback of shutter actor (Eltako FSB14, FSB61, FSB71 - actor for Shutter) if reaching the endposition and if motor is active 
```
A complete list of available EEPs is accessible at [EnOcean Alliance](http://www.enocean-alliance.org/eep/)


### Send commands: Tx EEPs

```
* A5_38_08_01		Regular switch actor command (on/off)
* A5_38_08_02		Dimmer command with fix on off command (on: 100, off:0)
* A5_38_08_03		Dimmer command with specified dim level (0-100)
* A5_3F_7F		Universal actuator command, e.g. blind control
* D2_01_07		Simple electronic switch
* D2_01_12		Simple electronic switch with 2 channels
```

The optional ref_level parameter defines default dim value when dimmer is switched on via the regular "on"" command.

## Functions
### Learning Mode

Devices that shall receive commands from the SmarthomeNG plugin must be subscribed (tought-in) first.
Generally follow the teach-in procedure as described by EnOcean:
1. Set the EnOcean device/actor into learn mode. See the manual of the respective EnOcean device for detailed information on how to enter learn mode.
2. While being in learn mode, trigger the learn telegram from SmarthomeNG (via webinterface or via interactive SmarthomeNG console)
3. Exit the learn mode of the actor

The SmarthomeNG interactive console can be reached via:

```bash
cd /usr/local/smarthome/bin
sudo systemctl stop smarthome
sudo ./smarthome.py -i
```
The learn message is issued by the following command:
```python
sh.enocean.send_learn_protocol(id_offset, device)
```
The teach-in commands vary for different EnOcean sensor/actors. The following classes are currently supported:

With device are different actuators defined:

- 10: Eltako Switch FSR61, Eltako FSVA-230V
- 20: Eltako FSUD-230V
- 21: Eltako FHK61SSR dim device (EEP A5-38-08)
- 22: Eltako FRGBW71L RGB dim devices (EEP 07-3F-7F)
- 30: Radiator Valve
- 40: Eltako shutter actors FSB61NP-230V, FSB14, FSB61, FSB71

Examples are:
```python
sh.enocean.send_learn_protocol() or sh.enocean.send_learn_protocol(0,10)
sh.enocean.send_learn_protocol(id_offset,20)
```

Where `id_offset`, range (0-127), specifies the sending ID-offset with respect to the Base-ID.
Later, the ID-offset is specified in the <item.yaml> for every outgoing send command, see the examples above.

Use different ID-offsets for different groups of actors.
After complete the teach-in procedure, leave the interactive console by `STRG+C` and add the applied id_offset to the respective EnOcean send item (enocean_tx_id_offset = ID_Offset).

### UTE teach-in

UTE stands for "Universal Uni- and Bidirectional Teach in".
When being activated on an EnOcean device the device will send a `D4` teach-in request. SmarthomeNG will answer within 500 ms with a telegram to complete the teach-in process.
To do so enable the UTE learn mode prior to the activation on the device. Again, enabling the UTE mode can be achieved via
a) The plugin webinterface
b) SmarthomeNG's interactive console - see above - and the following command `sh.enocean.start_UTE_learnmode(ID_Offset)`
