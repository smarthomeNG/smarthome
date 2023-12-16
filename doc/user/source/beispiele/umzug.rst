
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

Das Debian Linux gemäß der :doc:`Komplettanleitung </installation/komplettanleitung/01_debian>` installieren und
konfigurieren.


SmartHomeNG installieren
------------------------

SmartHomeNG gemäß der :doc:`Komplettanleitung </installation/komplettanleitung/02_smarthomeng>` installieren und
rudimentär konfigurieren. SmartHomeNG sollte dabei, wie in der Anleitung beschrieben, gestartet worden sein, damit
die im folgenden benötigten Verzeichnisse angelegt werden.


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
Als Shares sollten das SmartHomeNG Verzeichnis ``/usr/local/smarthome`` und das smartVISU Verzeichnis ``/var/www/html``
eingerichtet werden.

|

Konfiguration sichern/übertragen
================================

Nachdem Samba konfiguriert wurde, können auf einem Desktop Rechner die SmartHomeNG Verzeichnisse des alten und des
neuen Systems gemountet werden. Im Anschluß können die Dateien einfach vom alten auf das neue System kopiert werden.


Dienst-Konfigurationen übertragen
---------------------------------

Im folgenden ist beschrieben, wie die Konfigurationen der Dienste vom alten System auf das neue System übertragen
werden.

Da die Konfigurationsdateien der Dienste eventuell nur mit sudo Rechten gelesen werden können, sollten sie auf dem
alten System zuerst in ein Transfer-Verzeichnis kopiert werden. Am besten dazu auf dem alten und auf dem neuen System
ein Verzeichnis ``transfer`` Verzeichnis im SmartHomeNG Verzeichnis ``usr/local/smarthome`` anlegen.

Da die Konfigurationen der Dienste alle nur mit sudo-Rechten geschrieben werden können, werden die Dateien nachdem sie
auf das neue System übertragen wurden, mit sudo-Rechten aus dem Transfer Verzeichnis an ihren richtigen Ort verschoben.

Mosquitto
~~~~~~~~~

Für die Mosquitto Konfiguration muss das Verzeichnis ``/etc/mosquitto`` mit allen Unterverzeichnissen übertragen werden.


knxd
~~~~

Für die knxd Konfiguration muss die Datei ``/etc/knxd.conf`` übertragen werden.


Onewire
~~~~~~~

Für die Onewire Konfiguration muss die Datei ``/etc/owfs.conf`` übertragen werden.


Samba
~~~~~

Falls auf dem alten System weitere/andere Shares eingerichtet waren, als auf dem neuen System bisher eingerichtet sind,
muss die Datei ``/etc/samba/smb.conf`` übertragen werden.


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

Um die Cache Werte der Items zu übertragen, muss der Inhalt der Verzeichnisses ``/usr/local/smarthome/var/cache`` des
alten Systems in das gleichnamige Verzeichnis auf dem neuen System übertragen werden.


database Verzeichnis kopieren
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dieser Schritt ist nur notwendig, wenn SQlite3 als Datenbank verwendet wird.

Bei Verwendung von MySQL müssen die entsprechenden Daten nur übertragen werden, falls MySQL auf dem selben System
läuft wie SmartHomeNG. In diesem Fall bitte die MySQL Dokumentation zu rate ziehen, welche Daten übertragen werden
müssen.

Um die Datenbank zu übertragen, muss der Inhalt der Verzeichnisses ``/usr/local/smarthome/var/db`` des
alten Systems in das gleichnamige Verzeichnis auf dem neuen System übertragen werden.

Dieser Vorgang dauert einige Zeit, da die Datenbank Datei mehrere Gigabyte groß sein kann.


executor Verzeichnis kopieren
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Falls das executor Plugin genutzt wird, existiert ein Verzeichnis ``/usr/local/smarthome/var/executor_scripts``.
Der Inhalt dieses Verzeichnisses muss kopiert werden, damit die gespeicherten Skripte auf dem neuen System zur
Verfügung stehen.


knx Verzeichnis kopieren
~~~~~~~~~~~~~~~~~~~~~~~~

Um die Daten des knx Plugins zu übertragen, muss der Inhalt der Verzeichnisses ``/usr/local/smarthome/var/knx`` des
alten Systems in das gleichnamige Verzeichnis auf dem neuen System übertragen werden.


Logs kopieren
~~~~~~~~~~~~~

Um die Logdateien zu übertragen, muss der Inhalt des Verzeichisses ``/usr/local/smarthome/var/log`` des
alten Systems in das gleichnamige Verzeichnis auf dem neuen System übertragen werden.


plugins_cache Verzeichnis kopieren
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Falls das Verzeichnis ``/usr/local/smarthome/var/plugings_cache`` existiert und nicht leer ist, sollte der
Verzeichnisinhalt inclusive der Unterverzeichnisse kopiert werden.


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

Transfer Verzeichnis löschen
----------------------------

...

SmartHomeNG als Dienst einrichten
---------------------------------

...
