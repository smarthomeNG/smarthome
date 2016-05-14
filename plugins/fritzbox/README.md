# FritzBox

# Requirements
This plugin has no requirements or dependencies.
At the moment only fritzbox firmware versions after 5.50 are supported.

I have tested it with my FritzBox 7390 and FritzOS 06.03.

# Configuration

## plugin.conf
<pre>
[fritzbox]
    class_name = FritzBox
    class_path = plugins.fritzbox
    username = secret
    password = secret
#   host = fritz.box
#   cycle = 300
</pre>

### Attributes
  * `username`/password`: required login information
  * `host`: specifies the hostname or ip address of the FritzBox.
  * `cycle`: timeperiod between two update cycles. Default is 300 seconds.

## items.conf

### fritzbox
This attribute defines supported functions of the plugin. See the the example for the supported values and options.

### Example:
<pre>
[example]
    [[fritzbox]]
        [[[ip]]]
            type = str
            fritzbox = external_ip
        [[[connected]]]
            type = bool
            fritzbox = connected
        [[[packets_sent]]]
            type = num
            fritzbox = packets_sent
        [[[packets_received]]]
            type = num
            fritzbox = packets_received
        [[[bytes_sent]]]
            type = num
            fritzbox = bytes_sent
        [[[bytes_received]]]
            type = num
            fritzbox = bytes_received
        [[[tam]]]  # telephone answering machine
            type = bool
            fritzbox = tam # read only!
            fb_tam = 0
        [[[tam2]]]  # 2nd telephone answering machine
            type = bool
            fritzbox = tam # read only!
            fb_tam = 1
        [[[wlan]]]
            type = bool
            fritzbox = wlan
        [[[wlan_2]]]
            type = bool
            fritzbox = wlan
            fb_wlan = 2  # 5 GHz
        [[[link]]]
            type = bool
            fritzbox = link
        [[[host]]]
            type = bool
            fritzbox = host
            fb_mac = XX:XX:XX:XX:XX:XX 
    [[fbswitch]]
        type = bool
        fritzbox = switch
        fb_ain = 081111111111
        [[[energy]]]
            type = num
            fritzbox = energy  # Wh
        [[[power]]]
            type = num
            fritzbox = power  # mW
    [[fbswitch2]]
        type = num
        fritzbox = power
        fb_ain = 082222222222
        eval = value / 1000  # convert from mW to W
</pre>

## logic.conf
If you specify `fritzbox = callmonitor` your logic will be called at every call event of your FritzBox. Have a look at the trigger['value'] for information about the event.
You have to enable the monitor of your FritzBox by calling `#96*5*` from your phone. You could disable it with `#96*4*`.

<pre>
[Callmonitor]
    filename = callmonitor.py
    fritzbox = callmonitor
</pre>

# Functions

## call(from, to)
This function calls a specified number from the specified caller. If your calling external numbers, you could speed up the dial process by appending a `#` to the to-number.
<pre>
sh.fritzbox.call('**610', '**611')
</pre>

## calllist()
This function returns a list of all calls.

## hangup()
This function hangs up ongoing calls.

## reboot()
This function reboots the FritzBox.

## reconnect()
This function reconnect the upstream connection.

## webcm(commands)
This is a legacy function to the 'old' interface. See [www.wehavemorefun.de/fritzbox/Telcfg](http://www.wehavemorefun.de/fritzbox/Telcfg) for a list of possible commands.
e.g. to make a call:
<pre>
sh.fritzbox.webcm({'telcfg:settings/UseClickToDial': '1', 'telcfg:command/Dial': '**611', 'telcfg:settings/DialPort': '**610'})
</pre>
