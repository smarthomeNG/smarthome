# APC UPS

# Requirements

A running apcupsd with configured netserver (NIS). The plugin retrieves the information via network from the netserver. No local apcupsd is required.
The apcupsd package must be installed also on the local system (running daemon is not required). The plugin uses the "apcaccess" helper tool from the package.

## Supported Hardware

Should work on all APC UPS devices. Tested only on a "smartUPS".

# Configuration

## plugin.conf

Please provide a plugin.conf snippet for your plugin with ever option your plugin supports. Optional attributes should be commented out.

<pre>
[apcups]
    class_name = APCUPS
    class_path = plugins.apcups
#    host = localhost
#    port = 3551
</pre>

Description of the attributes:

* __host__: ip address of the NIS (optional, default: localhost)
* __port__: port of the NIS (optional, default: 3551)

## items.conf

There is only one attribute: apcups

For a list of values for this attribute call "apcaccess" on the command line. The plugin returns strings (status "online") or floats (235 =  235 Volt).

### Example

<pre>
# items/apcups.conf
[serverroom]
    [[apcups]]
        [[[linev]]]
            visu_acl = ro
            type = num 
            apcups = linev

        [[[status]]]
            visu_acl = ro
            type = str        
            apcups = status

        [[[timeleft]]]
            visu_acl = ro
            type = num       
            apcups = timeleft
</pre>
"type" depends on the values.

