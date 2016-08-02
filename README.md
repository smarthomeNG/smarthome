

# README.md

[![Join the chat at https://gitter.im/smarthomeNG/smarthome](https://badges.gitter.im/smarthomeNG/smarthome.svg)](https://gitter.im/smarthomeNG/smarthome?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
This file contains basic information about the basic directories of smarthomeNG

| directory | description|
| ---     | :--- |
|bin 	  | the main python file is based here |
|dev 	  | if you plan to create a plugin then this is the folder you want to have a closer look at |
|etc 	  | the three basic configuration files smarthome.conf, plugin.conf and logic.conf are located here, you will edit these files to reflect your basic settings|
|examples |	some examples of items, etc. this is only for informational purpose |
|items 	  | put here your own files for your items |
|lib 	  | some more core python modules are in this directory. You won't need to change anything here
|logics   |	here your logic files are put
|plugins  | one subdirectory for every plugin is located here
|scenes   | the scenes are stored here
|tools    | there are some tools which help you for creating an initial configuration 
|var 	  | everything that is changed by smarthome is put here, e.g. logfiles, cache, sqlite database etc.

## Some more detailed info on the configuration files

### etc/smarthome.conf
Upon installation you will need to create this file and specify your location.
<pre>
# smarthome.conf
# look e.g. at http://www.mapcoordinates.net/de
lat = 52.52
lon = 13.40
elev = 36
tz = 'Europe/Berlin'
</pre>

### etc/plugin.conf
Upon installation you will need to create this file and configure the plugins and their attributes. 
An example is shown below
<pre>
[knx]
   class_name = KNX
   class_path = plugins.knx
   host = 127.0.0.1
   port = 6720
#   send_time = 600 # update date/time every 600 seconds, default none
#   time_ga = 1/1/1 # default none
#   date_ga = 1/1/2 # default none
[ow]
    class_name = OneWire
    class_path = plugins.onewire
[visu]
    class_name = WebSocket
    class_path = plugins.visu_websocket
[smartvisu]
    class_name = SmartVisu
    class_path = plugins.visu_smartvisu
    smartvisu_dir = /var/www/html/smartVISU
[cli]
    class_name = CLI
    class_path = plugins.cli
    ip = 0.0.0.0
    update = True
[sql]
    class_name = SQL
    class_path = plugins.sqlite
</pre>

### etc/logic.conf
In the logic.conf you specify your logics and when they will be run. An example is shown below
<pre>
# etc/logic.conf
[AtSunset]
    filename = sunset.py
    crontab = sunset
</pre>

### items/
This directory contains one or more item configuration files. The filename does not matter, except it has to end with '.conf'.
<pre>
# items/global.conf
[global]
    [[sun]]
        type = bool
        attribute = foo
</pre>

### logics/
This directory contains your logic files. Simple or sophisitcated python scripts. You could address your smarthome item by `sh.item.path`.
If you want to read an item call `sh.item.path()` or to set an item `sh.item.path(Value)`.

<pre>
# logics/sunset.py
if sh.global.sun():  # if sh.global.sun() == True:
    sh.gloabl.sun(False)  # set it to False
</pre>

