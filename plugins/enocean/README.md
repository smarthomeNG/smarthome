EnOcean - Still under development.


Configure plugin.conf
=

Add the following lines to your plugin.conf and just adapt the serial port to your port name of your enocean-adpater.
A udev-rules for the enocean-adapter is recommend. The specification of the enocean tx_id is optional but mandatory for sending control commands from the stick to a device. When controlling multiple devices, it is recommended to use the stick's BaseID (not ChipID) as transmitting ID.
For further information regarding the difference between BaseID and ChipID, see https://www.enocean.com/en/knowledge-base-doku/enoceansystemspecification:issue:what_is_a_base_id/
With the specification of the BaseID, 128 different transmit IDs are available, ranging between BaseID and BaseID + 127.

<pre>
[enocean]
    class_name = EnOcean
    class_path = plugins.enocean
    serialport = /dev/ttyUSB0
    tx_id      = FFFF_4680
</pre>


Learning Mode:
For some enocean devices it is important to teach in the enocean stick first. In order to send a special learning message, start smarthome with the interactive console: ./smarthome.py -i
Then use the following command:
<pre>
    sh.enocean.send_learn(ID_Offset)
</pre>
, where ID_Offset, range (0-127), specifies the sending ID offset with respect to the BaseID. Later, the ID offset is specified in the item.conf for every outgoing send command, see example below.
Use different ID offsets for different groups of actors.
That's it!

Configure items
=

 The following example is for a rocker/switch with two rocker (EEP F6_02_01 or F6_02_02).
left rocker down = AI
left rocker up = AO
right rocker down = BI
right rocker up = BO

The following example is for a rocker/switch with two rocker and 6 available combinations (EEP F6_02_03).
left rocker down = AI
left rocker up = AO
right rocker down = BI
right rocker up = BO
last state of left rocker = A
last state of right rocker = B

Mechanical handle example:
handle_status = STATUS

An Enocean item must specify at minimum an enocean_rx_id (Enocean Identification Number (hex code)) and an enocean_rx_eep (Enocean Equipment Profile). Send items additionally hold an enocean_tx_id_offset.


Example item.conf
=
<pre>
[Enocean]
    [[Outside_Temperature]]
        type = num
        enocean_rx_id = 0180924D
        enocean_rx_eep = A5_02_05
        enocean_rx_key = TMP
    [[Door]]
        enocean_rx_id = 01234567
        enocean_rx_eep = D5_00_01
        [[[status]]]
            type = bool
            enocean_rx_key = STATUS
    [[FT55switch]]
        enocean_rx_id = 012345AA
        enocean_rx_eep = F6_02_03
            [[[up]]]
                type = bool
                enocean_rx_key = BO
            [[[down]]]
                type = bool
                enocean_rx_key = BI
    [[dimmer1]]
        enocean_rx_id = 00112233
        enocean_rx_eep = A5_11_04
        [[[light]]]
            type = bool
            enocean_rx_key = STAT
            enocean_tx_eep = A5_38_08_02
            enocean_tx_id_offset = 1
            [[[[level]]]]
                type = num
                enocean_rx_key = D
                enocean_tx_eep = A5_38_08_03
                enocean_tx_id_offset = 1
                ref_level = 80
    [[handle]]
        enocean_rx_id = 01234567
        enocean_rx_eep = F6_10_00
        [[[status]]]
            type = num
            enocean_rx_key = STATUS
    [[actor1]]
        enocean_rx_id = FFAABBCC
        enocean_rx_eep = A5_12_01
        [[[power]]]
            type = num
            enocean_rx_key = VALUE
    [[actor1B]]
        enocean_rx_id = FFAABBCD
        enocean_rx_eep = F6_02_03
        [[[light]]]
            type = bool
            enocean_rx_key = B
            enocean_tx_eep = A5_38_08_01
            enocean_tx_id_offset = 2
    [[rocker]]
        enocean_rx_id = 0029894A
        enocean_rx_eep = F6_02_01
        [[[short_800ms_directly_to_knx]]]
            type = bool
            enocean_rx_key = AI
            enocean_rocker_action = **toggle**
            enocean_rocker_sequence = released **within** 0.8
            knx_dpt = 1
            knx_send = 3/0/60
        [[[long_800ms_directly_to_knx]]]
            type = bool
            enocean_rx_key = AI
            enocean_rocker_action = toggle
            enocean_rocker_sequence = released **after** 0.8
            knx_dpt = 1
            knx_send = 3/0/61
        [[[rocker_double_800ms_to_knx_send_1]]]
            type = bool
            enforce_updates = true
            enocean_rx_key = AI
            enocean_rocker_action = **set**
            enocean_rocker_sequence = **released within 0.4, pressed within 0.4**
            knx_dpt = 1
            knx_send = 3/0/62
    [[brightness_sensor]]
        enocean_rx_id = 01234567
        enocean_rx_eep = A5_08_01
        [[[lux]]]
            type = num
            enocean_rx_key = BRI
        [[[movement]]]
            type = bool
            enocean_rx_key = MOV
    [[temperature_sensor]]
        enocean_rx_id = 01234567
        enocean_rx_eep = A5_04_02
        [[[temperature]]]
            type = num
            enocean_rx_key = TMP
        [[[humidity]]]
            type = num
            enocean_rx_key = HUM
        [[[power_status]]]
            type = num
            enocean_rx_key = ENG
</pre>

Add new listening enocean devices
=

You have to know about the EnOcean RORG of your device (please search the internet or ask the vendor). Further the RORG must be declared in the plugin. The following EEPs are supported:
A complete list of available EEPs is documented under http://www.enocean-alliance.org/eep/
* A5_02_01 - A5_02_0B    Temperature Sensors (40°C overall range, various starting offsets, 1/6°C resolution)
* A5_02_10 - A5_02_1B    Temperature Sensors (80°C overall range, various starting offsets, 1/3°C resolution)
* A5_02_20    High Precision Temperature Sensor (ranges -10*C to +41.2°C, 1/20°C resolution)
* A5_02_30    High Precision Temperature Sensor (ranges -40*C to +62.3°C, 1/10°C resolution)
* A5_04_02    Energy (optional), humidity and temperature sensor
* A5_08_01    Brightness and movement sensor
* A5_11_04    Dimmer status feedback
* A5_12_01    Power Measurement
* D5_00_01    Door/Window Contact, e.g. Eltako FTK, FTKB
* F6_02_01/F6_02_02    2-Button-Rocker
* F6_02_03    2-Button-Rocker, Status feedback from manual buttons on different actors, e.g. Eltako FT55, FSUD-230, FSVA-230V or Gira switches.
* F6_10_00    Mechanical Handle (value: 0(closed), 1(open), 2(tilted)

Send commands: Tx EEPs
=

* A5_38_08_01 Regular switch actor command (on/off)
* A5_38_08_02 Dimmer command with fix on off command (on: 100, off:0)
* A5_38_08_03 Dimmer command with specified dim level (0-100)
