.. index:: Plugins; smartmeter (Auslesen von Smartmetern)
.. index:: smartmeter

==========
smartmeter
==========

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Das Plugin dient zum Auslesen von Smartmetern, die das DLMS- oder das SML-Protokoll beherrschen.

Die vom SmartMeter übermittelten Datensätze werden mit sogenannten 
`OBIS Kennzahlen <http://de.wikipedia.org/wiki/OBIS-Kennzahlen>`__  den verschiedenen
Messungen im Smartmeter zugeordnet werden. Zusätzlich geben die Datensätze noch
Metadaten wie Einheit, Zeitstempel etc. an.

Sowohl die Messwerte wie auch die Metadaten können Items zugewiesen werden.


Anforderungen
=============

- SmartMeter / elektronischer Hauszähler

  - mit DLMS-Protokoll (Device Language Message Specification) gemäß IEC 62056-21
  - mit SML-Protoll (Smart Message Language) gemäß BSI TR-03109-1 Anlage IV Teil b

- ggf. USB-Schnittstelle mit IR Lesekopf (z.B. von `volkszaehler.org <http://www.volkszaehler.org>`_ )
- alternativ IP-fähiges SmartMeter (nur SML)

Das Python Module pyserial, SmlLib und (ggf.) pyserial_asyncio werden benötigt. Die Installation erfolgt
(ab SmartHomeNG 1.8) automatisch über den Inhalt der mitgelieferten Datei ``requirements.txt`` 
oder manuell auf der Konsole mit

.. code:: bash

   python3 -m pip install pyserial SmlLib pyserial_asyncio

Es muß sichergestellt sein, dass der Benutzer, der SmartHomeNG ausführt, auch die Berechtigung hat,
den seriellen Port zu verwenden. Unter Linux sollte dafür der Nutzer Mitglied der Gruppen ``dialout`` und/oder ``tty`` sein.

Zum einfacheren Handhabung des Zugriffs auf die serielle Schnittstelle kann eine udev-Regel erstellt werden. Dies kann für eine aktuelle Version des Volkszaehler IR-Lesekopfes z.B. wie folgt aussehen:

.. code:: bash

   echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", ATTRS{serial}=="0092C9FE", MODE="0666", GROUP="dialout" , SYMLINK+="hauszaehler"' > /etc/udev/rules.d/11-dlms.rules
   udevadm trigger

Der Symlink erhält dabei einen passenden Namen für die Schnittstelle, der natürlich den eigenen Anforderungen angepasst werden kann. In diesem Beispiel heißt die Gerätedatei ``/dev/hauszaehler``. Die im Beispiel angegebenen Vendor- und Product-IDs sowie die Seriennummer müssen an die eigenen Geräte angepasst werden.


Unterstützte Hardware
======================

- SmartMeter mit DLMS-Protokollunterstützung
- SmartMeter mit SML-Protokollunterstützung

Erfolgreich getestet wurden bisher:

