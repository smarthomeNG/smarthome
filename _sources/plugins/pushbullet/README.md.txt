# Pushbullet  

## Requirements  

### Python libraries  
* requests - [install instructions](http://docs.python-requests.org/en/latest/user/install/#install "http://docs.python-requests.org/en/latest/user/install/#install")
* magic - [install instructions](https://github.com/ahupp/python-magic "https://github.com/ahupp/python-magic")

### Other  
* Pushbullet API-KEY - get it from [__here__](http://www.pushbullet.com/ "http://www.pushbullet.com") for free  

---
## Changelog

__2018-09-07__:
* migrated to new parameter handling and logging convention

__2015-11-17__:

* Added "delete" function
* Changed any push function to return the pushbullet service result object
* Changed Logging to "warning"

__2014-08-26__:

* Added support for eMail-Addresses as deviceId
* Updated README.md with instructions "How to get your deviceId"  
* Added usage example to send a note to a specific device  

__2014-06-17__:

* __New python library dependecy: "magic" (see requirements section above)__
* Updated to pushbullet [api v2](http://www.pushbullet.com/api "http://www.pushbullet.com/api"), including new file handling  
* New *(optional)* "body" parameters for link and file pushes  

__2014-05-16__:

* Initial version

---
## Configuration  

### plugin.yaml

```
pushbullet:
    class_name: Pushbullet
    class_path: plugins.pushbullet
    # deviceid: <your-default-device-id>
    # apikey: <your-api-key>
```

Description of the attributes:

* __apikey__: set api-key globally so you do not have to set it in the function calls  
* __deviceid__: set deviceid globally so it will be used as defaul target, you can override this on each call  

---  
## How to get your deviceId

1) Use your browser to log into your account on [http://www.pushbullet.com](http://www.pushbullet.com "http://www.pushbullet.com")  
2) Select your desired target device  
3) Copy the last part of the browser url (behind the "device_iden=") into your clipboard.
4) Paste it to your plugin.yaml or your api call.  

---  
## Functions

*Pass a 'deviceid' if no set globally or if you want to send to another device.*  
*Add 'apikey' if not set globally.*  

### sh.pushbullet.note(title, body [, deviceid] [, apikey])
Send a note to your device.  

#### Parameters  
* __title__: The title of the note  
* __body__:  The note's body

#### Example

```python
#send simple note to default device
sh.pushbullet.note("Note to myself.", "Call my mother.")

#send simple note to device with id: x28d7AJFx13
sh.pushbullet.note("Note to myself.", "Call my mother.", "x28d7AJFx13")

#send simple note to user with email: teddy.tester@testing.de
sh.pushbullet.note("Note to myself.", "Call my mother.", "teddy.tester@testing.de")
```

### sh.pushbullet.link(title, url [, deviceid] [, apikey] [, body])
Send a link to your device.  

#### Parameters:  
* __title__: The title of the page linked to
* __url__:  The link url
* (optional) __body__: An optional message

#### Example
```python
# send link to device with id: x28d7AJFx13
#
sh.pushbullet.link("Pushbullet", "http://www.pushbullet.com", "x28d7AJFx13", body="Try this cool service.")
```

### sh.pushbullet.address(name, address [, deviceid] [, apikey])
Send a address to your device.  

#### Parameters:  
* __name__: The name of the place at the address  
* __address__:  The full address or Google Maps query  

#### Example
```python
# send address of "Eifel Tower" to default device
sh.pushbullet.address("Eifel Tower", "https://www.google.com/maps/place/Eiffelturm/@48.85837,2.294481,17z/data=!3m1!4b1!4m2!3m1!1s0x47e66e2964e34e2d:0x8ddca9ee380ef7e0")
```


### sh.pushbullet.list(title, title [, deviceid] [, apikey])
Send a list of items to your device.  

#### Parameters:  
* __title__: The title of the list  
* __items__:  The list items

#### Example
```python
#send a shopping list to default device
sh.pushbullet.list("Shopping list", ["Milk", "Eggs", "Salt"])
```

### sh.pushbullet.file(filepath [, deviceid] [, apikey] [, body])
Send a file to your device.  

#### Parameters:  
* __filepath__: absolute path to the file to push
* (optional) __body__: An optional message

#### Example
```python
#send smarthome log file to default device
sh.pushbullet.file("/usr/local/smarthome/var/log/smarthome.log", body="Take a look at this log-file")
```
### sh.pushbullet.delete(pushid)
Delete the push with the given id.  

#### Parameters:  
* pushid: id of of the push to delete

#### Example
```python
#send a push and delete it afterwards
result = sh.pushbullet.note("Note to myself.", "Call my mother.")
sh.pushbullet.delete(result['iden'])
```
