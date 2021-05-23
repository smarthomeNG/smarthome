
.. index:: Entwicklung; Logiken

.. role:: bluesup
.. role:: redsup


Logiken
=======


Einführung
----------

Logiken in SmartHomeNG sind in Python geschriebene Skript. Sie werden im Unterordner ``logics/`` abgelegt
und definiert in ``etc/logic.yaml``.
Die Konfigurationsdatei ``etc/logic.yaml`` beschreibt für SmartHomeNG unter welchen Bedingungen eine bestimmte Logik auszuführen ist.

Die folgende Beispielkonfiguration definiert 4 Logiken:

* Die erste Logik mit Namen ``InitSmartHomeNG`` befindet sich in der Datei ``logics/InitSmartHomeNG.py``.
  Das Attribut ``crontab: init`` weist SmartHomeNG an diese Logik direkt nach dem Start auszuführen.
* Die zweite Logik mit dem Namen ``Hourly`` befindet sich in der Datei ``logics/time.py``
  und das Attribut ``cycle: 3600`` weist SmartHomeNG an die Logik alle 3600 Sekunden (eine Stunde) auszuführen.
* Die dritte Logik mit Namen ``Gate`` befindet sich in der Datei ``logics/gate.py`` und das Attribut
  ``watch_item: gate.alarm`` weist SmartHomeNG an die Logik auszuführen, wenn der Wert des Items gate.alarm sich ändert.
* Die vierte Logik mit Namen ``disks`` befindet sich in der Datei ``logics/disks.py``. Der crontab Eintrag weist SmartHomeNG an
  diese Logik alle 5 Minuten auszuführen.

.. code-block:: yaml
   :caption:  etc/logic.yaml

   InitSmarthomeNG:
       filename: InitSmartHomeNG.py
       crontab: init

   Hourly:
       filename: time.py
       cycle: 3600

   Gate:
       filename: gate.py
       watch_item: gate.alarm    # monitor for changes

   disks:
       filename: disks.py
       # 'crontab: run at start and every 5 minutes'
       crontab:
         - init
         - '0,5,10,15,20,25,30,35,40,45,50,55 * * *'
       usage_warning: 500

Konfigurations Parameter
------------------------

Die folgenden Parameter können genutzt werden um eine Logik und ihre Ausführungsumstände festzulegen:

watch_item
~~~~~~~~~~

Die Liste der angegebenen Items wird auf Änderungen überwacht

.. code-block:: yaml
   :caption:  etc/logic.yaml

   logicnamehere:
      watch_item:
       - house.alarm
       - garage.alarm


Jede Änderung bei den Items **house.alarm** und **garage.alarm** löst die Ausführung der angegebenen Logik aus.
Es ist möglich einen Stern * für einen Pfadbestandteil zu setzen, ähnlich eines regulären Ausdrucks:

.. code-block:: yaml

   watch_item: '*.door'

Eine Änderung von **garage.door** oder auch **house.door** wird die Ausführung der Logik auslösen aber **nicht**
eine Änderung von **house.hallway.door**

cycle
~~~~~

Sorgt für eine zyklische Ausführung der Logik

.. code-block:: yaml

   cycle: 60


Optional kann ein Argument übergeben werden

.. code-block:: yaml

   cycle: 60 = 100


Dadurch wird die Logik alle 60 Sekunden ausgeführt und der Wert 100 an die Logik übergeben.
Innerhalb der Logik kann auf den Wert über ``trigger['value']`` zugegriffen werden

**Seit SmartHomeNG v1.3** gibt es erweiterte Konfigurations Optionen.

Die Zeitspanne für die zyklische Ausführung kann auf zwei Arten angegeben werden:

1. Eine Zahl die die Zeitspanne in Sekunden angibt, kann optional mit einem ``s`` gekennzeichnet werden oder
2. eine Zahl gefolgt von ``m`` die eine Zeitspanne in Minuten angibt

.. role:: bluesup

crontab :bluesup:`Update`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. Der Inhalt der Beschreibung von crontab wurde aus referenz/items/standard_attribute/crontab.rst 1:1 kopiert

Es gibt drei verschiedene Parametersätze für ein Crontab Attribut:

