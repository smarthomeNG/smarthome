
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

Neues System installieren
=========================

Das neue System wird gemäß der :doc:`Komplettanleitung </installation/komplettanleitung>` installiert,
jedoch **ohne den letzten Schritt** (SmartHomeNG als Dienst einrichten).

|

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

...


Konfiguration sichern/übertragen
================================

...

|

Neues System als produktiv einrichten
=====================================

...

|

Restarbeiten
============

...

