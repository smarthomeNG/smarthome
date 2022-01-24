
.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup

.. index:: Struktur; Logiken
.. index:: Logiken; Struktur

=========================
Grundstruktur einer Logik
=========================

Eine Logik besteht aus einem Python Skript sowie einer Reihe von Parametern die den Aufruf (das Triggern) der Logik
steuern. Eine Logik kan während der Laufzeit von SmartHomeNG geladen und entladen werden. Dadurch sind Veränderungen
ein einer Logik möglich, ohne SmartHomeNG neu starten zu müssen.

Das eigentliche Python Skript einer Logik muss im Verzeichnis ``../logics`` der SmartHomeNG Installation abgelegt
werden. Damit die Logik getriggert und ausgeführt wird, muss sie zusätzlich in der Konfigurationsdatei
``../etc/logic.yaml`` konfiguriert werden.

Zur Erstellung einer neuen Logik sollte die Template Datei ``logics/logic.tpl`` als Vorlage genutzt werden.

Die einfachste Methode zu Erstellung einer neuen Logik stellt die Verwendung der Admin GUI dar. Dort kann sowohl
das Skript erstellt werden, as auch die Parameter zur Konfiguration erfasst werden. Die Admin GUI ermöglicht auch
im Anschluß das Laden einer neuen Logik.

Einfache Logiken bestehen nur aus einer Hauptroutine. Es ist jedoch möglich, Funktionen und Klassen innerhalb einer
Logik zu defninieren, um bei umfangreichen Logiken den Code verständlich und wartbar zu halten.

Eine einfache Logik, die das Wohnzimmerlicht einschaltet, wenn sie getriggert wird, kann zum Beispiel so aussehen:

.. code-block:: python

   #!/usr/bin/env python
   # put on the light in the living room, if it is not on
   if not sh.living_room.light():
       sh.living_room.light('on')

Auf Items muß unter Nutzung von Klammern ``()`` zugegriffen werden, da es sich um eine Item Methode handelt und
nicht um eine Variable.