.. tabs::

      .. tab:: init
         Das Item wird zum Start von SmarthomeNG aktualisiert und triggert
         dadurch unter Umständen eine zugewiesene Logik:

         .. code-block:: yaml

            crontab: init

         Hier kann auch zusätzlich ein Offset angegeben werden um den
         tatsächlichen Zeitpunkt zu verschieben:

         .. code-block:: yaml

            crontab: init+10    # 10 Sekunden nach Start

      .. tab:: Zeitpunkte

         Das Item soll zu bestimmten Zeitpunkten aktualisiert werden.
         Die Schreibweise ist an Linux Crontab angelehnt, entspricht diesem aber nicht genau.
         Es gibt je nach Parameteranzahl 3 Varianten:

         * ``crontab: <Minute> <Stunde> <Tag> <Wochentag>``
         * ``crontab: <Minute> <Stunde> <Tag> <Monat> <Wochentag>``
         * ``crontab: <Sekunde> <Minute> <Stunde> <Tag> <Monat> <Wochentag>``

         Dabei sind je nach Variante folgende Werte zulässig:

         * Sekunde: ``0`` bis ``59``
         * Minute: ``0`` bis ``59``
         * Stunde: ``0`` bis ``23``
         * Tag: ``1`` bis ``31``
         * Monat: 1 bis 12  oder ``jan`` bis ``dec``
         * Wochentag ``0`` bis ``6``   oder ``mon``, ``tue``, ``wed``, ``thu``, ``fri``, ``sat``, ``sun``

         Alle Parameter müssen durch ein Leerzeichen getrennt sein und innerhalb eines Parameters
         darf kein zusätzliches Leerzeichen vorhanden sein, sonst kann der Parametersatz nicht ausgewertet werden.

         Im folgenden Beispiel wird jeden Tag um 23:59 ein Trigger erzeugt und der Wert 70 gesetzt.

         .. code-block:: yaml

            crontab: 59 23 * * = 70

         Für jede dieser Zeiteinheiten (Minuten, Stunde, Tag, Wochentag) werden
         folgende Muster unterstützt (Beispiel jeweils ohne Anführungszeichen verwenden):

         * eine einzelne Zahl, z.B. ``8`` → immer zur/zum 8. Sekunde/Minute/Stunde/Tag/Wochentag
         * eine Liste von Zahlen, z.B. ``2,8,16`` → immer zur/zum 2., 8. und 16. Sekunde/Minute/Stunde/Tag/Monat/Wochentag
         * ein Wertebereich, z.B. ``1-5`` → immer zwischen dem/der 1. und 5. Sekunde/Minute/Stunde/Tag/Monat/Wochentag
         * einen Interval, z.B. ``\*\/4`` → immer alle 4 Sekunden/Minuten/Stunden/Tage/Wochentage
         * einen Stern, z.B. ``*`` → jede Sekunde/Minute/Stunde/Tag/Monat/Wochentag

      .. tab:: Zeitpunkte bezogen auf Aufgang von Sonne oder Mond 

         Nach dem Muster ``[H:M<](sunrise|sunset|moonrise|moonset)[+|-][offset][<H:M] (<day> <month> <weekday>)`` kann ein Triggerpunkt bezogen 
         auf Sonne oder Mond berechnet werden:

         * ``sunrise`` → immer zum Sonnenaufgang
         * ``sunset`` → immer zum Sonnenuntergang
         * ``sunrise`` und untere Begrenzung → ``06:00<sunrise`` zum Sonnenaufgang, frühestens um 6 Uhr
         * ``sunrise`` und obere Begrenzung →  ``sunrise<09:00`` zum Sonnenaufgang, spätestens um 6 Uhr
         * ``sunset``  und obere und untere Begrenzung → ``17:00<sunset<20:00`` zum Sonnenuntergang, frühestens um 17:00 und spätestens um 20:00 Uhr
         * ``sunrise`` und Minuten-Offset → ``sunrise+10m`` 10 Minuten nach Sonnenaufgang
         * ``sunset``  und Minuten-Offset → ``sunset-10m`` 10 Minuten vor Sonnenuntergang
         * ``sunset`` und Grad-Offset → ``sunset+6`` Sonnenuntergang wenn Sonne 6 Grad am Horizont erreicht

         Soll die erweiterte Variante mit Angabe von Tag, Monat und Wochentag genutzt werden, so müssen immer alle Parameter angegeben werden.
         Die Zusatzangaben müssen dann durch einen Leerschritt getrennt werden.
         Sofern Zusatzangaben vorhanden sind, werden sie UND verknüpft. Das folgende Beispiel würde einen Triggerzeitpunkt festlegen für den nächsten
         Sonnenuntergang der an einem 24. Dezember stattfindet und ein Sonntag ist. (das wäre am 24.Dezember 2023)

         .. code-block:: yaml

            crontab: sunset 24 12 sun

         Das Item soll zu einem bestimmten Sonnenstand aktualisiert werden:

         .. code-block:: yaml

            crontab: sunrise-10m
            crontab: sunset+6
            crontab: sunset


