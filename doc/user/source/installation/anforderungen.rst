:tocdepth: 2

.. index:: Linux, MacOS, Unix, Windows
.. index:: Hardware Anforderungen
.. index:: Software Anforderungen

===============================
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
========

Ein beliebiger Rechner mit x86 or x64 CPU sollte funktionieren, genauso
wie Rechner mit einer ARM CPU wie zum Beispiel ein Raspberry Pi.

Häufig verwendete Hardware ist:

-  Raspberry Pi 3 oder 4 (der letztere wird aufgrund der besseren Hardware **unbedingt empfohlen**)
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
------------------

Eine brauchbare Grundlage um **SmartHomeNG** auszuprobieren ist eine
virtuelle Maschine mit 512MB RAM und zwischen 40GB und 80GB
Plattenplatz.


Raspberry Pi 3 oder 4
---------------------

SmartHomeNG ist auf einem Raspberry Pi 1 oder Pi 2 zwar lauffähig, sollte dann aber nur in einer Minimalkonfiguration
eingesetzt werden.

Vorteile:
~~~~~~~~~

-  recht günstig im Einstieg, auch gebraucht zu bekommen
-  weit verbreitet
-  fertiges
   `Image <https://knx-user-forum.de/forum/supportforen/smarthome-py/979095-smarthomeng-image-file>`__
   von Onkelandy verfügbar

Nachteile:
~~~~~~~~~~

-  Standardmäßig wird bei älteren Raspberry Pis nur eine SD-Karte als Massenspeicher unterstützt -
   Hochwertige SD-Karte wird dringend empfohlen aufgrund der häufigen
   Schreibzyklen (Alternativ ist eine `Auslagerung der
   Dateien <https://knx-user-forum.de/forum/supportforen/smarthome-py/862047-wie-sqlite-auf-schnelleres-medium-verlagern>`__
   auf einen USB-Stick möglich
   Aktuelle Raspbian Versionen unterstützen auch das Booten von USB Geräten, so dass eine HD oder SSD über USB angeschlossen
   werden kann.
-  Empfindlich, braucht eine **sehr stabile Spannungsversorgung**
-  ARM Plattform, es gibt nicht für alles fertige Pakete zum Download


Intel NUC oder vergleichbar
---------------------------

Intel NUC Systeme mit Atom CPUs sind vollkommen ausreichend. Core i3 Prozessoren oder höher werden nicht benötigt.

Vorteile:
~~~~~~~~~

-  verschiedene Hardwareausstattungen möglich
-  niedriger Verbrauch
-  Normale SSD kann verwendet werden (ab 40GB)
-  Installation über Docker-Container leicht möglich


Nachteile:
~~~~~~~~~~

-  teurer

   z.B.:

   - DN2820FYKH0 (Atom CPU)  bei 4GB RAM und 60GB SSD um 250 EUR)
   - NUC 7, Celeron CPU **ohne** RAM und SSD um 150 EUR)
   - NUC 7, Pentium CPU **ohne** RAM und SSD um 200 EUR)
   - NUC 11, Core i3 CPU **ohne** RAM und SSD um 350 EUR)



NAS (z.B. Synology, QNAP)
-------------------------

Vorteile:
~~~~~~~~~

-  zumeist bereits vorhanden
-  Leistung reicht für SmartHomeNG meist aus
-  Installation über Docker-Container leicht möglich


Nachteile:
~~~~~~~~~~

-  Es sind nicht immer alle Pakete verfügbar, abhängig von der Plattform
   und vom Prozessortyp
-  Bei Systemsoftware Updates des NAS werden zusätzliche Einstellungen
   oft wieder überschrieben


Weitere Einplatinencomputer (Banana PI, ODroid, BeagleBone, etc.)
-----------------------------------------------------------------

Vorteile:
~~~~~~~~~

-  recht günstig im Einstieg
-  teilweise mit SATA Anschluss für Festplatte/SSD

Nachteile:
~~~~~~~~~~

-  es hängt sehr von der Plattform ab ob sich Nachteile ergeben


Betriebssysteme
===============

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


.. _python_versionen:

Python Versionen
================

Minimum Python Version
----------------------

Die absolute Minimum Python Version in der SmartHomeNG startet wurde mit SmartHomeNG v1.9 auf **Python 3.7** angehoben,
da Features verwendet werden, die Unter Python 3.6 und davor nicht vorhanden sind und da Python 3.6 im Dezember 2021
End-of-Life (End of security fixes) gegangen ist. Bei einer Neuinstallation wird jedoch empfohlen auf einer der
neueren Python Versionen (3.8, 3.9 oder 3.10) aufzusetzen.

Die aktuelle Version von SmartHomeNG setzt Python der **Version 3.7** oder neuer voraus. Bei Einsatz einer älteren
Python Version, startet SmartHomeNG nicht.


Unterstützte Python Versionen
-----------------------------

