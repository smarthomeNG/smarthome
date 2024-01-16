
.. comment SmartDevicePlugin
.. comment =================

Das SmartDevicePlugin (sdp) ist aus der Notwendigkeit geboren, für jedes neue Plugin und jedes neue Gerät aufs Neue das
ganze Kern-Plugin neu zu erfinden - Item-Handling, Zuordnung von Items zu Befehlen (commands) und Kommunikation mit
Netzwerk- oder seriellen Treibern oder Libraries.

Hierzu bietet die sdp-Klasse ein fertiges Plugin, aus dem mit minimalem Aufwand ein eigenes Plugin erstellt werden kann.

Dazu besteht sdp aus mehreren modularen Ebenen, die hier zusammen mit den jeweiligen ausgetauschten Daten dargestellt
werden:

- SmartHomeNG
- + Items
- Plugin
- + Kommandos
- class SDPCommands (fasst commands zusammen, aus commands.py)
- + Werte
- class SDPCommand (stellt einzelnes command dar, aus commands.py)
- + (ggf. transformierte) Werte
- class DataType (kann beliebige Datentransformation nach Bedarf vornehmen)
- + gerätespezifisch transformierte Werte
- class SDPProtocol (optional, z.B. JSON-RPC, Binärprotokoll mit Verbindungsaufbau...)
- + gerätespezifisch transformierte Werte
- class SDPConnection (stellt die konkrete Verbindungsebene dar)
- + gerätespezifisch transformierte Werte
- Kommunikationsmodul (z.B. lib.network, serial, ...)
- + gerätespezifisch transformierte Werte
- Gerät

Das Plugin besteht aus dem (vererbten) Plugin-Code in `__init__.py`, der commands-Definition in `commands.py`, ggf.
pluginspezifischer Protokolldefinition in `protocol.py`, ggf. pluginspezifischen Datentypen in `datatypes.py` und den
Standarddateien `plugin.yaml` und ggf. `user_doc.rst`.


Plugin
------

Der folgende Code stellt ein minimales, uneingeschränkt lauffähiges Plugin dar (hier aus dem Beispielplugin
sdp_viessmann entnommen):

.. code::

    from lib.model.smartdeviceplugin import SmartDevicePlugin

    class sdp_viessmann(SmartDevicePlugin):
    """ Device class for Viessmann heating systems."""
    PLUGIN_VERSION = '1.0.0'

Nun wäre es naiv zu glauben, dass nur eine Codezeile ein beliebiges Plugin darstellen kann. Für ein nicht nur
lauffähiges, sondern auf funktionales Plugin bedarf es noch der wesentlichen Konfiguration, die im Zusammenhang mit sdp benötigt wird - den commands in der `commands.py`.


Kommandos
---------

Hier wird nach einer vorgegebenen Struktur definiert, welche Befehle wie für das Gerät "übersetzt" werden müssen.
Dabei gibt es eine Reihe von - zunehmend komplexen - Optionen, die in der Referenz im Detail behandelt werden. Im
Wesentlichen wird in der `commands.py` das dict `commands` definiert, dessen Inhalte die Intelligenz des Plugins
definieren. Der folgende Code ist ein Ausschnitt aus der commands-Definition des sdp_viessmann-Plugins:

