

Astronomie (Sonne und Mond)
===========================

sh.sun
------

Dieses Objekt bietet Zugriff auf Parameter der Sonne. Um dieses Objekt zu verwenden, ist es erforderlich,
den Breitengrad (latitude, z.B. lat: 53.5989481) und den Längengrad (longitude z.B. lon: 10.0459898),
sowie die Höhe über dem Meeresspiegel (elevation z.B.: elev: 20) in der Datei **../etc/smarthome.yaml** anzugeben.


sh.sun.pos()
~~~~~~~~~~~~

Die Methode ``sh.sun.pos()`` liefert die Position der Sonne und hat zwei optionale Parameter:

- Der erste Parameter ``offset`` ist der zeitliche Offset zu jetzt in Minuten
- Der zweite Parameter ``degree`` gibt an, ob das Ergebnis im Bogenmaß oder in Grad erfolgen soll.

.. code-block:: python
   :caption: Beispiele zur Sonnenstandsberechnung

   # sh.sun.pos(offset)   hierbei gibt offset die Differenz in Zeit-Minuten zur aktuellen Zeit an

   azimut, altitude = sh.sun.pos()   # liefert die aktuelle Position der Sonne, Ergbnis im Bogenmaß
   azimut, altitude = sh.sun.pos(30) # liefert die Position, welche die Sonne in 30 Minuten haben wird im Bogenmaß

   azimut, altitude = sh.sun.pos(degree=True) # liefert die aktuelle Position der Sonne in Grad
   azimut, altitude = sh.sun.pos(-45, True)   # liefert die Position, welche die Sonne vor 45 Minuten hatte in Grad


sh.sun.set()
~~~~~~~~~~~~

Die Methode ``sh.sun.set()`` hat liefert den Zeitpunkt des nächsten Sonnenuntergangs und hat einen optionale Parameter:

- Der Parameter ``offset`` ist der Offset zum Sonnenuntergang in Grad
  (eine negative Zahl gibt an, wieviel Grad die Sonne unter dem Horizont stehen soll)

Das Ergebnis ist ein auf UTC basierendes ``datetime`` Objekt

.. code-block:: python
   :caption: Beispiele zur Sonnenuntergangsberechnung

   # sh.sun.set(offset)   hierbei gibt offset die Differenz in Grad zum nächsten Sonnenuntergang an

   sunset = sh.sun.set()      # liefert den utc-basierten Zeitpunkt des nächsten Sonnenuntergangs
   sunset_tw = sh.sun.set(-6) # liefert den utc-basierten Zeitpunkt zu dem die Sonne 6° unter dem Horizont
                              # steht. (Ende der bürgerlichen Abenddämmerung)


sh.sun.rise()
~~~~~~~~~~~~~

Die Methode ``sh.sun.rise()`` hat liefert den Zeitpunkt des nächsten Sonnenuntergangs und hat einen optionale Parameter:

- Der Parameter ``offset`` ist der Offset zum Sonnenuntergang in Grad
  (eine negative Zahl gibt an, wieviel Grad die Sonne unter dem Horizont stehen soll)

Das Ergebnis ist ein auf UTC basierendes ``datetime`` Objekt

.. code-block:: python
   :caption: Beispiele zur Sonnenaufgangsberechnung

   # sh.sun.rise(offset)  hierbei gibt offset die Differenz in Grad zum nächsten Sonnenaufganges an

   sunrise = sh.sun.rise()      # liefert den utc-basierten Zeitpunkt des nächsten Sonnenaufganges
   sunrise_tw = sh.sun.rise(-6) # liefert den utc-basierten Zeitpunkt zu dem die Sonne wieder 6° unter
                                # dem Horizont steht. (Beginn der nächsten bürgerlichen Morgendämmerung)


sh.moon
-------

Neben den drei Funktionen ``pos``, ``set`` und ``rise`` (wie beim Objekt ``sh.sun``) gibt es noch
zwei weitere Funktionen:

