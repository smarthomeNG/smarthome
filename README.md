

# SmartHomeNG

![Github Tag](https://img.shields.io/github/v/release/smarthomeng/smarthome?sort=semver)
![Made with Python](https://img.shields.io/badge/made%20with-python-blue.svg)
[![Build Status on TravisCI](https://travis-ci.org/smarthomeNG/smarthome.svg?branch=develop)](https://travis-ci.org/smarthomeNG/smarthome)
[![Join the chat at https://gitter.im/smarthomeNG/smarthome](https://badges.gitter.im/smarthomeNG/smarthome.svg)](https://gitter.im/smarthomeNG/smarthome?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

SmartHomeNG [1] is a software that serves a basis for home automation. It interconnects multiple devices using plugins to access their specific interfaces.
This file contains basic information about the basic directories of SmartHomeNG.

User documentation ([german](https://www.smarthomeNG.de/user)) and Developer documentation ([german](https://www.smarthomeng.de/user/entwicklung/entwicklung.html)) can be found on [www.smarthomeNG.de](https://www.smarthomeNG.de). The developer documentation is being translated and adjusted to the last release.

Additional information / documentation can be found in the [SmartHomeNG Wiki](https://github.com/smarthomeNG/smarthome/wiki). The Wiki is written in german for the greatest part.

## Used Tools

| Tool | Description |
| ---     | :--- |
| <a href="https://www.jetbrains.com/?from=SmartHomeNG"><img src="https://smarthomeng.de/images/pycharm-logo.png" width="80" height="70"></a> | SmartHomeNG was built using the Pycharm IDE. |
| <a href="https://www.jetbrains.com/?from=SmartHomeNG"><img src="https://smarthomeng.de/images/webstorm-logo.png" width="70" height="70"></a> | The admin interface of SmartHomeNG was built using the WebStorm IDE. |


## Directory Structure

| directory | description|
| ---     | :--- |
|bin 	    | the main python file is based here |
|dev 	    | if you plan to create a plugin then this is the folder you want to have a closer look at |
|doc 	    | Source files for the user- and developer documentation |
|etc 	    | the three basic configuration files smarthome.yaml, module.yaml, plugin.yaml, logic.yaml and logging.yaml are located here, you will edit these files to reflect your basic settings|
|items 	  | put here your own files for your items |
|lib 	    | some more core python modules are in this directory. You won't need to change anything here
|logics   |	here your logic files are put
|modules  | here are all loadable core-modules located (one subdirectory for every module)
|plugins  | here are all plugins located (one subdirectory for every plugin). The plugins have to be installed from a separate repository (smarthomeNG/plugins)
|scenes   | the scenes are stored here
| tests   | The code for the automated travis tests is stored here
|tools    | there are some tools which help you for creating an initial configuration
|var 	    | everything that is changed by smarthome is put here, e.g. logfiles, cache, sqlite database etc.

## Some more detailed info on the configuration files

As of Version 1.5 the old conf format will still be valid but will be moved out of the docs since it's deprecated now for some time.

### etc/smarthome.yaml
Upon installation you will need to create this file and specify your location.

```yaml
# smarthome.yaml
# look e.g. at http://www.mapcoordinates.net/de
lat: '52.52'
lon: '13.40'
elev: 36
tz: Europe/Berlin
```

### etc/module.yaml
Upon installation you will need to create this file and configure the modules and their parameters. On first start of SmartHomeNG this file is created from ```etc/module.yaml.default```.

An example is shown below:

```yaml
# module.yaml
http:
    module_name: http
    starturl: admin

admin:
    module_name: admin

#enable, if mqtt protocol is going to be used
#mqtt:
#    module_name: mqtt

```
### etc/plugin.yaml
Upon installation you will need to create this file and configure the plugins and their parameters. On first start of SmartHomeNG this file is created from ```etc/plugin.yaml.default```.


An example is shown below:

```yaml
# plugin.yaml
database:
    plugin_name: database
    driver: sqlite3
    connect:
    -   database:./var/db/smarthomeng.db
    -   check_same_thread:0

cli:
    plugin_name: cli
    ip: 0.0.0.0
    update: True

websocket:
    plugin_name: visu_websocket


knx:
    plugin_name: knx
    host: 127.0.0.1
    port: 6720

ow:
    plugin_name: onewire

smartvisu:
    plugin_name: visu_smartvisu
    smartvisu_dir: /var/www/html/smartVISU


```

### etc/logic.yaml
In the logic.conf you specify your logics and when they will be run. 
On first start of SmartHomeNG this file is created from ```etc/logic.yaml.default```.

 An example is shown below

```yaml
# etc/logic.yaml
AtSunset:
    filename: sunset.py
    crontab: sunset
```

### items/
This directory contains one or more item configuration files.
The filename does not matter, except it has to end with '.yaml'.


```yaml
# items/global.yaml
global:
    sun:
        type: bool
        attribute: foo
```

### logics/
This directory contains your logic files. Simple or sophisitcated python scripts. You could address your smarthome item by `sh.item.path`.
If you want to read an item call `sh.item.path()` or to set an item `sh.item.path(Value)`.

```python
# logics/sunset.py
if sh.global.sun():       # if sh.global.sun() == True:
    sh.gloabl.sun(False)  # set it to False
```
