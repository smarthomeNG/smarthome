# eBus

## Requirements/Description
Description:
Connects to ebusd http://cometvisu.de/wiki/index.php?title=Ebusd wich is communicating with eBus heatings.
Requirements:
running ebusd in network (note: ebusd also requires an ebus-interface)

## Supported Hardware
I.e. Vaillant, Wolf, Kromschroeder or other eBus-heatings

## Configuration
### plugin.conf

<pre>
[ebus]
    class_name = eBus
    class_path = plugins.ebus
    host = localhost  # ip of ebusd
    port = 8888       # port of ebusd
    cycle = 240       # cycle of each item
</pre>  
  
    

### items.conf
Items need parameter "ebus_cmd" and "ebus_type".  
ebus_cmd is the command you use for telnet-connection to ebusd.  
ebus_type can be "get" or "set".
####ebus_set
Items are read/write. All "set"-items will be read cyclic too!
####ebus_get
Items will only be readable, i.e. sensors.

<pre>
[ebus]
  [[hk_pumpe_perc]]
    type = num
    knx_dpt = 5
    knx_send = 8/6/110
    knx_reply = 8/6/110
    ebus_cmd = "cir2 heat_pump_curr"
    ebus_type = "get"
    comment = akt. PWM-Wert Heizkreizpumpe

  [[ernergie_summe]]
    type = num
    knx_dpt = 12
    knx_send = 8/6/22
    knx_reply = 8/6/22
    ebus_cmd = "mv yield_sum"
    ebus_type = "get"
    comment = Energieertrag
  
  [[speicherladung]]
    type = bool
    knx_dpt = 1
    knx_listen = 8/7/1
    ebus_cmd = "short hw_load"
    ebus_type = "set"
    comment = Quick - WW Speicherladung
</pre>   
  
