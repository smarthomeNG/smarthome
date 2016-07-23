# RTR plug-in

# Configuration

## plugin.conf

<pre>
[rtr]
    class_name = RTR
    class_path = plugins.rtr
#    default_Kp = # Proportional gain
#    default_Ki = # Integral gain
</pre>

Description of the attributes:

* __default_Kp__: change default value for Kp (optional, default: 5)
* __default_Ki__: change default value for Ki (optional, default: 240)

## items.conf

To mark your item as current value add rtr_current = X
To mark your item as setpoint value add rtr_setpoint = X
To mark your item as actuator value add rtr_actuator = X

The X has to be replaced with a number. It indicate the actuator and has to be counted up.

### Example

<pre>
# items/gf.conf
[gf]
    [[floor]]
        [[[temp]]]
            name = Temp
            type = num
            knx_dpt = 9
            knx_send = 4/2/120
            knx_reply = 4/2/120
            ow_addr = 28.52734A030000
            ow_sensor = T
            rtr_current = 1

            [[[[set]]]]
                type = num
                visu = yes
                cache = On
                knx_dpt = 9
                knx_send = 4/3/120
                knx_listen = 4/3/120
                rtr_setpoint = 1

            [[[[state]]]]
                type = num
                visu = yes
                knx_dpt = 9
                knx_send = 4/1/120
                knx_listen = 4/1/120
                rtr_actuator = 1
</pre>

