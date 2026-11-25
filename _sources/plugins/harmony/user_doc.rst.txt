.. index:: Plugins; harmony
.. index:: harmony

=======
harmony
=======

Das Plugin verbindet SmartHomeNG mit einem Harmony Hub. Es kann Geräte-Kommandos und Aktivitäten
auslösen und die aktuell aktive Aktivität des Hubs in Items abbilden.

Voraussetzungen
================

Das Plugin benötigt ein Harmony Hub Gerät sowie das Python3-Modul **sleekxmpp**::

    sudo pip3 install sleekxmpp

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/harmony` beschrieben.

Geräte-IDs und Kommandos ermitteln
-----------------------------------

Vor der Item-Konfiguration müssen die Geräte-IDs bzw. Aktivitäts-IDs des Harmony Hubs und die
zugehörigen Kommandos ermittelt werden. Dafür wird das im Plugin-Verzeichnis enthaltene Skript
``get_config.py`` verwendet::

    python3 get_config.py -i HARMONY_HUB_IP

Die Ausgabe kann bei Bedarf in eine Datei umgeleitet werden::

    python3 get_config.py -i HARMONY_HUB_IP > /pfad/zur/ausgabe.txt

Das Skript listet alle konfigurierten Aktivitäten mit ihrer ID sowie alle Geräte mit ihrer
Geräte-ID und den jeweils verfügbaren Kommandos auf. Für ein direktes Geräte-Kommando werden
Geräte-ID und Kommandoname benötigt, für eine Aktivität die Aktivitäts-ID.

Item-Attribute
--------------

**harmony_command_0** / **harmony_command_1**

Beide Attribute sind nur für Items vom Typ **bool** gültig. Es muss mindestens eines der beiden
Attribute gesetzt werden, beide zusammen sind ebenfalls zulässig. Wird der Item-Wert auf **True**
gesetzt, wird das für **harmony_command_1** konfigurierte Kommando ausgelöst, bei **False**
entsprechend **harmony_command_0**.

Ein Kommando hat immer die Form ``GERAETE_ID:KOMMANDO(:VERZOEGERUNG)`` oder
``activity:AKTIVITAETS_ID(:VERZOEGERUNG)``. Die Verzögerung gibt die Wartezeit in Sekunden nach
dem vorherigen Kommando bzw. der vorherigen Aktivität an, ist optional und beträgt standardmäßig
0.2 Sekunden. Mehrere Kommandos und Aktivitäten können durch ``|`` getrennt aneinandergereiht und
beliebig gemischt werden: ``KOMMANDO1 | KOMMANDO2 | AKTIVITAET1 | KOMMANDO3 ...``

Beispiele für Kommandos::

    42282391:PowerOn
    42282391:PowerOn:0.5

Für eine Aktivität wird statt der Geräte-ID das Schlüsselwort ``activity`` (kurz: ``a``) verwendet::

    activity:12345678:1
    a:12345678:4

Die Standardaktivität "Power Off" des Harmony Hubs, die die aktuell aktive Aktivität beendet, wird
mit der ID ``-1`` ausgelöst::

    a:-1

Wird eine bereits aktive Aktivität erneut ausgelöst, reagiert der Harmony Hub darauf nicht. Um
dieses Verhalten zu umgehen, empfiehlt es sich, im Harmony-Setup eine ungenutzte, leere
Dummy-Aktivität anzulegen (mit Verzögerungen von 0 für das enthaltene Gerät) und diese am Ende der
``harmony_command``-Kommandokette mit auszulösen.

**harmony_item**

Über dieses Attribut wird ein Item mit Statusinformationen zur aktuell aktiven Aktivität des
Harmony Hubs versorgt. Es wird bei jeder Änderung der aktiven Aktivität aktualisiert, unabhängig
davon, ob die Änderung über SmartHomeNG oder eine andere Fernbedienung ausgelöst wurde.

Für die ID der aktuellen Aktivität wird ein Item vom Typ **num** benötigt::

    MyItem:
        type: num
        enforce_updates: true
        harmony_item: current_activity_id

Für den Namen der aktuellen Aktivität wird ein Item vom Typ **str** benötigt::

    MyItem:
        type: str
        enforce_updates: true
        harmony_item: current_activity_name

Beispiele
=========

::

    Shield:
        type: bool
        harmony_command_1:
          - 42282391:PowerOn:6
          - 42282391:InputBd:1
        harmony_command_0:
          - 42282391:PowerOff
          - activity:-1

Wird das Item **Shield** auf **True** gesetzt, schaltet sich der AV-Receiver mit 6 Sekunden
Verzögerung ein. Eine weitere Sekunde später wird auf den Eingang "Bluray" umgeschaltet. Wird das
Item auf **False** gesetzt, wird sofort "PowerOff" ausgelöst, gefolgt von der Standardaktivität
"Power Off" des Harmony Hubs.

::

    RTL:
        type: bool
        harmony_command_1:
          - a:12345123
          - 42282391:InputSat/Cbl:2
          - '31914808:3:0.3'
          - 31914808:Select

Dieses Kommando startet die Aktivität mit der ID 12345123. Nach 2 Sekunden Verzögerung wird der
Eingang des AV-Receivers auf SAT/Kabel umgeschaltet. Weitere 0.3 Sekunden später wird eine "3"
gesendet und mit "Select" bestätigt.
