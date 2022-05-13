# Kathrein

## Requirements
This plugin has no requirements or dependencies.

## ToDo

The webinterface needs to be implemented

## Configuration

### plugin.yaml

```yaml
kathrein:
    class_name: Kathrein
    class_path: plugins.kathrein
    host: 192.168.0.149
#    port: 9000
#    kathreinid: 1
```

#### Attributes

  * `host`: specifies the ip address of your Kathrein device.
  * `port`: if you want to use a nonstandard port.
  * `kathreinid`: if you have more than one Kathrein device, you can identify them with the kahtreinid in the item configuration.

### items.yaml

#### kathrein

There are two possibilities to use this attribute.
  * Define it on a string item and set it to `true`: With this configuration, every string you set to this item will be send to the Kathrein device.
  * Define it on a boolean item and set it to a key value: With this configuration, the specified key value is sent whenever you set the item to `true` (if the item is only for sending a specific command to the tv then you should consider using the `enforce_updates` attribute, too). It is even possible to define several keys separated with a '|'.

#### kathreinid

With this attribute you can define to which kathrein device you want to send the specified command. If there is only one device configured you can avoid setting this attribute (not tested yet -> give some feedback if it works).

```yaml
receiver:
    name: Receiver
    type: str
    kathrein: 'true'
    kathreinid: 1
    enforce_updates: 'true'

    mute:
        name: Mute
        type: bool
        visu_acl: rw
        kathrein: mute
        kathreinid: 1
        enforce_updates: 'true'

    media:
        name: Media
        type: bool
        visu_acl: rw
        kathrein: media
        kathreinid: 1
        enforce_updates: 'true'
        knx_dpt: 1
        knx_listen: 0/0/7
```

#### Key Values
And here is a list of possible key values. It depends on your device if all of them are supported.

```
tvr
0
1
2
3
4
5
6
7
8
9
menu
p+
p-
mute
epg
up
down
right
left
exit
standby
text
vol+
vol-
info
fav
pip
opt
tvr
archiv
media
fback
play
fforward
pause
rec
stop
```

### logic.yaml

Currently there is no logic configuration for this plugin.

## Functions

Currently there are no functions offered from this plugin.
