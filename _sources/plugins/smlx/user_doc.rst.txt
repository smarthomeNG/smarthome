smlx
====

Anforderungen
-------------

Normalerweise sendet die Hardware eines Smartmeter alle paar Sekunden Statusinformationen, 
die über eine Schnittstelle ausgelesen werden können. 

Für diese Plugin wird je nach Schnittstelle des Smartmeter entweder ein 
`IR Lesekopf <http://wiki.volkszaehler.org/hardware/controllers/ir-schreib-lesekopf>`__
an einer USB Schnittstelle oder ein RS485 zu USB Konverter benötigt.

Die vom Smartmeter gesendeten Daten werden entsprechend dem SML Protokoll (Smart Message Language) codiert und übertragen.
Nähere Informationen finden sich `hier <http://wiki.volkszaehler.org/software/sml>`__

Unter den übermittelten Daten befinden sich Statusinformationen die mittels
`OBIS Kennzahlen <http://de.wikipedia.org/wiki/OBIS-Kennzahlen>`__  den verschiedenen
Messungen im Smartmeter zugeordnet werden können.
Zusätzlich geben die Datensätze noch Metadaten wie Einheit, Zeitstempel etc. an.
Sowohl die Messwerte wie auch die Metadaten können Items zugewiesen werden.

Die implementierten Algorithmen um die Checksummen zu berechnen wurden von
`PyCRC <https://github.com/tpircher/pycrc/blob/master/pycrc/algorithms.py>`__
verwendet.

Notwendige Software
~~~~~~~~~~~~~~~~~~~

Es wird das Paket pyserial benötigt das in ``requirements.txt`` aufgeführt ist und ab SHNG 1.8 automatisch beim Start installiert wird.

Benutzer berichten davon, das es unter Linux notwendig ist den User smarthome den Gruppen dialout und tty hinzuzufügen.
Weiterhin kann es notwendig sein eine Regel zur automatischen Zuordnung der Schnittstelle zu einem festen Port einzurichten.
Die Vorgehensweise ist beim DLMS Plugin beschrieben

Unterstützte Geräte
~~~~~~~~~~~~~~~~~~~

Folgende Zähler wurden mit dem Plugin bisher ausgelesen:

-  Hager EHZ363Z5
-  Hager EHZ363W5
-  EHM eHZ-GW8 E2A 500 AL1
-  EHM eHZ-ED300L
-  Holley DTZ541 (2018 Modell mit fehlerhafter CRC Implementation)
-  Landis & Gyr E220

Konfiguration
-------------

plugin.yaml
~~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.

.. code-block:: yaml

   smlx:
     class_name: Smlx
     class_path: plugins.smlx
     serialport: /dev/ttyUSB0
     # host: 192.168.2.1
     # port: 1234
     # device: raw | hex | <known-device>
     # for CRC generation
     # poly: 0x1021
     # reflect_in: True
     # xor_in: 0xffff
     # reflect_out: True
     # xor_in: 0xffff
     # swap_crc_bytes: False
     # date_offset: 0

Das ``date_offset`` Attribut definiert den Zeitpunkt des ersten Starts des
Smartmeter nach dem dieser installiert wurde. Es ist ein Integer und repräsentiert
die Sekunden nach `Unix Epoch <https://de.wikipedia.org/wiki/Unixzeit>`__ (1.1.1970, 0:00 Uhr, UTC)
Es wird vom Plugin benutzt um den tatsächlichen Zeitpunkt eines OBIS Datenpunktes zu berechnen.

Wenn man Datum und Zeit nicht kennt kann wie folgt vorgegangen werden:

Konfigurieren des Loggings von SmartHomeNG so, das das smlx Plugin Debug Informationen ausgibt.
Die Logs dann auf ``DEBUG plugins.smlx`` zeilen prüfen.
Suchen nach ``Entry`` Zeilen die ``valTime`` enthalten. 
Wenn sich ein Eintrag ``valTime`` findet der aussieht wie z.B. ``[None, 8210754]``,
dann notieren der Integerzahl (hier: ``8210754``).
Ganz links im Logeintrag findet sich Uhrzeit und Datum des Logging Eintrags.
Über einen `Unix Zeit Konverter <https://www.unixtime.de>`__ dann diese Uhrzeit und Datum in einen Unix Zeitstempel umwandeln.
Daraus lässt sich ``date_offset`` berechnen als ``Unix timestamp`` - ``valTime``.

Beispiel Eintrag aus dem Log:

"2019-10-18  09:34:35 DEBUG    plugins.smlx        Entry {'objName': '1-0:1.8.0*255', 'status': 1839364, 'valTime': [None, 8210754], 'unit': 30, 'scaler': -1, 'value': 560445, 'signature': None, 'obis': '1-0:1.8.0*255', 'valueReal': 56044.5, 'unitName': 'Wh', 'realTime': 'Fri Oct 18 09:34:21 2019'}"

Umwandeln von '*2019-10-18  09:34:35*' in einen Unix Zeitstempel liefert das Ergebnis *1571384075*. 

Mit ``valTime`` = *8210754* aus dem Log ergibt sich ``date_offset`` = 1571384075 - 8210754 = *1563173321‬*.

Wenn ein SmartMeter für ``valTime`` keinen gültigen Wert liefert (``valTime: None``), 
dann ist ``date_offset`` nutzlos und kann weggelassen werden.


items.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.

Items können mit Hilfe einer OBIS-Kennung einen vom Plugin abgerufenen Wert oder eine Eigenschaft zuweisen. 

