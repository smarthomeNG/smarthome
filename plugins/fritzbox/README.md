# FritzBox

# Requirements
This plugin has no requirements or dependencies.
At the moment only fritzbox firmware versions before 5.50 are supported.

# Configuration

## plugin.conf
<pre>
[fritzbox]
    class_name = FritzBox
    class_path = plugins.fritzbox
    host = fritz.box
    password = blub
</pre>

### Attributes
  * `host`: specifies the hostname or ip address of the FritzBox.
  * `password`: the password of the FritzBox web interface.

## items.conf

### fritzbox
This attribute defines supported functions of the plugin. The function is executed, when the item is set to a bool `true` value.
Functions supported in the plugin:
 * `call <<from>> <<to>>`: The FritzBox will initiate a call from the number (outgoing line) defined with `from` to a number defined with `to`.

### fritzbox:<<telcfg>>
This attributes represents direct access to the FritzBox webinterface. Each attribute which starts with `fritzbox:` is taken to create a dictionary, which is sent to the FritzBox. Here you can use every command which is available for the telcfg interface (just replace the `telcfg:` with `fritzbox:`). A list of known commands is described here: http://www.wehavemorefun.de/fritzbox/Telcfg

Example item:

<pre>

[fb]
    [[call1]]
        type=bool
        fritzbox=call **610 **611
    [[call2]]
        type=bool
        fritzbox:settings/UseClickToDial = '1'
        fritzbox:command/Dial = '**610'
        fritzbox:settings/DialPort = '**611'

</pre>

Both `call1` and `call2` will have the same effect. The first uses the implemented call function. The later uses the telcfg commands which are used internally in the call function. With the second option you can control almost anything which can be controlled via the web interface of your FritzBox.

## logic.conf

Currently there is no logic configuration for this plugin.

# Functions

## call(from, to)
This function calls a specified number with the specified caller.
<pre>
sh.fritzbox.call('**610', '**611')
</pre>

