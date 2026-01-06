
.. role:: bluesup
.. role:: greensup
.. role:: redsup

.. index:: Konfiguration; Userfunctions
.. index:: Konfiguration; uf
.. index:: Konfiguration; Functions
.. index:: Userfunctions; Konfiguration

=============
Userfunctions
=============

Ab Version 1.9 von SmartHomeNG ist die Möglichkeit implementiert, benutzerdefinierte Funktionen (Userfunctions) zu
schreiben und in eval Statements sowie in Logiken zu verwenden. Diese Funktionen können zur Laufzeit verändert und
neu geladen werden.

Die Python Dateien mit den Funktionen müssen dazu im Verzeichnis **../functions** abgelegt werden. Es sind normale
Python Dateien, die mehrere Funktionen enthalten können. Als formale Anforderung sind nur Informationen zur Version
und eine kurze Beschreibung des Zwecks der Funktionen dieser Datei anzugeben.

Im folgenden Beispiel wird eine Datei (Funktionssammlung) mit dem Namen **anhalter.py** im Verzeichnis **../functions**
erzeugt:

Die Python Datei sieht folgendermaßen aus:

.. code-block:: python
   :caption: /usr/local/smarthome/functions/anhalter.py

   #!/usr/bin/env python3
   # anhalter.py

   _VERSION     = '0.1.0'
   _DESCRIPTION = 'Per Anhalter durch die Galaxis'

   def zweiundvierzig():

       return 'Die Antwort auf die Frage aller Fragen'


Wenn nach dem Erstellen dieser Datei SmartHomeNG neu gestartet wird, sieht man im Warnings-Log, dass die Datei
importiert wird:

.. code::

   2021-10-14  20:07:08 NOTICE   lib.smarthome        --------------------   Init SmartHomeNG 1.8.2d.b81166c3.develop   --------------------
   2021-10-14  20:07:08 NOTICE   lib.smarthome        Running in Python interpreter 'v3.8.3 final' in virtual environment, from directory /usr/local/shng_dev
   2021-10-14  20:07:08 NOTICE   lib.smarthome         - on Linux-4.9.0-6-amd64-x86_64-with-glibc2.17 (pid=4584)
   2021-10-14  20:07:08 NOTICE   lib.smarthome         - Nutze Feiertage für Land 'DE', Provinz 'HH', 1 benutzerdefinierte(r) Feiertag(e) definiert
   2021-10-14  20:07:11 NOTICE   lib.userfunctions    Userfunctions importiert aus 'anhalter' v0.1.0 - Per Anhalter durch die Galaxis
   2021-10-14  20:08:25 NOTICE   lib.smarthome        --------------------   SmartHomeNG initialization finished   --------------------


Nun kann man die in der Datei definierten Funktionen nutzen. Allen Userfunctions ist beim Aufruf **uf.** (für
userfunctions) gefolgt von dem Namen der Datei voranzustellen. Die Funktion **zweiundvierzig** ist also als
**uf.anhalter.zweiundvierzig()** aufzurufen.  In der Admin GUI im eval Syntax Checker sieht das denn folgendermaßen
aus:

.. image:: assets/uf_eval_checker1.jpg
   :class: screenshot

Analog können die Funtionen in **eval** Attributen in Item Definitionen und in Logiken aufgerufen werden.

Weitere Details zu Userfunctions sind im Abschnitt :doc:`Referenz </referenz/userfunctions/userfunctions>` zu finden.

