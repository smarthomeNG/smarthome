# Russound

## Requirements

This plugin needs a Russound audio device in the network to communicate with. 
The communication protocol for the ethernet port has to be set to RIO.

## Configuration

### plugin.yaml

```yaml
russound:
   class_name: Russound
   class_path: plugins.russound
   host: 192.168.1.123
   # port: 9621
```

This plugin talks by default with the Russound audio device with the given host ip on the 
default port 9621. 
If you have changed the default port you have to change it here as well.

### items.yaml

#### rus_path

This attribute is mandatory. If you don't provide one the item will be ignored.
The value must be given with the following format ``c.z.p`` where 
``c`` is the number of the controller,
``z`` is the number of the zone and 
``p`` is the system parameter of the Russound audio device like volume or treble.
Right know the following russound parameter types are supported:

* status = zone On/Off: item type must be bool
* volume = volume of the zone: item type must be num [0..50]
* bass = bass of the zone: item type must be num [-10..10]
* treble = treble of the zone: item type must be num [-10..10]
* balance = balance of the zone: item type must be num [-10..10]
* turnonvolume = volume on zone on: item type must be num [0..50]
* currentsource = number of the source: item type must be num
* mute = mute the zone volume: item type must be bool
* loudness = loudness of the zone: item type must be bool
* partymode = party mode setting of the zone: item type must be string [ON/OFF/MASTER]
* donotdisturb = do not disturb setting of the zone: item type must be string
* name = name of the zone (readonly)

For all parameters with specified ranges (volume, turnonvolume, bass, treble, balance)
all values out of range are ignored and the minimum or maximum value will be taken. 
So if you set balance to ``15`` the plugin will send ``10`` to the Russound audio device.

Besides the above parameters there are so called key codes. This are special values send
like from a remote control which effects the current state of the Russound audio device
itself or maybe a connected device if the Russound audio device can communicate with it.
Look in the manual of your Russound which key codes are possible. 
If you specify a parameter not on the above list it will be interpreted as key code and 
send to the russound audio device as a "KeyRelease" event. 
This way you can e.g. define ``rus_path=1.5.channelup`` which will send the key code 
"channelup" to the russound. In case of the internal radio tuner this will change the current channel.

For such key codes it will be best to define the item with the aditional attribute 
``enforce_updates=true`` so that the value of the item is not important. 
That means you can e.g. use a KNX push device that sends a ONE on every push 
to a group address and SmartHomeNG listens for that address. 
With this on every push the channelup key code is sent.

#### Example

```yaml
dg:

    bedroom:

        audio:
            type: bool
            rus_path: 1.1.status
            knx_dpt: 1
            knx_send: 12/1/0
            knx_listen: 12/1/0

            volume:
                type: num
                rus_path: 1.1.volume
                knx_dpt: 5
                knx_send: 12/1/1
                knx_listen: 12/1/1

            bass:
                type: num
                rus_path: 1.1.bass
                knx_dpt: 6
                knx_send: 12/1/2
                knx_listen: 12/1/2

            treble:
                type: num
                rus_path: 1.1.treble

            balance:
                type: num
                rus_path: 1.1.balance

            turnonvolume:
                type: num
                rus_path: 1.1.turnonvolume

            source:
                type: num
                rus_path: 1.1.currentsource

            mute:
                type: bool
                rus_path: 1.1.mute

            channelup:
                type: bool
                rus_path: 1.1.channelup
                knx_dpt: 1
                knx_listen: 12/1/9
                enforce_updates: 'true'

            loudness:
                type: bool
                rus_path: 1.1.loudness

            partymode:
                type: str
                rus_path: 1.1.partymode

            donotdisturb:
                type: str
                rus_path: 1.1.donotdisturb
```
