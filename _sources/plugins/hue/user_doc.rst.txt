.. index:: Plugins; hue
.. index:: hue

===
hue
===

Das Plugin bindet eine oder mehrere Philips Hue Bridges an SmartHomeNG an. Es liest den Status von
Lampen, Gruppen und der Bridge selbst per zyklischem Polling ein (die Hue Bridge sendet selbst
keine Benachrichtigungen über Änderungen) und sendet Befehle zur Steuerung von Lampen, Gruppen und
Szenen.

Voraussetzungen
================

Eine oder mehrere Philips Hue Bridges. Für jede Bridge wird ein autorisierter Benutzer
(**hue_user**) benötigt. Dieser kann über die Funktion **authorizeuser()** angelegt werden (siehe
Verwendung weiter unten); dazu muss zuvor der Link-Button auf der Bridge gedrückt werden.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/hue` beschrieben.

Bei mehreren Bridges werden **hue_ip**, **hue_port** und **hue_user** als Listen angegeben. Die
Position in der jeweiligen Liste bestimmt die **hue_bridge_id** (beginnend bei 0), über die eine
Lampe, Gruppe oder Bridge in den Items adressiert wird. Alle drei Listen müssen daher die gleiche
Länge und Reihenfolge haben::

    HUE:
        class_name: HUE
        class_path: plugins.hue
        hue_ip:
          - 192.168.2.2
          - 192.168.2.3
        hue_port:
          - '80'
          - '80'
        hue_user:
          - 38f625a739562a8bd261ab9c7f5e62c8
          - 38f625a739562a8bd261ab9c7f5e62c8

Item-Attribute
==============

Lampen
------

Jede Lampe wird über bis zu drei Adress-Attribute identifiziert. Sie können am Item selbst oder an
einem übergeordneten Item gesetzt werden und werden dann an die Kind-Items vererbt:

**hue_bridge_id**
    Nummer der Bridge (beginnend bei 0), an die die Lampe angeschlossen ist. Bei nur einer
    konfigurierten Bridge kann das Attribut entfallen, es wird dann **0** angenommen.

**hue_lamp_id**
    Nummer der Lampe auf der Bridge (beginnend bei 1). Fehlt dieses Attribut vollständig, meldet
    das Plugin einen Fehler und startet nicht.

**hue_lamp_type**
    Lampentyp für die Farbraumberechnung von **col_r**/**col_g**/**col_b**. Gültige Werte: **0**
    (Hue Bulb-Lampen) und **1** (LivingColors Bloom, Aura und Iris). Ein dritter Wert (**2**) wird
    vom Plugin ebenfalls akzeptiert. Fehlt das Attribut, wird **0** angenommen.

Zum Lesen und Schreiben des Lampenstatus dienen **hue_listen** und **hue_send**, jeweils mit dem
Namen des gewünschten Attributs als Wert:

.. list-table::
   :header-rows: 1
   :widths: 16 10 30 12 12

   * - Attribut
     - Typ
     - Wertebereich
     - Lesbar (**hue_listen**)
     - Schreibbar (**hue_send**)
   * - **on**
     - bool
     - False / True
     - ja
     - ja
   * - **bri**
     - num
     - 0-255
     - ja
     - ja
   * - **hue**
     - num
     - 0-65535
     - ja
     - ja
   * - **sat**
     - num
     - 0-255
     - ja
     - ja
   * - **ct**
     - num
     - 153-500
     - ja
     - ja
   * - **alert**
     - str
     - ``none``, ``select`` oder ``lselect``
     - ja
     - ja
   * - **effect**
     - str
     - ``none`` oder ``colorloop``
     - ja
     - ja
   * - **reachable**
     - bool
     - False / True
     - ja
     - nein
   * - **col_r** / **col_g** / **col_b**
     - num
     - 0-255
     - nein
     - ja
   * - **type** / **name** / **modelid** / **swversion** / **uniqueid** / **manufacturername**
     - str
     - Text
     - ja
     - nein

Alle Attribute außer 'on' können nur gesetzt werden, wenn die Lampe eingeschaltet ist. Anstelle des
Hue-eigenen 'xy'-Zustands implementiert das Plugin **col_r**, **col_g** und **col_b**, um die
Farbsteuerung direkt aus einem SmartVISU-Widget (z.B. Colordisc) heraus zu ermöglichen. Für eine
einfache Steuerung genügen üblicherweise **on**, **bri**, **hue**, **sat** und **ct**.

**hue_transitionTime** ist unter :doc:`/plugins_doc/config/hue` beschrieben.

Gruppen
-------

Für Gruppen (Räume) gelten die gleichen Zustands-Attribute wie für Lampen, mit Ausnahme von
**col_r**/**col_g**/**col_b** und der Lampen-Eigenschaften (**type**, **name** usw.). Anstelle von
**hue_listen**/**hue_send** werden **hue_listen_group**/**hue_send_group** verwendet, adressiert
über **hue_group_id** (beginnend bei 1, Default **1**) statt **hue_lamp_id**::

    wohnzimmer_gruppe:
        hue_group_id: 1
        hue_bridge_id: 0

        power:
            type: bool
            hue_send_group: 'on'
            hue_listen_group: 'on'

        bri:
            type: num
            hue_send_group: bri
            hue_listen_group: bri

Szenen
------

Eine auf der Bridge gespeicherte Szene wird über **hue_send** mit dem Wert ``scene`` aktiviert. Es
wird nur **hue_bridge_id** benötigt, keine Lampen- oder Gruppen-ID::

    scene:
        type: str
        hue_send: scene
        enforce_updates: 'true'

Der Item-Wert entspricht dem Namen der Szene, wie er auf der Bridge hinterlegt ist.

Bridge-Status
-------------

Über **hue_listen** an einem Item mit gesetzter **hue_bridge_id** lassen sich Statuswerte der
Bridge selbst lesen:

.. list-table::
   :header-rows: 1
   :widths: 20 12 68

   * - Attribut
     - Typ
     - Bedeutung
   * - **bridge_name**
     - str
     - Name der Bridge
   * - **zigbeechannel**
     - num
     - Zigbee-Kanal (1-13)
   * - **mac** / **ipaddress** / **netmask** / **gateway**
     - str
     - Netzwerkeinstellungen der Bridge
   * - **dhcp**
     - bool
     - DHCP aktiv
   * - **UTC** / **localtime** / **timezone**
     - str
     - Zeiteinstellungen der Bridge
   * - **bridge_swversion** / **apiversion**
     - str
     - Firmware- bzw. API-Version
   * - **swupdate** / **whitelist** / **portalstate**
     - dict
     - Rohdaten-Objekte der Bridge-Konfiguration
   * - **linkbutton**
     - bool
     - Status des Link-Buttons
   * - **portalservices** / **portalconnection**
     - bool / str
     - Status der Cloud-Anbindung der Bridge
   * - **errorstatus**
     - bool
     - **True**, wenn die Kommunikation zwischen Plugin und Bridge gestört ist

Dimmen über DPT3
----------------

Ein KNX-DPT3-Dimmer kann über ein Unter-Item eines dimmbaren Hue-Items (Typ **num**, z.B.
**bri** oder **hue**) angebunden werden, unabhängig davon, ob es sich um ein Hue-Item handelt:

**hue_dim_max**
    Maximalwert des Dimmbereichs. Ohne dieses Attribut funktioniert das DPT3-Dimmen nicht.

**hue_dim_step**
    Schrittweite je Dimmschritt. Muss zusammen mit **hue_dim_max** gesetzt werden, sonst wird eine
    Warnung geloggt und der Standardwert **25** verwendet.

**hue_dim_time**
    Zeit je Dimmschritt in Sekunden. Muss zusammen mit **hue_dim_max** gesetzt werden, sonst wird
    eine Warnung geloggt und der Standardwert **1** verwendet.

Werte unter 0.2 Sekunden sollten aus Performance-Gründen vermieden werden. Für ein gleichmäßiges
Dimmergebnis sollten **hue_transitionTime** und **hue_dim_time** auf den gleichen Wert gesetzt
werden. Ist die Lampe ausgeschaltet, schaltet das Plugin sie beim Start des Dimmens automatisch ein
und dimmt vom zuletzt bekannten Wert aus weiter.

Beispiel
========

::

    keller:
        hue:
            hue_lamp_id: 1
            hue_bridge_id: 0
            hue_lamp_type: 0

            power:
                type: bool
                hue_send: 'on'
                hue_listen: 'on'

            bri:
                type: num
                cache: 'on'
                hue_send: bri
                hue_listen: bri
                hue_transitionTime: '0.2'

                dim:
                    type: list
                    knx_dpt: 3
                    knx_listen: 8/0/2
                    hue_dim_max: 255
                    hue_dim_step: 10
                    hue_dim_time: '0.2'

            hue:
                type: num
                cache: 'on'
                hue_send: hue
                hue_listen: hue
                hue_transitionTime: '0.2'

            sat:
                type: num
                cache: 'on'
                hue_send: sat
                hue_listen: sat

            ct:
                type: num
                hue_send: ct
                hue_listen: ct

            reachable:
                type: bool
                hue_listen: reachable

Verwendung
==========

Das Plugin stellt zwei Funktionen bereit, die interaktiv über die Shell oder aus einer Logik heraus
aufgerufen werden:

**authorizeuser(hue_bridge_id='0')**
    Autorisiert den in **hue_user** konfigurierten Benutzer an der angegebenen Bridge. Der
    Link-Button auf der Bridge muss vorher gedrückt werden::

        sh.hue.authorizeuser('0')

**get_config(hue_bridge_id='0')**
    Schreibt die auf der Bridge gespeicherten Szenen und Gruppen in den Log (Level warning) und
    gibt die Gruppen der angegebenen Bridge zurück::

        sh.hue.get_config('0')
