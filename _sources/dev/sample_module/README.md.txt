# Module sample

This module allows plugins to do something. The API is described below.


## Requirements

This module is running under SmmartHomeNG versions beyond v1.6. It requires Python >= 3.5.

> Note: This module needs the module handling in SmartHomeNG to be activated. Make sure, that `use_modules`in `etc/smarthome.yaml` is **not** set to False!


## Configuration

### etc/module.yaml


```yaml
# etc/module.yaml
sample:
    module_name: sample
#    param1: 42
#    param2: 'example'

```

#### param1

This parameter ...

#### param2 (optional)

This parameter ...


## API of module sample

### Test if module mqtt is loaded

`sample` is a loadlable module. Therefore there is no guarantiee that it is present in every system. Before you can use this module, you have to make sure ist is loaded. You can do it by calling a method of the main smarthome object. Do it like this:

```
self.classname = self.__class__.__name__

try:
    self.mod_sample = self._sh.get_module('sample')
except:
    self.mod_sample = None
    
if self.mod_sample == None:
    # Do what is necessary if you can't use the sample module
    # for your plugin. For example:
    self.logger.error('{}: Module ''sample'' not loaded - Abort loading of plugin {0}'.format(self.classname))
    return
```


### Methods for implementing a web interface

#### get_...()
Returns ...

##### Parameters
- **param_a**	- ...
- **param_b**  - ...

