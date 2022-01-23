
.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup

.. index:: Struktur; Logiken
.. index:: Logiken; Struktur

=======================================================
Grundstruktur einer Logik :bluesup:`under construction`
=======================================================

Das eigentliche Python Skript einer Logik muss im Verzeichnis ``../logics`` der SmartHomeNG Installation abgelegt
werden. Damit die Logiken getriggert und ausgeführt werden, müssen sie zusätzlich in der Konfigurationsdatei
``../etc/logic.yaml`` konfiguriert werden.

> - - - - - - - - - -

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


