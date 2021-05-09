:tocdepth: 2

.. index:: Linux, MacOS, Unix, Windows

Hard- u. Software Anforderungen
===============================

Um SmartHomeNG nutzen zu können, braucht es nicht viel. Für jemanden,
der erstmalig SmartHomeNG installiert bietet es sich an zum Kennenlernen
eine virtuelle Maschine zu erstellen und dort als Betriebssystem ein
aktuelles Debian Buster (>= 10.x) oder Ubuntu (>= 18.04) zu verwenden.

Da SmartHomeNG in den meisten Fällen im Hintergrund laufen wird,
benötigt das System keine grafische Benutzeroberfläche und kann
entsprechend schlank installiert werden.

Hardware
--------

Ein beliebiger Rechner mit x86 or x64 CPU sollte funktionieren, genauso
wie Rechner mit einer ARM CPU wie Raspberry Pi.

Häufig verwendete Hardware ist:

-  Raspberry Pi 2, 3 oder 4 (der letztere wird aufgrund der besseren Hardware **unbedingt empfohlen**)
   besonders wenn die Webinterfaces der Plugins genutzt werden und falls die Visualisierung (smartVISU) auf dem
   selben System betrieben werden sollen. Der Großteil der Nutzer verwendet diese Hardware, siehe
   `Umfrage <https://knx-user-forum.de/forum/supportforen/smarthome-py/1112952-welche-hardware-nutzt-ihr-f%C3%BCr-euer-smarthomeng>`__
   Die verschiedenen Raspberry Pi Varianten wurden in diesem 
   `Geschwindigkeitstest <https://magpi.raspberrypi.org/articles/raspberry-pi-4-specs-benchmarks>`_ 
   miteinander verglichen.
-  Intel NUC (Empfohlen für Stabilität und Geschwindigkeit, auch wenn
   diese Rechner mehr Leistung haben, als benötigt wird. Unterstützt
   normale SATA Festplatten/SSD, was ein Vorteil gegenüber den Raspberry Pi
   mit ihren SD-Karten ist)
-  ODroid
-  Banana Pi
-  Beagle Bone
-  Virtuelle Maschine, die z.B. auf einem NAS gehostet wird
-  Docker Container

Virtuelle Maschine
~~~~~~~~~~~~~~~~~~

Eine brauchbare Grundlage um **SmartHomeNG** auszuprobieren ist eine
virtuelle Maschine mit 512MB RAM und zwischen 40GB und 80GB
Plattenplatz.


Raspberry Pi 2, 3 oder 4
~~~~~~~~~~~~~~~~~~~~~~~~

SmartHomeNG ist auf einem Raspberry Pi 1 zwar lauffähig, sollte dann aber nur in einer Minimalkonfiguration eingesetzt
werden.

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
   Aktuelle Raspbian Versionen unterstützen auch das Booten von USB Geräten, so dass eine HD oder SSD über USB angeschlossen
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
-  Normale SSD kann verwendet werden (ab 40GB)
-  Installation über Docker-Container leicht möglich


Nachteile:
^^^^^^^^^^

-  teurer (z.B. bei 4GB RAM und 60GB SSD um 250 EUR)


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


Betriebssysteme
---------------

Ein beliebiges **Linux** oder **Unix System** (mit Shell Zugang um die Requirements und SmartHomeNG zu installieren)
sollte funktionieren.

SmartHomeNG ist mindestens getestet auf Raspbian und Debian Buster (amd64)

Wenn eine Hardware ohne gepufferte Echtzeituhr (Realtime Clock) genutzt wird, ist der
Einsatz eines NTP Daemons notwendig, um die Zeit über das Internet zu
beziehen. Sonst wird SmartHomeNG aufgrund der fehlenden Zeitinformation
nicht starten.

Einige Libraries in SmartHomeNG benutzen Bibliotheken, die ein Unix-artiges Betriebssystem voraussetzen
oder spezielle Hardware erwarten.

Ab SmartHomeNG v1.6 sollte eine Installation unter **MacOS** (BSD Unix) möglich sein.

Ab SmartHomeNG v1.8.2 sollte eine Installation unter **Windows** möglich sein.


Python Versionen
----------------

Die aktuelle Version von SmartHomeNG setzt Python der Version 3.6 oder neuer voraus.

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
  "v1.8",            "Python 3.8",  "Python 3.6, 3.7, 3.8"
  "v1.9",            "Python 3.9",  "Python 3.7, 3.8, 3.9"
  "v1.10",           "Python 3.10", "Python 3.8, 3.9, 3.10"

Das bedeutet nicht automatisch, dass SmartHomeNG mit älteren Python Versionen nicht mehr funktioniert,
die Entwicklung wird nur nicht mehr mit älteren Versionen getestet. Zudem bekommen ältere Python Versionen keine
Bugfixes mehr sondern nur noch Sicherheits-Updates.

Python 3.6 jedoch hat eine Reihe sehr interessanter Features und Verbesserungen gebracht, die nur dann in SmartHomeNG
genutzt werden können, wenn sichergestellt ist dass SmartHomeNG mindestens unter Python 3.6 gestartet wurde. Daher
wurde für SmartHomeNG v1.8 die **Absolute Minimum Python Version** auf 3.6 angehoben.

Beispiele für Linux-System und mitgeliefere Versionen:

   * Debian 9 (Stretch) beinhaltet Python 3.5 und PHP 7.0
   * Debian 10 (Buster) beinhaltet Python 3.7 und PHP 7.3
   * Debian 11 (Bullseye) wird voraussichtlich Python 3.9 und PHP 7.4 beinhalten
   * Ubuntu 18.04 LTS (Bionic Beaver) beinhaltet Python 3.6 und PHP 7.2
   * Ubuntu 20.04 LTS (Focal Fossa) beinhaltet Python 3.8 und PHP 7.4

Aus den Beispielen ist ersichtlich, das Debian Stretch nicht mehr für Neuinstallationen verwendet werden sollte.
Bei Ubuntu sollte man die LTS (Long Term Support) Varianten bevorzugen um nicht andauern mit Systemänderungen konfrontiert zu werden

PHP wird für SmartHomeNG selbst nicht benötigt, ist jedoch eine Voraussetzung für den Einsatz der
`SmartVISU <https://www.smartvisu.de>`_.

