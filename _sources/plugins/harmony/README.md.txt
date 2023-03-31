# Harmony Hub Plugin

This is the SmarthomeNG-Plugin for a Harmony Hub device.
For support, questions and bug reports, please refer to [KNX-User-Forum](https://knx-user-forum.de/forum/supportforen/smarthome-py/1046500-harmony-hub-plugin)


## Requirenments

- an Harmony Hub device
- SmarthomeNG version >= 1.3
- Python3 module <b>sleekxmpp</b>
- (optional) create a dummy Harmony Hub activity, [see remarks](#dummy)

```
sudo pip3 install sleekxmpp
```
---

### Device IDs and Commands

Before you can start setting up your SmarthomNG items, you have to find out the device ids and/or activities of your
configured Harmony Hub devices and their associated commands. Therefor you can use the script ```get_config.py```,
normally located under '/usr/local/smarthome/plugins/harmony'.

Execute this script like this:

```
python3 get_config.py -i HARMONY_HUB_IP
```

If you want to save the output, you can redirect the stdout to a file:

```
python3 get_config.py -i HARMONY_HUB_IP > /your/path/here.txt
```

This is an example output:

```
Activities
----------
	Shield: 24569980
	dummy: 12345678
	Filmszene: 12345123
	PowerOff: -1
	...
	...

Philips 50PFL7956K/02     device id: 31913922
---------------------------------------------
    Power
        command: PowerOff
        command: PowerOn
        command: PowerToggle
    NumericBasic
        command: 0
        command: 1
        ...
    Volume
        command: Mute
        command: VolumeDown
        command: VolumeUp
        ...
    ...

Pace S HD 201     device id: 31914808
-------------------------------------
    Power
        command: PowerToggle
    Channel
        command: ChannelPrev
        command: ChannelDown
        command: ChannelUp
        ...
    NavigationBasic
        command: DirectionDown
        command: DirectionLeft
        command: DirectionRight
        ...
    TransportBasic
        command: Stop
        command: Play
        command: Rewind
    ...

Microsoft Xbox One     device id: 31907101
------------------------------------------
    Power
        command: PowerOff
        ...
    ...
```

For a direct Harmony Hub command, you need the device id and the name of the command,
for a Harmony Hub activity the activity id.

---

### Setup plugin

- Activate the plugin in your plugins.yaml
- Set the IP for your Harmony hub device

```yaml
    harmony:
        plugin_name: harmony
        harmony_ip: 192.168.178.78
        #harmony_port: 5222 # [default: 5222, int]
        #sleekxmpp_debug: false  #[default:false, bool]
```

### Setup harmony commands and activities

To configure Harmony command(s) vou have to set an item as follows:

```
MyItem:
    type: bool
    enforce_updates: true
    harmony_command_0: DEVICE_ID/activity:COMMAND/ACTIVITY_ID(:DELAY)| ... | .... | .... | .... | ....
    harmony_command_1: DEVICE_ID/activity:COMMAND/ACTIVITY_ID(:DELAY)| ... | .... | .... | .... | ....
```

**harmony_command_0|1**     [at least one required]

All plugin attributes are only valid for items with the type 'bool'. You have to set at least one of the attributes
<b>harmony_command_0</b> or <b>harmony_command_1</b>, both values together are valid too. If the item value is
'True', the command defined for harmony_command_1 will be triggered, harmony_command_0 vice versa.<p>

As you can see the format of a **command** is always ```DEVICE_ID:COMMAND(:DELAY)``` or ```activity:ACTIVITY_ID(:DELAY)```.

The delay parameter defines the time in seconds to wait after the previous command or activity was triggered.
This parameter is optional (default: 0.2s) and can be omitted. You have to find out the right value by yourself since it
heavily depends on your devices.  
You can group more than one command or activity together and like this: ```COMMAND1 | COMMAND2 | COMMAND3```. You can
also mix activities and commands in one line: ```COMMAND1 | COMMAND2 | ACTIVITY1 | COMMAND3 ...```

#### command

To trigger a command, you have to set up the device id, the command name and an optional delay value.

Run
```get_config.py``` in the plugin folder to get all devices and their commands.

```
42282391:PowerOn
42282391:PowerOn:0.5
```

#### activity

To trigger an Harmony Hub activity, you have to indicate this by the trigger word 'activity'. This can be shorten by
the character 'a'. Run ```python3 get_config.py``` in the plugin folder to get all devices and their commands. The
following syntax is possible:

```
activity:12345678:1
a:12345678:4
```

**Attention:**<a name="dummy"></a> If your're using activities with this plugin, it's highly recommended that you create a dummy Harmony Hub activity. Just add any unused device and create an empty activity. Without this dummy, it is not possible to trigger an activity twice, if it's currently activated by the Harmony In the Harmony Hub app, you
can set all delays to 0 for that device since it has no function. If this is done, you can add your dummy command in the
harmony_command chain to make sure, your activity is triggered.

You can also trigger the default Harmony Hub activity "Power Off", that switch the current active activity off. This
can be done by sending '-1' to the Hub.

```yaml
a:-1
```

---

### Setup Harmony status items

There are two more harmony item types. They are useful to retrieve status information about the current activated
activity in the Harmony Hub. Everytime the active activity was changed (by your logics or other remotes), the items blow
are set with status values about this activity.

#### Harmony Current Activity by ID

```yaml
MyItem:
    type: num
    enforce_updates: true
    harmony_item: current_activity_id
```
To retrieve the current activated activity ID in the Harmony Hub, your item has to be type 'num' an must implement
the attribute ```harmony_item = current_activity_id```

#### Harmony Current Activity by Name

```
MyItem:
    type: str
    enforce_updates: true
    harmony_item: current_activity_name
```

To retrieve name of the current activated activity in the Harmony Hub, your item has to be type 'str' and must implement the attribute ```harmony_item: current_activity_name```

---

### Limitations

There're neither plugin limitations of how many commands are triggered simultaneously nor a logic that checks whether commands or activities influence each other or not.

---

### Examples

```yaml
    Shield:
        type: bool
        harmony_command_1:
          - 42282391:PowerOn:6
          - 42282391:InputBd:1
        harmony_command_0:
          - 42282391:PowerOff
          - activity:-1
```

If the Item 'Shield' is set to True, the AV receiver is powered on with an delay of 6 seconds after the item 'Shield'
was set to "True". With an additional delay of one second, the input channel is set to 'Bluray'.
If the Item 'Shield' is set to False, the command "PowerOff" is triggered instantly. 5 seconds later, the default
Harmony Hub activity 'Power Off' is triggered

```yaml
RTL:
    type: bool
    harmony_command_1:
      - a:12345123
      - 42282391:InputSat/Cbl:2
      - '31914808:3:0.3'
      - 31914808:Select
```

This command starts the Harmony Hub activity with the id 12345123 (e.g. 'start movie scene'). After a delay of 2 seconds, the input channel of the AV receiver is switched to SAT/Cbl. 0.3 seconds later, a '3' is triggered and committed with a 'Select' command.
