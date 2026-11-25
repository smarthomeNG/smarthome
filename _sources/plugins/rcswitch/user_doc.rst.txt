.. index:: Plugins; rcswitch
.. index:: rcswitch

========
rcswitch
========

Das Plugin sendet RC-Switch-Kommandos, mit denen 433-MHz-Funksteckdosen aus SmartHomeNG heraus
geschaltet werden können. Es unterstützt zwei Betriebsarten: Der 433-MHz-Sender ist entweder direkt
an die Maschine angeschlossen, auf der SmartHomeNG läuft, oder er befindet sich auf einer anderen
Maschine und wird von SmartHomeNG per SSH angesprochen.

Voraussetzungen
================

Benötigte Hardware
-------------------

- RaspberryPi oder ein anderes Board mit digitalem GPIO
- 433-MHz-Sender
- 433-MHz-gesteuerte Funksteckdose, z.B. Brennenstuhl RCS 1000 N

Die VCC-Leitung des Senders wird an einen 5V-Ausgangspin des Boards angeschlossen, GND an einen
Massepin und DATA an einen GPIO-Pin (im Folgenden wird Pin 17 verwendet). Eine (lange) Antenne am
ANT-Pin des Senders erhöht die Reichweite.

Benötigte Software
--------------------

Auf der Maschine, an die der 433-MHz-Sender angeschlossen ist, werden **wiringPi** und
**rcswitch-pi** benötigt. Falls SmartHomeNG den Sender über das Netzwerk anspricht, werden
zusätzlich **ssh** und **sshpass** auf der SmartHomeNG-Maschine sowie ein SSH-Server auf der
Sender-Maschine benötigt.

wiringPi installieren::

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install git-core
    cd /usr/local/bin
    sudo git clone git://git.drogon.net/wiringPi
    cd wiringPi
    sudo ./build

rcswitch-pi installieren::

    cd /usr/local/bin
    sudo git clone https://github.com/r10r/rcswitch-pi.git

Vor dem Build muss in ``send.cpp`` der verwendete GPIO-Pin eingetragen und
``wiringPiSetup()`` durch ``wiringPiSetupSys()`` ersetzt werden, z.B.::

    int PIN = 17;
    ...
    if (wiringPiSetupSys() == -1) return 1;

Anschließend wird rcswitch-pi gebaut::

    cd rcswitch-pi
    make

Nicht-root-Zugriff und Test
------------------------------

Für einen ersten Test kann Schreibzugriff auf den GPIO-Pin für Nicht-root-Benutzer freigegeben
werden::

    gpio export 17 out

Eine Funksteckdose mit Code 11111 und Adresse 2 (=B) wird dann so eingeschaltet::

    ./send 11111 2 1

Schaltet die Funksteckdose an dieser Stelle nicht, sollte die Ursache geklärt werden, bevor mit der
Plugin-Konfiguration fortgefahren wird.

Da die GPIO-Freigabe einen Neustart nicht übersteht, sollte sie dauerhaft eingerichtet werden.
Dazu die Datei ``/usr/local/scripts/exportGPIO17`` anlegen::

    #!/bin/sh
    echo "17" > /sys/class/gpio/export
    echo "out" > /sys/class/gpio/gpio17/direction
    chmod 666 /sys/class/gpio/gpio17/value
    chmod 666 /sys/class/gpio/gpio17/direction

Die Datei ausführbar machen und beim Systemstart aufrufen, indem folgende Zeile in
``/etc/rc.local`` vor dem ``exit 0`` eingefügt wird::

    /usr/local/scripts/exportGPIO17

Zusätzlich muss der Benutzer, unter dem SmartHomeNG läuft, Mitglied der Gruppe **gpio** sein::

    sudo usermod -aG gpio smarthome
    sudo reboot

ssh und sshpass installieren (nur bei Fernzugriff)::

    apt-get update
    apt-get upgrade
    apt-get install ssh sshpass

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/rcswitch` beschrieben.

Beispiel
========

::

    Basement:
        LivingRoom:
            RCpowerPlug:
                TV:
                    switch:
                        type: bool
                        rc_code: 11111
                        rc_device: 2
