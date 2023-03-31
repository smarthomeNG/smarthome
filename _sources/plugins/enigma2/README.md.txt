# Enigma2

## Description
The Enigma2 plugin allows to control and read info from linux based Enigma2 satellite receivers, on which the OpenWebIF is installed.

## Requirements
This plugin requires lib requests. You can install this lib with:
<pre>
sudo pip3 install requests --upgrade
</pre>

It is completely based on the openwebif interface for Enigma2 devices

Forum thread to the plugin: https://knx-user-forum.de/forum/supportforen/smarthome-py/943871-enigma2-plugin

The plugin is tested with a VUSolo2 and a VUSolo4k with newest VTI Image.
It is currently also tested with a Dreambox 8000 and Dreambox 7020hd.

The version is tested with new multi-instance functionality of SmartHomeNG.

## Configuration

### plugin.yaml

The samples use multi-instance feature of SmartHomeNG.

```yaml
vusolo4k:
    plugin_name: enigma2
    host: xxx.xxx.xxx.xxx
    port: 81    # 81 for "vu"-boxes, it may be port 80 for a dreambox
    cycle: 240
    fast_cycle: 30
    ssl: False    # use https or not
    verify: False    # verify ssl certificate
    instance: vusolo4k

vusolo2:
    plugin_name: enigma2
    host: xxx.xxx.xxx.xxx
    port: 81    # 81 for "vu"-boxes, it may be port 80 for a dreambox
    cycle: 240
    fast_cycle: 30
    ssl: False    # use https or not
    verify: False    # verify ssl certificate
    instance: vusolo2
```

Note: Depending on the device a shorter cycle time can result in problems with CPU rating and, in consequence with the accessibility of the services on the device.
If cycle time is reduced, please carefully watch your device and your sh.log. In the development process, 240 seconds also worked worked fine on the used devices.

#### Attributes
  * `username`: Optional login information #not tested so far
  * `password`: Optional login information #not tested so far
  * `host`: Hostname or ip address of the Enigma2 Device.
  * `port`: Port of the Enigma2 Device, typically 80 or 81
  * `cycle`: timeperiod between two update cycles. Default is 240 seconds.
  * `ssl`: True or False => True will add "https", False "http" to the URLs in the plugin
  * `verify`: True or False => Turns certificate verification on or off. Typically False
  * `instance`: Unique identifier for each Enigma2Device / each instance of the plugin

### items.yaml

#### Example:

