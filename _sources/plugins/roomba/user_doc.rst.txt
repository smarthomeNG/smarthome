.. index:: Plugins; roomba
.. index:: roomba

======
roomba
======

Das Plugin verbindet SmartHomeNG mit ausgewählten iRobot-Roomba-Staubsaugrobotern. Es
liest Sensorwerte des Roomba aus und sendet Fahr-/Reinigungskommandos über die Roomba
Serial Command Interface (SCI).

Voraussetzungen
================

Die Verbindung zum Roomba erfolgt entweder über Bluetooth oder über Ethernet (TCP).

Für Bluetooth wird auf dem SmartHomeNG-Rechner ``bluez`` benötigt:

::

    sudo apt-get install bluez

In diesem Fall wird **socket_type** auf ``bt`` gesetzt und **socket_addr** erhält die
Bluetooth-MAC-Adresse des Roomba. Getestet wurde dies mit einem selbstgebauten
Bluetooth-Modul sowie mit einem fertigen Adapter (z. B. "FT41 BlueRoom" von
Fussel-Tronic); ein WLAN-RS232-Adapter wurde nicht getestet.

Für die TCP-Verbindung wird **socket_type** auf ``tcp`` gesetzt, **socket_addr** erhält
die IP-Adresse und **socket_port** den Port des Roomba-Empfängers. Diese Verbindungsart
wurde bisher nicht getestet.

Für den Aufbau eigener Byte-Sequenzen über **roomba_raw** ist die Dokumentation der
Roomba SCI hilfreich, z. B. `hacking_roomba.pdf
<http://www.robotiklubi.ee/_media/kursused/roomba_sumo/failid/hacking_roomba.pdf>`_.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/roomba`
beschrieben.

Item-Attribute
===============

roomba_cmd
----------

**roomba_cmd** sendet eines der folgenden Kommandos an den Roomba: **clean**, **dock**,
**power_off**, **spot**, **max**, sowie die Fahrkommandos **forward**, **backward**,
**spin_left**, **spin_right** und **stop**.

Es kann auch eine ganze "Fahrszene" als Liste angegeben werden. Dabei werden Kommandos
und Zahlenwerte gemischt: eine Zahl in der Liste wird als Wartezeit in Sekunden vor dem
nächsten Kommando interpretiert. Das folgende Beispiel fährt 2 Sekunden rückwärts, dreht
2 Sekunden nach links, fährt 3 Sekunden vorwärts, dreht 3 Sekunden nach rechts und
beginnt nach weiteren 2 Sekunden mit der Reinigung:

::

    roomba_cmd:
      - backward
      - '2'
      - spin_left
      - '2'
      - forward
      - '3'
      - spin_right
      - '3'
      - stop
      - '2'
      - clean

roomba_raw
----------

**roomba_raw** sendet eine als Liste von Ganzzahlen angegebene, eigene Byte-Sequenz nach
der Roomba SCI direkt an den Roomba, z. B. ``[137, 0, 0, 0, 0]`` für den Stopp-Befehl.

Beispiele
=========

Das Plugin liefert die Item-Structs **roomba.commands** und **roomba.sensors** mit, die
die gängigen Kommando- und Sensor-Items fertig vorkonfiguriert enthalten:

::

    roomba:

        commands:
            struct: roomba.commands

        sensors:
            struct: roomba.sensors

        raw:
            stop:
                type: bool
                enforce_updates: 'true'
                roomba_raw:
                  - '137'
                  - '0'
                  - '0'
                  - '0'

        test_scene:
            enforce_updates: 'true'
            type: bool
            roomba_cmd:
              - backward
              - '2'
              - spin_left
              - '2'
              - forward
              - '3'
              - spin_right
              - '3'
              - stop
              - '2'
              - clean
