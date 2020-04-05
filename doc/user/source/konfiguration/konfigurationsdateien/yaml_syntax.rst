.. index:: YAML Syntax

.. _`YAML Syntax`:

.. role:: redsup

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