```yaml
enigma2:

    vusolo2:

        disc_model:
            type: str
            enigma2_data_type@vusolo2: e2hdd/e2model
            enigma2_page@vusolo2: deviceinfo
            visu_acl: ro

        disc_capacity:
            type: num
            enigma2_data_type@vusolo2: e2capacity
            enigma2_page@vusolo2: deviceinfo
            visu_acl: ro

        disc_free_space:
            type: num
            enigma2_data_type@vusolo2: e2free
            enigma2_page@vusolo2: deviceinfo
            visu_acl: ro

        e2ip:
            type: str
            enigma2_data_type@vusolo2: e2ip
            enigma2_page@vusolo2: deviceinfo
            visu_acl: ro

        e2dhcp:
            type: str
            enigma2_data_type@vusolo2: e2dhcp
            enigma2_page@vusolo2: deviceinfo
            visu_acl: ro

        e2mac:
            type: str
            enigma2_data_type@vusolo2: e2mac
            enigma2_page@vusolo2: deviceinfo
            visu_acl: ro

        e2gateway:
            type: str
            enigma2_data_type@vusolo2: e2gateway
            enigma2_page@vusolo2: deviceinfo
            visu_acl: ro

        e2netmask:
            type: str
            enigma2_data_type@vusolo2: e2netmask
            enigma2_page@vusolo2: deviceinfo
            visu_acl: ro

        e2enigmaversion:
            type: str
            enigma2_data_type@vusolo2: e2enigmaversion
            enigma2_page@vusolo2: deviceinfo
            visu_acl: ro

        e2imageversion:
            type: str
            enigma2_data_type@vusolo2: e2imageversion
            enigma2_page@vusolo2: deviceinfo
            visu_acl: ro

        e2webifversion:
            type: str
            enigma2_data_type@vusolo2: e2webifversion
            enigma2_page@vusolo2: deviceinfo
            visu_acl: ro

        e2model:
            type: str
            enigma2_data_type@vusolo2: e2model
            enigma2_page@vusolo2: about
            visu_acl: ro

        e2apid:
            type: num
            enigma2_data_type@vusolo2: e2apid
            enigma2_page@vusolo2: about
            visu_acl: ro

        e2vpid:
            type: num
            enigma2_data_type@vusolo2: e2vpid
            enigma2_page@vusolo2: about
            visu_acl: ro

        e2instandby:
            type: bool
            enigma2_data_type@vusolo2: e2instandby
            enigma2_page@vusolo2: powerstate
            visu_acl: ro

        current:

            e2videowidth:
                type: str
                enigma2_data_type@vusolo2: e2videowidth
                enigma2_page@vusolo2: about
                visu_acl: ro

            e2videoheight:
                type: str
                enigma2_data_type@vusolo2: e2videoheight
                enigma2_page@vusolo2: about
                visu_acl: ro

            eventtitle:
                type: str
                enigma2_data_type@vusolo2: current_eventtitle
                visu_acl: ro

            # more complex logic behind that data type
            eventdescription:
                type: str
                enigma2_data_type@vusolo2: current_eventdescription
                visu_acl: ro

            eventdescriptionextended:
                type: str
                enigma2_data_type@vusolo2: current_eventdescriptionextended
                visu_acl: ro

            currentvolume:
                type: num
                enigma2_data_type@vusolo2: current_volume
                visu_acl: rw

            servicename:
                type: str
                enigma2_data_type@vusolo2: e2servicename
                enigma2_page@vusolo2: subservices
                visu_acl: ro

            servicereference:
                type: str
                enigma2_data_type@vusolo2: e2servicereference
                enigma2_page@vusolo2: subservices
                visu_acl: rw

            servicestream:
                type: str
                visu_acl: rw
                eval: "'<a href=\"http://'+sh.vusolo2._enigma2_device.get_host()+':'+str(sh.vusolo2._enigma2_device.get_port())+'/web/stream.m3u?ref='+sh.enigma2.vusolo2.current.servicereference()+'\"><img class=\"ui-corner-all\" id=\"mjpgImage\" style=\"width:95%\" alt=\"Processing...\" src=\"http://'+sh.vusolo2._enigma2_device.get_host()+':'+str(sh.vusolo2._enigma2_device.get_port())+'/grab?format=png&r=720&'+sh.enigma2.vusolo2.current.servicereference()+'\"></a>'"
                eval_trigger:
                  - enigma2.vusolo2.current.servicereference

        services:

            DasErste_HD:
                type: bool
                sref@vusolo2: '1:0:19:283D:3FB:1:C00000:0:0:0:'
                enforce_updates: 'true'
                visu_acl: rw

            ZDF_HD:
                type: bool
                sref@vusolo2: '1:0:19:2B66:3F3:1:C00000:0:0:0:'
                enforce_updates: 'true'
                visu_acl: rw

            DREI_SAT:
                type: bool
                sref@vusolo2: '1:0:19:2B8E:3F2:1:C00000:0:0:0:'
                enforce_updates: 'true'
                visu_acl: rw

            PHOENIX:
                type: bool
                sref@vusolo2: '1:0:19:285B:401:1:C00000:0:0:0:'
                enforce_updates: 'true'
                visu_acl: rw

            ARTE:
                type: bool
                sref@vusolo2: '1:0:19:283E:3FB:1:C00000:0:0:0:'
                enforce_updates: 'true'
                visu_acl: rw

            KIKA:
                type: bool
                sref@vusolo2: '1:0:19:2B98:3F2:1:C00000:0:0:0:'
                enforce_updates: 'true'
                visu_acl: rw

            BR:
                type: bool
                sref@vusolo2: '1:0:19:2855:401:1:C00000:0:0:0:'
                enforce_updates: 'true'
                visu_acl: rw

            EINSPLUS:
                type: bool
                sref@vusolo2: '1:0:19:2889:40F:1:C00000:0:0:0:'
                enforce_updates: 'true'
                visu_acl: rw

            ZDFNEO:
                type: bool
                sref@vusolo2: '1:0:19:2B7A:3F3:1:C00000:0:0:0:'
                enforce_updates: 'true'
                visu_acl: rw

            SERVUSTV:
                type: bool
                sref@vusolo2: '1:0:19:1332:3EF:1:C00000:0:0:0:'
                enforce_updates: 'true'
                visu_acl: rw

        # see http://dream.reichholf.net/wiki/Enigma2:WebInterface#RemoteControl
        remote:

            TEXT:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 388
                enforce_updates: 'true'

            RED:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 398
                enforce_updates: 'true'

            GREEN:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 399
                enforce_updates: 'true'

            YELLOW:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 400
                enforce_updates: 'true'

            BLUE:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 401
                enforce_updates: 'true'

            PAUSE:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 119
                enforce_updates: 'true'

            STOP:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 128
                enforce_updates: 'true'

            PLAY:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 207
                enforce_updates: 'true'

            FF:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 159
                enforce_updates: 'true'

            REWIND:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 168
                enforce_updates: 'true'

            POWER:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 116
                enforce_updates: 'true'

            OK:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 352
                enforce_updates: 'true'

            EXIT:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 174
                enforce_updates: 'true'

            INFO:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 352
                enforce_updates: 'true'

            AUDIO:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 392
                enforce_updates: 'true'

            VIDEO:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 393
                enforce_updates: 'true'

            EPG:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 358
                enforce_updates: 'true'

            MENU:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 139
                enforce_updates: 'true'

            SUBTITLE:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 370
                enforce_updates: 'true'

            UP:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 103
                enforce_updates: 'true'

            DOWN:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 108
                enforce_updates: 'true'

            LEFT:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 105
                enforce_updates: 'true'

            RIGHT:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 106
                enforce_updates: 'true'

            VolUP:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 115
                enforce_updates: 'true'

            VolDOWN:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 114
                enforce_updates: 'true'

            MUTE:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 113
                enforce_updates: 'true'

            NEXT:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 407
                enforce_updates: 'true'

            PREVIOUS:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 412
                enforce_updates: 'true'

            KEY_0:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 11
                enforce_updates: 'true'

            KEY_1:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 2
                enforce_updates: 'true'

            KEY_2:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 3
                enforce_updates: 'true'

            KEY_3:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 4
                enforce_updates: 'true'

            KEY_4:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 5
                enforce_updates: 'true'

            KEY_5:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 6
                enforce_updates: 'true'

            KEY_6:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 7
                enforce_updates: 'true'

            KEY_7:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 8
                enforce_updates: 'true'

            KEY_8:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 9
                enforce_updates: 'true'

            KEY_9:
                type: bool
                visu_acl: rw
                enigma2_remote_command_id@vusolo2: 10
                enforce_updates: 'true'
```

## Functions

### get_audio_tracks()
This function returns an array of dicts with the following keys: "e2audiotrackdescription" (string), "e2audiotrackid" (int), "e2audiotrackpid" (int), "e2audiotrackactive" (bool)
<pre>
sh.vusolo2.get_audio_tracks()
</pre>

### send_message(messagetext, messagetype=1, timeout=10)
Sets a message to the device
messagetype: Number from 0 to 3, 0= Yes/No, 1= Info, 2=Message, 3=Attention
timeout: Number of seconds the message should stay on the device, default: 10

```python
sh.vusolo2.send_message("Testnachricht",1,10)
```

### set_power_state(value)
Sets the power state to a specific value:
0 = Toggle Standby
1 = Deepstandby
2 = Reboot
3 = Restart Enigma2
4 = Wakeup from Standby
5 = Standby

E.g. toggle standby:
```python
sh.vusolo2.set_power_state(0)
```

### get_answer()
This function checks for an answer to a sent message. If you call this method, take into account the timeout until the message can be answered and e.g. set a "while (count < 0)"

```python
sh.vusolo2.get_answer()
```