Sämtliche Optionen können in einer \*.yaml durch Listenbildung erstellt werden. Im Admin Interface können die einzelnen Parametersätze durch `` | `` getrennt werden.

Durch Anhängen eines ``= value`` wird der entsprechende Wert ``value`` mitgesendet. 
Das Beispiel setzt den Wert des Items täglich um Mitternacht auf ``20``:


.. code-block:: yaml

   crontab:
      - 0 0 * * = 20
      - sunrise

Möchte man einen Wert im Minutentakt aktualisieren, ist es notwendig den Ausdruck ``* * * *`` unter Anführungszeichen zu setzen.

.. code-block:: yaml

   crontab: '* * * * = 1'

Folgendes Beispiel zeigt wie alle 15 Sekunden der Wert ``42`` gesendet wird:

.. code-block:: yaml

   crontab: '*/15 * * * * * = 42'


enabled
~~~~~~~

``enabled`` kann auf ``False`` gesetzt werden um die Ausführung der Logik auszusetzen
Der Ausführungsstatus der Logik kann über das CLI-Plugin oder das Admin Interface gesetzt werden

prio
~~~~

Setzt die Priorität der Logik im Kontext des Schedulers.
Jeder Wert zwischen ``1`` und ``10`` ist erlaubt mit ``1`` für die höchste Priorität und ``10`` die niedrigste.
Im Normalfall ist eine Angabe der Priorität nicht notwendig, die Vorgabe für alle Logiken ohne
Prioritätsangabe ist ``5``

Andere Parameter
~~~~~~~~~~~~~~~~

Weitere Parameter können innerhalb der Logik mit ``self.parameter_name`` abgefragt werden.
Im ersten Beispiel ist für die vierte definierte Logik ein Parameter ``usage_warning: 500`` angelegt worden.


Grundstruktur einer Logik
-------------------------

Das wichtigste Objekt einer Logik ist das Smarthome Objekt ``sh``.
Über dieses Objekt kann auf alle Items, Plugins und Funktionen von SmartHomeNG
zugegriffen werden.
Um den Wert eines Items abzufragen kann zum Beispiel ``sh.area.itemname()`` verwendet werden.
Um dem gleichen Item einen neuen Wert mitzugeben, kann dieser Wert als Argument
übergeben werden ``sh.area.itemname(new\_value)``

.. code-block:: python

   #!/usr/bin/env python
   # put on the light in the living room, if it is not on
   if not sh.living_room.light():
       sh.living_room.light('on')

Auf Items muß unter Nutzung von Klammern ``()`` zugegridden werden sonst wird eine Ausnahme
erzeugt.

``sh`` kann genutzt werden um über alle Items durchzulaufen:

.. code-block:: python

   for item in sh:
       print item
       for child_item in item:
           print child_item


Bereits geladene Python Module
------------------------------

Innerhalb von Logiken sind folgende Python Module bereits geladen:

-  sys
-  os
-  time
-  datetime
-  ephem
-  random
-  Queue
-  subprocess

Weitere Module können mit ``import <modulname>`` zusätzlich geladen werden.



Vorhandene Objekte und Methoden
-------------------------------

Ausser dem Smarthome Objekt ``sh`` gibt es weitere vordefinierte Objekte und Methoden innerhalb von Logiken

logic
~~~~~

Dieses Objekt bietet Zugriff auf das aktuelle Logik Objekt.
Es ist möglich die Attribute wie ``crontab``, ``cycle``, etc. während der Laufzeit zu ändern.
Die Änderungen werden aber nicht in die ``logic.yaml`` geschrieben und sind nach einem
Neustart von SmartHomeNG verloren.

``logic.alive``
   Der Code ``while logic.alive:`` erzeugt eine Endlos-Schleife die bis zum Beenden
   von SmartHomeNG läuft.

``logic.name``:
   Liefert den Namen der Logik wie in ``logic.yaml`` definiert

``logic.last\_time()``:
   Diese Funktion liefert die letzte Ausführungszeit der Logik vor dem aktuellen Aufruf

``logic.prio``:
   Lesen und setzen der Priorität dieser Logik

``logic.trigger()``:
   Wie ``sh.trigger()``, aber triggert nur die aktuelle Logik. Diese Funktion ist nützlich
   um die Logik zu einem späteren Zeitpunkt (noch einmal) auszuführen

