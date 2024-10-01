
.. index:: ESPHome; ESPHome Dashboard Installation

.. role:: bluesup
.. role:: redsup

===============================
ESPHome Dashboard :redsup:`new`
===============================

Wenn ESPHome Devices mit SmartHomeNG verwendet werden sollen, kann es hilfreich sein das ESPHome Dashboard auf dem
Rechner zu installieren, auf dem SmartHomeNG läuft.

Im folgenden wird beschrieben, wie das ESPHome Dashboard auf dem SmartHomeNG System installiert werden sollte.

|

Virtuelles Environment erstellen
================================

Das ESPHome Dashboard verwendet eine recht große Anzahl von Python Packages. Um Konflikte mit Packages/Package-Versionen
die in SmartHomeNG verwendet werden zu vermeiden, sollte das ESPHome Dashboard in einem eigenen virtuellen Environment
laufen. Die minimal benötigte Python Version für das ESPHome Dashboard ist zurzeit Python 3.10.

Das virtuelle Environemnt hierfür wird mit dem folgenden Befehl angelegt:

.. code-block:: bash

    $ make_venv 3.10 esphome

|

ESPHome Dashboard installieren
==============================

Das ESPHome Dashboard muss im laufenden virtuellen Environment installiert werden. Das virtuelle Environment muss dazu
vorher mit dem folgenden Befehl aktiviert werden:

.. code-block:: bash

    $ source act epshome

Nun kann das ESPHome Dashboard mit den folgenden Befehlen angelegt werden:

.. code-block:: bash

    (py_esphome) $ pip3 install wheel
    (py_esphome) $ pip3 install esphome

Nun sollte das ESPHome Dashboard installiert sein. Mit dem folgenden Befehl kann die Installation überprüft und
die installierte Version angezeigt werden:

.. code-block:: bash

    (py_esphome) $ esphome version
    Version: 2024.9.2

Nun muss noch das Verzeichnis angelegt werden, in dem die Konfigurationen für ESPHome gespeichert werden.

.. code-block:: bash

    (py_esphome) $ mkdir /usr/local/smarthome/var/esphome
    (py_esphome) $ mkdir /usr/local/smarthome/var/esphome/config

Die Dateien aus dem Verzeichnis ``/usr/local/smarthome/var/esphome/config`` werden beim Backup und Restore der
Konfiguration von SmartHomeNG mit gesichert bzw. zurück gespielt.

|

ESPHome Dashboard starten und testen
====================================

Innerhalb des virtuellen Environments wird das Dashboard mit dem folgenden Befehl gestartet:

.. code-block:: bash

    (py_esphome) $ cd /Users/Martin/ESPHome
    (py_esphome) $ esphome dashboard /usr/local/smarthome/var/esphome/config

Nun sollte das Dashboard mit einem Browser (Chrome oder Safari) aufgerufen werden können. Die URL dazu ist

    <Name/ip des SmartHomeNG Systems>:6052

Nun sollte das ESPHome Dashboard angezeigt werden.

Der folgende Screenshot zeigt das Dashboard, welches im lokalen Netzwerk bereits ein ESPHome Device entdeckt
(discovered) hat.

.. image:: /_static/img/esphome-dashboard.jpg
   :class: screenshot

|

ESPHome Dashboard als Dienst einrichten
=======================================

Damit das ESPHome Dashboard bei jedem Start des Systems automatisch gestartet wird, muss es als Dienst eingerichtet
werden.

...

.. code-block:: bash

   [Unit]
   Description=ESPHome dashboard daemon
   After=network.target

   [Service]
   Type=forking
   ExecStart=/usr/local/smarthome/venvs/py_esphome/bin/esphome dashboard /usr/local/smarthome/var/esphome/config
   WorkingDirectory=/usr/local/smarthome
   User=smarthome
   PIDFile=/usr/local/smarthome/var/run/esphome.pid
   Restart=on-failure
   TimeoutStartSec=900
   RestartForceExitStatus=5

   [Install]
   WantedBy=default.target


...
