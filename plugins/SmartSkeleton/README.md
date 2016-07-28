# My Plugin

# Requirements

List the requirements of your plugin. Does it need special software or hardware?

## Supported Hardware

* list
* the
* supported
* hardware

# Configuration

## plugin.conf

Please provide a plugin.conf snippet for your plugin with ever option your plugin supports. Optional attributes should be commented out.

<pre>
[My]
   class_name = MyPlugin
   class_path = plugins.myplugin
   host = 10.10.10.10
#   port = 1010
</pre>

Please provide a description of the attributes.
This plugin needs an host attribute and you could specify a port attribute which differs from the default '1010'.

## items.conf

List and describe the possible item attributes.

### my_attr

Description of the attribute...

### my_attr2

### Example

Please provide an item configuration with every attribute and usefull settings.

<pre>
# items/my.conf

[someroom]
    [[mydevice]]
        type = bool
        my_attr = setting
</pre>

## logic.conf
If your plugin support item triggers as well, please describe the attributes like the item attributes.


# Methods
If your plugin provides methods for logics. List and describe them here...

## method1(param1, param2)
This method enables the logic to send param1 and param2 to the device. You could call it with `sh.my.method1('String', 2)`.

## method2()
This method does nothing.
