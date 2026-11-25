.. index:: Plugins; mlgw
.. index:: mlgw

====
mlgw
====

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Das Plugin verbindet SmartHomeNG mit einem Bang & Olufsen Masterlink Gateway. Es kann Befehle an
alle am Gateway angeschlossenen B&O Audio- und Videogeräte senden (die gleichen Befehle, die auch
eine B&O Fernbedienung wie die Beo4 senden kann) und **LIGHT**- sowie **CONTROL**-Telegramme
empfangen, die von einem B&O Gerät gesendet werden.

Voraussetzungen
================

Benötigt wird ein B&O Masterlink Gateway, mit dem sich das Plugin per TCP/IP verbindet. Eine
Verbindung über RS232 wird nicht unterstützt.

Unterstützt werden:

* B&O Masterlink Gateway v2 mit Firmware v2.24a oder neuer
* B&O Beolink Gateway mit Firmware v1.1.0 oder neuer

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/mlgw`
beschrieben.

Mit **log_mlgwtelegrams** lässt sich mitschneiden, welche mlgw-Telegramme im Logfile protokolliert
werden (Loglevel wird dafür auf WARNING angehoben, damit die Ausgabe auch im quiet mode sichtbar
ist):

======  ==========================================================================
Wert    Bedeutung
======  ==========================================================================
0       Keine Telegramme werden protokolliert.
1       Empfangene, vom Plugin nicht verarbeitete Telegramme werden protokolliert.
2       Alle empfangenen Telegramme werden protokolliert.
3       Gesendete und empfangene Telegramme werden protokolliert.
4       Wie 3, zusätzlich inklusive Keep-Alive-Datenverkehr.
======  ==========================================================================

**rooms** und **mlns** ordnen die am Masterlink Gateway konfigurierten Raum- bzw.
Geräte-(MLN-)Nummern lesbaren Namen zu, die dann in den Item-Attributen **mlgw_room** und
**mlgw_mln** anstelle der Nummer verwendet werden können.

Item-Attribute
---------------

Befehle senden
~~~~~~~~~~~~~~~

Zum Senden eines Befehls an ein B&O Gerät wird **mlgw_send** gesetzt, entweder auf ``cmd`` (Senden
eines Befehls, wie ihn auch ein Tastendruck auf der Fernbedienung auslöst) oder auf ``ch``
(Senden einer Programm-/Kanalnummer als Ziffernfolge). **mlgw_mln** legt fest, an welches Gerät
(Masterlink Node) der Befehl gesendet wird, entweder als Nummer oder als in **mlns** definierter
Name. **enforce_updates: true** muss zusammen mit **mlgw_send** gesetzt werden, sonst wird der
Befehl nur beim ersten Schreiben des Items gesendet.

Bei **mlgw_send: cmd** bestimmt der **type** des Items, wie der Befehl übergeben wird:

* **type: str** — der Name des Befehls wird direkt in das Item geschrieben (z.B. ``DVD``).
* **type: bool** — der zu sendende Befehl wird stattdessen fest in **mlgw_cmd** hinterlegt
  (z.B. **mlgw_cmd**: ``DVD``); das Item löst den Befehl beim Schreiben von ``True`` aus.

Bei **mlgw_send: ch** muss der **type** des Items ``num`` sein; die geschriebene Zahl wird als
Folge von Digit-Befehlen gesendet.

Folgende Befehle werden für **mlgw_send** unterstützt:

* Quellenwahl: ``Standby``, ``Sleep``, ``TV``, ``Radio``, ``DTV2``, ``Aux_A``, ``V.Mem``, ``DVD``,
  ``Camera``, ``Text``, ``DTV``, ``PC``, ``Doorcam``, ``A.Mem``, ``CD``, ``N.Radio``, ``N.Music``,
  ``CD2``
* Ziffern: ``Digit-0`` bis ``Digit-9``
* Quellensteuerung: ``STEP_UP``, ``STEP_DW``, ``REWIND``, ``RETURN``, ``WIND``, ``Go / Play``,
  ``Stop``, ``Yellow``, ``Green``, ``Blue``, ``Red``
* Ton-/Bildsteuerung: ``Mute``, ``P.Mute``, ``Format``, ``Sound / Speaker``, ``Menu``,
  ``Volume UP``, ``Volume DOWN``, ``Cinema_On``, ``Cinema_Off``
* Sonstige: ``BACK``, ``Exit``, ``Key Release``
* Cursor: ``SELECT``, ``Cursor_Up``, ``Cursor_Down``, ``Cursor_Left``, ``Cursor_Right``
* Funktionen: ``Light``

Befehle empfangen
~~~~~~~~~~~~~~~~~~

Zum Empfang von Telegrammen eines B&O Geräts wird **mlgw_listen** auf ``light`` oder ``control``
gesetzt, je nachdem welcher Befehlssatz einer B&O Fernbedienung abgehört werden soll.
**mlgw_room** legt fest, aus welchem Raum die Telegramme stammen müssen, entweder als Nummer oder
als in **rooms** definierter Name.

* Um auf einen bestimmten Befehl zu reagieren, wird dieser in **mlgw_cmd** angegeben und der
  **type** des Items auf ``bool`` gesetzt; das Item wird beim Empfang des Befehls auf ``True``
  gesetzt. **enforce_updates: true** wird empfohlen, damit auch mehrfach aufeinanderfolgend
  empfangene Befehle korrekt verarbeitet werden.
* Um auf beliebige Befehle zu reagieren, bleibt **mlgw_cmd** leer und der **type** des Items wird
  auf ``str`` gesetzt; der Name des empfangenen Befehls wird in das Item geschrieben.

Folgende Befehle werden für **mlgw_listen** unterstützt:

* Ziffern: ``Digit-0`` bis ``Digit-9``
* Aus der Quellensteuerung: ``STEP_UP``, ``STEP_DW``, ``REWIND``, ``RETURN``, ``WIND``,
  ``Go / Play``, ``Stop``, ``Yellow``, ``Green``, ``Blue``, ``Red``
* Ton-/Bildsteuerung (nur **CONTROL**, nur bei BeoSystem-3-basierten TV-Geräten): ``Cinema_On``,
  ``Cinema_Off``
* Sonstige: ``BACK``
* Cursor: ``SELECT``, ``Cursor_Up``, ``Cursor_Down``, ``Cursor_Left``, ``Cursor_Right``

Beispiel
========

::

    Someroom:

        bv10:
            name: BeoVision 10
            type: str
            enforce_updates: 'true'
            mlgw_send: cmd
            mlgw_mln: 3

            channel:
                name: 'BeoVision 10: Channel'
                type: num
                enforce_updates: 'true'
                mlgw_send: ch
                mlgw_mln: 3

            digit_1:
                name: 'BeoVision 10: Digit "1"'
                type: bool
                enforce_updates: 'true'
                mlgw_send: cmd
                mlgw_mln: 3
                mlgw_cmd: Digit-1

        living_light0:
            name: 'living room: Light "0"'
            type: bool
            mlgw_listen: light
            mlgw_room: living
            mlgw_cmd: Digit-0

        living_lightup:
            name: 'living room: Light Step_Up'
            type: bool
            mlgw_listen: light
            mlgw_room: living
            mlgw_cmd: Step_Up

        living_control0:
            name: 'living room: Control "0"'
            type: bool
            mlgw_listen: control
            mlgw_room: 6
            mlgw_cmd: Digit-0

Das Attribut **name** ist nicht erforderlich, es dient in diesem Beispiel nur als Kommentar.
