.. index:: Plugins; milight
.. index:: milight

=======
milight
=======

Das Plugin sendet Änderungen von Item-Werten an ein MiLight Gateway und steuert darüber
Leuchtmittel. Es können mehrere Instanzen des Plugins parallel betrieben werden.

Voraussetzungen
================

Für das Plugin wird eine MiLight-WLAN-Bridge ab Version 3.0 benötigt, die MiLight-,
Easybulb- oder LimitlessLED-Leuchtmittel bzw. LED-RGBW-Streifen-Controller mit 2,4 GHz
ansteuert. Bridges der Version 2.0 sind in der Regel kompatibel, nutzen als
UDP-Kommunikationsport aber einen anderen Standardwert als Version 3.0. Auch der
ESP8266-basierte Ersatz-Hub `esp8266_milight_hub
<https://github.com/sidoh/esp8266_milight_hub>`_ wird von Anwendern erfolgreich mit dem
Plugin eingesetzt.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/milight`
beschrieben.

Beispiele
=========

Über die Item-Attribute wird jeweils der Kanal der MiLight-Bridge angesprochen. Kanal
**0** steuert alle Gruppen, die Kanäle **1** bis **4** entsprechen den Gruppen auf der
Fernbedienung. Mehrere Kanäle können als Liste angegeben werden, um sie gemeinsam
anzusprechen.

::

    milight:

        all:
            type: bool
            milight_sw: 0

        wohnen:
            type: bool
            milight_sw: 1
            knx_dpt: 1
            knx_send: 1/0/107
            knx_listen: 1/0/65

            dimmen:
                type: num
                milight_dim: 1
                knx_dpt: 5
                knx_listen: 1/0/66
                knx_send: 1/0/67

            farbe:
                type: num
                milight_col: 1

            white:
                type: bool
                milight_white: 1

            disco:
                type: bool
                milight_disco: 1
                enforce_updates: 'on'

            discospeedup:
                type: bool
                milight_disco_up: 1
                enforce_updates: 'yes'

            discospeeddown:
                type: bool
                milight_disco_down: 1
                enforce_updates: 'yes'

        flur:
            type: bool
            milight_sw: 2

            dimmen:
                type: num
                milight_dim: 2

            farbe:
                type: num
                milight_col: 2

            white:
                type: bool
                milight_white: 2

            rgb:
                type: list
                knx_dpt: 232
                milight_rgb: 1
                knx_sent: 1/1/1

        eg:
            type: bool
            milight_sw:
              - '1'
              - '2'

            dimmen:
                type: num
                milight_dim:
                  - '1'
                  - '2'

            farbe:
                type: num
                milight_col:
                  - '1'
                  - '2'

            white:
                type: bool
                milight_white:
                  - '1'
                  - '2'

Bei den Items **milight_disco**, **milight_disco_up** und **milight_disco_down** sollte
**enforce_updates** gesetzt werden, damit jeder Tastendruck der Fernbedienungs-Simulation
auch bei gleichem Item-Wert erneut gesendet wird.

RGB-Auswahl in SmartVISU
-------------------------

Da SmartVISU keine Tabelleneingabe für die RGB-Auswahl unterstützt, kann folgende
Item-Struktur genutzt werden, um den RGB-Wert aus drei einzelnen Eingaben für Rot, Grün
und Blau zu berechnen:

::

    living_room:
        rgb:
            name: RGB
            type: list
            milight_rgb: 1
            cache: yes
            eval: "[sh..r(), sh..g(), sh..b()]"
            eval_trigger:
              - .r
              - .g
              - .b

            r:
                name: value for red
                type: num
                cache: yes
                visu_acl: rw

            g:
                name: value for green
                type: num
                cache: yes
                visu_acl: rw

            b:
                name: value for blue
                type: num
                cache: yes
                visu_acl: rw

Wird das SmartVISU-Autogenerierungs-Plugin verwendet, kann folgender Code-Schnipsel als
Basis für die RGB-Auswahl dienen:

::

    {{ basic.color('', 'living_room.rgb', '', '', [0,0,0], [255,255,255], '', '', 'rect', 'rgb') }}
