:tocdepth: 3

.. role:: redsup

==========================
Konfiguration über Dateien
==========================

Für die Konfiguration sind die Verzeichnisse ***../etc***, ***../items***, ***../scenes*** und ***../logics*** wichtig.
In diesen Verzeichnissen wird die Konfiguration gespeichert und gepflegt. Im folgenden sind
die Konfigurationsdateien beschrieben, die in diesen Verzeichnissen gespeichert werdeen.

Die Konfiguration erfolgt im weit verbreiteten `yaml <https://en.wikipedia.org/wiki/YAML>`_ Format.

Ältere Versionen von smarthome.py und SmartHomeNG benutzten das `configobj <http://www.voidspace.org.uk/python/articles/configobj.shtml>`_
Dateiformat, welches ähnlich zum bekannten `ini-file <https://en.wikipedia.org/wiki/INI_file>`_ Format
ist, jedoch die Möglichkeit hat, Abschnitte mit Unterstrukturen in Multilevel Strukturen anzulegen.
Dieses Dateiformat ist von SmartHomeNG noch unterstützt. Es ist jedoch veraltet und wird nur für Umsteiger aus
älteren Versionen beschrieben. Dieses Dateiformat wird in zukünftigen Versionen von SmartHomeNG
nicht mehr unterstützt werden. Ab welcher Version die Unterstützung entfallen wird, ist noch nicht festgelegt.

Wenn das Backend-Plugin konfiguriert ist, können damit Abschnitte des alten .conf Dateiformats in das yaml Format
überführt werden.

Es gibt außerdem ein Service Tool im Verzeichnis ***../tools***, welches dazu dient, die gesamte Konfiguration zu
konvertieren. Hierbei kann gewählt werden, ob die Inhalte des ***../etc*** Verzeichnisses, des ***../items*** Verzeichnisses
oder beide konvertiert werden sollen.

Genaueres bitte unter :doc:`../../tools/tools` nachlesen.


Verzeichnisse
=============

Im folgenden sind die Verzeichnisse beschrieben, in denen Konfigurationsdateien abgelagt werden.


Verzeichnis *../etc*
--------------------

In diesem Verzeichnis werden die allgemeineren Konfigurationsdateien abgelegt. Im einzelnen sind das folgende
Dateien:

- smarthome.yaml
- holidays.yaml
- module.yaml
- plugin.yaml
- logic.yaml
- logging.yaml
- struct.yaml


Verzeichnis *../items*
----------------------

In diesem Verzeichnis werden eine oder mehrere Dateien abgelegt, welche die Item Definitionen enthalten. Der
Name der Dateien ist dabei beliebig. Sie müssen nur gültige YAML Dateien sein und die Endung **.yaml**
tragen.

- \*.yaml


Verzeichnis *../logics*
-----------------------

In diesem Verzeichnis werden die Python Code Dateien der Logiken abgelegt. Zusätzlich legt das Blockly Plugin
hier auch die Blockly Definitionen ab, die von dem Plugin in Python Code übersetzt werden.

- \*.py
- \*.blockly


Verzeichnis *../scenes*
-----------------------

In diesem Verzeichnis werden Szenen Definitionen gespeichert. Außerdem legt SmartHomeNG hier für Szenen, bei
denen das Lernen von Werten erlaubt ist, eine Datei mit den gelernten Werten zu der Szenendefinition ab.
Die Dateien müssen als Namen den Item-Pfad des Items tragen, welches die Szene repräsentiert.

- \*.yaml


Aufbau der Konfigurationsdateien
================================

Die Konfiguration von SmartHomeNG erfolgt über Dateien. Die
Funktionalität wird für **Items**, **Logiken** und **Plugins** in
jeweils eigenen Konfigurationsdateien vorgenommen.

Diese Seite beschäftigt sich mit dem grundlegenden Format der
Konfigurationsdateien. Für die vollständigen
Konfigurationsmöglichkeiten, bitte auf den jeweiligen Wiki Seiten
nachsehen.

Seit dem Release 1.3 von SmartHomeNG können zur Konfiguration von
**Items**, **Logiken** und **Plugins** auch Dateien im YAML Format
eingesetzt werden. Dieses ist das ab Release 1.5 das Standardformat. Das
Format der YAML Dateien (Endung **.yaml**) wird im folgenden
beschrieben.