trigger
~~~~~~~

Das Dictionary ``trigger`` liefert Informationen zur Laufzeit der Logik
über das Ereignis, das zum Aufruf der Logik geführt hat.

``trigger['by']``:
   Ursprung

``trigger['source']``
   Quelle

``trigger['dest']``:
   Ziel

``trigger['value']``:
   Wert

logger und sh.log
-----------------

Das ``logger`` Objekt wird zum Generieren von Log Mitteilungen verwendet.
Es stellt fünf unterschiedliche Logging Einstufungen (level) bereit:
``debug``, ``info``, ``warning``, ``error`` und ``critical``.

Die Angabe ``logger.info('42')`` schreibt einen Eintrag ``42`` in den zugehörigen Logger.
Damit Logging Einträge auch in Logs auftauchen, muß in der ``logging.yaml``
eine entsprechende Logging Einstellung vorhanden sein.
Die Grundeinstellung in der ``logging.yaml`` sorgt dafür, das die Einstufungen
``warning``, ``error`` und ``critical`` aufgezeichnet werden.

.. attention::

   Die Zeitangabe in den Log Mitteilungen beziehen sich immer auf die lokal eingestellte Zeit

SmartHomeNG Methoden
--------------------

sh.now und sh.utcnow
~~~~~~~~~~~~~~~~~~~~

Diese beiden Funktionen geben ein ``datetime`` Objekt zurück das die lokale Zeitzone berücksichtigt.
Es ist möglich mit anderen Zeitzonen zu rechnen.
``sh.tzinfo()`` und ``sh.utcinfo()`` geben die lokale Zeitzone und die UTC Zeitzone zurück.

sh.sun
~~~~~~

Dieses Modul gibt Zugriff auf das Sonnenobjekt.
Vorbedingung ist die Definition von Längen- und Breitengrad in ``smarthome.yaml``.

``sh.sun.pos([offset], [degree=False])``
   Gibt die aktuelle Position der Sonne zurück, optional einen Offset in Minuten and und 
   ob der Rückgabe in Grad anstatt in Rad erfolgen soll

   ``azimut, altitude = sh.sun.pos()``:
      liefert die aktuelle Position der Sonne

   ``azimut, altitude = sh.sun.pos(degree=True)``:
       liefert die aktuelle Position der Sonne in Grad

   ``azimut, altitude = sh.sun.pos(30)``
      liefert die Position, die die Sonne in 30 Minuten haben wird

``sh.sun.set([offset])``:
   Gibt den nächsten Sonnenuntergang zurück, optional mit einem Offset in Grad.

   ``sunset = sh.sun.set()``:
      Liefert ein auf UTC basierendes ``datetime`` Objekt mit dem nächsten Sonnenuntergang

   ``sunset_tw = sh.sun.set(-6)``:
      Liefert ein auf UTC basierendes ``datetime`` Objekt mit der Zeitangabe
      des nächsten Sonnenuntergangs zuzüglich der Zeit bis die Dämmerung beendet ist.

``sh.sun.rise([offset])``:
   Gibt analog zu ``set`` den nächsten Sonnenaufgang zurück, optional mit einem Offset in Grad.


sh.moon
~~~~~~~

Neben den drei Funktionen ``pos``, ``set`` und ``rise`` (wie beim Objekt ``sh.sun``) gibt es noch
zwei weitere Funktionen:

``sh.moon.light(offset)``:
   liefert einen Wert im Bereich [0...100] der hellen Oberfläche zur aktuellen Zeit plus einen Offset

``sh.moon.phase(offset)``:
   Liefert die Mondphase als Ganzzahl Wert im Bereich [0...7]:
   0 = Neumond
   4 = Vollmond
   7 = abnehmender Halbmond


Scheduler
---------

sh.scheduler.trigger() / sh.trigger()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Diese globale Funktion triggert eine gegebene Logik unter Angabe ihres Namens

``sh.trigger(name [, by] [, source] [, value] [, dt])`` 
   ``name``:
      der Name der zu triggernden Funktion
      
   ``by``:
      Name einer aufrufenden Logik, der Vorgabewert ist ``Logic``

   ``source``:
      der Grund für das triggern

   ``value`` 
      eine Variable
      
   ``dt``:
      ein datetime Objekt das die Triggerzeit angibt (lokale Zeitzone berücksichtigt)

sh.scheduler.change()
~~~~~~~~~~~~~~~~~~~~~