Die älteste offiziell unterstützte Python Version für SmartHomeNG Release 1.9.x ist **Python 3.7**. (Diese Version
muss nicht mit der *Minimum Python Version* übereinstimmen.

Die Grundregel nach der sich der Support für Python Versionen richten
soll ist folgende:

**Unterstützt werden die bei Enwicklungsstart einer SmartHomeNG
Version aktuelle Python Version und die zwei Vorgängerversionen.**

.. csv-table:: Zur Verdeutlichung
  :header: "SmartHomeNG", "akt. Python zu Entwicklungsstart", "unterstützte Python Versionen", "minimale Python Version"

  "v1.4",            "Python 3.6",  "Python 3.4, 3.5, 3.6", "Python 3.3"
  "v1.5",            "Python 3.6",  "Python 3.4, 3.5, 3.6", "Python 3.4"
  "v1.6",            "Python 3.7",  "Python 3.5, 3.6, 3.7", "Python 3.4"
  "v1.7",            "Python 3.7",  "Python 3.5, 3.6, 3.7", "Python 3.5"
  "v1.8",            "Python 3.8",  "Python 3.6, 3.7, 3.8", "Python 3.6"
  "v1.9",            "Python 3.9",  "Python 3.7, 3.8, 3.9", "Python 3.7"
  "v1.10",           "Python 3.10", "Python 3.8, 3.9, 3.10", "tbd"

Wenn die eingesetzte Python Version nicht in den unterstützen Python Versionen aufgelistet ist, bedeutet das nicht
automatisch, dass SmartHomeNG mit älteren/neueren Python Versionen nicht funktioniert. Die Entwicklung wird nur
nicht (mehr) mit anderen Versionen getestet.

Die minimale Python Version mit der die jewilige SmartHomeNG Version startet, ist in der Tabelle oben angegeben.
Ältere Python Versionen können nicht genutzt werden, da die SmartHomeNG Version Python Features nutzt, die in
den älteren Versionen noch nicht implementiert waren.

Zudem bekommen ältere Python Versionen keine Bugfixes mehr sondern nur noch Sicherheits-Updates bzw. fallen ganz
als dem Python Lifecycle und erhalten keinerlei Updates mehr. Das Supportende der verschiedenen Python Versionen
ist in der folgenden Tabelle aufgelistet:

.. csv-table:: Aktive Python Releases (wie auf python.org dokumentiert)
  :header: "Python Version", "Maintenance Status", "Erstes Release", "Support Ende"

  "3.6",   "end of life",  "22\. Dezember 2016",   "13\. Dezember 2021"
  "3.7",   "end of life",  "27\. Juni 2018",       "27\. Juni 2023"
  "3.8",   "security",     "14\. Oktober 2019",    "Oktober 2024"
  "3.9",   "security",     "5\. Oktober 2020",     "Oktober 2025"
  "3.10",  "security",     "4\. Oktober 2021",     "Oktober 2026"
  "3.11",  "bugfix",       "24\. Oktober 2022",    "Oktober 2027"
  "3.12",  "prerelease",   "2\. Oktober 2023",     "Oktober 2028"


Python (und PHP) Versionen unter Linux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Linux Distributionen bringen eine installierte Version von Python mit. Die installierte Python Version ist abhängig
von der Linux Distribution. Diese Version sollte nicht mit einer neuen Python Version aktialisiert werden, da einige
Tools der Distribution darauf aufsetzen und dann evtl. nicht mehr funktionieren. Es ist aber möglich zusätzliche
Python Versionen zu installieren (Sies Abschnitt Referenz).

Hier sind einige Beispiele für Linux-System und mitgeliefere Software Versionen:

.. csv-table:: Distributionen und enthaltene Python und PHP Versionen
  :header: "Distribution", "Python Version", "PHP Version"

   "Debian 10 (Buster)",                  "Python 3.7",   "PHP 7.3"
   "Debian 11 (Bullseye)",                "Python 3.9",   "PHP 7.4"
   "Debian 12 (Bookworm)",                "Python 3.11",  "PHP 8.2"
   "Ubuntu 18.04 LTS (Bionic Beaver)",    "Python 3.6",   "PHP 7.2"
   "Ubuntu 20.04 LTS (Focal Fossa)",      "Python 3.8",   "PHP 7.4"
   "Ubuntu 22.04 LTS (Jammy Jellyfish)",  "Python 3.10",  "PHP 8.1"


Aus den Beispielen ist ersichtlich, das Debian Stretch nicht mehr für Neuinstallationen verwendet werden sollte.
Bei Ubuntu sollte man die LTS (Long Term Support) Varianten bevorzugen um nicht andauern mit Systemänderungen konfrontiert zu werden

PHP wird für SmartHomeNG selbst nicht benötigt, ist jedoch eine Voraussetzung für den Einsatz der
`SmartVISU <https://www.smartvisu.de>`_.