- EMH eHZB (SML)
- ZPA GH302 (SML)
- Iskra MT681 (SML)
- Landis & Gyr E320 (SML)
- efr SGM-D4-A920N (SML)
- (wird bei Vorliegen weiterer Testergebnisse ergänzt)


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/smartmeter` beschrieben.


Beispiele für die plugin.yaml
------------------------------

.. code:: yaml

   smartmeter:
       plugin_name: smartmeter
       serialport: /dev/hauszaehler
       cycle: 300

Im Beispiel wird das Plugin alle 300 Sekunden, also alle 5 Minuten, das Smartmeter abfragen.
Da cycle nicht zu einem bestimmten Zeitpunkt aufgerufen wird sondern der Abstand zwischen den Abfragen
nur entsprechend lang ist, ist auch der Zeitpunkt der Daten recht variabel.

Alternativ kann (derzeit nur bei SML) auch statt zyklischer Abfragen dauerhaft auf Daten
vom SmartMeter gewartet werden. Diese Funktion benötigt pyserial_asyncio und kann je nach
SmartMeter jede Sekunde Daten liefern:

.. code:: yaml

   smartmeter:
      plugin_name: smartmeter
      serialport: /dev/hauszaehler
      poll: false


Einrichtungsverfahren:
----------------------

Das Plugin unterstützt die Diagnoseabfrage von SML- und DLMS-SmartMetern über die
Kommandozeile. Dazu ist aus dem SmartHomeNG-Basisordner das jeweilige Modul des
Plugins aufzurufen:

``python3 plugins/smartmeter/dlms.py --help``

bzw.

``python3 plugins/smartmeter/sml.py --help``

Die Module geben jeweils die unterstützten Optionen aus.

Eine manuelle Identifizierung ist allerdings normalerweise nicht mehr notwendig.
Ohne Angabe des Kommunikationsprotokolls in der **plugin.yaml** versucht das
Plugin automatisch, das korrekte Protokoll zu ermitteln. Sofern dies gelingt,
wird es automatisch genutzt und im Web-Interface angezeigt.
Sollte die Identifizierung fehlschlagen, wird die Log-Ausgabe im Web-Interface
angezeigt.

Das manuelle Eintragen des Protokolls in die plugin.yaml kann beim Start von
SmartHomeNG den Start des Plugins beschleunigen, da nicht jedesmal automatisch
das Protokoll identifiziert werden muss.

Optional
--------

Mit dem Python-Skript ``get_manufacturer_ids.py`` im Plugin-Ordner kann eine
Liste von Herstellern von DLMS-SmartMetern im Excel-Format geladen werden. Aus
dieser Liste wird die YAML-Datei ``manufacturer.yaml`` erstellt. Wenn das Plugin
ein DLMS-SmartMeter ausliest, für das entsprechende Informationen vorliegen,
werden die Ausgabedaten entsprechend angereichert. Wenn diese Datei nicht vorhanden
ist, werden die gelesenen Daten 1:1 ausgegeben.

Dieses Skript benötigt das Python Modul ``openpyxl`` dieses ist nicht in der
``requirements.txt`` aufgeführt, weil es nur für dieses Skript benötigt wird.


Item-Konfiguration / Ermittlung von OBIS-Codes
==============================================

Hintergrundinformationen zu OBIS-Codes
--------------------------------------

OBIS-Kennzahlen werden zur Datenübertragung in der Energiewirtschaft verwendet, und können
universell verschiedene Daten übertragen (u.a. elektrische oder thermische Daten). Diese
sind im Standard IEC 62056-6-1 für elektrische Energie spezifiziert.

Im Umfeld von SmartMetern werden sie hauptsächlich genutzt, um Bezug und Einspeisung
elektrischer Energie, Energieflüsse und Leistungswerte zu übertragen.

Sie bestehen aus einer Kombination von sechs Wertgruppen, die die genaue Bedeutung jedes Datenelements beschreiben:

Eine einzelne **Zeile** kann so aussehen:

.. code:: text

   A-B:C.D.E*F(Wert*Einheit)(anderer Wert)

Die Wertegruppen **A** und **B** sind optional, ebenso **E** und **F**.
Der "andere Wert" kann weggelassen werden, ebenso die Einheit des ersten Wertes.

Die Bedeutung der einzelnen Codes ist im Prinzip festgelegt, kann aber in verschiedenen
SmartMetern unterschied verwendet werden. Details lassen sich der Spezifikation
des jeweiligen SmartMeters entnehmen.

Im Folgenden werden die Bedeutungen in Bezug auf Elektrizität angegeben.

A
    Grundlegende **Eigenschaft** des Datenelements (abstrakte Daten, Strom-, Gas-, Wärme-, wasserbezogene Daten)

    - **0** Abstrakte Objekte
    - **1** Objekte mit Bezug auf Elektrizität

B
    **Kanalnummer**, d.h. die Nummer des Eingangs bei Geräten mit mehreren Eingängen

C
    **Messgröße** (Wirk-, Blind-, Scheinleistung, Strom, Spannung, ...)

D
    **Messart** (Maximum, aktueller Wert, Energie, ...)

E
    **Tarifstufe** (0 bei Eintarifzähler oder Summe aus den anderen Tarifen)

F
    wird im deutschen Energiemarkt nicht verwendet.


OBIS-Codebeispiele
------------------

Zunächst zwei Codebeispiele von unterschiedlichen Smartmetern, um eine Vorstellung von den Unterschieden zu bekommen:

OBIS-Codebeispiel A
^^^^^^^^^^^^^^^^^^^

Einige erste Zeilen einer beispielhaften OBIS-Code-Auslesung für einen
**Landis & Gyr ZMD 310** SmartMeter für industrielle Zwecke

.. code:: text

   1-1:F.F(00000000)
   1-1:0.0.0(50871031)
   1-1:0.0.1(50871031)
   1-1:0.9.1(155420)
   1-1:0.9.2(170214)
   1-1:0.1.2(0000)
   1-1:0.1.3(170201)
   1-1:0.1.0(18)
   1-1:1.2.1(0451.17*kW)
   1-1:1.2.2(0451.17*kW)
   1-1:2.2.1(0060.24*kW)
   1-1:2.2.2(0060.24*kW)
   1-1:1.6.1(27.19*kW)(1702090945)
   1-1:1.6.1*18(28.74)(1701121445)
   1-1:1.6.1*17(28.95)(1612081030)
   1-1:1.6.1*16(25.82)(1611291230)
   1-1:1.8.0(00051206*kWh)
   1-1:1.8.0*18(00049555)
   1-1:1.8.0*17(00045862)
   ...

OBIS-Codebeispiel B
^^^^^^^^^^^^^^^^^^^

Beispiel für das Auslesen eines OBIS-Codes von einem relativ einfachen **Pafal 12EC3g**
SmartMeter:

.. code:: text

   0.0.0(72044837)(72044837)
   0.0.1(PAF)(PAF)
   F.F(00)(00)
   0.2.0(1.29)(1.29)
   1.8.0*00(000783.16)(000783.16)
   2.8.0*00(000045.38)(000045.38)
   C.2.1(000000000000)(                                                )(000000000000)(                                                )
   0.2.2(:::::G11)!(:::::G11)(!)

Werte aus den Codezeilen ermitteln
----------------------------------

Im Vergleich der Beispiele wird offensichtlich das der grundsätzlich gleiche OBIS Code leicht
unterschiedlich erscheint:


+-------------------------+--------------------------------+
| Beispiel A              | Beispiel B                     |
+=========================+================================+
| 1-1:F.F(00000000)       | F.F(00)(00)                    |
+-------------------------+--------------------------------+
| 1-1:1.8.0(00051206*kWh) | 1.8.0*00(000783.16)(000783.16) |
+-------------------------+--------------------------------+

Um den Wert von ``1-1:1.8.0(00051206*kWh)`` in ein Item zu bekommen, bekommt das Item folgende
Attribute:

.. code:: yaml

   zaehler:
      type: num
      obis_code: '1-1:1.8.0'

Um den Wert von ``1.8.0*00(000783.16)(000783.16)`` in ein Item zu bekommen, bekommt das Item folgende
Attribute:

.. code:: yaml

   zaehler:
      type: num
      obis_code: '1.8.0*00'

Um die Einheit von ``1-1:1.8.0(00051206*kWh)`` in ein Item zu bekommen, bekommt das Item folgende Attribute:

.. code:: yaml

   zaehler_unit:
      type: str
      obis_code: '1-1:1.8.0'
      obis_property: unit

Item-Konfiguration
------------------

Eine Beispielhafte **item.yaml** für die OBIS Codes aus **Beispiel A** könnte wie folgt aussehen:

.. code:: yaml

   Stromzaehler:
       Auslesung:
           type: str
           obis_readout: true

       Seriennummer:
           type: str
           obis_code: '1-1:0.0.0'

       Ablesung:
           # Datum und Uhrzeit der letzten Ablesung
           Uhrzeit:
               type: foo
               obis_code: '1-1:0.9.1'
           Datum:
               type: foo
               obis_code: '1-1:0.9.2'
           Datum_Aktueller_Abrechnungsmonat:
               type: foo
               obis_code: '1-1:0.1.3'
           Monatszaehler:
               # Billing period counter
               type: num
               obis_code: '1-1:0.1.0'

       Bezug:
           Energie:
               type: num
               sqlite: yes
               obis_code: '1-1:1.8.1'

           Energie_Einheit:
               type: str
               sqlite: yes
               obis_code: '1-1:1.8.1'
               obis_property: unit

       Lieferung:
           Energie:
               type: num
               sqlite: yes
               obis_code: '1-1:2.8.1'

           Energie_Einheit:
               type: str
               sqlite: yes
               obis_code: '1-1:2.8.1'
               obis_property: unit


Alternativ kann die automatische Item-Konfiguration im Web-Interface verwendet werden.

Web Interface
=============

Das smartmeter Plugin verfügt über ein Webinterface, mit dessen Hilfe die Items,
die das Plugin nutzen, sowie die roh ausgelesenen Werte übersichtlich dargestellt
werden.

Item-Konfiguration automatisch erstellen
----------------------------------------

Weiterhin gibt es die Funktion, alle gelesenen Werte so in eine Datei zu schreiben,
dass diese für die Item-Konfiguration für SmartHomeNG verwendet werden kann.

Wenn der Button **Items erstellen** gedrückt wird, erstellt das Plugin die Datei
``smartmeter-<Serialnummer vom Zähler>.yaml`` im ``items``-Verzeichnis von 
SmartHomeNG. Beim nächsten Start wird diese automatisch eingebunden.
Das Stammitem erhält als Namen die Seriennummer des Zählers, alle einzelnen Werte
und ihre Einheiten werden unterhalb des Stammitems angelegt.

Wenn eine strukturiertere Itemkonfiguration gewünscht wird, müssen diese Daten
von Hand an anderer Stelle in die Itemkonfiguration eingefügt werden. Die Arbeit,
für jedes einzelne Item die OBIS-Codes und die Einheiten auszulesen, ist dabei
aber schon erledigt.


Aufruf des Webinterfaces
------------------------

Das Plugin kann aus dem backend aufgerufen werden. Dazu auf der Seite Plugins in
der entsprechenden Zeile das Icon in der Spalte **Web Interface** anklicken.


Beispiele
---------

Folgende Informationen können im Webinterface angezeigt werden:

- Oben rechts werden allgemeine Parameter zum Plugin angezeigt.

- Im ersten Tab werden alle Items aufgelistet, die für dieses Plugin konfiguriert sind.

- Im zweiten Tab werden alle Datenpunkte der letzten Auslesung mit ihren OBIS-Codes
  und ggf. Properties aufgelistet. Das können Einheiten und/oder Bezeichnungen des
  Datenpunkts im Klartext sein.

- Im dritten Tab werden detaillierte Statusinformationen über den Zähler angezeigt.
