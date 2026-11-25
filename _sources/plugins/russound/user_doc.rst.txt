.. index:: Plugins; russound
.. index:: russound

========
russound
========

Das Plugin bindet Russound-Audiogeräte im Netzwerk an.


Voraussetzungen
================

Es wird ein Russound-Audiogerät im Netzwerk benötigt. Auf dessen Ethernet-Port muss das
Kommunikationsprotokoll RIO eingestellt sein.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/russound` beschrieben.

Item-Attribute
--------------

**rus_path**
    Pflichtattribut, ohne das ein Item ignoriert wird. Der Wert hat das Format ``c.z.p``, wobei
    ``c`` die Nummer des Controllers, ``z`` die Nummer der Zone und ``p`` der Systemparameter des
    Russound-Geräts ist, z.B. Lautstärke oder Höhen. Unterstützt werden:

    - status: Zone an/aus, Item-Typ ``bool``
    - volume: Lautstärke der Zone, Item-Typ ``num`` [0..50]
    - bass: Bass der Zone, Item-Typ ``num`` [-10..10]
    - treble: Höhen der Zone, Item-Typ ``num`` [-10..10]
    - balance: Balance der Zone, Item-Typ ``num`` [-10..10]
    - turnonvolume: Einschaltlautstärke der Zone, Item-Typ ``num`` [0..50]
    - currentsource: Nummer der aktuellen Quelle, Item-Typ ``num``
    - mute: Stummschaltung der Zone, Item-Typ ``bool``
    - loudness: Loudness der Zone, Item-Typ ``bool``
    - partymode: Party-Modus der Zone, Item-Typ ``str`` [ON/OFF/MASTER]
    - donotdisturb: "Nicht stören"-Einstellung der Zone, Item-Typ ``str``
    - name: Name der Zone (nur lesbar)

    Werte außerhalb der angegebenen Bereiche (volume, turnonvolume, bass, treble, balance) werden
    auf den jeweiligen Grenzwert begrenzt, z.B. wird ein gesetzter balance-Wert von ``15`` als ``10``
    an das Gerät gesendet.

    Alle nicht in dieser Liste aufgeführten Parameter werden als Key Code interpretiert und als
    "KeyRelease"-Ereignis an das Gerät gesendet, z.B. ``rus_path: 1.5.channelup``. Welche Key Codes
    ein Gerät unterstützt, steht im Handbuch des jeweiligen Russound-Geräts. Für Key-Code-Items
    empfiehlt sich zusätzlich das Attribut ``enforce_updates: true``, da der konkrete Item-Wert dabei
    keine Rolle spielt.


Beispiele
=========

::

    dg:

        bedroom:

            audio:
                type: bool
                rus_path: 1.1.status
                knx_dpt: 1
                knx_send: 12/1/0
                knx_listen: 12/1/0

                volume:
                    type: num
                    rus_path: 1.1.volume
                    knx_dpt: 5
                    knx_send: 12/1/1
                    knx_listen: 12/1/1

                channelup:
                    type: bool
                    rus_path: 1.1.channelup
                    knx_dpt: 1
                    knx_listen: 12/1/9
                    enforce_updates: 'true'


Die Kommunikation mit dem Russound-Gerät kann aus Logiken heraus über die Funktionen
**suspend()**/**activate()** unterbrochen und wieder gestartet werden (Instanzname entsprechend der
eigenen Konfiguration, z.B. ``sh.russound.suspend()``); siehe :doc:`/plugins_doc/config/russound`.
