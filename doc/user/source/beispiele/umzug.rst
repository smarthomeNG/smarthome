
.. role:: redsup
.. role:: bluesup
.. role:: darkbluesup
.. role:: greensup
.. role:: blacksup

.. index:: SmartHomeNG umziehen; Tipps & Tricks
.. index:: Tipps & Tricks; SmartHomeNG umziehen
.. index:: Umzug, Tipps & Tricks

==================================
SmartHomeNG umziehen :redsup:`Neu`
==================================

Im folgenden wird ein mögliches Vorgehen beschrieben, um SmartHomeNG auf ein neues System (mit neuem Betriebssystem)
umzuziehen.

Diese Beschreibung ist **Work in Progress**

|

.. contents:: Schritte der Installation
   :local:

|

Neues System installieren
=========================

Das neue System wird gemäß der :doc:`Komplettanleitung </installation/komplettanleitung/komplettanleitung>` installiert,
jedoch **ohne den letzten Schritt** (SmartHomeNG als Dienst einrichten).

Linux installieren
------------------

...


SmartHomeNG installieren
------------------------

...


Mosquitto installieren
----------------------

Den MQTT Broker Mosquitto gemäß der :doc:`Komplettanleitung </installation/komplettanleitung/03_mosquitto>` installieren.
Mosquitto braucht nicht konfiguriert zu werden. Die Konfiguration wird in einem späteren Schritt vom alten System
übernommen.


smartVISU installieren
----------------------

Die smartVISU gemäß der :doc:`Komplettanleitung </installation/komplettanleitung/04_smartvisu>` installieren und
konfigurieren.

Falls die Seiten der smartVISU nicht durch das entsprechende SmartHomeNG Plugin generiert werden, müssen die
entsprechenden Dateien aus dem Verzeichnis `/var/www/html` vom alten System auf das neue System übertragen werden.


knxd installieren
-----------------

Den KNX Daemon knxd gemäß der :doc:`Komplettanleitung </installation/komplettanleitung/05_knxd>` installieren.
knxd braucht nicht konfiguriert zu werden. Die Konfiguration wird in einem späteren Schritt vom alten System übernommen.


Onewire installieren
--------------------

Die Onewire Unterstützung gemäß der :doc:`Komplettanleitung </installation/komplettanleitung/06_onewire>` installieren.
Onewire braucht nicht konfiguriert zu werden. Die Konfiguration wird in einem späteren Schritt vom alten System
übernommen.


Samba installieren
------------------

Die SMB Unterstützung Samba gemäß der :doc:`Komplettanleitung </installation/komplettanleitung/07_samba>` installieren.
Als Shares sollten das SmartHomeNG Verzeichnis ``/usr/local/smarthome``, das smartVISU Verzeichnis ``/var/www/html``
und das Home Verzeichnis des Users **smarthome** eingerichtet werden. Das Home Verzeichnis wird als Transfer
Verzeichnis benötigt, um die Konfigurationen der System Dienste zu übertragen.

|

Konfiguration sichern/übertragen
================================

...

Dienst-Konfigurationen übertragen
---------------------------------

Die Konfigurationen der folgen Dienste vom alten auf das neue System übertragen. Da die Konfigurationen nur mit
sudo-Rechen geschrieben werden können, sollten die Dateien (mit Hilfe von Samba) in das Home Verzeichnis kopiert werden
und anschließend in der Shell des neuen Systems mit sudo-Rechten an ihren richtigen Ort verschoben werden.

- Mosquitto
- knxd
- Onewire
- Samba (falls weitere/andere Shares eingerichtet waren)

...

SmartHomeNG Konfiguration sichern
---------------------------------

Mit Hilfe der Admin GUI ein Backup der Konfiguration von SmartHomeNG erstellen.

Kopieren weiterer Daten
-----------------------

Im folgenden werden weitere Daten, die im ``../var`` Verzeichnis von SmartHmeNG gespeichert sind, auf das neue System
übertragen.

Für die folgen Schritte ist es **wichtig**, dass SmartHomeNG weder auf dem alten System, noch auf dem neuen System läuft.
Falls SmartHomeNG auf einem der Systeme läuft, bitte mit ``python3 bin/smarthome.py -s`` SmartHomeNG beenden.

Item cache Verzeichnis kopieren
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

...

database Verzeichnis kopieren
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dieser Schritt ist nur notwendig, wenn SQlite3 als Datenbank verwendet wird.

Bei Verwendung von MySQL müssen die entsprechenden Daten nur übertragen werden, falls MySQL auf dem selben System
läuft wie SmartHomeNG. In diesem Fall bitte die MySQL Dokumentation zu rete ziehen, welche Daten übertragen werden
müssen.

...

executor Verzeichnis kopieren
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

...

knx Verzeichnis kopieren
~~~~~~~~~~~~~~~~~~~~~~~~

...

Logs kopieren
~~~~~~~~~~~~~

...

plugins_cache Verzeichnis kopieren
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Falls das Verzeichnis ``../var/plugings_cache`` existiert und nicht leer ist, sollte der Verzeichnisinhalt inclusive
der Unterverzeichnisse kopiert werden.

...

SmartHomeNG zum Test starten
----------------------------

...

|

Neues System als produktiv einrichten
=====================================

...

|

Restarbeiten
============

...

