# Phillips HUE

# Requirements

Needs httplib

## Supported Hardware

Philips hue bridge

# Configuration

## plugin.conf

Typical configuration
<pre>
[HUE]
   class_name = HUE
   class_path = plugins.hue
   hue_user = 38f625a739562a8bd261ab9c7f5e62c8
</pre>

### hue_user
A user name for the hue bridge. Usually this is a hash value of 32 hexadecimal digits.

If the user/hash is not yet authorized, you can use sh.hue.authorizeuser() (via interactive shell or via logic)
to authorize it. The link button must be pressed before.

### hue_ip
IP or host name of the hue bridge. Per default this is "Philips-hue", so that you normally don't have to
specify a value here.

### hue_port
Port number of the hue bridge. Default 80. Normally there is no need to change that.

### cycle
Cycle in seconds to how often update the state of the lights in smarthome.

Note: The hue bridge has no notification feature. Therefore changes can only be detected via polling.

## items.conf

### hue_id

Specify the lamp id. Via this parameter the hue connection
is established. 

The feature which is to be controlled is determined
via the type of the item.

type = bool - controls feature 'on' (switching lamp on/off)

type = num - controls feature 'bri' (brightness)

type = dict - controls all features

### hue_feature

Determines which feature to control. If this parameter is given, exactly that
feature is controlled. You have to choose the item type accordingly.

hue_feature = hue - controls the hue. Type must be num

hue_feature = effect - controls the effect. Type must be str.

Special: hue_feature = all - controls all settings via dict.

### Example

<pre>
# items/my.conf

[someroom]
    [[mydevice]]
        type = bool
        hue_id = 1
    [[[level]]]
        type = num
        hue_id = 1
    [[[effect]]]
        type = str
        hue_id = 1
        hue_feature = effect
    [[[all]]]
        type = dict
        hue_id = 1
        hue_feature = all
</pre>

Hint: on and bri are currently coupled, like a KNX dimmer.

## logic.conf
No logic attributes.


# Methodes

## authorizeuser()
Authorizes the user configured by hue_user config property. You have to press the link button.

<pre>
sh.hue.authorizeuser()
</pre>
