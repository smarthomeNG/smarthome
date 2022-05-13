yamahayxc
#########

Ein Plugin zur Steuerung von Yamaha MusicCast-kompatiblen Geräten (Receiver, Streaminglautsprecher u.ä.), z.B. An/Aus, Eingangswahl, Lautstärke und Mute, Play/Pause, aktuellen Status lesen

Die Grundlage für das Plugin wurde schamlos bei Raoul Thill geklaut, dem Autor des yamaha-Plugins für ältere Yamaha-Receiver in SmartHomeNG.


Anmerkungen
===========

Das Plugin wird nach Bedarf weiterentwickelt und unterstützt noch längst nicht alle möglichen Funktionen, die im Yamaha Extended Control (YXC)-Standard definiert sind. Ich nutze es aber selbst täglich. Die genutzten und getesteten Geräte sind RX-V483, ISX-18D und WX-010.
Das Plugin nutzt die YXC API, welche auf dem Austausch von JSON-formatierten Daten basiert. Es abonniert die Daten der konfigurierten Geräte, um laufend mit Statusmeldungen versorgt zu werden. Diese werden per UDP verteilt, solange eine Kommunikation zwischen Client (Plugin) und Gerät erfolgt und 10 Minuten nach der letzten Kommunikation. Das Plugin kann mit mehreren Verbindungen gleichzeitig umgehen. Bisher habe ich keine Fehler feststellen können, aber ich habe nur 5 Geräte zum Testen.

Items können nach eigenen Vorstellungen eingerichtet werden; sie werden vom Plugin durch das Item-Attribut ``yamahayxc_cmd`` identifiziert. Steuerungs- und Statusitems können unterhalb des Geräteitems nicht verzweigen, sie müssen alle auf derselben Ebene unmittelbar unterhalb des Geräteitems sein. (sorry)

Das ``update``-Item hat keine eigene Funktion. Wenn dieses Item geändert wird, wird der aktuelle Status vom Gerät aktiv abgefragt. Solange das Abonnement aktiv ist, wird das nicht benötigt, weil die Daten vom Gerät aktiv aktuell gehalten werden. Wenn der Timeout von 10 Minuten überschritten ist und mit dem ``update``-Item die Informationen abgefragt werden, läuft das Abonnement von Neuem los.

Änderungen, Hinweise und Erweiterungen werden jederzeit angenommen, Wünsche können etwas dauern...

Derzeit sind nur die Zonen `main` und `netusb` implementiert. Weitere Zonen werden gern aufgenommen, wenn Testhardware zur Verfügung gestellt wird ;)

Seit SmartHomeNG v1.7 werden Item-Structs bereitgestellt, mit denen die Funktionalitäten eines einfachen Players und zusätzlich Weckerfunktionen genutzt werden können.


Anforderungen
=============

Das folgende Python-Modul muss vorhanden sein:

  - requests

Dies wird normalerweise durch SmartHomeNG automatisch installiert. Wer es manuell installieren möchte, kann das über das PIP-Tool oder über die Distribution tun:

.. code-block:: bash

    # Python
    pip3 install requests

    # Debian based
    sudo apt-get install python3-requests

    # Arch Linux
    sudo pacman -S python-requests

    # Fedora
    sudo dnf install python3-requests


Konfiguration
=============

plugin.yaml
-----------

.. code-block:: yaml

    yamahayxc:
        plugin_name = YamahaYXC


items.yaml
----------

.. code-block:: yaml

    media:        
        wx010:
            yamahayxc_host: 192.168.2.211
            yamahayxc_zone: main

            struct: yamahayxc.basic


oder ohne Item-Structs (mit identischem Resultat):

.. code-block:: yaml

    media:

        wx010:
            yamahayxc_host: 192.168.2.211
            yamahayxc_zone: main

    # writable items to control device/playback
            # True = power on, False = standby
            power:
                type: bool
                yamahayxc_cmd: power
                enforce_updates: 'True'

            # numeric volume. Range is 0..60 on my devices. May vary
            volume:
                type: num
                yamahayxc_cmd: volume
                enforce_updates: 'True'

            # True = mute enable, False = mute disable
            mute:
                type: bool
                yamahayxc_cmd: mute
                enforce_updates: 'True'

            # input source as string. Heavily dependent on device.
            input:
                type: str
                yamahayxc_cmd: input
                enforce_updates: 'True'

            # possible values are 'play', 'stop', 'pause', 'previous', 'next'...
            playback:
                type: str
                yamahayxc_cmd: playback
                enforce_updates: 'True'
                
            # values are numeric and can (as of now) not be queried by the plugin
            preset:
                type: num
                yamahayxc_cmd: preset
                enforce_updates: 'True'

            # values are numeric and can be 0 / 30 / 60 / 90 / 120 [minutes]
            sleep:
                type: num
                yamahayxc_cmd: sleep
                enforce_updates: 'True'
                
    # read-only items to monitor device/playback status
            # name of current track, if available
            track:
                type: str
                yamahayxc_cmd: track

            # name of current artist, if available. Radio station name for net_radio
            artist:
                type: str
                yamahayxc_cmd: artist

            # this is the URL of current album art image, if supported / supplied
            # it is hosted on the respective yamaha device
            albumart:
                type: str
                yamahayxc_cmd: albumart

            # current time of playback in percent of total_time
            # -1 if total_time is not available
            play_pos:
                type: num
                yamahayxc_cmd: play_time

            # total time of playback in seconds. 0 if not applicable / available
            totaltime:
                type: num
                yamahayxc_cmd: total_time

    # write-only item to pass arbitrary command. Use at own discretion
            passthru:
                type: str
                yamahayxc_cmd: passthru
                enforce_updates: 'True'

    # write-only item to force update of all items above. See notes.
             update:
                type: bool
                yamahayxc_cmd: state
                enforce_updates: 'True'


    # the following items are only valid for devices with alarm clock functions
    # these are included in addition to the others from the 'alarm' struct:

            # enable / disable alarm function
            alarm_on:
                type: bool
                yamahayxc_cmd: alarm_on
                enforce_updates: 'True'

            # enable / disable alarm beep (solo or in addition to music)
            alarm_beep:
                type: bool
                yamahayxc_cmd: alarm_beep
                enforce_updates: 'True'

            # get/set alarm time. Formatted as 4 digit 24 hour string
            alarm_time:
                type: str
                yamahayxc_cmd: alarm_time
                enforce_updates: 'True'



Beispiel der Nutzung per CLI-Plugin
-----------------------------------

.. code-block::

    > up media.wx010.power=True
    > up media.wx010.input=net_radio
    > up media.wx010.volume=15
    > up media.wx010.mute=True
    > up media.wx010.mute=False
    > up media.wx010.playback=play
    > up media.wx010.power=False
    > up media.wx010.passthru='v1/Main/setPower?power=off'
    > up media.wx010.alarm_time='1430'


:PS: Das war gelogen. Der WX-010 hat gar keine Wecker-Funktionen...