Neben den drei Funktionen ``sh.moon.pos()``, ``sh.moon.set()`` und ``sh.moon.rise()`` (analog zum ``sh.sun`` Objekt)
stehen zwei weitere Funktionen (``sh.moon.light()`` und ``sh.moon.phase()``) zur Verfügung.


sh.moon.pos()
~~~~~~~~~~~~~

Die Methode ``sh.moon.pos()`` liefert die Position des Mondes und hat zwei optionale Parameter:

- Der erste Parameter ``offset`` ist der zeitliche Offset zu jetzt in Minuten
- Der zweite Parameter ``degree`` gibt an, ob das Ergebnis im Bogenmaß oder in Grad erfolgen soll.

.. code-block:: python
   :caption: Beispiele zur Mondstandsberechnung

   # sh.moon.pos(offset)   hierbei gibt offset die Differenz in Zeit-Minuten zur aktuellen Zeit an

   azimut, altitude = sh.moon.pos()   # liefert die aktuelle Position des Mondes, Ergbnis im Bogenmaß
   azimut, altitude = sh.moon.pos(30) # liefert die Position, welche der Mond in 30 Minuten haben wird im Bogenmaß

   azimut, altitude = sh.moon.pos(degree=True) # liefert die aktuelle Position des Mondes in Grad
   azimut, altitude = sh.moon.pos(-45, True)   # liefert die Position, welche der Mond vor 45 Minuten hatte in Grad


sh.moon.set()
~~~~~~~~~~~~~

Die Methode ``sh.moon.set()`` hat liefert den Zeitpunkt des nächsten Monduntergangs und hat einen optionale Parameter:

- Der Parameter ``offset`` ist der Offset zum Monduntergang in Grad
  (eine negative Zahl gibt an, wieviel Grad der Mond unter dem Horizont stehen soll)

Das Ergebnis ist ein auf UTC basierendes ``datetime`` Objekt

.. code-block:: python
   :caption: Beispiele zur Monduntergangsberechnung

   # sh.moon.set(offset)   hierbei gibt offset die Differenz in Grad zum nächsten Monduntergang an

   moonset = sh.moon.set()      # liefert den utc-basierten Zeitpunkt des nächsten Monduntergangs
   moonset_tw = sh.moon.set(-6) # liefert den utc-basierten Zeitpunkt zu dem der Mond 6° unter dem Horizont steht


sh.moon.rise()
~~~~~~~~~~~~~~

Die Methode ``sh.moon.rise()`` hat liefert den Zeitpunkt des nächsten Monduntergangs und hat einen optionale Parameter:

- Der Parameter ``offset`` ist der Offset zum Monduntergang in Grad
  (eine negative Zahl gibt an, wieviel Grad der Mond unter dem Horizont stehen soll)

Das Ergebnis ist ein auf UTC basierendes ``datetime`` Objekt

.. code-block:: python
   :caption: Beispiele zur Mondaufgangsberechnung

   # sh.moon.rise(offset)  hierbei gibt offset die Differenz in Grad zum nächsten Mondaufganges an

   moonrise = sh.moon.rise()      # liefert den utc-basierten Zeitpunkt des nächsten Mondaufganges
   moonrise_tw = sh.moon.rise(-6) # liefert den utc-basierten Zeitpunkt zu dem der Mond wieder 6° unter
                                  # dem Horizont steht.


sh.moon.light()
~~~~~~~~~~~~~~~

``sh.moon.light(offset)`` liefert einen Wert von 0 bis 100 der beleuchteten Fläche zur aktuellen Zeit + Offset.


sh.moon.phase()
~~~~~~~~~~~~~~~

``sh.moon.phase(offset)`` gibt die Mondphase als ganze Zahl (0 bis 7) zurück,
wobei: 0 = Neumond, 4 = Vollmond, 6 = abnehmender Halbmond

