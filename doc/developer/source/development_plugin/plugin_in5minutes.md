# How to write a Plugin in 5 min.

Plugins are additions to the SmartHomeNG code that enable additional functions. Plugins are written in Python. To add a plugin you need the plugin code itself and an additional entry in the plugin.conf file. 
A good basis for your own plugin is found in ``dev/sample_plugin/__init__.py``

## Plugin description

### Overview

The plugin is placed in it's own folder within the plugins folder. The name of the folder ist the name of the plugin and has to be **all lowercase**.

At the moment, the Plugin is made up of a minimum of three files, which are located within that folder.

Those files are:

- `__init__.py`
- `README.md`
- `plugin.yaml`

The file `__init__.py` contains the Python code of the plugin. The code should be at least Python 3.4 compatible.

The file `README.md` contains the basic documentation (in english language) of the plugin.

The file `plugin.yaml` contains metadata for the plugin. It is used to build the documentation. In the future, additional entries will be used by a graphical configuration frontend.

To get thee plugin loaded, it has to be configured in the configuration file etc/plugin.yaml (or etc/plugin.conf for older installations).

#### The `README.md` file

The README.md file should have the following structure.

Make sure, that the first heading with the plugin name is the only first level heading (with one #) in the file.

```
# <plugin name>

## Description

Describe what the plugin does (what is it good for?)

## Support

If a support forum or thread exists, describe it and add a link to it in this section

## Version / Change History

If you want, enter the change history here

## Requirements

What other software or what hardware ist needed to use the plugin

## Configuration

### plugin.yaml

#### Parameters

#### Example plugin configuration

### items.yaml

#### Attributes

#### Example item configuration

### logic.yaml

## Functions

```

#### The metadata file `plugin.yaml`

The file containing metadata of the plugin has the following sections:

* `plugin`  -  global attributes of the plugin 
* `parameters`  - definition of the parameters used in `etc/plugin.yaml`
* `item_attributes`  -  definition of the item-attributes that are defined by this plugin
* `item_structs`  -  templates of item structures (sub-trees) for use with the plugin
* `logic_parameters`  -  definition of parameters for logics, that are implemented in the plugin
* `plugin_functions`  -  functions definied in the plugin to be used by logics


The type of the plugin is required an can be one of the following:

* gateway
* interface
* protocol
* system
* web


Example of a meta data file:

```yaml
# meta data for the plugin
plugin:
    # Global plugin attributes
    type: interface                # plugin type (gateway, interface, protocol, system, web)

parameters:
    # Definition of parameters to be configured in etc/plugin.yaml
    
item_attributes:
    # Definition of item attributes defined by this plugin
    
item_structs: NONE

logic_parameters: NONE

plugin_functions: NONE

```

### Configuring the plugin in the configuration file `etc/plugin.yaml`

The file plugin.yaml (or plugin.conf) is located in the subdirectory ``etc`` of SmartHomeNG base directory. It tells SmartHomeNG which plugins to load and where to find them. The following box is a typical entry for your new plugin in that file (old configuration file format.

Let's assume you are writing a new plugin named **myplugin**.

In the new configuration file format (yaml) the entry looks like this:

```yaml
# etc/plugin.yaml
myplugin_instance:
    plugin_name: myplugin
    parameter1: 42
```


Let's look at the parameters:

`myplugin_instance:`

This is the name you give to actual loaded instance of the plugin. You can choose whatever you like. This is the name of the plugin instance when running SmartHomeNG. If you are running multiple instances of the plugin: This name you distinguishes the instances.

`plugin_name:`

The parameter plugin_name is of course the name you give to plugin as it's directory name (all lower case). 

`parameter1`

You can add several parameters to the init file that are passed to your plugin during initialization. You can use them to set it up in a proper way.

### The file plugins/myplugin/__init__.py:

The next thing you need is the plugin itself. The main code is in the file …/plugins/myplugin/__init__.py. All plugins have the same structure. There are several functions that need to exist which are called by SmartHomeNG at certain events. For ease of use you can find an empty plugin at ``dev/sample_plugin/__init__.py``.

The name of the directory where the plugin files reside **in has to be in lower case**!

In addition you need to write your own functions for the plugin. Normally those functions are executed by the SmartHomeNG scheduler.
You can program the scheduler to call your functions at specified times or cycles. See chapter “The Scheduler” for more information.

**!! Look at the sample plugin in /dev/sample_plugin for an actual template !!**

```python
#!/usr/bin/env python3

import logging
from lib.model.smartplugin import SmartPlugin
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Myplugin(SmartPlugin):

ALLOW_MULTIINSTANCE = False
PLUGIN_VERSION = "a.b.c"

    def __init__(self, sh, *args, **kwargs):
        """
        Initializes the plugin. The parameters describe for this method are pulled from the entry in plugin.conf.

        :param sh:  The instance of the smarthome object, save it for later references
        """
        # attention:
        # if your plugin runs standalone, sh will likely be None so do not rely on it later or check it within your code
        
        self._sh = sh
        self.logger = logging.getLogger(__name__) 	# get a unique logger for the plugin and provide it internally

        # todo:
        # put any initialization for your plugin here


    def run(self):
        """
        Run method for the plugin
        """        
        self.logger.debug("run method called")
        self.alive = True


    def stop(self):
        """
        Stop method for the plugin
        """
        self.logger.debug("stop method called")
        self.alive = False


    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is initialized.
        The plugin can, corresponding to its attribute keywords, decide what to do with
        the item in future, like adding it to an internal array for future reference

        :param item:    The item to process.
        :return:        If the plugin needs to be informed of an items change you should return a call back function
                        like the function update_item down below. An example when this is needed is the knx plugin
                        where parse_item returns the update_item function when the attribute knx_send is found.
                        This means that when the items value is about to be updated, the call back function is called
                        with the item, caller, source and dest as arguments and in case of the knx plugin the value
                        can be sent to the knx with a knx write function within the knx plugin.

        """
        if self.has_iattr(item.conf, 'foo_itemtag'):
            self.logger.debug("parse item: {0}".format(item))

        # todo
        # if interesting item for sending values:
        #   return update_item


    def parse_logic(self, logic):
        """
        Default plugin parse_logic method
        """
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass


    def update_item(self, item, caller=None, source=None, dest=None):
        """
        Write items values

        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
        # todo 
        # change 'foo_itemtag' into your attribute name
        if item():
            if self.has_iattr(item.conf, 'foo_itemtag'):
                self.logger("update_item ws called with item '{}' from caller '{}', source '{}' and dest '{}'".format(item, caller, source, dest))
                pass


def run_logic(self, logic, caller=None, source=None, dest=None):
    # …

def bla(self):
    logger.info("bla")
```

**!! Look at the sample plugin in /dev/sample_plugin for an actual template !!**

First you import certain things you need and get access to the logger. The logger allows you to log output of your plugin into the
smarthome.log file. Then you start you class. The class name has to match the ``class_name`` parameter in the plugin.conf file.
Afterwards you define the required functions.

```python
def __init__(self, smarthome, Parameter1 = False):
```

The function __init__ is called once when SmartHomeNG initializes before the items are loaded. Here you place the code that is needed to initialize you plugin. For example you can open a serial port if you need to communicate to an external device, open files, initialize other variables you need and so on.
The function receives the parameter ``smarthome`` which gives access to the SmartHomeNG functions. You should save the value in a variable for later use like in the example above.
Other parameter values are received from the file plugin.conf. You can default values for the case that the parameter is not defined in the plugin.conf file. It is a good practice to log your plugin name to the smarthome.log file.

```python
def run(self):
```

The function run is called once when SmartHomeNG starts. Run is executed after all items are loaded. You need to set the variable self.alive=True here.

```python
def stop(self):
```

This is called when SmartHomeNG shuts down. This is the right place to close files and data connections. You need to set the variable self.alive=False here.

```python
def parse_item(self, item):
```

This function is called for each item during startup when SmartHomeNG reads the item.conf file. You can access item parameters and start according action here. For example you have the following item defined in …/items/xxx.yaml

```yaml
    # items/xxx.yaml
    upstairs:
        lamp:
            type: bool
            visu_acl: rw
            ivalue: 1
            knx_dpt: 1
            …
```

You can access the parameter ``ivalue`` using the following code:

```python
    if 'ivalue' in item.conf:
        ad=item.conf['ivalue']
        return self.update_item
    else:
        return None
```

Here you check if the parameter ivalue is defined in the item. It case it is, the variable ad is set to the parameter value and the function update_item is returned. The function update_item is called each time when the item changes. Each time the lamp is switched on or off by KNX or something else, the function update_item is called.
The parameter values are always string values. Even if you set ``ivalue: 1`` in the plugin.yaml your code
will receive the string '1'. If you need a number you must convert it on your own.
If the parameter ivalue is not in the item definition, nothing is done and a change of the item does not affect you plugin at all.

```python
def parse_logic(self, logic):    # (version>=1.3)
```

This function called for each logic during startup when SmartHomeNG reads the logic.conf file. You can access logic parameters and start according action here. For example you have the following logic defined in …/etc/logic.yaml


```yaml
    etc/logic.yaml
    jalousie_up:
        filename: jalousie-up.py
        crontab: sunrise+20m
        some_plugin_setting: send-notify
```

A plugin can now check the `some_plugin_setting` to find logics where the execution is interesting for it. The following implementation could be used to register a hook for such logics:

```python
    if 'some_plugin_setting' in logic.conf:
        return self.run_logic
    else:
        return None
```

```python
def update_item(self, item, caller=None, source=None, dest=None):
```

This function is called each time an item changes. It receives several parameters:

`caller`

This is a string that identifies the one who changed the item. It’s value is e.g. KNX if the item has been changed by the KNX plugin.

`source`

…

`dest`

…

```python
def run_logic(self, logic, caller=None, source=None, dest=None):    # (version>=1.3)
```

This is like the `update_item()` method except that it is called on logic execution.

Besides those pre-defined functions you can define additional functions that are needed for your plugin.

## SmartHomeNG functions

### The Scheduler

The scheduler is one of the most important functions of SmartHomeNG It is the main time machine that starts functions at specified times. In order for your own functions to be executed you need to propagate them to the scheduler. You do this by calling certain scheduler functions. The scheduler is part of SmartHomeNG, so you need to access it using the variable you defined in the __init__ function. The most important function is add:

#### Add

```python
    self.scheduler.add('name',
                       obj,
                       prio=3,
                       cron=None,
                       cycle=None,
                       value=None,
                       offset=None,
                       next=None)
```

scheduler.add adds an entry to the scheduler. You need to call it with at least three parameters, the name, object and one timing parameter. 

`name=string`

This is a string value which is the name you give to the scheduler entry. You need the name in case you want to remove the entry from the scheduler.

`obj=function`

Obj is a function that has been defined in your plugin. This function will be called by the scheduler. If you want to pass arguments to the function use **kwargs (see description of parameter value below).

`cron`

…

`cycle=int`

Cycle is an integer value of seconds. It tells the scheduler to call your function defined by obj regularly. If you set cycles to 60 your function will be called each 60 seconds as long as long as SmartHomeNG is up.

`value`

The parameter value allows you to pass parameters to the function that is called be the scheduler. You can use a keyworded variable list of parameters. Define you function in the following way:

```python
_bla(self, **kwargs):
    if 'heinz' in kwargs:
        logger.info("found")
        em = kwargs['heinz']
```

In that case you should call the scheduler with a value list:

```python
self.scheduler.add('name',
                    self._bla,
                    value={'heinz': bla, 'tom': 10},
                    next=_ndate)
```

> **Warning**: Passing values via the scheduler only works when the scheduler is called with one single trigger time using the “next” parameter. When the scheduler is called with cycle, no parameters are passed to the called function.

`offset=int`

Offset is a value in seconds that works together with cycle. It defines the delay of the first trigger after the plugin is initialized. For example: You set offset to 20 and cycle to 10. The scheduler will trigger the first time 20 seconds after initialization and then each 10 seconds. If you do not define offset or set it to none, SmartHomeNG will choose a random value between 10 and 15 seconds.

`next=dateobject`

Next is a time object that tells the scheduler to trigger once at a specified time. It is a date object that you create e.g. using datetime like here:

```python
    nd=datetime.strptime('Jan 14 2015 8:09PM','%b %d %Y %I:%M%p').replace(tzinfo=self._sh.tzinfo())
```

Important: It is important to include the time zone info in the object. Otherwise the scheduler will crash. Here we use the time zone info from SmartHomeNG.

#### Remove

```python
    self.scheduler.remove(name)
```

The function remove removes an entry from the scheduler.

`Name=string`

Name is a string value with the name of the entry.

## Finding Items

```python
    sh.return_item(item_path)
```

Return_item allows you to find an item by its name.

`item_path=string`

The path of the item as defined in the items configuration file e.g. Floor1.Room1.Lamp1.
The function returns the item object which can be called to modify the value or access other
properties.

### Modify Items
An item can be modified by calling it like a function.

```python
item(value, caller)
```

`value`

The value that the item is set to. For a binary item is it True or False. 

`caller=string`

A name you choose the names the one who made the change to the item. This is passed caller argument of the function update_item.

## Summary

![Summary](https://github.com/smarthomeNG/smarthome/wiki/assets/pluginsummary.png)
