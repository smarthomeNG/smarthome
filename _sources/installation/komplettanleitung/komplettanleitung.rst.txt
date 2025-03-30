
.. index:: Komplettanleitung

.. role:: bluesup
.. role:: redsup

=================
Komplettanleitung
=================

Diese Anleitung beschreibt eine komplette Installation von **SmartHomeNG v1.10** auf
einem Linuxsystem mit Debian 12 (bookworm).

Zusätzlich wird die Installation folgender weiterer Pakete beschrieben:

- Mosquitto (MQTT-Broker).
- SmartVISU (Visualisierung für SmartHomeNG und andere Systeme),
- knxd (KNX daemon),
- Onewire (Günstiges Bussystem zur Bereitstellung von Messdaten wie Temperatur, Luftfeuchte, etc.) und
- Samba (Dateifreigabe für Windows Clients)

Es bietet sich an die allererste Installation einfach in einer virtuellen Maschine
(VirtualBox, VMWare, etc.) durchzuführen um den Ablauf einmal gesehen zu haben.

.. toctree::
   :maxdepth: 5
   :hidden:

   01_debian
   02_smarthomeng
   03_mosquitto
   04_smartvisu
   05_knxd
   06_onewire
   07_samba
   08_shng_daemon
   09_esphome

