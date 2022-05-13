# Pushover  

Pushover is one out of many push services, which is compatible with Android, IOS and Windows Clients. This plugin make it possible to push messages to your clients from SmartHomeNG.

## Requirements

* Pushover API-KEY - get it from [__here__](https://pushover.net/apps/ "https://pushover.net/apps/") for free, after registration.

---
## Changelog
__2018-10-04__:

* Use new lib.network
* Added possibility to attach images

__2017-08-13__:

* Initial version

---
## Configuration  

### plugin.yaml

```yaml
po:
    class_name: Pushover
    class_path: plugins.pushover
    apiKey: <your-api-key>
    userKey: <your-user-key>
#   device: <your-device-string(optional)>
```

Description of the attributes:

* __apiKey__: set api-key globally of the sending application
* __userKey__: set user-key globally so it will be used as defaul receiving user - you can override this on each call
* __device__: set receiving device globally to filter the receive device - you can override this on each call - you can define multiple devices seperated by comma - this is optional - without all devices will receive messages

---    
## Usage:

### sh.po(title, message [, priority] [, retry] [, expire] [, sound] [, url] [, url_title] [, device] [, userKey] [, apiKey])
Send a message to your device.  

#### Parameters  
* __title__: The title of the message
* __message__:  The message - some html code possible, read https://pushover.net/api#html
* __priority__: Priority of the message - read https://pushover.net/api#priority
* __retry__: when Emergency priority set, this specifies how often (in seconds) the Pushover servers will send the same notification to the user - read https://pushover.net/api#priority
* __expire__: when Emergency priority set, this specifies how many seconds your notification will continue to be retried for (every retry seconds) - read https://pushover.net/api#priority
* __sound__: override a user's default tone choice on a per-notification basis - read https://pushover.net/api#sounds
* __url__: adds a supplementary URL that is not included in the message text, but available for the user to click on - read https://pushover.net/api#urls
* __url_title__: the title for the a supplementary URL - read https://pushover.net/api#urls
* __device__: defines and/or override the globally defined name of the receiving device
* __userKey__: defines and/or override the globally defined user-key of the receiving user
* __apiKey__: defines and/or override the globally defined api-key of the sending application
* __attachment__: adds a path/filename of a file (mostly images) to attach to the push message

All params can set to None (only message not), so they will not be set or in case of device, userKey and apiKey the global vars will be used.

#### Example
```python

# send simple message, without title (this are the min. params you need, if you defined userKey and apiKey globally)
sh.po(None, "This is my test message.")

# send simple message, with title
sh.po("Simple Test", "This is my test message.")

# send a high priority message
sh.po("Warning", "Your door is not locked!", 1)

# send simple message to device with id: e6653
sh.po("Simple Test", "This is my test message", None, None, None, None, None, None, "e6653")

# send a message with an attached image (camera snapshot for example)
sh.po(title="Simple Test", message="This is my test message", attachment="/tmp/snapshot.jpg")


```
