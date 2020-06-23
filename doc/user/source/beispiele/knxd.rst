:tocdepth: 1

.. index:: eval_trigger; Beispiele
.. index:: eval; Beispiele

================================
knxd: Hinweise und Konfiguration
================================

Hier finden sich einige Hinweise und Konfigurationsbeispiele für die Anwendung von knxd


Wichtig
=======

Diese Liste soll eine Sammlung von Beispielkonfigurationen verschiedenster Schnittstellen liefern. Sie ersetzt nicht die Dokumentation von knxd auf dem Git-Repository.
Sie ist in Lieferanten und anschließend deren Schnittstellen gegliedert. Bei den Beispielen bitte bei "IP-Adresse" die IP der Schnittstelle / des Routers angeben (bspw. 192.168.178.30).


Beispielkonfigurationen
=======================


busware.de
----------

* **TPUART USB Modul**

* **RTC-Onewire-TPUART Erweiterung für Raspberry Pi (ROT)**


MDT
---

* **SCN-IP000.01:**



* **SCN-IP100.02:**
    *KNXD_OPTS="-u /tmp/eib -i -b ipt:"IP-Adresse"*

* **SCN-USBR.01:**
    *KNXD_OPTS="--eibaddr=1.1.0 --client-addrs=1.1.245:4 --GroupCache --Discovery -Tunnelling --Routing --Server --layer2=usb"* oder kurz: *KNXD_OPTS="-e=1.1.0 -E=1.1.245:4 -c -DTRS -b usb"* wobei --eibaddr=1.1.0... eine freie Busadresse für den knxd ist und --client-addrs=1.1.245:4... den Adressbereich darstellt, den der knx-Server an seine Clients vergibt. Hier von 1.1.245 bis 1.1.249.


Weinzierl
---------

* **KNX USB Interface 311**
* **KNX USB Interface 312**
* **KNX USB Interface 330**
* **KNX IP Interface 730**
    *KNXD_OPTS="-e 0.0.0 -c --no-tunnel-client-queuing -b ipt:IP-Adresse -D -R -T -S"*; Ab KNXD Version 0.14 arbeitet der knxd Prozess mit einer INI Datei. Die Kommandozeilenparameter kann mit einem Tool in das INI Datei Format umwandeln lassen. Beispiel: /usr/lib/knxd_args -e 0.0.1 -E 0.0.2:8 -DTRS --error=3 -t 1023 -i --send-delay=30 ipt:IP-Adresse
* **KNX IP Interface 731**
* **KNX IP Interface 732**
* **KNX IP Interface 740 wireless**
* **KNX IP Router 750**
* **KNX IP Router 751**
* **KNX IP Router 752**
* **KNX IP Linemaster 760**
* **KNX IP Linemaster 762**


ABB
---

* **ABB IP/R2.1**