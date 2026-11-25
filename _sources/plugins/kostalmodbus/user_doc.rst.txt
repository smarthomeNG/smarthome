.. index:: Plugins; kostalmodbus
.. index:: kostalmodbus

============
kostalmodbus
============

Das Plugin liest die Betriebsdaten eines Kostal-Wechselrichters über Modbus TCP aus und stellt sie
als Items zur Verfügung.

Voraussetzungen
================

Das Plugin verbindet sich per TCP/IP mit dem Wechselrichter. Eine Verbindung über RS232 wird nicht
unterstützt.

Folgende Wechselrichter werden unterstützt:

======================  ===========
Wechselrichter           Getestet
======================  ===========
PLENTICORE plus 4.2      nein
PLENTICORE plus 5.5      nein
PLENTICORE plus 7.0      ja
PLENTICORE plus 8.5      ja
PLENTICORE plus 10       ja
PIKO IQ 4.2              nein
PIKO IQ 5.5              nein
PIKO IQ 7.0              nein
PIKO IQ 8.5              nein
PIKO IQ 10               nein
======================  ===========

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter
:doc:`/plugins_doc/config/kostalmodbus` beschrieben.

Für die Items kann die Vorlage ``files/kostal_item_template.yaml`` als Basis verwendet werden, die
bereits alle unterstützten Item-Attribute enthält.

Item-Attribute
---------------

Ein Item wird mit dem Plugin verbunden, indem eines der folgenden Attribute gesetzt wird. Der Wert
des Attributs selbst wird nicht ausgewertet, das Item wird bei jedem Zyklus mit dem zugehörigen
Registerwert des Wechselrichters aktualisiert:

