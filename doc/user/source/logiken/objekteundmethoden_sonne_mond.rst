Zeit, Sonne und Mond
====================


sh.sun
------

Dieses Objekt bietet Zugriff auf Parameter der Sonne. Um dieses Objekt zu verwenden, ist es
erforderlich, den Breitengrad (latitude, z.B. lat: 53.5989481) und den
Längengrad (longitude z.B. lon: 10.0459898),
sowie die Höhe über dem Meeresspiegel (elevation z.B.: elev: 20)
in der Datei **../etc/smarthome.yaml** anzugeben.

.. code-block:: python
   :caption: Beispiele zur Sonnenstandsberechnung

   # sh.sun.pos(offset)   hierbei gibt offset die Differenz in Zeit-Minuten zur aktuellen Zeit an
   azimut, altitude = sh.sun.pos()   # liefert die aktuelle Position der Sonne
   azimut, altitude = sh.sun.pos(30) # liefert die Position, welche die Sonne in 30 Minuten haben wird

   # sh.sun.set(offset)   hierbei gibt offset die Differenz in Grad zum nächsten Sonnenuntergang an
   sunset = sh.sun.set()      # liefert den utc-basierten Zeitpunkt des nächsten Sonnenuntergangs
   sunset_tw = sh.sun.set(-6) # liefert den utc-basierten Zeitpunkt zu dem die Sonne 6° unter dem Horizont
                              # steht. (Ende der bürgerlichen Abenddämmerung)

   # sh.sun.rise(offset)  hierbei gibt offset die Differenz in Grad zum nächsten Sonnenaufganges an
   sunrise = sh.sun.rise()      # liefert den utc-basierten Zeitpunkt des nächsten Sonnenaufganges
   sunrise_tw = sh.sun.rise(-6) # liefert den utc-basierten Zeitpunkt zu dem die Sonne wieder 6° unter
                              # dem Horizont steht. (Beginn der nächsten bürgerlichen Morgendämmerung)


sh.moon
-------

Neben den drei Funktionen (sh.moon.pos, sh.moon.set, sh.moon.rise) stehen zwei weitere zur Verfügung.

**sh.moon.light(offset)** liefert einen Wert von 0 bis 100 der beleuchteten Fläche zur aktuellen Zeit + Offset.
**sh.moon.phase(offset)** gibt die Mondphase als ganze Zahl (0 bis 7) zurück, wobei: 0 = Neumond, 4 = Vollmond, 6 = abnehmender Halbmond



