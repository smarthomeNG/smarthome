
.. index:: Komplettanleitung

.. role:: bluesup
.. role:: redsup

=================
Komplettanleitung
=================

Diese Anleitung beschreibt eine komplette Installation von **SmartHomeNG v1.12** auf
einem Linuxsystem mit Debian 13 (trixie).

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
   02_smartvisu
   03_smarthomeng
   04_mosquitto
   05_knxd
   06_onewire
   07_samba
   08_shng_daemon
   09_node_js
   10_esphome

