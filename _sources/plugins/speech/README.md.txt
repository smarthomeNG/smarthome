# Speech

#### Version 1.6.0

This Plugin gets text from a smartphone running with Tasker and AutoVoice Plugin and analyses it for actions or queries with SmartHomeNG.

## Requirements
### Supported Hardware

* An Android Smartphone with

### Needed software

* Tasker and AutoVoice Plugin on Android

## Configuration

### plugin.yaml

```yaml
sp:
    class_name: Speech_Parser
    class_path: plugins.speech
    config_file: /usr/smarthome/etc/speech.py
    ip: 0.0.0.0
    # acl: w.x.y.z
    port: 2788
    default_access: rw
```

#### Attributes
  * `config_file`: path to the speech.py configuration file, with the variables and the parsing rules. You could find an example configuration file in the plugin/speech folder of smartvisu.
  * `ip`: specifies the listening IP address. By default it listens on all addresses.
  * `port`: specifies the listening port for HTTP-connections. By default it listens on 2788.
  * `acl`: with this attribute you could specify a list or a single IP address to allow HTTP updates from. By default it accepts every incoming request.
  * `default_access`: with this attribute you could specify a default access to the items, without setting the sp attribute in every item.


### items.yaml

#### sp

If this "sp"-attribute is set to 'rw' you could update this item, with the value 'ro' you only read it (status).

```yaml
test:

    item1:
        type: string
        sp: rw
```

You could test the parsing rules with a browser and as URL the path, for example: http://smarthome.pi:2788/switch lights in the kitchen on

### logic.yaml

You could use the same network attribute as in items.yaml to trigger logics.

In the context of the KNX plugin the trigger dictionary consists of the following elements:

* trigger['by']     the received text
* trigger['source']     IP adress of the sender
* trigger['value']     payload

### speech.py

speech.py ist the main configuration file with some python variables and a dict with error messages.
An example "speech.py"-file is located in the plugin directory (/plugins/speech/speech.py), you should use a copy as starting point. Specify the copy of "speech.py" in the "plugin.yaml"-file.
The error messages can be customized in dictError, the construction is self explained in the example-file.

The importend list ist "varParse" with the rules to analyze the received message.

This is the construction of varParse:
```
    Name of the list                               Return value                              Answer again with place holders
          |     Item- or Logic-Name with placeholder      | Searchstring with variables/lists             |     Optional: "item" (default) or "logic"
    varParse = [                  |                       |                   |           |                  |                    |
                     ["%x%.lights.kitchen.switch", "%y%", [varXYZ, 'search word1', varWXY], "OK, the command has been executed", 'item'],
                     [ ... ]
               ]
```

The order determines the priority, only the first rule that applies is executed all other no more.
The numbering wildcard (%x%) corresponds to the order of the lists/words starting with zero,
example: [varLight, varRoom, varSwitch] the numbering wildcard %0% will be replaced with the return value of varLight, %1% by varRoom and %2% from varSwitch.
If no type is specified a item will be assumed, if you wish to trigger a logic then must 'logic' be specified.
varParse must have this name and be entered after the other lists.

The other lists (varXYZ) are mounted together as follows:

```
    Name of list        searchstring1 is the replace value
          |         return value         |               other searchstrings
    varExample = [       |               |                |               |
                     ['return_value', ['searchstring1', 'searchstring2', 'searchstring3']],
                     [ ... ]
                   ]
```

The return value can, for example, be a part of the item or a value that is returned.
Is defined as the return value %status%, then the value of the item is retrieved and returned (see example temperature)
Important: All Keywords in lowercase!

## Usage

This speech parser plugin works with Android Smartphones with installed tasker and the AutoVoice-Plugin.

Configuration of Tasker with AutoVoice-Plugin:

1. Add a new profile, as first context choose "Event", than "Plugin" and next "AutoVoice No Match".
2. Enter Task choose New Task and give it a name for example speech_parser
3. Add an Action, choose "Variables", than "Variable Set" and use the following Variables for Name "%avcommsEncode" and for To "%avcomms()"
4. Add a next Task, choose again "Variables", than "Variable Convert" with Name "%avcommsEncode" and as Function "URL Encode".
5. Add a third Task, choose "Net and "HTTP Get", with the values Server:Port for example "http://smarthome.pi:2788" and as Path "/%avcommsEncode".
6. And finally add a fourth Task, choose "Alert", than "Say" and as Text use "%HTTPD"

That's all, use the microphone symbol to speak a command and tasker sends this as text to smarthome.py.

KNXfriend at "knx-user-forum.de" wrote that it also works with Automagic.

## Links

* Tasker: https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm
* AutoVoice: https://play.google.com/store/apps/details?id=com.joaomgcd.autovoice
* AutoVoice Pro: https://play.google.com/store/apps/details?id=com.joaomgcd.autovoice.unlock
* Automagic (alternative for Tasker with AutoVoice, thanks for the tip from KNXfriend): https://play.google.com/store/apps/details?id=ch.gridvision.ppam.androidautomagic


