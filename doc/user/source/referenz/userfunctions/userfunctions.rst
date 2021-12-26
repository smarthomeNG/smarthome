
.. role:: bluesup
.. role:: greensup
.. role:: redsup

===========================
Userfunctions :redsup:`Neu`
===========================

Ab Version 1.9 von SmartHomeNG ist die Möglichkeit implementiert, benutzerdefinierte Funktionen (Userfunctions) zu
schreiben und in eval Statements sowie in Logiken zu verwenden.


Erstellung und Speicherung
==========================

Die Python Dateien mit den Funktionen müssen dazu im Verzeichnis **../functions** abgelegt werden. Es sind normale
Python Dateien, die mehrere Funktionen enthalten können. Als formale Anforderung sind nur Informationen zur Version
und eine kurze Beschreibung des Zwecks der Funktionen dieser Datei anzugeben. Diese müssen in der Python Datei
als globale Variablen **_VERSION** und **_DESCRIPTION** definiert werden.

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


Verwendung der Admin GUI
------------------------

In der Admin GUI steht ein Editor zum erstellen und bearbeiten von Userfunctions zur Verfügung. Dieser findet sich
unter **Dienste/User-Funktionen**.

.. image:: /referenz/assets/uf_editor1.jpg
   :class: screenshot



Initialisierung der Userfunctions
=================================

Wenn nach dem Erstellen dieser Datei SmartHomeNG neu gestartet wird, sieht man im Warnings-Log, dass die Datei
importiert wird:

.. code::

   2021-10-14  20:07:08 NOTICE   lib.smarthome        --------------------   Init SmartHomeNG 1.8.2d.b81166c3.develop   --------------------
   2021-10-14  20:07:08 NOTICE   lib.smarthome        Running in Python interpreter 'v3.8.3 final' in virtual environment, from directory /usr/local/shng_dev
   2021-10-14  20:07:08 NOTICE   lib.smarthome         - on Linux-4.9.0-6-amd64-x86_64-with-glibc2.17 (pid=4584)
   2021-10-14  20:07:08 NOTICE   lib.smarthome         - Nutze Feiertage für Land 'DE', Provinz 'HH', 1 benutzerdefinierte(r) Feiertag(e) definiert
   2021-10-14  20:07:11 NOTICE   lib.userfunctions    Importing userfunctions uf.anhalter v0.1.0 - Per Anhalter durch die Galaxis
   2021-10-14  20:08:25 NOTICE   lib.smarthome        --------------------   SmartHomeNG initialization finished   --------------------


Nun kann man die in der Datei definierten Funktionen nutzen.

Aufruf einer Userfunction
=========================

Allen Userfunctions ist beim Aufruf **uf.** (für userfunctions) gefolgt von dem Namen der Datei voranzustellen. Die
Funktion **zweiundvierzig** ist also als ``uf.anhalter.zweiundvierzig()`` aufzurufen. In der Admin GUI im
**eval Syntax Checker** sieht das denn folgendermaßen aus:

.. image:: /referenz/assets/uf_eval_checker1.jpg
   :class: screenshot

Analog können die Funtionen in **eval** Attributen in Item Definitionen und in Logiken aufgerufen werden.


Logging aus Userfunctions
=========================

Als Hilfestellung bei der Erstellung und dem Testen von Funktionen kann aus den Funktionen heraus geloggt werden.
Dazu muss das Logging Modul importiert und ein Logger definiert werden:

.. code-block:: python
   :caption: /usr/local/smarthome/functions/anhalter.py

   #!/usr/bin/env python3
   # anhalter.py

   import logging
   _logger = logging.getLogger(__name__)

   _VERSION     = '0.1.0'
   _DESCRIPTION = 'Per Anhalter durch die Galaxis'

   def zweiundvierzig():

       _logger.warning("Die Userfunction 'zweiundvierzig' wurde aufgerufen")
       return 'Die Antwort auf die Frage aller Fragen'


Der Name des Loggers im obigen Beispiel ist **functions.anhalter**:

.. code::

   2021-10-15  10:08:14 NOTICE   lib.smarthome        --------------------   SmartHomeNG initialization finished   --------------------
   2021-10-15  10:12:29 WARNING  functions.anhalter   Die Userfunction 'zweiundvierzig' wurde aufgerufen


Damit aus Funktionen ein Logging mit Leveln kleiner als WARNING erfolgt, muss in der Logging Konfiguration
../etc/logging.yaml ein entsprechender Logger für **functions** ergänzt werden:

.. code:: yaml

   loggers:
       functions:
           handlers: [shng_details_file]
           level: INFO


Nutzung von Item Werten
=======================

Für die Berechungen in den Userfunctions werden häufig die aktuellen Werte von Items benötigt. Um diese Werte in
den Userfunctions zu erhalten, gibt es zwei Möglichkeiten.


Übergabe als Parameter
----------------------