Diese Methode ändert Optionen zur Laufzeit der Logiken. Beispiel:

``sh.scheduler.change('alarmclock', active=False)`` deaktiviert die Logik ``alarmclock``

Zusätzlich zum ``active`` parameter können auch ``cron`` und ``cycle`` geändert werden.

sh.tools Objekt
---------------

Das ``sh.tools`` Objekt stellt folgende nützliche Funktionen zur Verfügung:

sh.tools.ping()
~~~~~~~~~~~~~~~

Sendet ein Ping an einen Computer und liefert das Ergebnis. Beispiel:

``sh.office.laptop(sh.tools.ping('hostname'))``

setzt das Item ``office.laptop`` entsprechend der Rückmeldung ob ein Ping erfolgreich war oder nicht.

sh.tools.dewpoint()
~~~~~~~~~~~~~~~~~~~

Berechnet den Taupunkt für eine gegebene Temperatur und Feuchtigkeit. Beispiel:

``sh.office.dew(sh.tools.dewpoint(sh.office.temp(), sh.office.hum())``

setzt das Item ``office.dew`` auf das Ergebnis der Taupunktberechnung der Itemwerte von ``office.temp`` und ``office.hum``

sh.tools.fetch\_url()
~~~~~~~~~~~~~~~~~~~~~

Liefert dem Inhalt einer Webseite als String oder ``False`` wenn ein Fehler auftritt.

``sh.tools.fetch_url('https://www.regular.com')`` 

Es ist möglich als Parameter den Benutzernamen und ein Password anzugeben um die Abfrage bei der zu authentifizieren.

``sh.tools.fetch_url('https://www.special.com', 'username', 'password')``

Weiterhin kann ein Parameter für eine Zeitüberschreitung bestimmt werden:

``sh.tools.fetch_url('https://www.regular.com', timeout=4)``

bricht nach 4 Sekunden ohne Ergebnis ab

sh.tools.dt2ts(dt)
~~~~~~~~~~~~~~~~~~

Wandelt ein datetime Objekt in einen Unix Zeitstempel um.

sh.tools.dt2js(dt)
~~~~~~~~~~~~~~~~~~

Wandelt ein datetime Objekt in einen json Zeitstempel um.


sh.tools.rel2abs(temp, hum)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wandelt einen relativen Feuchtigkeitswert in einen absoluten Feuchtigkeitswert um.

Zugriffe auf Items
------------------

Die Nutzung des ``sh`` Objektes für Items wird nicht weitergeführt. Es ist besser das Item API wie folgt zu nutzen:

.. code:: python

   from lib.item import Items
   items = Items.get_instance()

Mit dem ``items`` Objekt können nun die folgenden Funktionen verwendet werden:

items.return_item(path)
~~~~~~~~~~~~~~~~~~~~~~~

Liefert ein Item Objekt für den angegebenen Pfad zurück. Beispiel:

``items.return_item('first_floor.bath')``

items.return_items()
~~~~~~~~~~~~~~~~~~~~

Liefert alle Item Objekte zurück

.. code-block:: python

   for item in items.return_items():
      logger.info(item.id())

items.match_items(regex)
~~~~~~~~~~~~~~~~~~~~~~~~

Liefert alle Item Objekte deren Pfad mit einem regulären Ausdruck gefunden wird und die optional ein bestimmtes Attribut aufweisen.

.. code-block:: python

   for item in items.match_items('*.lights'):     # selects all items ending with 'lights'
       logger.info(item.id())

   for item in items.match_items('*.lights:special'):     # selects all items ending with 'lights' and attribute 'special'
       logger.info(item.id())

items.find_items(configattribute)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Abhängig von ``configattribute`` werden die folgenden Items zurückgegeben:

.. table::

   ======================  =========================================================
   Attribut                Ergebnis
   ======================  =========================================================
   ``attribute``           Nur Items bei denen keine Instanz ID angegeben ist
   ``attribute@``          Items mit oder ohne Instanz ID
   ``attribute@instance``  Items mit einem bestimmten Attribut und einer Instanz ID
   ``@instance``           Items mit einer bestimmten Instanz ID
   ======================  =========================================================


.. code:: python

   for item in items.find_items('my_special_attribute'):
       logger.info(item.id())

find\_children(parentitem, configattribute):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Liefert alle Kind Item Objekte eines Elternitems mit einem gegebenen ``configattribute``.
Die Suche nach dem ``configattribute`` wird genauso durchgeführt wie in ``find_items(configattribute)`` weiter oben.
