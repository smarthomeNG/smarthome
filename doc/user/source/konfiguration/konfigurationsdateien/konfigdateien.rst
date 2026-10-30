:tocdepth: 3

.. role:: redsup

==========================
Konfiguration über Dateien
==========================

Für die Konfiguration sind die Verzeichnisse ``etc``, ``etc/items``, ``etc/structs``, ``etc/logics``, ``etc/scenes``
und ``etc/functions`` wichtig.
In diesen Verzeichnissen wird die Konfiguration gespeichert und gepflegt. Im folgenden sind
die Konfigurationsdateien beschrieben, die in diesen Verzeichnissen gespeichert werdeen.

Die Konfiguration erfolgt im weit verbreiteten `yaml <https://en.wikipedia.org/wiki/YAML>`_ Format.

Verzeichnisse
=============

Im folgenden sind die Verzeichnisse beschrieben, in denen Konfigurationsdateien abgelegt werden.


Verzeichnis *etc*
-----------------

In diesem Verzeichnis werden die allgemeineren Konfigurationsdateien abgelegt. Im einzelnen sind das folgende
Dateien:

- smarthome.yaml
- holidays.yaml
- module.yaml
- plugin.yaml
- logic.yaml
- logic_groups.yaml
- logging.yaml

Fehlt eine dieser Dateien beim Start, legt SmartHomeNG sie aus der Vorlage im Verzeichnis ``templates`` an.
Eine ``struct.yaml`` oder ``struct_<name>.yaml`` älterer Installationen wird beim Start in das Verzeichnis
``etc/structs`` verschoben.


Verzeichnis *etc/items*
-----------------------

In diesem Verzeichnis werden eine oder mehrere Dateien abgelegt, welche die Item Definitionen enthalten. Der
Name der Dateien ist dabei beliebig. Sie müssen nur gültige YAML Dateien sein und die Endung ``.yaml``
tragen.

- \*.yaml


Verzeichnis *etc/structs*
-------------------------

In diesem Verzeichnis werden die Dateien mit den struct Definitionen (Item-Templates) abgelegt
(siehe :doc:`struct <struct>`).

- \*.yaml


Verzeichnis *etc/logics*
------------------------

In diesem Verzeichnis werden die Python Code Dateien der Logiken abgelegt. Zusätzlich legt das Blockly Plugin
hier auch die Blockly Definitionen ab, die von dem Plugin in Python Code übersetzt werden.

- \*.py
- \*.blockly


Verzeichnis *etc/scenes*
------------------------

In diesem Verzeichnis werden Szenen Definitionen gespeichert. Außerdem legt SmartHomeNG hier für Szenen, bei
denen das Lernen von Werten erlaubt ist, eine Datei mit den gelernten Werten zu der Szenendefinition ab.
Die Dateien müssen als Namen den Item-Pfad des Items tragen, welches die Szene repräsentiert.

- \*.yaml


Verzeichnis *etc/functions*
---------------------------

In diesem Verzeichnis werden die Dateien mit den Userfunctions abgelegt
(siehe :doc:`Userfunctions </konfiguration/userfunctions>`).

- \*.py


Aufbau der Konfigurationsdateien
================================

Die Konfiguration von SmartHomeNG erfolgt über Dateien. Die
Funktionalität wird für **Items**, **Logiken** und **Plugins** in
jeweils eigenen Konfigurationsdateien vorgenommen.

Diese Seite beschäftigt sich mit dem grundlegenden Format der
Konfigurationsdateien. Für die vollständigen
Konfigurationsmöglichkeiten, bitte auf den jeweiligen Wiki Seiten
nachsehen.

Dieser Abschnitt beschäftigt sich nur mit den Teilen der
Markup-Language, die für SmartHomeNG relevant sind. Bei einem
weitergehenden Interesse an YAML, bitte auf Wikipedia oder
`yaml.org <http://yaml.org>`__ (auf Englisch) nachlesen. SmartHomeNG liest YAML Dateien nach YAML 1.2 (siehe
:ref:`YAML 1.1 und YAML 1.2 <yaml_versionen>`).

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
Es müssen Leerzeichen verwendet werden, die Struktur
einer YAML Datei wird durch Einrückungen bestimmt. Der Doppelpunkt, der
einem Sektions-/Key-Namen folgt, kann direkt nach diesem Namen folgen.
Er **muss** jedoch von einem Leerzeichen gefolgt werden

Formate von Values in YAML Dateien
----------------------------------

Values können in YAML Dateien alles, von einfachen Werten über binäre
Daten bis hin zu Python Objekten sein. Für die Konfigurationsdateien
werden folgende Value-Typen unterstützt:

-  Numerische Werte
-  Strings
-  Listen

Besonderheiten boolscher Werte
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Boolsche Werte werden ohne Quotes angegeben, z.B. **``cache: true``** oder **``enforce_updates: false``**.
SmartHomeNG wandelt den Wert in den Typ um, den das Item-Attribut, der Plugin- oder der Logik-Parameter erwartet;
dabei werden auch Strings wie ``'true'``, ``'yes'`` oder ``'on'`` als boolsche Werte erkannt.

