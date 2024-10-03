
.. index:: ESPHome; ESPHome Dashboard Installation

.. role:: bluesup
.. role:: redsup

===============================
ESPHome Dashboard :redsup:`new`
===============================

Wenn ESPHome Devices mit SmartHomeNG verwendet werden sollen, kann es hilfreich sein das ESPHome Dashboard auf dem
Rechner zu installieren, auf dem SmartHomeNG läuft.

Das ESPHome Dashboard verwendet eine recht große Anzahl von Python Packages. Um Konflikte mit Packages/Package-Versionen
die in SmartHomeNG verwendet werden zu vermeiden, wird das ESPHome Dashboard in einem eigenen virtuellen Environment
installiert. Die minimal benötigte Python Version für ESPHome ist zurzeit Python 3.9.

Zur Installation und Verwaltung von ESPHome sind Skripte im ``tools`` Verzeichnis der SmartHomeNG Installation
vorhanden.

Die Installation erfolgt mithilfe des Skripts `esphome_install`.

.. code-block:: bash

    $ esphome_install

Das Skript

  - prüft ob eine für ESPHome benötigte Python Version auf dem System gefunden wird
  - erstellt ein virtuelles Environment mit der entsprechenden Python Version
  - aktiviert das erstellte virtuelle Environment
  - installiert ESPHome in das virtuelle Environment
  - zeigt anschließend die Version von ESPHome an, die installiert wurde
  - und erzeugt das Verseichnis in dem die Konfigurationen für ESPHome gespeichert werden

Die Dateien aus dem Verzeichnis ``/usr/local/smarthome/var/esphome/config`` werden beim Backup und Restore der
SmartHomeNG Konfiguration mit gesichert bzw. zurück restauriert.

|

ESPHome Dashboard starten und testen
====================================

Das ESPHome Dashboard kann im aktuellen Terminal Fenster mit dem Befehl

.. code-block:: bash

    $ esphome_start

gestartet werden und mit Ctrl-C wieder beendet werden.

Nun sollte das Dashboard mit einem Browser (Chrome oder Safari) aufgerufen werden können. Die URL dazu ist

    <Name/IP des SmartHomeNG Systems>:6052

Nun sollte das ESPHome Dashboard angezeigt werden.

Der folgende Screenshot zeigt das Dashboard, welches im lokalen Netzwerk bereits ein ESPHome Device entdeckt
(discovered) hat.

.. image:: ../assets/esphome-dashboard.jpg
   :class: screenshot

|

ESPHome Dashboard als Dienst einrichten
=======================================

Damit das ESPHome Dashboard bei jedem Start des Systems automatisch gestartet wird, muss es als Dienst eingerichtet
werden.

Da ESPHome in ein virtuelles Environment installiert wurde, muss dieses virtuelle Environment zum starten dest
Dienstes genutzt werden. Es muss der Python Interpreter aus diesem virtuellen Environment genutzt werden um
esphome zu betreiben. Dazu muss der folgende Text in die Datei ``/etc/systemd/system/esphome.service`` eingefügt werden:

.. code-block:: bash

    [Unit]
    Description=ESPHome-dashboard daemon
    After=network-online.target

    [Service]
    Type=simple
    ExecStart=/usr/local/smarthome/tools/esphome_start
    User=smarthome
    Restart=on-failure
    RestartSec=30
    TimeoutStartSec=900
    RestartForceExitStatus=5
    Environment="PATH=/usr/local/smarthome/venvs/py_esphome/bin:/usr/local/sbin:/usr$

    [Install]
    WantedBy=default.target

|

Starten des Dienstes
====================

Der so vorbereitete Dienst kann über den **systemctl** Befehl gestartet
werden.

.. code-block:: bash

   sudo systemctl start esphome.service

Wenn alles ok ist, kann der Autostart aktiviert werden:

.. code-block:: bash

   sudo systemctl enable esphome.service

Bei Systemstart wird nun das ESPHome Dashboard automatisch gestartet.

Um den Dienst wieder auszuschalten und den Neustart bei Systemstart zu
verhindern nutzt man:

.. code-block:: bash

   sudo systemctl disable esphome.service

Um zu sehen, ob das ESPHome Dashboard läuft, genügt ein

.. code-block:: bash

   systemctl status esphome.service

Läuft es noch nicht und man möchte sozusagen manuell starten reicht ein:

.. code-block:: bash

   sudo systemctl start esphome.service

Ein Neustart des Dashboards würde mit

.. code-block:: bash

   sudo systemctl restart esphome.service

funktionieren, ein Stop von SmartHomeNG entsprechend

.. code-block:: bash

   sudo systemctl stop esphome.service

