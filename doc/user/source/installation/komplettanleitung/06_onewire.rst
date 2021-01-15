
.. index:: Onewire installieren

.. role:: bluesup
.. role:: redsup

====================
Onewire installieren
====================

.. contents:: Schritte der Installation
   :local:


zusätzliche Linux Pakete installieren
=====================================

SmartHomeNG realisiert den Zugriff auf einen OneWire Bus über ein Plugin.
Das Plugin nutzt dazu das Paket ``owserver``.
Die dazu benötigten Komponenten werden installiert mit:

.. code-block:: bash

   sudo apt-get -y install owhttpd owserver


Owserver konfigurieren
======================

Nach der Paketinstallation von ``owserver`` muß die Konfigurationsdatei ``/etc/owfs.conf``
noch auf den verwendeten Adapter angepasst werden:

.. code-block:: bash

   sudo nano /etc/owfs.conf

Eine Beispieldatei für einen USB-Adapter wie den weit verbreiteten
**DS9490R** kann z.B. so aussehen:

.. code-block:: ini

   ######################## SOURCES ########################
   #
   # With this setup, any client (but owserver) uses owserver on the
   # local machine...
   ! server: server = 127.0.0.1:4304
   #
   # ...and owserver uses the real hardware, by default fake devices
   # This part must be changed on real installation
   #server: FAKE = DS18S20,DS2405
   #
   # USB device: DS9490
   server: usb = all
   #
   # Serial port: DS9097
   #server: device = /dev/ttyS1
   #
   # owserver tcp address
   #server: server = 192.168.10.1:3131
   #
   # random simulated device
   #server: FAKE = DS18S20,DS2405
   #
   ######################### OWFS ##########################
   #
   mountpoint = /mnt/1wire
   allow_other
   #
   ####################### OWHTTPD #########################
   http: port = 2121
   ####################### OWFTPD ##########################
   ftp: port = 2120
   ####################### OWSERVER ########################
   server: port = 127.0.0.1:4304

Wichtig dabei ist vor allem das in der Config nicht **localhost** steht
sondern **127.0.0.1** explizit angegeben wird. Dadurch wird eine Bindung
des Ports **4304** an eine normale IP erreicht und nicht an IPv6 wie es
sonst der Fall wäre. Mit tcp6 wiederum könnte das Smarthome.py derzeit
nichts anfangen.

Bei der Installation werden ``owserver`` und ``owhttp`` automatisch gestartet.
Nach der Konfigurationsänderung wird der ``owserver`` neu gestartet:

.. code-block:: bash

   sudo systemctl restart owserver


SmartHomeNG Plugin konfigurieren
================================

Die Konfiguration des Plugins erfolgt über das Admin Interface (Siehe Abschnitt Konfiguration).

Alternativ kann die Konfiguration des Onewire-Plugin natürlich auch über die Konfigurationsdatei
**../etc/plugin.yaml** erfolgen. Dazu muss dort noch folgendes eingefügt werden:

.. code-block:: yaml

    ow:
      plugin_name: onewire
      host: 127.0.0.1
      port: 4304
      cycle: 60  # update every minute

