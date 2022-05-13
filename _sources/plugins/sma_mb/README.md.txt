modbuspy mindestens 2.3.0 (getestet, vielleicht geht es ab 1.3.2), ich verwende aktuell 2.5.1

sudo pip3 uninstall pymodbus
sudo pip3 install pymodbus==2.3.0   oder
sudo pip3 install pymodbus==2.5.1


###plugin_yaml:

```
SMAModbus1:
    plugin_name: sma_mb
    #instance: si44    # Name des Wechselrichters, nur bei mehreren laufenden Plugin Instanzen angeben
    host: <IP Adresse reinschreiben>    # z.B.: 192.168.xxx.xxx
    # port: 502        # optional: Port nummer auf dem Host
    # cycle: 150       # optional: Zyklus Zeit zur Abfrage in Sekunden    
```

###Beispiel Item

items:

```
    akku:
        ladestand:
            type: num
            smamb_register: 30005          # Seriennummer U32 RAW RO
            #smamb_register@si44: 30845    # Bei mehreren laufenden Plugin Instanzen - Sunny Island 4.4 Ladestand vom Akku
```
