.. index:: Plugins; roomba_980
.. index:: roomba_980

==========
roomba_980
==========

Das Plugin steuert einen iRobot Roomba der Serie 900.


Voraussetzungen
================

Das Plugin benötigt das Projekt `Roomba980-Python <https://github.com/NickWaterton/Roomba980-Python>`_.
Das darin enthaltene Verzeichnis ``roomba`` muss in das Plugin-Verzeichnis ``roomba_980`` kopiert
werden.

Um die für die Konfiguration nötige ``blid`` und das Passwort des Roomba zu ermitteln, wird das im
selben Projekt enthaltene Skript ``getpassword.py`` ausgeführt. Es fragt das Gerät ab und gibt u.a.
IP-Adresse, ``blid`` und Passwort aus::

    found 1 Roomba(s)
    Make sure your robot (Robii) at IP 192.168.0.100 is on the Home Base and powered on
    (green lights on). Then press and hold the HOME button on your robot until it plays
    a series of tones (about 2 seconds). Release the button and your robot will flash
    WIFI light.
    Press Enter to continue...
    Received: {
      "robotname": "Robii",
      "ip": "192.168.5.147",
      ...
    }
    Roomba (Robii) IP address is: 192.168.0.100
    blid is: 123456789013456
    Password=> ABCD EFGGDBAN <= Yes, all this string.

Die ausgegebene IP-Adresse, ``blid`` und das Passwort werden für die Parameter **adress**, **blid**
und **roombaPassword** in ``etc/plugin.yaml`` benötigt.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/roomba_980` beschrieben.


Beispiele
=========

::

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

**start**, **stop** und **dock** sind Aktoren, deren Wert nach einer kurzen Zeit automatisch
(``autotimer``) wieder zurückgesetzt wird, da sie nur den Befehl auslösen.
