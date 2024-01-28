# roombapysh

Dies ist ein Plugin für das SmarthomeNG Projekt um iRobot Roomba's zu steuern.
Das Plugin basiert auf https://github.com/pschmitt/roombapy.
Zur Verbindung mit einem Roomba braucht man die "blid" und das Passwort.

## Wie bekomme ich meine blid und mein Passwort?

Im Plugin-Verzeichnis findet ihr zwei Programme: discovery.py und password.py

Die discovery.py findet Roomba Staubsauger in eurem Netzwerk und zeigt einige Grunddaten an.
Sie kann ohne Parameter aufgerufen werden, oder mit der IP-Adresse des Roomba, falls diese bekannt ist.

Die Ausgabe sollte so aussehen:

```
smarthome@raspberrypi:/usr/local/smarthome/plugins/roombapysh $ python3 discovery.py

hostname=Roomba-31F4072471914530, firmware=3.4.67, ip=192.168.64.112, 
mac=48:E7:DA:BE:B2:2E, robot_name=Harry, sku=e619240, 
capabilities={'ota': 1, 'eco': 1, 'svcConf': 1}, blid=31xxxxxxxxxxxxxx
```
Um das Passwort herauszufinden, die password.py mit der IP-Adresse des Roomba aufrufen
und den Anweisungen auf dem Bildschirm folgen.

```
smarthome@raspberrypi:/usr/local/smarthome/plugins/roombapysh $ python3 password.py 192.168.64.112

Roomba have to be on Home Base powered on.
Press and hold HOME button until you hear series of tones.
Release button, Wi-Fi LED should be flashing
Press Enter to continue...
hostname=Roomba-31F4072471914530, firmware=3.4.67, ip=192.168.64.112,
mac=48:E7:DA:BE:B2:2E, robot_name=Harry, sku=e619240, 
capabilities={'ota': 1, 'eco': 1, 'svcConf': 1}, blid=31xxxxxxxxxxxxxx, 
password=:1:1yyyyyyyyyyyyyyyyyyyyyyyyyy
```
Bitte beachten, dass eine Roomba nur eine Verbindung gleichzeitig haben kann.
Wenn der Staubsauger bereits mit der iRobot App verbunden ist, bitte zuerst die App beenden!

Aus diesem Grund baut das Plugin nicht automatisch bei der Initialisierung eine
Verbindung mit dem Roomba auf. Dies muss manuell über das connect-Item eingeleitet werden.
Ich würde empfehlen, das Item auch automatisch über den autotimer (z.B. nach 2 Stunden) zurückzusetzen.

```
Harry:
    connect:
        type: bool
        roombapysh: 'connect'
        visu_acl: rw
        autotimer: 7200 = False
```

## Um das Plugin zu aktivieren, müsst ihr Folgendes in eure plugin.yaml aufnehmen:

```
Roomba:
    plugin_name: roombapysh
    address: www.xxx.yyy.zzz                        # IP Adresse des Roomba
    blid: 31xxxxxxxxxxxxxx                          # die blid des roomba Staubsaugers
    roombaPassword: :1:1yyyyyyyyyyyyyyyyyyyyyyyyyy  # das Passwort des roomba Staubsaugers
    cycle: 10                                       # Optional, nach wie vielen Sekunden die Items upgedated werden
```


## Hinweise:
- Ein Beispiel für eine item-Konfiguration findet ihr im Plugin-Verzeichnis (Harry.yaml)
- Ein Beispiel für eine smartVisu Seite findet ihr ebenfalls im Plugin-Verzeichnis (roomba.html)
