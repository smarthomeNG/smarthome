.. index:: Plugins; dashbutton
.. index:: dashbutton

==========
dashbutton
==========

Das Plugin bindet Amazon-Dashbuttons ein und löst bei einem Tastendruck eine Item-Aktion aus, ohne
dass der Button selbst Internetzugriff benötigt.


Voraussetzungen
================

Der Dashbutton muss zunächst über die Amazon-App eingerichtet werden. Danach darf er keinen
Internetzugriff mehr haben, z.B. über die "Kindersicherung" / "No Internet Policy" einer AVM
Fritzbox.

Das Plugin erkennt Tastendrücke durch Mitschneiden von ARP-Anfragen des Buttons im Netzwerk und
benötigt dafür:

- die Python-Bibliothek ``scapy``
- das Systemprogramm ``tcpdump``::

    sudo apt-get install tcpdump

- Zugriffsrechte für den unprivilegierten Nutzer, um Pakete mitzuschneiden::

    sudo setcap cap_net_raw=eip /usr/bin/python3
    sudo setcap cap_net_raw=eip /usr/sbin/tcpdump

  Pfad zu Python und ``tcpdump`` ggf. an die eigene Installation anpassen.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/dashbutton` beschrieben.

Item-Attribute
--------------

**dashbutton_mac**
    MAC-Adresse des Dashbuttons. Ein Item kann mehrere MAC-Adressen zugewiesen bekommen.

**dashbutton_mode**
    ``flip`` oder ``value``. Im Modus ``flip`` muss das Item vom Typ ``bool`` sein, das Attribut
    **dashbutton_value** wird dabei ignoriert und der Item-Wert bei jedem Tastendruck umgeschaltet
    (0->1 bzw. 1->0).

**dashbutton_value**
    Nur im Modus ``value`` relevant. Ein einzelner Wert oder eine Liste von Werten. Bei einer Liste
    wird bei jedem Tastendruck der jeweils nächste Wert gesetzt, nach dem letzten Listenelement wieder
    von vorn begonnen. Wurde der Item-Wert zwischenzeitlich anders gesetzt und ist er kein Element der
    Liste, setzt der nächste Tastendruck das erste Listenelement.

**dashbutton_reset**
    Reset-Zeit in Sekunden. Ändert sich der Item-Wert innerhalb dieser Zeit nicht (weder durch
    Tastendruck noch anderweitig), wird bei der nächsten Aktivierung wieder das erste Element der
    **dashbutton_value**-Liste gesetzt. Ohne Liste in **dashbutton_value** wird dieses Attribut
    ignoriert.


Beispiele
=========

Modus ``flip``, mehrere Buttons schalten dasselbe Item::

    Room:

        Dining_Room:
            name: Light DiningRoom
            type: bool
            knx_dpt: 1
            knx_send: 1/1/1
            knx_listen: 1/1/1
            dashbutton_mac:
              - cc:66:de:dd:55:11
              - xx:xx:xx:xx:xx:01
              - xx:xx:xx:xx:xx:02
            dashbutton_mode: flip

Modus ``value`` mit einer Werteliste und Reset-Timer::

    Room:

        Kitchen:
            name: Light Dimm Kitchen
            type: num
            knx_dpt: 5
            knx_send: 1/2/1
            knx_listen: 1/2/1
            dashbutton_mac:
              - dd:11:12:55:55:22
              - cc:66:de:dd:55:11
            dashbutton_mode: value
            dashbutton_value:
              - '30'
              - '10'
              - '20'
              - '0'
            dashbutton_reset: 240
