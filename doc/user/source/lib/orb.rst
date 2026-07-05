lib.orb
-------

.. role:: greensup

.. automodule:: lib.orb
    :members:
    :undoc-members:
    :show-inheritance:


lib.orb Backends :greensup:`Update`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Die Bibliothek `lib.orb` kann intern mit verschiedenen Backends arbeiten:
 
  - ephem (pyephem)
  - skyfield
  - skyfield mit Cache

``ephem`` hat den Vorteil, dass es als native C-Bibliothek sehr schnell ist.
Nachteilig ist, dass es auf manchen Plattformen keine fertigen Pakete gibt
oder die Installation schwierig ist.

``skyfield`` ist als reines Python-Modul trivial zu installieren, muss vor dem
erstmaligen Start eine Datei (17 MB) herunterladen, die bis 2053 gültig bleibt.
Die Berechnungen sind langsamer als ephem.

In der Variante von ``skyfield`` mit Cache werden alle Daten für ein Jahr auf einen Schlag
berechnet und alle folgenden Abfragen, die in das Fenster der 365 Tage fallen,
werden ohne erneute Berechnung zurückgegeben.

``ephem`` ist pro Einzelabfrage mit Abstand am schnellsten (~70-100x schneller
als ungecachted ``skyfield``) - die Cache-Schicht gleicht das nur gegenüber
``skyfield`` selbst aus, nicht gegenüber ``ephem``. Der Cache-Aufbau kostet
konstant ~7ms, unabhängig von der Anzahl der Aufrufe, und amortisiert sich
gegenüber ungecachtem ``skyfield`` bereits nach 3-4 Abfragen. Sequenzielle
Abfragen (das reale Nutzungsmuster von ``Skytime``, Tag fuer Tag vorwärts)
profitieren deutlich stärker vom Cache als zufällige Abfragen, da letztere
gelegentlich einen erneuten Cache-Aufbau auslösen.

.. table:: Benchmark-Ergebnisse: lib.orb Backends (Berlin, 365-Tage-Fenster)

   =========  ============  ============  =============  ======================  =================
   Aufrufe    Modus         ephem (ms)    skyfield (ms)  skyfield-cached Ø (ms)  Cache-Aufbau (ms)
   =========  ============  ============  =============  ======================  =================
   10         zufällig      0,033         2,441          0,788                   6,9
   10         sequenziell   0,029         2,409          0,013                   7,0
   100        zufällig      0,027         1,952          0,149                   7,1
   100        sequenziell   0,025         1,889          0,010                   6,8
   1000       zufällig      0,025         1,863          0,039                   6,8
   1000       sequenziell   0,022         1,859          0,023                   6,9
   =========  ============  ============  =============  ======================  =================

Werte = Durchschnitt pro Aufruf in Millisekunden
außer "Cache-Aufbau" = einmalige Kosten für die erste Abfrage

Die Backends können über den ``etc/smarthome.yaml``-Parameter
`orb_backend: <Wert>` konfiguriert werden. Gültige Werte sind
"ephem", "skyfield" und "skyfield-cache".