Folgend eine Liste von nützlichen OBIS Codes die mit dem Attribut ``sml_obis`` verwendet werden können:

-  129-129:199.130.3*255 - Hersteller
-  1-0:0.0.9*255 - ServerId / Seriennummer
-  1-0:1.8.0*255 - Total Bezug [kWh]
-  1-0:1.8.1*255 - Tarif 1 Bezug [kWh]
-  1-0:1.8.2*255 - Tarif 2 Bezug [kWh]
-  1-0:2.8.0*255 - Total Einspeisung [kWh]
-  1-0:2.8.1*255 - Tarif 1 Einspeisung [kWh]
-  1-0:2.8.2*255 - Tarif 2 Einspeisung [kWh]
-  1-0:16.7.0*255 - Momentane Leistung [W]

Anstatt den (Mess-) Wert für einen bestimmten OBIS-Code zuzuweisen, kann auch eine weitere Eigenschaft
des Datenpunktes zugewiesen werden. Das kann durch ein zusätzliches Attribut ``sml_prop``
erreicht werden.
Hat ein Item ein Attribut ``sml_obis`` zugewiesen, aber kein Attribut ``sml_prop``, so wird 

Die folgenden Eigenschaften für ``sml_prop`` können verwendet werden:

-  ``objName`` - der OBIS Code als Zeichenkette / binäre Daten 
-  ``status`` - Ein Statuswert
-  ``valTime`` - die Zeit entsprechend dem Wert (als Sekunden der Einheit start oder als Zeitstempel)
-  ``unit`` - Identifiziert die Einheit des entsprechenden Wertes (z.B. W, kWh, V, A, ...)
-  ``scaler`` - der Skalierungsfaktor (10-factor shift) der benutzt wird um den echten Wert zu berechnen
-  ``value`` - der Wert
-  ``signature`` - Die Signatur um die Daten zu schützen

Zusätzlich können die folgenden Eigenschaften für ``sml_prop`` verwendet werden, die bei Bedarf berechnet werden:

-  ``obis`` - Der OBIS Code als Zeichenkette
-  ``valueReal`` - Der echte Wert, der sich unter Berücksichtigung des Skalierungsfaktors errechnet
-  ``unitName`` - Die Bezeichnung der Einheit
-  ``actualTime`` - ein String mit Datum und Zeit der tatsächlichen Zeit (z.B. 'Fri Oct 18 09:34:21 2019')


Der Status des Smartmeter ist ein String mit binären Daten. 
Die ersten 8 Bits sind immer 0000 0100
Alle anderen Bits haben eine spezielle Bedeutung und werden in folgende Attribute dekodiert:

-  ``statRun`` - True: Smartmeter zählt, False: Stillstand
-  ``statFraudMagnet`` - True: Manipulation mit Magneten entdeckt, False: Alles ok
-  ``statFraudCover`` - True: Manipulation der Abdeckung entdeckt, False: Alles ok
-  ``statEnergyTotal`` - Energiefluss total. True: -A, False: +A
-  ``statEnergyL1`` - Energiefluss L1. True: -A, False: +A
-  ``statEnergyL2`` - Energiefluss L2. True: -A, False: +A
-  ``statEnergyL3`` - Energiefluss L3. True: -A, False: +A
-  ``statRotaryField`` - True Drehfeld nicht L1->L2->L3, False: Alles ok
-  ``statBackstop`` - True backstop aktiv, False: backstop nicht aktive
-  ``statCalFault`` - True Kalibrationsfehler, False: ok
-  ``statVoltageL1`` - True Spannung L1 vorhanden, False: nicht vorhanden
-  ``statVoltageL2`` - True Spannung L2 vorhanden, False: nicht vorhanden
-  ``statVoltageL3`` - True Spannung L3 vorhanden, False: nicht vorhanden

Beispiel
^^^^^^^^

.. code:: yaml

   power:

       home:

           total:
               type: num
               sml_obis: 1-0:1.8.0*255

           current:
               type: num
               sml_obis: 1-0:16.7.0*255

           unit:
               type: num
               sml_obis: 1-0:16.7.0*255
               sml_prop: unitName


logic.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Funktionen
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Beispiele
---------

Hier ist noch was zu tun


Web Interface
-------------

SmartHomeNG liefert eine Reihe Komponenten von Drittherstellern mit, die für die Gestaltung des Webinterfaces genutzt werden können. Erweiterungen dieser Komponenten usw. finden sich im Ordner ``/modules/http/webif/gstatic``.

Wenn das Plugin darüber hinaus noch Komponenten benötigt, werden diese im Ordner ``webif/static`` des Plugins abgelegt.
 

Besonderheiten bestimmter Hardware
----------------------------------


Holley DTZ541
~~~~~~~~~~~~~

Normalerweise sollte es nicht notwendig sein die CRC Prüfsummenbildung zu ändern.
Aber zumindest das Holley DTZ541 nutzt falsche Parameter. Daher sind folgende Einstellungen
für dieses Gerät in der ``plugin.yaml`` vorzunehmen

.. code-block:: yaml

   HolleyDTZ541:
       plugin_name: smlx
       serialport: /dev/ttyUSB0
       buffersize: 1500
       poly: 0x1021
       reflect_in: true
       xor_in: 0x0000
       reflect_out: true
       xor_out: 0x0000
       swap_crc_bytes: True
       date_offset: 1563173307

Die Werte für ``serialport``, ``buffersize`` und ``date_offset`` müssen dabei auf die lokalen Gegebenheiten angepasst werden