Bisher erfolgt die Konfiguration in **.conf** Dateien in einem
smarthome-spezifischen Format. Das **.conf** Format wird noch weiterhin
unterstützt. Dokumentiert wird jedoch nur noch das **yaml** Format. Das
**.conf** Format wird ab einem späteren Release (voraussichtlich v2.0)
nicht mehr unterstützt werden.

Ganz neu war die Nutzung des YAML Formats für SmartHomeNG im Release 1.3
nicht. Seit dem Übergang von smarthome.py zu SmartHomeNG wird bereits
dass Logging in einer YAML Datei konfiguriert.

Zur Konvertierung von **.conf** in **.yaml** Dateien, ist ab Release 1.3
von SmartHomeNG ein Tool beigefügt, welches diese Konvertierung für die
Item Dateien durchführt.

**.conf** und **.yaml** Dateien können gemischt eingesetzt werden. Es
ist dabei unbedingt darauf zu achten, dass keine Konfiguration doppelt
(1 mal in .conf und 1 mal in .yaml) vorgenommen wird bzw. von
SmartHomeNG eingelesen werden kann. Es darf für Plugins und Logiken also
nur entweder eine .conf oder .yaml Datei geben. Sollte doch eine .conf
und eine .yaml Datei für Plugins oder Logiken im /etc Verzeichnis
liegen, so wird die .conf Datei ignoriert und die Konfiguration aus der
.yaml Datei gelesen. Im Items-Verzeichnis können beide Dateitypen
gleichzeitig vorkommen. Hier ist bei der Umstellung nur darauf zu
achten, dass nicht aus Versehen ein Item sowohl in einer .conf **und**
einer .yaml Datei definiert ist.


Neues Dateiformat - .yaml Dateien
---------------------------------

Das YAML Format wird seit SmartHomeNG **Release 1.3** unterstützt.

Dieser Abschnitt beschäftigt sich nur mit den Teilen der
Markup-Language, die für SmartHomeNG relevant sind. Bei einem
weitergehenden Interesse an YAML, bitte auf Wikipedia oder
`yaml.org <http://yaml.org>`__ (auf Englisch) nachlesen. Der aktuell in
SmartHomeNG eingesetzte Parser unterstützt die YAML Version 1.1.

Im YAML Format sehen die Beschreibungen für **Plugins** und **Logiken**
dann folgendermaßen aus:

.. code-block:: yaml

   section1:
       key1: value1
       key2: value2

   section2:
       key3: value3
       key4: value4

Und die Beschreibungen für **Items** sehen so aus:

.. code-block:: yaml

   section:
       key1: value1
       key2: value2

       subsection:
           key3: value3

           sub_subsection:
               key4: value4

Wichtig ist dabei folgendes: - In YAML Dateien sind keine TABs erlaubt.
Es müssen Leerzeichen verwendet werden. - Im Gegensatz zu
Item\ **.conf** Dateien, bei denen die Struktur durch die Anzahl eckiger
Klammern um den Sektions(Item)-Namen bestimmt wird, wird die Struktur
einer YAML Datei durch Einrückungen bestimmt. - Der Doppelpunkt, der
einem Sektions-/Key-Namen folgt, kann direkt nach diesem Namen folgen.
Er **muss** jedoch von einem Leerzeichen gefolgt werden

Formate von Values in YAML Dateien
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Values können in YAML Dateien alles, von einfachen Werten über binäre
Daten bis hin zu Python Objekten sein. Für die Konfigurationsdateien
werden folgende Value-Typen unterstützt:

-  Numerische Werte
-  Strings
-  Listen

Besonderheiten boolscher Werte
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SmartHomeNG verarbeitet, wie schon smarthome.py, die Values als Strings.
Dies gilt insbesondere bei der Übergabe von Werten an Plugins. Das ist
besonders bei der Angabe boolscher Werte zu beachten. Da der YAML Parser
bei einer Angabe wie **``boolwert: true``** einen boolschen Wert in die
Item Hierarchie von SmartHomeNG schreiben würde, muss durch Quotes
sichergestellt werden, dass ein String übergeben wird, also
folgendermaßen: **``boolwert: 'true'``**.

YAML interpretiert bis inclusive Version 1.1 auch **yes** und **no** als
boolsche Werte. Deshalb müssen auch diese Werte in Quotes eingeschlossen
werden. Es ist empfehlenswert nur **true** und **false** für boolsche
Werte zu verwenden.

