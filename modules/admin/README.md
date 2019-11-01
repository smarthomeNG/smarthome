# Module admin

This module implements the administration interface for SmartHomeNG.


## Requirements

This module is running under SmmartHomeNG versions beyond develop version v1.5d. It requires Python >= 3.4 as well as ... . You can install the libraries (python modules) with:

```
(sudo apt-get install ...)
sudo pip3 install ...
```

And please pay attention that the lib(s) are installed for Python3 and not an older Python 2.7 that is probably installed on your system. Be carefull to use `pip3` and nor `pip`.

> Note: This module needs the module handling in SmartHomeNG to be activated. Make sure, that `use_modules`in `etc/smarthome.yaml` is **not** set to False!


## Configuration

### etc/module.yaml


```yaml
# etc/module.yaml
admin:
    module_name: admin
```


## API of module admin

Im folgenden sind die einzelnen Teile des REST APIs beschrieben, 
welches das admin Modul zur Verfügung stellt und intern nutzt.

Wenn zur Nutzung des einzelen APIs eine Authentifizierung notwendig 
ist, ist dieses erwähnt.


### AUTH API -  Authentification for clients

#### POST /api/auth/
Authentifiziert den Client bei SmartHomeNG und erhält einen
Token (JWT) bei erfolgreicher Authentifizierung.


### CONFIG API - Get and update information about the core's configuration

#### GET /api/config
liefert die Konfiguration des Core von SmartHomeNG

#### GET /api/config/\<module (or 'common')>
liefert die Konfiguration der Modules oder des allgemeinen 
(common) Teils von SmartHomeNG

#### PUT /api/config/\<module (or 'common')>
Macht ein Update auf den entsprechenden Teil der Konfiguration

-> authentication_needed = True


### LOGICS API - xxx

#### ???


### LOGS API - Get information about logs and get log content

#### GET /api/logs
liefert die Liste der vorhandenen logs

#### GET /api/logs/\<logname>
liefert den Inhalt einer log-Datei


### PLUGINS API - Get information about installed or configured plugins

#### GET /api/plugins
liefert die Liste der installierten Plugins

#### GET /api/plugins/config
liefert die gesamte config


## PLUGIN API  -  Handle a single plugin configuration

#### POST /api/plugin/config/\<neu> 
legt eine neue Confic-section Namens ‚\<neu>‘ an

-> authentication_needed = True

#### PUT /api/plugin/config/\<plgsection>
Macht ein Update auf die Section ‚\<plgsection>‘

-> authentication_needed = True

#### DELETE /api/plugin/config/\<plgsection> 
Löscht die Section ‚\<plgsection>‘

-> authentication_needed = True


## SCENES API  -  Get information about configured scenes

####GET /api/scenes
liefert die Liste der konfigurierten Szenen


## SCHEDULER API  -  Get information about configured schedulers

####GET /api/sched
liefert die Liste der konfigurierten Scheduler


## SCHEDULER API  -  Get information about the SmartHomeNG server configuration

####GET /api/serverinfo
liefert Informationen über die Konfiguration des SmartHomeNG Servers


## THREADS API  -  Get information about running threads

####GET /api/threads
liefert die Liste der laufenden Threads


## STATUS API  -  Get running status of the SmartHomeNG server instance

####GET /api/status
liefert den aktuellen Status von SmartHomeNG


## RESTART API  -  Restart the SmartHomeNG server instance

####GET /api/restart
Startet die SmartHomeNG Server Instanz neu


##


### Test if module admin is loaded

`dummy` is a loadlable module. Therefore there is no guarantiee that it is present in every system. Before you can use this module, you have to make sure ist is loaded. You can do it by calling a method of the main smarthome object. Do it like this:

```
self.class_name = self.__class__.__name__

try:
    self.mod_admin = self._sh.get_module('admin')
except:
    self.mod_admin = None
    
if self.mod_admin == None:
    # Do what is necessary if you can't use the admin interface
    # for your plugin. For example:
    self.logger.error('{}: Module ''admin'' not loaded - Abort loading of plugin {0}'.format(self.class_name))
    return
```

