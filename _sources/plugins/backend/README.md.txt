# Backend GUI

This plugin delivers information about the current SmartHomeNG installation. Right now it serves as a support tool for helping other users with an installation that does not run properly. Some highlights:

* a list of installed python modules is shown versus the available versions from PyPI
* a list of items and their attributes is shown
* a list of logics and their next execution time
* a list of current schedulers and their next execution time
* direct download of sqlite database (if plugin is used) and smarthome.log
* some information about frequently used daemons like knxd/eibd is included
* supports basic authentication
* multi-language support

There is however only basic protection against unauthorized access or use of the plugin so be careful when enabling it with your network.

Call the backend-webserver: **```http://<ip of your SmartHomeNG server>:8383```**

Support is provided trough the support thread within the smarthomeNG forum:

[knx-user-forum.de/forum/supportforen/smarthome-py/959964-support-thread-f%C3%BCr-das-backend-plugin](https://knx-user-forum.de/forum/supportforen/smarthome-py/959964-support-thread-für-das-backend-plugin)

## Requirements

This version of the plugin needs **SmartHomeNG v1.4 or newer**.

This plugin is running under **Python >= 3.4** as well as the libs cherrypy and jinja2. You can install them with:
```
(sudo apt-get install python-cherrypy)
sudo pip3 install cherrypy
(sudo apt-get install python-jinja2)
sudo pip3 install jinja2
```

And please pay attention that the libs are installed for Python3 and not an older Python 2.7 that is probably installed on your system.

The log level filter in the log file view will only work with "%(asctime)s %(levelname)-8s" in the beginning of the configured format! Dateformat needs to be datefmt: '%Y-%m-%d %H:%M:%S'

> Note: This plugin needs the SmartHomeNG loadable module `http` to be installed/configured.

To support visualization, the visu_websocket plugin has to be used. It has to be PLUGIN_VERSION >= "1.1.2".


## Configuration

### plugin.yaml

```yaml
# /etc/plugin.yaml
BackendServer:
    plugin_name: backend
    #updates_allowed: 'True'
    #developer_mode: 'on'
    #pypi_timeout: 5
```


#### updates_allowed

By default, the backend server allows updates to the running smarthomeNG instance. For instance, it is possible to trigger or to reload a logic. Setting **`updates_allowed`** to **`False`**, you can disable these features.

#### developer_mode (optional)

You may specify develper_mode = on, if you are developiing within the backend plugin. At the moment, the only thing that changes is an additional button **``reload translation``** on the services page

#### pypi_timeout (optional)

Timeout for PyPI accessibility check (seconds). PyPI is queried on page "Systeminfo" to compare installed python module versions with current versions if accessible. If you receive the message "PyPI inaccessible" on systems with internet access you may increase the value. On systems where PyPI can not be reached (no/restricted internet access) you may set the timeout to 0 which disables the PyPI queries.
