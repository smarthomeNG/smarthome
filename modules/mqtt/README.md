# Module mqtt (README.md)

This module allows plugins to utilize the MQTT protocol. The API is described below.


## Requirements

This module is running under SmartHomeNG versions beyond v1.6.

> Note: This module needs the module handling in SmartHomeNG to be activated. Make sure, that `use_modules`in `etc/smarthome.yaml` is **not** set to False!


## Configuration

### etc/module.yaml


```yaml
# etc/module.yaml
http:
    module_name: mqtt
#    port: 8383
#    servicesport: 8384
#    showpluginlist: False
#    showservicelist: True
#    starturl: backend
#    threads: 8
#    showtraceback: True

```

#### user (optional

username for the web access. By default username `admin` is used.

#### password (optional)

password for the web access. By default empty. Without a password access is available for everyone.

#### hashed_password (optional)

hashed password for the web access. By default empty. Without a hashed password the parameter password is used.

#### service_user (optional

username for the access to webservices. By default username `serviceuser` is used.

#### service_password (optional)

password for the access to the web services. By default empty. Without a password access is available for everyone.

#### service_hashed_password (optional)

hashed password for access to the web services. By default empty. Without a hashed password the parameter Service_password is used.

#### port (optional)
The port on which the html interface listens. By default port **`8383`** is used.

#### servicesport (optional)
The port on which the html interface listens. By default port **`8384`** is used.

#### showpluginlist
If set to `False` no list of pluins with web interface is shown under `smarthomeNG.local:8383/plugins`. By default, **showpluginlist** is **True**.

#### showservicelist
If set to `True` a list of webservices is shown under `smarthomeNG.local:8384/services`. By default, ** showservicelist** is **False**.

#### starturl (optional)
The name of the plugin that is started when calling url `smarthomeNG.local:8383` without further detailing that url. If you want to startup the **backend** plugin for example: You set `starturl: backend`. That results in a redirect which redirects `smarthomeNG.local:8383` to `smarthomeNG.local:8383/backend`. 

if `starturl` is not specified or point to an url that does not exist, a redirect to `smarthomeNG.local:8383/plugins` will take place (if ** showpluginlist** is **True**). It points to a page that lists all plugins that have registered a html interface and allows you to start those interfaces.

> Note: If you have redirected to a specific plugin, you can always get to the page with the list of all plugins that have registered a html interface, by entering the url `smarthomeNG.local:8383/plugins`.

####  threads (optional)
Number of worker threads to start by cherrypy (default 8, which may be too much for slow CPUs)

#### showtraceback
If set to **True, error-pages (except for error 404) will show the Python traceback for that error.


## API of module mqtt

### Test if module mqtt is loaded

`mqtt` is a loadlable module. Therefore there is no guarantiee that it is present in every system. Before you can use this module, you have to make sure ist is loaded. You can do it by calling a method of the main smarthome object. Do it like this:

```
self.classname = self.__class__.__name__

try:
    self.mod_mqtt = self._sh.get_module('mqtt')
except:
    self.mod_mqtt = None
    
if self.mod_mqtt == None:
    # Do what is necessary if you can't use the mqtt protocol
    # for your plugin. For example:
    self.logger.error('{}: Module ''mqtt'' not loaded - Abort loading of plugin {0}'.format(self.classname))
    return
```


### Methods for implementing a web interface

#### get_local_ip_address()
Returns the ip address under which the web interface is listening.

#### get_local_hostname()
Returns the hostname (with domain) under which the web interface is listening.

#### get_local_port()
Returns the port under which the implemented web interfaces can be reached.

#### get_local_servicesport( ... )
Returns the port under which the implemented webservices can be reached.

#### register_app()

##### Parameters
- **app**	- Instance of the CherryPy App
- **pluginname**  - Standard would be: Shortname of the plugin (name of the plugin's directory)
- **conf**  - dict with CherryPy App-Config
- **pluginclass**  - Class of the plugin
- **instance**   - Optional: Instance of the plugin (if multi-instance)
- **description**  - Optional: Description to be shown on page with plugin-list

#### register_service( ... )

##### Parameters
- **service**	- Instance of the CherryPy App
- **servicename**  - Standard would be: Shortname of the plugin (name of the plugin's directory)
- **conf**  - dict with CherryPy App-Config
- **pluginclass**  - Class of the plugin
- **instance**   - Optional: Instance of the plugin (if multi-instance)
- **description**  - Optional: Description to be shown on page with services-list