.. code-block:: yaml

    commands = {
        'Allgemein': {'item_attrs': {'cycle': 45},
            'Temperatur': {
                'Aussen':             {'read': True, 'write': False, 'opcode': '0101', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getTempA -- Information - Allgemein: Aussentemperatur (-40..70)
            },
            # Anlagenstatus
            'Betriebsart':            {'read': True, 'write': True,  'opcode': 'b000', 'reply_pattern': '*', 'item_type': 'str',  'dev_datatype': 'H', 'params': {'value': 'VAL', 'len': 1}, 'lookup': 'operatingmodes', 'item_attrs': {'attributes': {'md_read_initial': True}, 'lookup_item': True}},     # getBetriebsart -- Bedienung HK1 - Heizkreis 1: Betriebsart (Textstring)
            'Manuell':                {'read': True, 'write': True,  'opcode': 'b020', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'len': 1}, 'cmd_settings': {'force_min': 0, 'force_max': 2}},     # getManuell / setManuell -- 0 = normal, 1 = manueller Heizbetrieb, 2 = 1x Warmwasser auf Temp2
            # Allgemein
            'Outdoor_Fanspeed':       {'read': True, 'write': False, 'opcode': '1a52', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'len': 1}},     # getSpdFanOut -- Outdoor Fanspeed
            'Status_Fanspeed':        {'read': True, 'write': False, 'opcode': '1a53', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'len': 1}},     # getSpdFan -- Geschwindigkeit Luefter
            'Kompressor_Freq':        {'read': True, 'write': False, 'opcode': '1a54', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'len': 1}},     # getSpdKomp -- Compressor Frequency
            'SollLeistungVerdichter': {'read': True, 'write': False, 'opcode': '5030', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'len': 1}},     # getPwrSollVerdichter -- Diagnose - Anlagenuebersicht: Soll-Leistung Verdichter 1 (0..100)
        },
        'Pumpen': {
            'Sekundaer':              {'read': True, 'write': False, 'opcode': '0484', 'reply_pattern': '*', 'item_type': 'bool', 'dev_datatype': 'V', 'params': {'value': 'VAL', 'len': 1}, 'lookup': 'returnstatus'},     # getStatusSekP -- Diagnose - Anlagenuebersicht: Sekundaerpumpe 1 (0..1)
            'Heizkreis':              {'read': True, 'write': False, 'opcode': '048d', 'reply_pattern': '*', 'item_type': 'bool', 'dev_datatype': 'V', 'params': {'value': 'VAL', 'len': 1}, 'lookup': 'returnstatus'},     # getStatusPumpe -- Information - Heizkreis HK1: Heizkreispumpe (0..1)
            'Zirkulation':            {'read': True, 'write': False, 'opcode': '0490', 'reply_pattern': '*', 'item_type': 'bool', 'dev_datatype': 'V', 'params': {'value': 'VAL', 'len': 1}, 'lookup': 'returnstatus'},     # getStatusPumpeZirk -- Information - Warmwasser: Zirkulationspumpe (0..1)
        },
        'Heizkreis': {
            'Temperatur': {
                'Raum': {
                    'Soll':           {'read': True, 'write': False, 'opcode': '2000', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getTempRaumSollNormal -- Bedienung HK1 - Heizkreis 1: Raumsolltemperatur normal (10..30)
                    'Soll_Reduziert': {'read': True, 'write': False, 'opcode': '2001', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getTempRaumSollRed -- Bedienung HK1 - Heizkreis 1: Raumsolltemperatur reduzierter Betrieb (10..30)
                    'Soll_Party':     {'read': True, 'write': False, 'opcode': '2022', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getTempRaumSollParty -- Bedienung HK1 - Heizkreis 1: Party Solltemperatur (10..30)
                },
                'Vorlauf': {
                    'Ist':            {'read': True, 'write': False, 'opcode': '0105', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getTempSekVL -- Information - Heizkreis HK1: Vorlauftemperatur Sekundaer 1 (0..95)
                    'Soll':           {'read': True, 'write': False, 'opcode': '1800', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getTempVLSoll -- Diagnose - Heizkreis HK1: Vorlaufsolltemperatur HK1 (0..95)
                    'Mittel':         {'read': True, 'write': False, 'opcode': '16b2', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getTempSekVLMittel -- Statistik - Energiebilanz: mittlere sek. Vorlauftemperatur (0..95)
                },
                'Ruecklauf': {
                    'Ist':            {'read': True, 'write': False, 'opcode': '0106', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getTempSekRL -- Diagnose - Anlagenuebersicht: Ruecklauftemperatur Sekundaer 1 (0..95)
                    'Mittel':         {'read': True, 'write': False, 'opcode': '16b3', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getTempSekRLMittel -- Statistik - Energiebilanz: mittlere sek.Temperatur RL1 (0..95)
                },
            },
            'Heizkennlinie': {
                'Niveau':             {'read': True, 'write': False, 'opcode': '2006', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getHKLNiveau -- Bedienung HK1 - Heizkreis 1: Niveau der Heizkennlinie (-15..40)
                'Neigung':            {'read': True, 'write': False, 'opcode': '2007', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getHKLNeigung -- Bedienung HK1 - Heizkreis 1: Neigung der Heizkennlinie (0..35)
            },
        },
        'Warmwasser': {
            'Ist':                    {'read': True, 'write': False, 'opcode': '010d', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}},     # getTempWWIstOben -- Information - Warmwasser: Warmwassertemperatur oben (0..95)
            'Soll':                   {'read': True, 'write': True,  'opcode': '6000', 'reply_pattern': '*', 'item_type': 'num',  'dev_datatype': 'V', 'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}, 'cmd_settings': {'force_min': 10, 'force_max': 60}},     # getTempWWSoll -- Bedienung WW - Betriebsdaten WW: Warmwassersolltemperatur (10..60 (95))
            'Ventil':                 {'read': True, 'write': False, 'opcode': '0494', 'reply_pattern': '*', 'item_type': 'bool', 'dev_datatype': 'V', 'params': {'value': 'VAL', 'len': 1}, 'lookup': 'returnstatus'},     # getStatusVentilWW -- Diagnose - Waermepumpe: 3-W-Ventil Heizen WW1 (0 (Heizen)..1 (WW))
        }
    }


Hier soll am Beispiel einer Zeile der wesentliche Inhalt erläutert werden:

.. code-block:: yaml

    'Aussen': { 				# Name des Kommandos, Code für das Item-Attribut
    	'read': True, 			# Kommando kann Wert vom Gerät lesen
    	'write': False, 		# Kommando kann Wert - nicht - auf Gerät schreiben
    	'opcode': '0101', 		# "Code", der an das Gerät gesendet wird
    	'reply_pattern': '*', 	# Identifier, um Antwort auf dieses Kommando zu erkennen
		'item_type': 'num',		# Datentyp, der an SmartHomeNG gesendet wird
		'dev_datatype': 'V', 	# Datentyp, der zur Kommunikation mit dem Gerät verwendet wird
		'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}}
                                # Werttransformation: signed int, 2 Bytes ("word")
								# Wert vom Gerät wird durch 10 geteilt (ergibt eine Nachkommastelle)
	}


Die einzelnen Attribute der command-Definitionen sind in der Datei `./dev/sample_smartdevice_plugin/commands.py` im
Detail erklärt.


Protokoll
---------

Standardmäßig wird kein Protokoll benötigt und somit nicht konfiguriert. Wenn Protokolle konfiguriert werden, so sind
sie sowohl für das Plugin als auch für die konfigurierte Verbindung transparent.

Zum Lieferumfang gehören die Protokollklassen `SDPProtocol` (keine gesonderte Funktion, Basisklasse, kann zum Testen
verwendet werden) sowie `SDPProtocolJsonrpc` (stellt transparente Format- und Datenformatierung nach Json-RPC-Standard
zur Verfügung).

Eigene Protokolle können definiert werden - im Beispiel sdp_viessmann z.B. die binären Protokolltypen P300 und KW2,
die einen Verbindungsaufbau mit Handshake benötigen.


Verbindung
----------

Die `SDPConnection`- sowie die davon abgeleiteten Klassen stellen die Verbindungsschicht zum Gerät dar. Durch die
standardisierte Schnittstelle ist das Plugin unabhängig von der konkret gewählten Verbindung. So ist es z.B. kein
Problem, wahlweise netzwerkbasierte oder serielle Verbindungen im selben Plugin zu nutzen, indem nur die Konfiguration
in der plugin.yaml entsprechend angepasst wird.

Zum Lieferumfang gehörten die Verbindungsklassen `SDPConnection` (keine Funktion, Basisklasse, kann zum Testen
verwendet werde), `SDPConnectionNetTcpRequest` (Netzwerkverbindung mit HTTP-Requests und -Antworten über TCP),
`SDPConnectionNetTcpClient` (direkte TCP-Verbindung mit persistenter Sendeverbindung und Listener zum
asnychronen Datenempfang), `SDPConnectionNetUdpRequest` (wie SDPConnectionNetTcpRequest, aber mit zusätzlichem
UDP-Listener, z.B. für Multicast), `SDPConnectionSerial` (Anfrage-Antwort-Verbindung über serielle Schnittstelle)
sowie `SDPConnectionSerialAsync` (serielle Verbindung mit Listener, der eingehende Daten unabhängig von gesendeten
Kommandos empfangen kann).


DataTypes
---------

Die Basisklasse `DataType` und die davon abgeleiteten Klassen bieten eine Schnittstelle, Datenformate zwischen
SmartHomeNG und Gerät zu konvertieren. Eine Reihe von vorgefertigten Datentypen werden bereits mitgeliefert, eigene
Datentypen können zusätzlich definiert werden.

Zum Lieferumfang gehören neben der Basisklasse `DataType` die abgeleiteten Klassen `DT_none` (Testklasse, keine
Datenweitergabe), `DT_raw`, `DT_bool`, `DT_int`, `DT_num`, `DT_str`, `DT_list`, `DT_dict`, `DT_tuple`, `DT_bytes`,
`DT_bytearray`, `DT_json` und `DT_webservices`. Die meisten der gelisteten Klassen funktionieren wie ein einfaches
typecast, JSON und Webservices sind spezielle Formate für JSON-RPC und das Webservices-Plugin.


Commands
--------

Die Klasse `SDPCommands` ist ein "intelligentes" dict, das die `commands.py` liest und verarbeitet und strukturieren
Zugriff auf die konfigurierten Kommandos ermöglicht.

Die Klasse `SDPCommand` stellt für jedes konfigurierte Kommando eine eigene Instanz dar, die die notwendigen
Informationen und Methoden zum Zugriff und zur notwendigen Datentransformation bereitstellt. Die einzelnen Instanzen
werden durch die `SDPCommands`-Klasse erstellt und entsprechend den Angaben in `commands.py` konfiguriert.

Auf Plugin-Ebene kann festgelegt werden, ob die Standardklasse `SDPCommand` oder bei Bedarf eine abgeleitete Klasse
verwendet werden soll. Die abgeleiteten Klassen umfassen `SDPCommandStr` für Kommandos, die textbasiert arbeiten
(z.B. HTTP oder Textprotokolle), `SDPCommandParseStr` mit zusätzlichen Möglichkeiten zur Text- und Datenextraktion,
SDPCommandJSON für JSON-RPC-Kommunikation sowie SDPCommandViessmann für die binären Datenformate der
Viessmann-Heizungen.