.. list-table::
   :header-rows: 1
   :widths: 15 55 10

   * - Attribut
     - Bedeutung
     - Einheit
   * - **kostal_06**
     - Artikelnummer des Wechselrichters
     - --
   * - **kostal_14**
     - Seriennummer des Wechselrichters
     - --
   * - **kostal_30**
     - Anzahl bidirektionaler Wandler
     - --
   * - **kostal_32**
     - Anzahl AC-Phasen
     - --
   * - **kostal_34**
     - Anzahl PV-Stränge
     - --
   * - **kostal_36**
     - Hardware-Version
     - --
   * - **kostal_38**
     - Software-Version Hauptcontroller (MC)
     - --
   * - **kostal_46**
     - Software-Version IO-Controller (IOC)
     - --
   * - **kostal_54**
     - Power-ID
     - --
   * - **kostal_56**
     - Wechselrichterstatus
     - --
   * - **kostal_98**
     - Temperatur der Controller-Platine
     - °C
   * - **kostal_100**
     - Gesamte DC-Leistung
     - W
   * - **kostal_104**
     - Status des Energiemanagers
     - --
   * - **kostal_106**
     - Eigenverbrauch aus Batterie
     - W
   * - **kostal_108**
     - Eigenverbrauch aus Netz
     - W
   * - **kostal_110**
     - Gesamtverbrauch aus Batterie
     - Wh
   * - **kostal_112**
     - Gesamtverbrauch aus Netz
     - Wh
   * - **kostal_114**
     - Gesamtverbrauch aus PV
     - Wh
   * - **kostal_116**
     - Eigenverbrauch aus PV
     - W
   * - **kostal_118**
     - Gesamtverbrauch
     - Wh
   * - **kostal_120**
     - Isolationswiderstand
     - Ohm
   * - **kostal_122**
     - Leistungsbegrenzung durch EVU
     - %
   * - **kostal_124**
     - Eigenverbrauchsquote
     - %
   * - **kostal_144**
     - Betriebszeit
     - Sekunden
   * - **kostal_150**
     - Aktueller cos φ
     - cos
   * - **kostal_152**
     - Netzfrequenz
     - Hz
   * - **kostal_154**
     - Strom Phase 1
     - A
   * - **kostal_156**
     - Wirkleistung Phase 1
     - W
   * - **kostal_158**
     - Spannung Phase 1
     - V
   * - **kostal_160**
     - Strom Phase 2
     - A
   * - **kostal_162**
     - Wirkleistung Phase 2
     - W
   * - **kostal_164**
     - Spannung Phase 2
     - V
   * - **kostal_166**
     - Strom Phase 3
     - A
   * - **kostal_168**
     - Wirkleistung Phase 3
     - W
   * - **kostal_170**
     - Spannung Phase 3
     - V
   * - **kostal_172**
     - Gesamte AC-Wirkleistung
     - W
   * - **kostal_174**
     - Gesamte AC-Blindleistung
     - Var
   * - **kostal_178**
     - Gesamte AC-Scheinleistung
     - VA
   * - **kostal_190**
     - Ladestrom der Batterie
     - A
   * - **kostal_194**
     - Anzahl Batteriezyklen
     - --
   * - **kostal_200**
     - Aktueller Batterie-Lade-(-)/Entladestrom (+)
     - A
   * - **kostal_202**
     - Status der PSSB-Sicherung
     - --
   * - **kostal_208**
     - Batterie-Bereit-Flag
     - --
   * - **kostal_210**
     - Aktueller Ladezustand
     - %
   * - **kostal_214**
     - Batterietemperatur
     - °C
   * - **kostal_216**
     - Batteriespannung
     - V
   * - **kostal_218**
     - cos φ (Stromzähler)
     - cos
   * - **kostal_220**
     - Frequenz (Stromzähler)
     - Hz
   * - **kostal_222**
     - Strom Phase 1 (Stromzähler)
     - A
   * - **kostal_224**
     - Wirkleistung Phase 1 (Stromzähler)
     - W
   * - **kostal_226**
     - Blindleistung Phase 1 (Stromzähler)
     - Var
   * - **kostal_228**
     - Scheinleistung Phase 1 (Stromzähler)
     - VA
   * - **kostal_230**
     - Spannung Phase 1 (Stromzähler)
     - V
   * - **kostal_232**
     - Strom Phase 2 (Stromzähler)
     - A
   * - **kostal_234**
     - Wirkleistung Phase 2 (Stromzähler)
     - W
   * - **kostal_236**
     - Blindleistung Phase 2 (Stromzähler)
     - Var
   * - **kostal_238**
     - Scheinleistung Phase 2 (Stromzähler)
     - VA
   * - **kostal_240**
     - Spannung Phase 2 (Stromzähler)
     - V
   * - **kostal_242**
     - Strom Phase 3 (Stromzähler)
     - A
   * - **kostal_244**
     - Wirkleistung Phase 3 (Stromzähler)
     - W
   * - **kostal_246**
     - Blindleistung Phase 3 (Stromzähler)
     - Var
   * - **kostal_248**
     - Scheinleistung Phase 3 (Stromzähler)
     - VA
   * - **kostal_250**
     - Spannung Phase 3 (Stromzähler)
     - V
   * - **kostal_252**
     - Gesamtwirkleistung (Stromzähler)
     - W
   * - **kostal_254**
     - Gesamtblindleistung (Stromzähler)
     - Var
   * - **kostal_256**
     - Gesamtscheinleistung (Stromzähler)
     - VA
   * - **kostal_258**
     - Strom DC1
     - A
   * - **kostal_260**
     - Leistung DC1
     - W
   * - **kostal_266**
     - Spannung DC1
     - V
   * - **kostal_268**
     - Strom DC2
     - A
   * - **kostal_270**
     - Leistung DC2
     - W
   * - **kostal_276**
     - Spannung DC2
     - V
   * - **kostal_278**
     - Strom DC3
     - A
   * - **kostal_280**
     - Leistung DC3
     - W
   * - **kostal_286**
     - Spannung DC3
     - V
   * - **kostal_320**
     - Gesamtertrag
     - Wh
   * - **kostal_322**
     - Tagesertrag
     - Wh
   * - **kostal_324**
     - Jahresertrag
     - Wh
   * - **kostal_326**
     - Monatsertrag
     - Wh
   * - **kostal_384**
     - Netzwerkname des Wechselrichters
     - --
   * - **kostal_420**
     - IP-Adresse
     - --
   * - **kostal_428**
     - Subnetzmaske
     - --
   * - **kostal_436**
     - Gateway
     - --
   * - **kostal_446**
     - DNS1
     - --
   * - **kostal_454**
     - DNS2
     - --
   * - **kostal_512**
     - Bruttokapazität der Batterie
     - Ah
   * - **kostal_514**
     - Aktueller Ladezustand der Batterie
     - %
   * - **kostal_515**
     - Firmware Hauptcontroller (MC)
     - --
   * - **kostal_517**
     - Batteriehersteller
     - --
   * - **kostal_525**
     - Batteriemodell-ID
     - --
   * - **kostal_529**
     - Nutzbare Kapazität
     - Wh
   * - **kostal_531**
     - Maximale Leistung des Wechselrichters
     - W
   * - **kostal_535**
     - Hersteller des Wechselrichters
     - --
   * - **kostal_559**
     - Seriennummer des Wechselrichters
     - --
   * - **kostal_575**
     - Aktuelle Erzeugungsleistung
     - W
   * - **kostal_577**
     - Erzeugte Energie
     - Wh
   * - **kostal_582**
     - Aktuelle Lade-/Entladeleistung der Batterie
     - W
   * - **kostal_586**
     - Firmware der Batterie
     - --
   * - **kostal_588**
     - Batterietyp
     - --
   * - **kostal_768**
     - Produktname
     - --
   * - **kostal_800**
     - Leistungsklasse
     - --
   * - **kostal_1056**
     - Gesamte DC-PV-Energie (Summe aller PV-Eingänge)
     - Wh
   * - **kostal_1058**
     - Gesamte DC-Energie von PV1
     - Wh
   * - **kostal_1060**
     - Gesamte DC-Energie von PV2
     - Wh
   * - **kostal_1062**
     - Gesamte DC-Energie von PV3
     - Wh
   * - **kostal_1064**
     - Gesamte AC-seitige Energie ins Netz
     - Wh
   * - **kostal_1066**
     - Gesamte DC-Leistung (Summe aller PV-Eingänge)
     - W
