# Module http (README)

This module allows plugins to implement a web interface. The API is described below. The first plugin to utilize this API is the backend plugin.

> Note: To write a plugin that utilizes this module, you have to be familiar with CherryPy. 


## Requirements

This module is running under SmartHomeNG versions beyond v1.3. It requires Python >= 3.4 as well as the lib **cherrypy**. You can install the libraries (python modules) with:

```
(sudo apt-get install python-cherrypy)
sudo pip3 install cherrypy
```

And please pay attention that the lib(s) are installed for Python3 and not an older Python 2.7 that is probably installed on your system. Be carefull to use `pip3` and nor `pip`.

> Note: This module needs the module handling in SmartHomeNG to be activated. Make sure, that `use_modules`in `etc/smarthome.yaml` is **not** set to False!


## Configuration

### etc/module.yaml


```yaml
# etc/module.yaml
http:
    module_name: http
#    port: 8383
#    servicesport: 8384
#    showpluginlist: False
    showservicelist: True
#    starturl: backend
#    threads: 8
#    showtraceback: True

```

#### user (optional)

username for the web access. By default username `admin` is used.

#### password (optional)

password for the web access. By default empty. Without a password access is available for everyone.

#### hashed_password (optional)

hashed password for the web access. By default empty. Without a hashed password the parameter password is used.

#### service_user (optional

username for the access to webervices. By default username `serviceuser` is used.

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


## API of module http

### Test if module http is loaded

`http` is a loadlable module. Therefore there is no guarantiee that it is present in every system. Before you can use this module, you have to make sure ist is loaded. You can do it by calling a method of the main smarthome object. Do it like this:

```
self.classname = self.__class__.__name__

try:
    self.mod_http = self._sh.get_module('http')
except:
    self.mod_http = None
    
if self.mod_http == None:
    # Do what is necessary if you can't start a web interface
    # for your plugin. For example:
    self.logger.error('{}: Module ''http'' not loaded - Abort loading of plugin {0}'.format(self.classname))
    return
```

### Registering a web application/interface

For registering a web interface (or a web application in CherryPy terminology) you first have to define an application configuration for cherrypy.

> Note: Be careful not to include a CherryPy ``global`` configuration.

An application configuration for CherryPy can look like this;

```
app_config = {
    '/': {
        'tools.staticdir.root': current_dir,
        'tools.auth_basic.on': self._basic_auth,
        'tools.auth_basic.realm': 'earth',
        'tools.auth_basic.checkpassword': self.validate_password,
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(current_dir, 'static')
    }
}
```

> Note: The `tools.auth_basic`entries in this example are for implementing a basic logon security. If you don`t want/need login security, delete those enties.

For registering a web application/interface you have to call the `register_app` of module `http`:

```
register_app(app_object, 
             appname, 
             app_config, 
             pluginclass, instance,
             description)
```

For example:

```
appname = 'backend'    # Name of the plugin
pluginclass = self.__class__.__name__
instance = self.get_instance_name()

self.mod_http.register_app(Backend(self, self.updates_allowed, language, self.developer_mode, self.pypi_timeout), 
                          appname, 
                          app_config, 
                          pluginclass, instance,
                          description='Administration interface for SmartHomeNG')
```

## Implementing a web interface for you plugin

For details about implementing a web interface (CherryPy application) for your plugin, refer to the CherryPy documentation.

The documentation will tell you how to expose parts of your python code to be availabe through CheryPy`s http-server.

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

