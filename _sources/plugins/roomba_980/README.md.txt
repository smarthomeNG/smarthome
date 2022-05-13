# roomba_980

Dies ist ein Plugin für das SmarthomeNG Projekt um den iRobot Roomba 980 zu steuern.

zusätzlich muss das Projekt https://github.com/NickWaterton/Roomba980-Python in das Plugin Verzeichniss hinterlegt werden


## Wie bekomme ich meine blid und mein Passwort

zu erst müsst ihr das Projekt Roomba980-Python herrunterladen und das roomba Verzeichnis in das rooomba_980 Plugin Verzeichnis kopieren

in dem Verzeichnis befindet sich ein getpassword.py, das ihr ausführen müsst, danach bekommt ihr folgende meldung:

```
found 1 Roomba(s)
Make sure your robot (Robii) at IP 192.168.0.100 is on the Home Base and powered on (green lights on). Then press and hold the HOME button on your robot until it plays a series of tones (about 2 seconds). Release the button and your robot will flash WIFI light.
Press Enter to continue...
Received: {
  "robotname": "Robii",
  "sku": "R980040",
  "nc": 0,
  "ver": "3",
  "proto": "mqtt",
  "ip": "192.168.5.147",
  "hostname": "Roomba-123456789013456",
  "sw": "v2.4.6-3",
  "mac": "F0:03:8C:B5:68:63",
  "cap": {
    "carpetBoost": 1,
    "pp": 1,
    "langOta": 1,
    "binFullDetect": 1,
    "ota": 2,
    "maps": 1,
    "pose": 1,
    "eco": 1,
    "multiPass": 2,
    "edge": 1,
    "svcConf": 1
  }
}
Roomba (Robii) IP address is: 192.168.0.100
blid is: 123456789013456
Password=> ABCD EFGGDBAN <= Yes, all this string.
Use these credentials in roomba.py
```

Ganz am ende stehen die IP, blid und das Passwort welches ihr für die plugin.ymal braucht


## Um das Plugin zu aktivieren müsst ihr Folgendes in eure plugin.ymal aufnehmen:

```
roomba_980:
    class_name: ROOMBA_980
    class_path: plugins.roomba_980
    adress: '192.168.0.100'         # IP Adresse des Roomba
    blid: '123456789013456'         # die blid des roomba Staubsaugers -> kann mit der getpassword.py ausgelesen werden"
    roombaPassword: 'ABCD EFGGDBAN' # das Passwort des roomba Staubsaugers -> kann mit der getpassword.py ausgelesen werden"
    # cycle: 900                    # Optional, nach wie vielen Sekunden die nächste Statusabfrage durchgeführt wird
```


## Hier meine item.yaml:
```
roomba:

    status_batterie:
        type: num
        roomba_980: status_batterie

    status_bin_full:
        type: bool
        roomba_980: status_bin_full

    status_cleanMissionStatus_phase:
        type: str
        roomba_980: status_cleanMissionStatus_phase

    status_cleanMissionStatus_error:
        type: num
        roomba_980: status_cleanMissionStatus_error

    start:
        type: bool
        roomba_980: start
        visu_acl: rw
        autotimer: 2 = False

    stop:
        type: bool
        roomba_980: stop
        visu_acl: rw
        autotimer: 2 = False

    dock:
        type: bool
        roomba_980: dock
        visu_acl: rw
        autotimer: 2 = False

    uszu:
        name: roomba_uzsu
        type: dict
        uzsu_item: roomba.uzsu.text
        cache: 'True'
        visu_acl: rw
        enforce_updates: 'True'

        text:
            name: roomba Text
            type: str
            enforce_updates: 'True'
            autotimer: 2 = ""


    # Integration der Zeitschaltuhr mit der Abfrage vom Feiertag und Urlaubs Item
    uzsu_start:
        type: bool
        roomba_980: start
        eval: True if ( sh.roomba.uzsu.text() == "start" and sh.calendar.urlaub() == False and sh.calendar.feiertag() == False ) else False
        eval_trigger: roomba.uzsu.text

    uzsu_stop:
        type: bool
        roomba_980: stop
        eval: True if ( sh.roomba.uzsu.text() == "stop" and sh.calendar.urlaub() == False and sh.calendar.feiertag() == False ) else False
        eval_trigger: roomba.uzsu.text

    uzsu_dock:
        type: bool
        roomba_980: dock
        eval: True if ( sh.roomba.uzsu.text() == "dock" and sh.calendar.urlaub() == False and sh.calendar.feiertag() == False ) else False
        eval_trigger: roomba.uzsu.text

```

