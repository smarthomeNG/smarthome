# mlgw Plugin - Bang & Olufsen Masterlink Gateway

## Changelog

### Version 1.1.1

This plugin can send commands to all Bang & Olufsen audio- and video systems which are connected to a Masterlink Gateway. Supported commands are the commands, a B&O remote can produce.

This plugin can receive telegrams, which are send by an B&O audio- or video system. These commands are the **LIGHT** and **CONTROL** commands, which originate from a B&O remote control (e.g. Beo4).

### Changes Since version 0.5

- Changed to SmartPlugin for smarthomeNG


### Changes Since version 0.4

- handling of listening for SOURCE STATUS command implemented
- handling of listening for PICT&SND STATUS commands implemented
- mlns in item.yaml can now be specified by their names (as defined in plugin.yaml) or by their number (as before)


### Changes Since version 0.3

- listening vor any LIGHT or CONTROL command implemented
- handling of listening for CONTROL Cinema-Off command for BeoSystem 3 documented
- handling of listening for CONTROL commands corrected


## Requirements

This plugin need a Bang & Olufsen Masterlink Gateway and can connect to it via TCPIP. Connecting via RS232 are not supported.

## Supported Hardware

* B&O Masterlink Gateway v2 with firmware v2.24a or later
* B&O Beolink Gateway with firmware v1.1.0 or later


## Configuration

### plugin.yaml

```yaml
mlgw:
    plugin_name: mlgw
    host: mlgw.local
    # port: 9000
    # username: mlgw
    # password: mlgw
    # rooms:
    #   - 'living'
    #   - 'kitchen'
    # Mlns: ''
    # log_mlgwtelegrams: 0
```

This plugins is looking for a masterlink gateway. By default it tries to connect to the host 'mlgw.local' on port 9000. You could change this in your plugin.yaml.

If the masterlink gateway requires a login, you can specify username and password.

To make logging output more readable, you can specify a list of rooms and MLNs.

With **log_mlgwtelegrams** you can control if decoded mlgw telegrams should be logged in the smarthome.log fie. The log level is raised to WARNING to ensure logging, if sh.py is running in quiet mode, its standard mode of operation.

	- 0 no telegrams are written to the log
	- 1 received telegrams that are not handled by the plugin are logged
	- 2 received telegrams are logged
	- 3 sent and received telegrams are logged
	- 4 send and received telegrams are logged, including keep alive traffic


### items.yaml

The following attributes are used to **send commands** to a B&O device:

#### mlgw_send
**mlgw_send** has to be specified to send commands to a B&O device. To send a b&o command (like a beo4 key-press), you have to set **mlgw_send** = *cmd*. Alternatively you could set **mlgw_send** = *ch*. In this case, you send a program/channel number to the B&O device.

When setting **mlgw_send** = *cmd*, you have two options for the datatype. You could set **type** = *str*. In this case the name of the command has to be passed to the item (e.g. 'DVD'). For the list of supported commands look at the description of the attribute **mlgw_cmd**.

As second option you could set **type** = *bool*. This way you have to specify the command to send with **mlgw_cmd**. (e.g.: **mlgw_cmd** = *'DVD'*). In this case you have to pass *True* to the item to send the preconfigured command.

When setting **mlgw_send** = *ch*, you have to define the datatype as numeric (**type** = *num*). The number passed to the item is then sent out as a sequence of mlgw Digit-commands.

**enforce_updates** = *true* has to be set in conjunction with **mlgw_send**. Otherwise the command will be send only the first time.

#### mlgw_cmd
**mlgw_cmd** has to be specified, if you set **mlgw_send** = *cmd* and define the item's datatype as *bool*. In conjunction with **mlgw_send**, the attribute **mlgw_cmd** specifies the command to send (e.g.: **mlgw_cmd** = *'DVD'*).