Quotes werden nur benötigt, wenn ein Text gemeint ist, der von YAML sonst als boolscher Wert gelesen würde,
z.B. bei einem Item vom Typ **str**: Ohne Quotes wird aus **``initial_value: true``** der Text ``True``,
mit **``initial_value: 'true'``** bleibt es ``true``.

Es ist empfehlenswert nur **true** und **false** für boolsche Werte zu verwenden. In Dateien, die noch nach YAML 1.1
gelesen werden, sind auch **yes**, **no**, **on**, **off** und einzelne Buchstaben wie **y** und **N** boolsche
Werte (siehe unten).

Quotes für Texte, die wie Zahlen aussehen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Texte, die YAML als Zahl lesen würde, müssen in Quotes eingeschlossen werden, z.B. Telefonnummern, PINs oder
Passwörter mit führender Null (**``pin: '0815'``**) und Uhrzeiten (**``initial_value: '12:30'``**). Ohne Quotes wird
aus ``0815`` die Zahl ``815``.

.. _yaml_versionen:

YAML 1.1 und YAML 1.2
^^^^^^^^^^^^^^^^^^^^^

SmartHomeNG liest YAML Dateien nach YAML 1.2. Beginnt eine Datei mit der Zeile ``%YAML 1.1``, wird sie nach YAML 1.1
gelesen; beim Speichern über die Admin GUI bleibt die Version einer Datei erhalten. Empfohlen wird YAML 1.2: Die
mitgelieferten Vorlagen und alle Dateien, die SmartHomeNG neu anlegt, enthalten keine ``%YAML 1.1`` Zeile mehr.
Dateien früherer Installationen (z.B. die aus den damaligen Vorlagen erzeugten Dateien in ``etc``) können die Zeile
noch enthalten.

Die beiden Versionen lesen einige Werte ohne Quotes unterschiedlich:

.. list-table::
   :header-rows: 1
   :widths: 20 25 25 30

   * - Wert
     - YAML 1.1
     - YAML 1.2
     - in YAML 1.2 schreiben als
   * - ``yes``, ``no``, ``on``, ``off``
     - ``true`` / ``false``
     - Text
     - ``true`` / ``false``
   * - ``y``, ``Y``, ``n``, ``N``
     - ``true`` / ``false``
     - Text
     - ``true`` / ``false`` oder der Text
   * - ``12:30``, ``1:20:30``
     - Zahl (Basis 60: 750, 4830)
     - Text
     - ``'12:30'``
   * - ``010``
     - Zahl 8 (oktal)
     - Zahl 10
     - ``0o10`` bzw. ``10``
   * - ``08``, ``0049123456``
     - Text
     - Zahl (8, 49123456)
     - ``'08'``, ``'0049123456'``
   * - ``0o17``
     - Text
     - Zahl 15
     - ``'0o17'``

Für boolsche Item-Attribute, Plugin- und Logik-Parameter macht es keinen Unterschied, ob ``yes`` als boolscher Wert
oder als Text gelesen wird, da SmartHomeNG beides umwandelt. Anders ist es bei Werten, die als Text verwendet werden,
und in der ``etc/logging.yaml``, deren Werte direkt an das Python Logging übergeben werden.

Umstellen einer Datei von YAML 1.1 auf YAML 1.2:

1. SmartHomeNG beenden.
2. ``tools/upgrade_check.py --only yaml-1.1`` ausführen. Es listet alle Dateien mit ``%YAML 1.1`` und alle Werte, die
   YAML 1.2 anders lesen würde.
3. ``tools/upgrade_check.py --only yaml-1.1 --fix`` ausführen. Bei Dateien, deren Werte eindeutig umgestellt werden
   können, wird die Zeile ``%YAML 1.1`` entfernt, ``yes``/``no``/``on``/``off`` werden durch ``true``/``false``
   ersetzt und Texte, die YAML 1.2 als Zahl lesen würde, in Quotes gesetzt. Die geänderten Dateien werden vorher
   nach ``etc/upgrade_check_backup`` gesichert.
4. Die übrigen gemeldeten Werte von Hand anpassen: Dabei entscheiden, was gemeint war (z.B. ist ``12:30`` meist als
   Uhrzeit gemeint, wurde von YAML 1.1 aber als 750 gelesen) und den Wert eindeutig schreiben (siehe Tabelle).
   Anschließend Schritt 3 wiederholen, oder die Zeile ``%YAML 1.1`` von Hand entfernen.
5. SmartHomeNG starten und das Log auf Warnungen prüfen.

Ohne das Tool genügt es, die Zeile ``%YAML 1.1`` zu entfernen und die Werte aus der Tabelle in der Datei zu prüfen.

Besonderheiten bei der Angabe von Wertelisten
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Wertelisten werden in einer YAML Datei vorzugsweise mehrzeilig angegeben:

.. code-block:: yaml

   section:
      key1:
         - value1
         - value2

Beispiel von Item Definitionen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^

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
^^^^^^^^^

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
^^^^^^^^^^^

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
^^^^^^^^^^

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