Damit die Funktionen unabhängig von der Item Struktur der aktuellen SmartHomeNG sind, sollten Item Werte als
Parameter übergeben werden. Dadurch können Dateien mit Userfunctions einfach an andere Anwender weiter gegeben
werden:

.. code:: yaml

   test_item:
       type: num
       eval_trigger: env.location.sun_position.elevation.degrees
       eval: uf.lamellen_oeffnung_ost( sh.env.location.sun_position.elevation.degrees() )


Die Userfunction dazu kann z.B. folgendermaßen aussehen:

.. code-block:: python
   :caption: /usr/local/smarthome/functions/beschattung.py

   _VERSION     = '0.1.0'
   _DESCRIPTION = 'Hilfsfunktionen zur Beschattungssteuerung per Stateengine'

   def lamellen_oeffnung_ost(elevation):
       """
       Bestimmung der Stellung der Ost Lamellen im Wohnbereich

       :param elevation: Sonnen Position (Höhe in Grad)
       :return: Schließung der Lamellen in Prozent
       """

       return 87 if elevation <= 6.6 else 84 if elevation <= 11.5 else 81 if elevation <= 14.8 else 78 if elevation <= 19.4 else 74 if elevation <= 16.1 else 70 if elevation <= 28 else 65 if elevation <= 30.9 else 60 if elevation <= 33.9 else 54


durch das Smarthome-Objekt
--------------------------

Falls eine größere Zahl an Item Werten übergeben werden soll und eine Weitergabe an andere Anwender nicht geplant ist,
kann die Userfunction so geschrieben werden, dass sie die Item Struktur kennt und voraussetzt.

Statt mehrere Items als einzelne Parameter zu übergeben, braucht dann nur das Smarthome-Objekt übergeben zu werden.
Das folgende Beispiel zeigt beide Varianten (übergabe der Item Werte und Referenzierung über das Smarthome-Objekt).

.. code:: yaml

   test_item:
       # Übergabe der Item Werte
       type: num
       eval_trigger:
         - env.location.sun_position.azimut.degrees
         - env.location.sun_position.elevation.degrees
       eval: uf.lamellen_oeffnung_sued( sh.env.location.sun_position.azimut.degrees(), sh.env.location.sun_position.elevation.degrees() )


.. code-block:: python
   :caption: /usr/local/smarthome/functions/beschattung.py

   _VERSION     = '0.2.0'
   _DESCRIPTION = 'Hilfsfunktionen zur Beschattungssteuerung per Stateengine'

   def lamellen_oeffnung_sued(azimut, elevation):
       """
       Bestimmung der Stellung der Ost Lamellen im Wohnbereich

       :param azimut: Sonnen Position (Himmelsrichtung in Grad)
       :param elevation: Sonnen Position (Höhe in Grad)
       :return: Schließung der Lamellen in Prozent
       """

    return 60 if (azimut>=230 and elevation>0.0 ) else 63 if (azimut>=214 and elevation>0.0 )else 72 if elevation<=7.0 else 69 if elevation<=24.0 else 66


kann das Smarthome-Objekt übergeben werden. Das würde dann folgendermaßen aussehen:

.. code:: yaml

   test_item:
       # Übergabe des Smarthome-Objektes sh
       type: num
       eval_trigger:
         - env.location.sun_position.azimut.degrees
         - env.location.sun_position.elevation.degrees
       eval: uf.lamellen_oeffnung_sued(sh)


Die Userfunction dazu kann z.B. folgendermaßen aussehen:

.. code-block:: python
   :caption: /usr/local/smarthome/functions/beschattung.py

   _VERSION     = '0.2.1'
   _DESCRIPTION = 'Hilfsfunktionen zur Beschattungssteuerung per Stateengine'

   def lamellen_oeffnung_sued(sh):
       """
       Bestimmung der Stellung der Ost Lamellen im Wohnbereich

       :param sh: smarthome objekt
       :return: Schließung der Lamellen in Prozent
       """

       azimut    = sh.env.location.sun_position.azimut.degrees()
       elevation = sh.env.location.sun_position.elevation.degrees()

    return 60 if (azimut>=230 and elevation>0.0 ) else 63 if (azimut>=214 and elevation>0.0 )else 72 if elevation<=7.0 else 69 if elevation<=24.0 else 66


Reload von Userfunctions
========================

Benutzerdefinierte Funktionen können während der Laufzeit von SmartHomeNG verändert und neu geladen werden. Dabei
können einzelne Module mit Userfunctions neu geladen werden oder alle Module mit Usewrfunctions auf einmal.

In der Admin GUI erfolgt das auf der Seite mit dem Editor für Userfunctions. Alternativ können die Module über
den **eval Syntax Checker** neu geladen werden. Um die Datei des obigen Beispiels neu zu laden, muss
man **uf.reload('anhalter')** eingeben und **Prüfen** klicken.

Man kann auch alle benutzerdefinierte Dateien neu laden, indem man **uf.reload_all()** eingibt und **Prüfen** klickt.