The following commands are supported in conjunction with **mlgw_send** at the moment:

    Source selection:
      'Standby', 'Sleep', 'TV', 'Radio', 'DTV2', 'Aux_A', 'V.Mem'),
      'DVD', 'Camera', 'Text', 'DTV', 'PC', 'Doorcam', 'A.Mem', 'CD',
      'N.Radio', 'N.Music', 'CD2'
    Digits:
      'Digit-0', 'Digit-1', 'Digit-2', 'Digit-3', 'Digit-4',
      'Digit-5', 'Digit-6', 'Digit-7', 'Digit-8', 'Digit-9'
    Source control:
      'STEP_UP', 'STEP_DW', 'REWIND', 'RETURN', 'WIND', 'Go / Play',
      'Stop', 'Yellow', 'Green', 'Blue', 'Red'
    Sound and picture control:
      'Mute', 'P.Mute', 'Format', 'Sound / Speaker', 'Menu', 'Volume UP',
      'Volume DOWN', 'Cinema_On', 'Cinema_Off'
    Other controls:
      'BACK', 'Exit'
    Continue functionality:
      'Key Release'
    Cursor functions:
      'SELECT', 'Cursor_Up', 'Cursor_Down', 'Cursor_Left', 'Cursor_Right'
    Functions:
      'Light'


#### mlgw_mln
**mlgw_mln** specifies the destination (B&O device) to which the command is being sent. The *Masterlink Node* (MLN) numbers of the B&O devices have been specified in the Masterlink Gateway configuration. You can specify the numeric value (as defined in the masterlink gateway) or for better readability, you can specify the corresponding string (as defined in *mlns = []* in plugin.yaml)

---

The following attributes are used to **receive triggers** from a B&O device. They can be used to define triggers to use within smarthome.py:

#### mlgw_listen
**mlgw_listen** has to be specified to listen for command telegrams from a B&O device. You have to specify *LIGHT* or *CONTROL* to listen for the corresponding command set. You can listen for a specific command or listen for any command

If you want to listen for a specific command, the command to listen for has to be specified in **mlgw_cmd** and the **type** of the item has to be **bool**. The item is set to true, when the corresponding command is received. Remember to set **enforce_updates** to **true** to ensure correct handling of multiple occurrences of the same command.

If you want to listen for any command, the **type** of the item has to be **str** and **mlgw_cmd** has not to be specified. In this case, the name of the command (e.g.: 'STEP_UP'*) is returned in the item.

#### mlgw_room
**mlgw_room** specifies the room (the B&O device is in) from which the command originated. The room numbers of the B&O devices have been specified in the Masterlink Gateway configuration. You can specify the numeric value (as defined in the masterlink gateway) or for better readability, you can specify the corresponding string (as defined in *rooms: []* in plugin.yaml)

#### mlgw_cmd
**mlgw_cmd** has to be specified, if you define **mlgw_listen**. In conjunction with **mlgw_listen**, the attribute **mlgw_cmd** specifies the command from a B&O remote control to listen for (e.g.: **mlgw_cmd** = *'STEP_UP'*).

The following commands are supported in conjunction with **mlgw_listen** at the moment:

    Digits:
      'Digit-0', 'Digit-1', 'Digit-2', 'Digit-3', 'Digit-4',
      'Digit-5', 'Digit-6', 'Digit-7', 'Digit-8', 'Digit-9'
    from Source control:
      'STEP_UP', 'STEP_DW', 'REWIND', 'RETURN', 'WIND', 'Go / Play',
      'Stop', 'Yellow', 'Green', 'Blue', 'Red'
    Sound and picture control (only CONTROL, only on BeoSystem 3 based TVs):
      'Cinema_On', 'Cinema_Off'
    Other controls:
      'BACK'
    Cursor functions:
      'SELECT', 'Cursor_Up', 'Cursor_Down', 'Cursor_Left', 'Cursor_Right'


#### Example

The following example item configuration illustrates every attribute and some useful settings.

```yaml
Someroom:

    bv10:
        name: BeoVision 10
        type: str
        enforce_updates: 'true'
        mlgw_send: cmd
        mlgw_mln: 3

        channel:
            name: 'BeoVision 10: Channel'
            type: num
            enforce_updates: 'true'
            mlgw_send: ch
            mlgw_mln: 3

        digit_1:
            name: 'BeoVision 10: Digit "1"'
            type: bool
            enforce_updates: 'true'
            mlgw_send: cmd
            mlgw_mln: 3
            mlgw_cmd: Digit-1

    living_light0:
        name: 'living room: Light "0"'
        type: bool
        mlgw_listen: light
        mlgw_room: living
        mlgw_cmd: Digit-0

    living_lightup:
        name: 'living room: Light Step_Up'
        type: bool
        mlgw_listen: light
        mlgw_room: living
        mlgw_cmd: Step_Up

    living_control0:
        name: 'living room: Control "0"'
        type: bool
        mlgw_listen: control
        mlgw_room: 6
        mlgw_cmd: Digit-0
```

The attribute **name** does not need to be specified. It serves in this example as a remark only.
