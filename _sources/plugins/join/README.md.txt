# Join

Version 1.0

This plugin allows to send command to your mobile phone via the Join API: https://joaoapps.com/join/api/

Support is provided trough the support thread within the smarthomeNG forum:

[https://knx-user-forum.de/forum/supportforen/smarthome-py/1113523-neues-plugin-join-tts-sms-phonecall-notification-uvm](https://knx-user-forum.de/forum/supportforen/smarthome-py/1113523-neues-plugin-join-tts-sms-phonecall-notification-uvm)

## Requirements
This plugin requires the library ``requests``. You can install this lib with:

```bash
sudo pip3 install requests --upgrade
```

## Configuration

### plugin.yaml

```yaml
join:
    class_name: Join
    class_path: plugins.join
    device_id: <your deviceid>
    api_key: <your apikey>
```

#### Attributes
  * `device_id`: Your own device_id.
  * `api_key`: Your own personal api key.

## Functions

### send( title=None, text=None, icon=None, find=None, smallicon=None, device_id=None, device_ids=None, device_names=None, url=None, image=None, sound=None, group=None, clipboard=None, file=None, callnumber=None, smsnumber=None, smstext=None, mmsfile=None, wallpaper=None, lockWallpaper=None, interruptionFilter=None, mediaVolume=None, ringVolume=None, alarmVolume=None)

For the definition of the respective variables refer to the Join API: https://joaoapps.com/join/api/

### get_devices()

Returns an array of all devices registered for the Join API

## Logics

```python
if (sh.your.item() == 1):
    sh.join.send(smsnumber="0123456789", smstext="Hello World") #to write a SMS from your device to a target number

if (sh.your.item() == 1):
    sh.join.send(title="01234567892", text="Hello World") #to write a notification to your device

if (sh.your.item() == 1):
    sh.join.send(find="true") #to find your device
```