Besonderheiten bei der Angabe von Wertelisten
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Im Gegensatz zu den bisherigen .conf Dateien, in denen Wertelisten auf
einer Zeile spezifiziert wurden und die Werte durch ein ‘\|’-Zeichen
getrennt wurden, ist die Spezifikation in einer YAML Datei vorzugsweise
mehrzeilig.

Statt

::

       [section]
           key1 = value1 | value2

gibt man jetzt folgendes an:

.. code-block:: yaml

   section:
      key1:
         - value1
         - value2

Beispiel von Item Definitionen in YAML
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   # items.yaml
   wohnung:
       kochen:
           strahler:
               name: Strahler Küchenwand
               type: bool
               knx_dpt: 1
               knx_send: 1/1/6
               knx_init: 1/2/6

               level:
                   type: num
                   knx_dpt: 5
                   knx_send: 1/4/6
                   knx_init: 1/5/6

   # ...

           kochfeldgesamt:
               name: Kochfeld Gesamt
               watt:
                   type: num
                   sqlite: 'true'
                   eval: sh.wohnung.kochen.kochfeld1.watt() + sh.wohnung.kochen.kochfeld2.watt()
                   eval_trigger:
                   - wohnung.kochen.kochfeld1.watt
                   - wohnung.kochen.kochfeld2.watt

