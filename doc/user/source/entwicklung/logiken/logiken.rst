
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

crontab
~~~~~~~

Ähnlich wie Unix crontab mit den folgenden Optionen:

* ``crontab: init``
   Ausführung der Logik beim Start von SmartHomeNG

* ``crontab: Minute Stunde Tag Wochentag``
   Siehe Beschreibung von Unix crontab und Online Generatoren für Details

   - Minute: Wert im Bereich [0...59], oder Komma getrennte Liste, oder * (jede Minute)
   - Stunde: Wert im Bereich [0...23], oder Komma getrennte Liste, oder * (jede Stunde)
   - Tag: Wert im Bereich [0...28], oder Komma getrennte Liste, oder * (jeden Tag)
     **Achtung**: Derzeit keine Werte für Tage größer 28 nutzen
   - Wochentag: Wert im Bereich [0...6] (0 = Montag), oder Komma getrennte Liste, oder * (jeden Wochentag)

``crontab: sunrise``
   Startet die Logik bei Sonnenaufgang

``crontab: sunset``
   Startet die Logik bei Sonnenuntergang

   Für Sonnenaufgang oder Sonnenuntergang können folgende Erweiterungen genutzt werden:

   - Ein Offsetwert zum Horizont in Grad.
     Beispiel ``crontab: sunset-6``
     Dazu muss in der smarthome.yaml Längen und Breitengrad eingestellt sein.
   - Ein Offsetwert in Minuten der durch ein angehängtes m gekennzeichnet wird
     Beispiel: ``crontab: sunset-10m``
   - Eine Beschränkung der Zeit für die Ausführung

   .. code-block:: yaml
      :caption:  Konfiguration mit YAML Syntax

       crontab: '17:00<sunset'        # Sonnenuntergang, aber nicht vor 17:00 Uhr (lokaler Zeit)
       crontab: sunset<20:00          # Sonnenuntergang, aber nicht nach 20:00 (lokaler Zeit)
       crontab: '17:00<sunset<20:00'  # Sonnenuntergang, zwischen 17:00 Uhr und 20:00 Uhr
       crontab: '15 * * * = 50'       # Ruft die Logik mit dem Wert ``50`` auf, also nach Aufruf der Logik hat ``trigger['value']`` den Wert ``50``

Mehrere crontab Einträge können auch als Liste angegeben werden:

.. code-block:: yaml
   :caption:  Konfiguration mit YAML Syntax

   crontab:
     - init = start
     - sunrise-2
     - '0 5 * *'

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
