

# SmartHomeNG

[![Made with Python](https://img.shields.io/badge/made%20with-Python-blue.svg)](https://www.python.org)
[![Made with Angular](https://img.shields.io/badge/made%20with-Angular-blue.svg)](https://angular.io)
[![Forum](https://img.shields.io/badge/forum-KNX_User_Forum-brightgreen.svg)](https://knx-user-forum.de/forum/supportforen/smarthome-py)
[![Chat on Gitter](https://img.shields.io/badge/chat-On_Gitter-brightgreen)](https://gitter.im/smarthomeNG/smarthome?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Website smarthomeng.de](https://img.shields.io/website-up-down-green-red/http/smarthomeng.de.svg)](http://smarthomeng.de/)
[![GitHub forks](https://badgen.net/github/forks/smarthomeNG/smarthome/)](https://GitHub.com/smarthomeNG/smarthome/network/)
[![GitHub license](https://img.shields.io/github/license/smarthomeNG/smarthome.svg)](https://github.com/smarthomeNG/smarthome/blob/master/LICENSE)

![Github Tag](https://img.shields.io/github/v/release/smarthomeng/smarthome?sort=semver)
[![Aktuelles Release](https://img.shields.io/github/actions/workflow/status/smarthomeNG/smarthome/unittests.yml?branch=master)](https://github.com/smarthomeNG/smarthome/actions/workflows/unittests.yml)

develop: [![Aktuelles Release](https://img.shields.io/github/actions/workflow/status/smarthomeNG/smarthome/unittests.yml?branch=develop)](https://github.com/smarthomeNG/smarthome/actions/workflows/unittests.yml)


SmartHomeNG [1] ist eine Software die eine Basis für eine Heimautomation bereitstellt. Über Plugins können spezielle Schnittstellen angesprochen und damit die Funktionalität des Gesamtsystems erweitert werden.

Auf der ([Webseite des Projektes](https://www.smarthomeNG.de)) kann eine [Benutzerdokumentation](https://www.smarthomeNG.de) eingesehen werden.

Ein [Wiki](https://github.com/smarthomeNG/smarthome/wiki) existiert zumeist in deutscher Sprache.

Die Kernfunktionalität wird alle 6-9 Monate in einem Release erweitert und freigegeben.

## Benutzte Werkzeuge

| Werkzeug | beschreibung |
| ---     | :--- |
| <a href="https://www.jetbrains.com/?from=SmartHomeNG"><img src="https://smarthomeng.de/images/pycharm-logo.png" width="80" height="70"></a> | SmartHomeNG wird mit der Pycharm IDE entwickelt. |
| <a href="https://www.jetbrains.com/?from=SmartHomeNG"><img src="https://smarthomeng.de/images/webstorm-logo.png" width="70" height="70"></a> | Das Admin Interface von SmartHomeNG wird mit WebStorm IDE entwickelt. |

<nr>
    
---

# SmartHomeNG and other languages

SmartHomeNG [1] is a software that serves as a basis for home automation. It interconnects multiple devices using plugins to access their specific interfaces.

User documentation ([german](http://docs.smarthomeNG.de)) and developer documentation ([now part of the unified documentation](http://docs.smarthomeng.de/entwicklung/entwicklung.html)) can be found on [www.smarthomeNG.de](https://www.smarthomeNG.de)

Additional information can be found in the [SmartHomeNG Wiki](https://github.com/smarthomeNG/smarthome/wiki).

It is possible to read the documentation with [Google's translation service](https://translate.google.com/translate?hl=&sl=de&tl=en&u=https://www.smarthomeng.de/dev/user/) in other languages as well.

This readme file contains basic information about the root directories of SmartHomeNG for an overview.


## Used Tools

| Tool | Description |
| ---     | :--- |
| <a href="https://www.jetbrains.com/?from=SmartHomeNG"><img src="https://smarthomeng.de/images/pycharm-logo.png" width="80" height="70"></a> | SmartHomeNG was built using the Pycharm IDE. |
| <a href="https://www.jetbrains.com/?from=SmartHomeNG"><img src="https://smarthomeng.de/images/webstorm-logo.png" width="70" height="70"></a> | The admin interface of SmartHomeNG was built using the WebStorm IDE. |


## Directory Structure

| directory | description|
| ---       | :--- |
|bin 	    | the main python file is based here |
|dev 	    | sample files for creating own plugins and modules |
|doc 	    | Source files for the user- and developer documentation |
|etc 	    | the five basic configuration files smarthome.yaml, module.yaml, plugin.yaml, logic.yaml and logging.yaml are located here, you need to edit these files to reflect your basic settings |
|items 	    | put your own files for your items here |
|lib 	    | some more core python modules are in this directory. You won't need to change anything here |
|logics     | put your own files for your logics here |
|modules    | here are all loadable core-modules located (one subdirectory for every module) |
|plugins    | here are all plugins located (one subdirectory for every plugin). The plugins have to be installed from a separate repository (smarthomeNG/plugins) |
|scenes     | the scenes are stored here |
|tests      | the code for the automated tests is stored here |
|tools      | there are some tools which help you with creating an initial configuration |
|var 	    | everything that is changed by smarthome is put here, e.g. logfiles, cache, sqlite database etc. |

## Some more detailed info on the configuration files

As of Version 1.5 the old conf format will still be valid but is removed from the docs since it's been deprecated now for some time.

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
Upon installation you will need to create this file and configure the modules and their parameters. On first start of SmartHomeNG this file is created from ```etc/module.yaml.default```, if not already present.

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
Upon installation you will need to create this file and configure the plugins and their parameters. On first start of SmartHomeNG this file is created from ```etc/plugin.yaml.default```, if not already present.


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
    update: true

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
    sh.global.sun(False)  # set it to False
```
