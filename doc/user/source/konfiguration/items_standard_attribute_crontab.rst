.. index:: Standard-Attribute; crontab
.. index:: crontab

crontab
=======

Das Item wird zum Start von SmarthomeNG aktualisiert und triggert
dadurch unter Umständen eine zugewiesene Logik:

.. code-block:: yaml

   crontab: init

Hier kann auch zusätzlich ein Offset angegeben werden um den
tatsächlichen Zeitpunkt zu verschieben:

.. code-block:: yaml

   crontab: init+10    # 10 Sekunden nach Start

Das Item soll zu bestimmten Zeitpunkten aktualisiert werden:

.. code-block:: yaml

   crontab: <Minute> <Stunde> <Tag> <Wochentag>

Für jede dieser Zeiteinheiten (Minuten, Stunde, Tag, Wochentag) werden
folgende Muster unterstützt (Beispiel jeweils ohne Anführungszeichen verwenden):

* eine einzelne Zahl, z.B. "8" (immer zur/zum 8. Minuten/Stunde/Tag/Wochentag)
* eine Liste von Zahlen, z.B. "0,8,16" (immer zur/zum 0., 8. und 16. Minute/Stunde/Tag/Wochentag)
* ein Wertebereich, z.B. "0-8" (immer zwischen dem/der 0. und 8. Minute/Stunde/Tag/Wochentag)
* einen Interval, z.B. "\*\/4" (immer alle 4 Minuten/Stunden/Tage/Wochetag)
* einen Stern, z.B. "*" (jede Minuten/Stunde/Tag/Wochentag)

Die numerische Angabe des Wochentages wird mit 0=Montag und 6=Sonntag
abgebildet!

Ausser diesem Muster wird noch ein weiteres Muster in Bezug auf den
Sonnenauf- sowie Sonnenuntergang unterstützt, z.B:

* den Wert “sunrise”, z.B. ``crontab = sunrise`` (immer zum Sonnenaufgang)
* den Wert “sunset”, z.B. ``crontab = sunset`` (immer zum Sonnenuntergang)
* den Wert (z.B. “sunrise”) und Limitierung vorher, z.B.
  ``crontab = 06:00<sunrise`` (zum Sonnenaufgang, frühestens um 6 Uhr)
* den Wert (z.B. “sunrise”) und Limitierung nachher, z.B.
  ``crontab = sunrise<06:00`` (zum Sonnenaufgang, spätestens um 6 Uhr)
* den Werte (z.B. “sunset”) und Limitierung vorher, z.B.
  ``crontab = 18:00<sunset`` (zum Sonnenuntergang, frühestens um 18 Uhr)
* den Werte (z.B. “sunset”) und Limitierung nachher, z.B.
  ``crontab = sunset<20:00`` (zum Sonnenaufgang, spätestens um 20 Uhr)
* den Wert (z.B. “sunset”) und beider Limitierungen, z.B.
  ``crontab = 17:00<sunset<20:00`` (zum Sonnenuntergang, frühestens um
  17:00 und spätestens um 20:00 Uhr)
* den Wert (z.B. “sunrise”) und Minuten-Offset, z.B. ``crontab = sunrise+10m`` (10 Minuten nach
  Sonnenaufgang)
* den Wert (z.B. “sunset”) und Minuten-Offset, z.B.
  ``crontab = sunset-10m`` (10 Minuten vor Sonnenuntergang)
* den Wert (z.B. “sunset”) und Grad-Offset, z.B. ``crontab = sunset+6``
  (Sonnenuntergang wenn Sonne 6 Grad am Horizont (Altitude der Sonne)
  erreicht)

Das Item soll zu einem bestimmten Sonnenstand aktualisiert werden:

.. code-block:: yaml

   crontab: sunrise-10m
   crontab: sunset+6
   crontab: sunset

Sämtliche Optionen können in \*.conf durch ‘\|’ kombiniert werden oder in
einer \*.yaml durch Listenbildung erstellt. Durch Anhängen eines weiteren
‘=’ wird der aufzurufenden Logik der entsprechende Wert mitgesendet. Das
Beispiel setzt den Wert des Items täglich um Mitternacht auf 20:


.. code-block:: yaml

   crontab:
     - 0 0 \* \* = 20
     - sunrise
