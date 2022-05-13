# Blockly Logic Editor (beyond shNG v1.3)

## Requirements

This plugin is running under Python >= 3.4 as well as the libs cherrypy and jinja2. You can install them with:
```
(sudo apt-get install python-cherrypy)
sudo pip3 install cherrypy
(sudo apt-get install python-jinja2)
sudo pip3 install jinja2
```

And please pay attention that the libs are installed for Python3 and not an older Python 2.7 that is probably installed on your system.

> Note: This plugin needs the SmartHomeNG loadable module `http` to be installed/configured.


## Configuration

### plugin.yaml

```yaml
# /etc/plugin.yaml
Blockly:
    plugin_name: blockly
```
