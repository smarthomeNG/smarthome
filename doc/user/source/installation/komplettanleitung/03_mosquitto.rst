
.. index:: MQTT Broker installieren
.. index:: Mosquitto installieren

.. role:: bluesup
.. role:: redsup

========================
MQTT Broker installieren
========================

Ab Version 1.7 wird MQTT direkt vom Core von SmartHomeMG unterstützt. Um MQTT zu nutzen, muss ein Broker verwendet werden,
mit dem die MQTT Clients kommunizieren. Wenn im Netzwerk noch kein Broker installiert ist, kann auf dem Rechner auf dem
SmartHomeNG installiert wird, auch ein Broker installiert werden.

.. contents:: Schritte der Installation
   :local:


Mosquitto installieren
======================

Ein populärer Open Source Broker ist **Eclipse Mosquitto™**. Die Installation dieses Brokers wird im folgenden beschrieben.
Weitergehende Informationen zu dem Broker sind unter https://mosquitto.org zu finden.

Mosquitto ist bei Debian seit dem Stretch-Release im Standard Repository enthalten und kann daher einfach mit
dem folgenden Kommando installiert werden:

.. code-block:: bash

   sudo apt-get install mosquitto


Anschließend kann mit dem Befehl

.. code-block:: bash

   systemctl status mosquitto


überprüft werden, ob der Broker läuft. Wenn der Service läuft, sieht man eine ähnliche Ausgabe wie folgende:

.. code-Block:: bash

    ● mosquitto.service - LSB: mosquitto MQTT v3.1 message broker
       Loaded: loaded (/etc/init.d/mosquitto; generated; vendor preset: enabled)
       Active: active (running) since Wed 2018-05-30 13:39:47 CEST; 5min ago
         Docs: man:systemd-sysv-generator(8)
       CGroup: /system.slice/mosquitto.service
               └─3548 /usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf

    Mai 30 13:39:47 SmartHomeNG systemd[1]: Starting LSB: mosquitto MQTT v3.1 message
    Mai 30 13:39:47 SmartHomeNG mosquitto[3543]: Starting network daemon:: mosquitto
    Mai 30 13:39:47 SmartHomeNG systemd[1]: Started LSB: mosquitto MQTT v3.1 message


Der Service kann dann mit den folgenden Befehlen gestartet, gestoppt und neu gestartet werden:


.. code-Block:: bash

   systemctl start mosquitto
   systemctl stop mosquitto
   systemctl restart mosquitto


Mosquitto als Service einrichten
================================

Falls die Abfrage des Status einen Fehler liefert:

.. code-Block:: bash

    Unit mosquitto.service could not be found


muss noch eine Startup-Datei für **systemd** erstellt werden.

Zum Einrichten den Texteditor starten mit:

.. code-Block:: bash

    sudo nano /etc/systemd/system/mosquitto.service

und folgenden Text hineinkopieren:

.. code-block:: bash

    [Unit]
    Description=mosquitto MQTT message broker
    After=network.target

    [Service]
    ExecStart=/usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf
    WorkingDirectory=/etc/mosquitto
    User=mosquitto
    Restart=always
    TimeoutStartSec=90

    [Install]
    WantedBy=multi-user.target


Der Servicee kann dann wie oben beschrieben gestartet werden.


Mosquitto konfigurieren
=======================

Nach der Installation ist der Broker ohne weitere Konfiguration nutzbar. Allerdings kann
jeder Client den Broker nutzen, da der Client sich nicht authentifizieren muss.

Wenn eine Authentifizierung gewünscht wird, muss Mosquitto entsprechend der Dokumentation
(https://mosquitto.org/man/mosquitto-conf-5.html) konfiguriert und neu gestartet werden.

Gleiches gilt, wenn zusätzlich zum MQTT Protokoll (auf Port 1883) auch noch Websockets genutzt
werden sollen.

.. note::

   SmartHomeNG nutzt zur Kommunikation mit dem Broker nur das MQTT Protokoll.

