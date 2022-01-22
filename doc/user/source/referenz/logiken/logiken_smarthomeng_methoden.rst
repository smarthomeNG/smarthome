:tocdepth: 5

.. index:: SmartHomeNG Methoden; Logiken
.. index:: Logiken; SmartHomeNG Methoden


====================
SmartHomeNG Methoden
====================

Datum und Uhrzeit
=================

sh.now und sh.utcnow
~~~~~~~~~~~~~~~~~~~~

Diese beiden Funktionen geben ein ``datetime`` Objekt zurück das die lokale Zeitzone berücksichtigt.
Es ist möglich mit anderen Zeitzonen zu rechnen.
``sh.tzinfo()`` und ``sh.utcinfo()`` geben die lokale Zeitzone und die UTC Zeitzone zurück.

shtime
------

. . .


Astronomie
==========

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
=========

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
===============

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

