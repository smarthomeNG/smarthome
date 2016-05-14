# Solarlog

# Requirements
This plugin has no requirements or dependencies.

# Configuration

## plugin.conf
<pre>
[solarlog]
    class_name = SolarLog
    class_path = plugins.solarlog
    host = http://solarlog.fritz.box/
</pre>

### Attributes
  * `host`: specifies the hostname of the SolarLog.

## items.conf
You need to know the format details of the SolarLog to define the valid values for this plugin to work correctly. All the plugin does is to request the JavaScript files from the device and parse them. Almost the same way the webpage does when you visit the URL of your SolarLog in the browser. A description of the format can be found here (german): [http://photonensammler.homedns.org/wiki/doku.php?id=solarlog_datenformat](http://photonensammler.homedns.org/wiki/doku.php?id=solarlog_datenformat)

### solarlog
This is the only attribute for items. To retrieve values from the SolarLog data format you just have to use their variable name like on the site which was mentioned above described. If you want to use values from a array structure like the PDC value from the seconds string on the first inverter then you have to use the variable name underscore inverter-1 underscore string-1:

var[_inverter[_string]]

Maybe the next example makes it clearer.

<pre>
[pv]
    [[pac]]
        type = num
        solarlog = Pac
        rrd = 1

    [[kwp]]
        type = num
        solarlog = AnlagenKWP

        [[[soll]]]
            type = num
            solarlog = SollYearKWP

    [[inverter1]]
        [[[online]]]
            type = bool
            solarlog = isOnline

        [[[inverter1_pac]]]
            type = num
            solarlog = pac_0
            rrd = 1

        [[[out]]]
            type = num
            solarlog = out_0
            rrd = 1

        [[[string1]]]
            [[[[string1_pdc]]]]
                type = num
                solarlog = pdc_0_0
                rrd = 1
            [[[[string1_udc]]]]
                type = num
                solarlog = udc_0_0
                rrd = 1

        [[[string2]]]
            [[[[string2_pdc]]]]
                type = num
                solarlog = pdc_0_1
                rrd = 1
            [[[[string2_udc]]]]
                type = num
                solarlog = udc_0_1
                rrd = 1
</pre>

## logic.conf

Currently there is no logic configuration for this plugin.

# Functions

Currently there are no functions offered from this plugin.