In YAML Dateien können String-Values mehrzeilig sein. Der lesbarste Weg
ist es, den String-Value mit einem ‘\|’-Zeichen anfangen zu lassen und
den eigentlichen Wert auf der Folgezeile zu beginnen. Der gesamte String
muss/darf dann nicht in Single-Quotes (’) oder Double-Quotes (")
eingeschlossen werden. Wenn innerhalb dieses Strings Double-Quotes
verwendet werden sollen, so müssen diese *escaped* werden (").

Im folgenden Beispiel wird das anhand einer Widget Definition für
smartVISU gezeigt:

.. code-block:: yaml

   wohnung:
       kochen:
           sv_page: room
           name: Kochen
           visu_downlights:
               name: Downlights Tresen
               sv_widget: |
                   {{ device.dimmer('wohnung.kochen.dl_aussen', 'Äußere Downlights', 'wohnung.kochen.dl_aussen', ''wohnung.kochen.dl_aussen.level'') }}
                   {{ device.dimmer('wohnung.kochen.dl_innen', 'Innere Downlights', 'wohnung.kochen.dl_innen', ''wohnung.kochen.dl_innen.level'') }}
                   {{ device.dimmer('wohnung.kochen.dl_mitte', 'Mittleres Downlight', 'wohnung.kochen.dl_mitte', 'wohnung.kochen.dl_mitte.level') }}

Bei einzeiligen String-Values muss der String in Single-Quotes oder
Double-Quotes eingeschlossen werden. Wenn der String selbet Quotes (’)
enthält, kann der gesamte String mit Doppel-Quotes (") an Stelle der
Single-Quotes (’) eingeschlossen werden. Dann braucht man Single-Quotes
nicht zu *escapen*. Allerdings müssen dann evtl. vorkommende
Doppel-Quotes escaped werden.

Beispiel:

.. code-block:: yaml

   wohnung:
       kochen:
           sv_page: room
           name: Kochen
           visu_downlights:
               name: Downlights Tresen
               sv_widget: "{{ device.dimmer('wohnung.kochen.dl_aussen', 'Äußere Downlights', 'wohnung.kochen.dl_aussen', 'wohnung.kochen.dl_aussen.level') }}"

Konvertierung von .conf Dateien in das YAML Format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Im Verzeichnis **../tools** von SmartHomeNG liegt ein Tool
(conf_to_yaml_converter.py) zur Konvertierung der .conf Dateien in YAML
Dateien.

Der Konverter konvertiert sowohl die .conf Dateien im **../items**
Verzeichnis, als auch die .conf Dateien im **../etc** Verzeichnis. Nach
dem Start des Konverters fragt er für jedes der beiden Verzeichnisse ab,
ob die Dateien in dem Verzeichnis konvertiert werden sollen. Wichtig:
Der Konverter muss vom Verzeichnis tools gestartet werden.

   Wenn in den .conf Dateien Blöcke auskommentiert sind, so werden diese
   als Kommentare übernommen und nicht konvertiert. Falls es gewünscht
   ist diese Blöcke zu konvertieren, so muss die Auskommentierung der
   Zeilen vor der Konvertierung entfernt werden und nach der
   Konvertierung wieder hinzugefügt werden.

Die ursprünglichen .conf Dateien bleiben bei der Konvertierung
unverändert in den Verzeichnissen liegen.

Nacharbeiten
^^^^^^^^^^^^

**../items**-Verzeichnis: Als Nacharbeiten **müssen** die .conf Dateien
aus dem **../items** Verzeichnis heraus bewegt werden, da SmartHomeNG im
**../items** Verzeichnis alle .conf und alle .yaml Dateien einliest.
Dabei würden die Definitionen der Items zweimal eingelesen (einmal aus
der .conf Datei und einmal aus der .yaml Datei).

**../etc**-Verzeichnis: Als Nacharbeiten sollten die .conf Dateien aus
dem **../etc** Verzeichnis heraus bewegt werden, um Verwirrungen zu
vermeiden. Das herausbewegen ist nicht unbedingt notwendig, da die
SmartHomeNG beim Einlesen der Konfigurationsdateien nur eine Version
einliest. Ist eine .yaml Datei vorhanden, wird diese eingelesen. Nur
wenn keine .yaml Datei vorhanden ist, wird die .conf Datei gelesen.


Vorteile von YAML
-----------------

-  Standard Dateiformat
-  bessere Lesbarkeit
-  Tools zur formalen Prüfung der YAML-Konformität von Dateien verfügbar
-  leichtere Editierbarkeit:

   -  Sytax Highlighting mit diversen Editoren möglich
   -  Code-Faltung zur besser Übersicht in großen Dateien mit diversen
      Editoren möglich
   -  Ein- und Ausrücken von Items (bzw. Item-Strukturen) mit diversen
      einfach möglich, ohne Notwendigkeit weiterer Anpassungen (Anzahl
      eckiger Klammern bei jedem bewegtem Item)

- Neue Features von SmartHomeNG werden zum Teil nur bei Verwendung von
  YAML Dateien verfügbar sein.


Altes Dateiformat - .conf Dateien
---------------------------------

Die .conf Dateien bestehen aus einer Reihe von Sektionen (Plugin- bzw.
Logikdefinitionen), die Key/Value-Listen enthalten. Für Plugins und
Logiken sind Sektionen nur auf der obersten Ebene zulässig.

::

   [section1]
       key1 = value1
       key2 = value2

   [section2]
       key3 = value3
       key4 = value4

Für Items können Sektionen (Itemdefinitionen) weitere Unter-Sektionen
(weitere Itemdefinitionen) enthalten.

::

   [section]
       key1 = value1
       key2 = value2

       [[subsection]]
           key3 = value3

           [[[sub_subsection]]]
               key4 = value4



.. index:: YAML Syntax

.. _`YAML Syntax`:

YAML Syntax
===========

YAML steht für "YAML Ain't Markup Language" und wird in SmartHomeNG für Konfigurationsdateien
verwendet.

YAML ist im Grunde ein lesbares strukturiertes Datenformat. Es ist weniger komplex und unhandlich
als XML oder JSON, bietet jedoch ähnliche Funktionen. Im Wesentlichen ermöglicht es,
leistungsstarke Konfigurationseinstellungen bereitzustellen, ohne einen komplexeren Codetyp
wie CSS, JavaScript und PHP erlernen zu müssen.

YAML ist von Grund auf so aufgebaut, dass es einfach zu bedienen ist. Im Kern wird eine YAML-Datei
zur Beschreibung von Daten verwendet.

Hier ist ein kurzer Überblick über den grundlegenden YAML Umfang, der in SmartHomeNG genutzt wird.


Grundlegende YAML Regeln
------------------------

Es gibt einige Regeln, die YAML implementiert hat, um Probleme im Zusammenhang mit Mehrdeutigkeiten
in Bezug auf verschiedene Sprachen und Bearbeitungsprogramme zu vermeiden. Diese Regeln ermöglichen es,
dass eine einzelne YAML-Datei konsistent interpretiert wird, unabhängig davon, welche Anwendung
und/oder Bibliothek zur Interpretation verwendet wird.

- YAML-Dateien sollten möglichst in .yaml enden.
- YAML unterscheidet zwischen Groß- und Kleinschreibung.
- YAML erlaubt nicht die Verwendung von Tabs. Stattdessen werden Leerzeichen verwendet.


.. note::

   Es muss darauf geachtet werden, dass Einrückungen **immer** mit der **selben Anzahl** an Leerzeichen erfolgen.

   Zur Strukturierung der Daten ist eine Einrückung um ein Leerzeichen zwar hinreichend. Allerdings
   macht eine so geringe Einrückung die Daten schnell unleserlich/unübersichtlich.

   Es wird **DRINGEND** empfohlen für Einrückungen **4 Leerzeichen** zu verwenden!


Basis DataTypen in YAML
-----------------------

YAML zeichnet sich durch die Verwendung von Mappings (Dictionaries), Sequenzen (Listen) und
Skalaren (Strings / Numbers) aus. Obwohl es mit den meisten Programmiersprachen verwendet werden
kann, funktioniert es am besten mit Sprachen, die um diese Datenstrukturtypen herum gebaut sind.
Dazu gehören: PHP, Python, Perl, JavaScript und Ruby.


Skalare
~~~~~~~

Skalare sind ein ziemlich grundlegendes Konzept. Sie sind die Zeichenfolgen und Zahlen, aus denen
sich die Daten auf der Seite zusammensetzen. Ein Skalar könnte eine boolesche Eigenschaft sein,
wie Yes, Integer (Zahl) wie 42 oder eine Textzeichenfolge wie ein Satz oder der Titel Ihrer Website.

Skalare werden oft als Variablen in der Programmierung bezeichnet. Wenn Sie eine Liste von Pflanzen
erstellen würden, wären dies die Namen, die diesen Pflanzen gegeben wurden.

Die meisten Skalare sind nicht in Anführungszeichen gesetzt. Wenn Sie jedoch eine Zeichenfolge
eingeben, die Interpunktionszeichen und andere Elemente verwendet, die mit der YAML-Syntax verwechselt
werden können (Bindestriche, Doppelpunkte usw.), können Sie diese Daten in einfache oder doppelte
Anführungszeichen setzen. Doppelte Anführungszeichen ermöglichen die Verwendung von Escapes zur
Darstellung von ASCII- und Unicode-Zeichen.

.. code-block:: yaml

   integer: 42
   string: "42"
   float: 42.0
   boolean: Yes


Sequenzen
~~~~~~~~~

Hier ist eine einfache Sequenz, die Sie in SmartHomeNG finden können. Es ist eine einfache Liste,
bei der jeder Eintrag in der Liste in einer eigenen Zeile steht und mit einem öffnenden Bindestrich
beginnt.

.. code-block:: yaml

   - Aus
   - Gedimmt
   - Hell


Diese Sequenz platziert jedes Element in der Liste auf derselben Ebene.

Wenn Sie eine verschachtelte Sequenz mit Elementen und Unterelementen erstellen möchten
(wird in SmartHomeNG standerdmäßig nicht verwendet), können Sie dies tun, indem Sie vor jedem
Bindestrich in den Unterelementen ein einzelnes Leerzeichen einfügen. YAML verwendet Leerzeichen
(keine Tabs) zum Einrücken. Sie können ein Beispiel dafür unten sehen.

.. code-block:: yaml

   -
     - Hund
     - Katze
     - Maus
   -
     - Rind
     - Schwein
     - Ziege


Zuordnungen
~~~~~~~~~~~

Mit der Zuordnung können Sie Schlüssel mit Werten auflisten. Dies ist nützlich, wenn Sie einem
bestimmten Element einen Namen oder eine Eigenschaft zuweisen.

.. code-block:: yaml

   dimmwert: 25

In diesem Beispiel wird der Wert 25 dem *dimmwert* zugeordnet. In Verbindung mit einer Sequenz
kann eine Zuordnung folgendermaßen aussehen:

.. code-block:: yaml

   helligkeiten:
     - Aus
     - Gedimmt
     - Hell


Kommentare
~~~~~~~~~~

YAML Dateien können Kommentare enthalten. Kommentare beginnen mit einem #-Zeichen und reichen
immer bis zum Ende der Zeile.


Konfigurationsdateien
=====================

Auf den folgenden Seiten sind die einzelnen Konfigurationsdateien beschrieben.


.. toctree::
   :maxdepth: 4
   :titlesonly:

   smarthome.rst
   holidays.rst
   module.rst
   plugin.rst
   logic.rst
   logging.rst
   struct.rst
   items.rst
   logics.rst
   scenes.rst
