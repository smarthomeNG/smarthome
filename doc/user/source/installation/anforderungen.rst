Hard- u. Software Anforderungen
===============================

Um SmartHomeNG nutzen zu können, braucht es nicht viel. Für jemanden,
der erstmalig SmartHomeNG installiert bietet es sich an zum Kennenlernen
eine virtuelle Maschine zu erstellen und dort als Betriebssystem ein
aktuelles Debian Stretch (>= 9.x) oder Ubuntu (>= 15.x) zu verwenden.

Da SmartHomeNG in den meisten Fällen im Hintergrund laufen wird,
benötigt das System keine grafische Benutzeroberfläche und kann
entsprechend schlank installiert werden.

Hardware
--------

Ein beliebiger Rechner mit x86 or x64 CPU sollte funktionieren, genauso
wie Rechner mit einer ARM CPU wie Raspberry Pi.

Häufig verwendete Hardware ist:

-  Raspberry Pi 2 oder Raspberry Pi 3 (der Letztere wird aufgrund der besseren Hardware **unbedingt empfohlen**)
   besonders wenn die Webinterfaces der Plugins genutzt werden und falls die Visualisierung (smartVISU) auf dem
   selben System betrieben werden sollen. Der Großteil der Nutzer verwendet diese Hardware, siehe
   `Umfrage <https://knx-user-forum.de/forum/supportforen/smarthome-py/1112952-welche-hardware-nutzt-ihr-f%C3%BCr-euer-smarthomeng>`__
-  Intel NUC (Empfohlen für Stabilität und Geschwindigkeit, auch wenn
   diese Rechner mehr Leistung haben, als benötigt wird. Unterstützt
   normale SATA Festplatten, was ein Vorteil gegenüber den Raspberry Pi
   mit ihren SD-Karten ist)
-  ODroid
-  Banana Pi
-  Beagle Bone
-  Virtuelle Maschine, die z.B. auf einem NAS gehostet wird
-  Docker Container

Virtuelle Maschine
~~~~~~~~~~~~~~~~~~

Eine brauchbare Grundlage um **SmartHomeNG** auszuprobieren ist eine
Virtuelle Maschine mit 512MB RAM und zwischen 20GB und 60GB
Plattenplatz.


Raspberry Pi 2 oder 3, jeweils Modell B oder B+
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SmartHomeNG ist auf einem Raspberry Pi 1 zwar lauffähig, sollte dann aber nur in einer Minimalkonfiguration eingesetzt
werden. Das
Vorteile:
^^^^^^^^^

-  recht günstig im Einstieg, auch gebraucht zu bekommen
-  weit verbreitet
-  fertiges
   `Image <https://knx-user-forum.de/forum/supportforen/smarthome-py/979095-smarthomeng-image-file>`__
   von Onkelandy verfügbar

Nachteile:
^^^^^^^^^^

-  Standardmäßig wird nur eine SD-Karte als Massenspeicher unterstützt -
   Hochwertige SD-Karte wird dringend empfohlen aufgrund der häufigen
   Schreibzyklen (Alternativ ist eine `Auslagerung der
   Dateien <https://knx-user-forum.de/forum/supportforen/smarthome-py/862047-wie-sqlite-auf-schnelleres-medium-verlagern>`__
   auf einen USB-Stick möglich
   Aktuelle Raspbian Versionen unterstüten auch das booten von USB Devices, so dass eine HD oder SSD über USB angeschlossen
   werden kann.
-  Empfindlich, braucht eine **sehr stabile Spannungsversorgung**
-  ARM Plattform, es gibt nicht für alles fertige Pakete zum Download


Intel NUC (z.B. DN2820FYKH0) oder vergleichbar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Intel NUC Systeme mit Atom CPUs sind vollkommen ausreichend. Core i3 Prozessoren oder höher werden nicht benötigt.

Vorteile:
^^^^^^^^^

-  verschiedene Hardwareausstattungen möglich
-  niedriger Verbrauch
-  Normale SSD kann verwendet werden (60GB oder 120GB macht Sinn)
-  Installation über Docker-Container leicht möglich


Nachteile:
^^^^^^^^^^

-  teurer (z.B. bei 4GB RAM, 60GB SSD um 250 EUR)


NAS wie z.B. Synology, QNAP
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Vorteile:
^^^^^^^^^

-  zumeist bereits vorhanden
-  Leistung reicht für SmartHomeNG meist aus
-  Installation über Docker-Container leicht möglich


Nachteile:
^^^^^^^^^^

-  Es sind nicht immer alle Pakete verfügbar, abhängig von der Plattform
   und vom Prozessortyp
-  Bei Systemsoftware Updates des NAS werden zusätzliche Einstellungen
   oft wieder überschrieben


Weitere Einplatinencomputer (Banana PI, ODroid, BeagleBone, etc.)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Vorteile:
^^^^^^^^^

-  recht günstig im Einstieg
-  teilweise mit SATA Anschluss für Festplatte/SSD

Nachteile:
^^^^^^^^^^

-  es hängt sehr von der Plattform ab ob sich Nachteile ergeben


Betriebssystem
--------------

Ein beliebiges Linux oder Unix System (mit Shell Zugang um die Requirements und SmartHomeNG zu installieren) sollte
funktionieren.

SmartHomeNG ist mindestens getestet auf Raspbian und Debian Stretch (amd64)

Wenn eine Hardware ohne gepufferte Echtzeituhr (Realtime Clock) genutzt wird, ist der
Einsatz eines NTP Daemons notwendig, um die Zeit über das Internet zu
beziehen. Sonst wird SmartHomeNG aufgrund der fehlenden Zeitinformation
nicht starten.

Einige Libraries in SmartHomeNG benutzen noch Bibliotheken, die ein Unix-artiges Betriebssystem voraussetzen.
Daher läuft SmartHomeNG nicht auf Windows.

Ab SmartHomeNG v1.6 sollte eine Installation unter MacOS möglich sein.


weitere Software
----------------

Die aktuelle Version 1.6 von SmartHomeNG setzt Python der Version 3.5
oder neuer voraus.

Die Grundregel nach der sich der Support für Python Versionen richten
soll ist folgende:

**Unterstützt werden die bei Enwicklungsstart einer SmartHomeNG
Version aktuelle Python Version und die zwei Vorgängerversionen.**

.. csv-table:: Zur Verdeutlichung
  :header: "SmartHomeNG", "akt. Python zu Entwicklungsstart", "unterstützte Python Versionen"

  "v1.2 und davor",  "diverse",     "Python 3.2, 3.3, 3.4"
  "v1.3",            "Python 3.5",  "Python 3.3, 3.4, 3.5"
  "v1.4",            "Python 3.6",  "Python 3.4, 3.5, 3.6"
  "v1.5",            "Python 3.6",  "Python 3.4, 3.5, 3.6"
  "v1.6",            "Python 3.7",  "Python 3.5, 3.6, 3.7"
  "v1.7",            "Python 3.7",  "Python 3.5, 3.6, 3.7"

Das bedeutet nicht automatisch, dass SmartHomeNG auf älteren Versionen
von Python nicht mehr funktioniert. Die Entwicklung wird nur nicht mehr
gegen die älteren Versionen getestet.

