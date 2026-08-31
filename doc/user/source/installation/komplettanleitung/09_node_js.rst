
.. index:: Node.js installieren

.. role:: bluesup
.. role:: redsup

=========================
Node.js :bluesup:`Update`
=========================

Einige Software Pakete, die zusätzlich installiert werden um z.B. das Zigbee2Mqtt Gateway, das MobileAlerts
Gateway oder das ``matter`` Plugin zu unterstützen, benötigen node.js. Deshalb wird für diejenigen, die es
benötigen, im folgenden die Installation von Node.js und Node Packet Manager (npm) beschrieben. Es wird dabei
**eine** Node.js Installation für alle drei genutzt - Details dazu im nächsten Abschnitt.

.. contents:: Schritte der Installation
   :local:

Node.js Installation
====================

Die von Debian mitgelieferten ``nodejs``/``npm`` Pakete (Paketquelle ``apt``) hinken der aktuellen Node.js Version
oft weit hinterher - schon auf Debian 12 (Bookworm) sind sie älter als das, was Zigbee2MQTT selbst voraussetzt
(``>=20.x``), und älter als der spezifische Versionsbereich des ``matter`` Plugins (``>=20.19.0 <22.0.0`` oder
``>=22.13.0``). Deshalb wird hier stattdessen die von Node.js selbst betriebene Paketquelle NodeSource genutzt, die
eine aktuelle LTS-Version bereitstellt - das deckt üblicherweise auch die Anforderung des ``matter`` Plugins ab.

Zunächst werden die Voraussetzungen installiert (``curl`` zum Einrichten der Paketquelle, sowie Build-Werkzeuge, die
einige Node.js-Pakete beim Installieren benötigen):

.. code-block:: bash

    sudo apt update
    sudo apt install -y curl git make g++ gcc libsystemd-dev

|

Anschließend wird die NodeSource-Paketquelle eingerichtet und Node.js (inkl. npm) installiert:

.. code-block:: bash

    sudo curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt install -y nodejs

|

Mit den folgenden Kommandos kann die Installation überprüft werden, sie geben die Versionen von node.js und npm aus:

.. code-block:: bash

    node -v

und

.. code-block:: bash

    npm -v

.. note::

   Falls das ``matter`` Plugin genutzt werden soll: Der Versionsbereich ``22.0.0`` bis ausschließlich ``22.13.0``
   wird von matter-server **nicht** unterstützt. Sollte ``node -v`` zufällig eine Version aus diesem schmalen
   Bereich ausgeben, in der NodeSource-Paketquelle auf die nächste bzw. vorherige LTS-Linie wechseln (z.B.
   ``setup_22.x`` oder ``setup_20.x`` statt ``setup_lts.x`` in obigem Kommando).

|

Da Zigbee2MQTT den Paketmanager ``pnpm`` benötigt, wird dieser noch über das in Node.js enthaltene ``corepack``
aktiviert:

.. code-block:: bash

    sudo corepack enable

|

Zigbee2MQTT Gateway installieren
================================

.. code-block:: bash

    # Create a directory for zigbee2mqtt and set your user as owner of it
    sudo mkdir /opt/zigbee2mqtt
    sudo chown -R ${USER}: /opt/zigbee2mqtt

    # Clone Zigbee2MQTT repository
    git clone --depth 1 https://github.com/Koenkk/zigbee2mqtt.git /opt/zigbee2mqtt

    # Install dependencies (as user "smarthome")
    cd /opt/zigbee2mqtt
    pnpm install --frozen-lockfile

|

Zigbee2MQTT Gateway konfigurieren
----------------------------------

Bevor Zigbee2MQTT gestartet wird, muss ein MQTT-Broker (z.B. Mosquitto) auf dem System installiert sein.

Zum ersten Start und zur Konfiguration wird Zigbee2MQTT direkt aus dem Installationsverzeichnis gestartet:

.. code-block:: bash

    cd /opt/zigbee2mqtt
    pnpm start

Anschließend ist unter ``http://<IP-Adresse des Systems>:8080`` die Onboarding-Oberfläche erreichbar, über die die
Verbindung zum MQTT-Broker und der serielle Adapter (Zigbee-Funkstick) konfiguriert werden. Nach abgeschlossener
Konfiguration kann der Prozess mit Ctrl-C wieder beendet werden.

|

Zigbee2MQTT Gateway als Dienst einrichten
------------------------------------------

Um Zigbee2MQTT als Dienst einzurichten, muss die Konfiguration folgendermaßen eingerichtet werden:

Den Texteditor starten mit

.. code-block:: bash

   sudo nano /etc/systemd/system/zigbee2mqtt.service

und den folgenden Text hinein kopieren:

.. code-block:: bash

    [Unit]
    Description=zigbee2mqtt
    After=network.target

    [Service]
    Environment=NODE_ENV=production
    Type=notify
    ExecStart=/usr/bin/node index.js
    WorkingDirectory=/opt/zigbee2mqtt
    StandardOutput=inherit
    StandardError=inherit
    WatchdogSec=10s
    Restart=always
    RestartSec=10s
    User=smarthome

    [Install]
    WantedBy=multi-user.target

Nun muss systemd neu geladen werden, damit der neue Service erkannt wird:

.. code-block:: bash

    sudo systemctl daemon-reload

Mit

.. code-block:: bash

    sudo systemctl start zigbee2mqtt.service

kann der Dienst nun gestartet werden. Damit der Service beim Neustart des Servers gestartet wird, muss noch

.. code-block:: bash

    sudo systemctl enable zigbee2mqtt.service

eingegeben werden.

|

MobileAlerts Proxy installieren
===============================

...

.. code-block:: bash

    # Create a directory for mobile alerts proxy and set your user as owner of it
    sudo mkdir /opt/ma
    sudo chown -R ${USER}: /opt/ma

    # Clone mobile alerts proxy repository
    git clone https://github.com/sarnau/MMMMobileAlerts.git /opt/ma

|

MobileAlerts Proxy konfigurieren
--------------------------------

Im Verzeichnis /opt/ma/maserver eine Datei mit dem Namen config.json anlegen und folgenden Inhalt einfügen

.. code-block:: json

    {
      "localIPv4Address": "<IP-Adresse des SmarthomeNG Systems>",
      "mqtt": "mqtt://<IP-Adresse des Brokers (des SmartHomeNG Systems)>",
      "mqtt_home": "MobileAlerts/",
      "mqtt_username": "<Username für den Broker>",
      "mqtt_password": "<Password für den Broker>",
      "publish_type": "default",
      "sonoffPublish_prefix": null,
      "logfile": "./MobileAlerts.log",
      "logGatewayInfo": true,
      "proxyServerPort": 8080,
      "mobileAlertsCloudForward": true,
      "serverPost": null,
      "serverPostUser": null,
      "serverPostPassword": null,
      "locale": "en-US"
    }

Nun noch die Angaben für ``mqtt``, ``mqtt_username`` und ``mqtt_password`` auf die eigene Umgebung anpassen. Wenn
der Broker auf dem selben System läuft, kann als IP Adresse in ``mqtt`` der Wert ``127.0.0.1`` angegeben werden.

Weitere Informationen zur Konfiguration finden sich hier: https://github.com/sarnau/MMMMobileAlerts/blob/master/maserver/README.md

Nun mit dem Kommando

.. code-block:: bash

    cd /opt/ma/maserver
    npm install

die Abhängigkeiten installieren. Nun kann zum Test mit dem Befehl ``/usr/bin/node mobilealerts.js`` der Proxy gestartet
werden. (mit Ctrl-C wieder beenden)


MobileAlerts Proxy als Dienst einrichten
----------------------------------------

Um den MobileAlerts Proxy als Dienst einzurichten muss die Konfiguration folgendermaßen eingerichtet werden:

Den Texteditor starten mit

.. code-block:: bash

   sudo nano /etc/systemd/system/maserver.service

und den folgenden Text hinein kopieren:

.. code-block:: bash

    [Unit]
    Description=Mobile Alerts Proxy Server
    Documentation=https://github.com/sarnau/MMMMobileAlerts/tree/master/maserver
    After=network-online.target
    StartLimitInterval=200
    StartLimitBurst=5

    [Service]
    Type=simple
    Restart=always
    RestartSec=30

    User=smarthome

    WorkingDirectory=/opt/ma/maserver
    ExecStart=/usr/bin/node /opt/ma/maserver/mobilealerts.js

    StandardOutput=syslog
    StandardError=syslog
    SyslogIdentifier=maserver

    [Install]
    WantedBy=multi-user.target

Nun muss systemd neu geladen werden, damit der neue Service erkannt wird:

.. code-block:: bash

    sudo systemctl daemon-reload

Mit

.. code-block:: bash

    sudo systemctl start maserver.service

kann der Dienst nun gestartet werden. Damit der Service beim Neustart des Servers gestartet wird, muss noch

.. code-block:: bash

    sudo systemctl enable maserver.service

eingegeben werden.

|

Matter Plugin
=============

Das ``matter`` Plugin startet eigene Node.js-Prozesse (matter-server-Sidecar und ggf. Bridge). Die oben installierte
Node.js Version genügt dafür (siehe den Hinweis zum unterstützten Versionsbereich im vorigen Abschnitt). Die
Node.js-Abhängigkeiten des Plugins werden im Sidecar-Verzeichnis des Plugins installiert:

.. code-block:: bash

    cd plugins/matter/sidecar
    npm install

Details zur Konfiguration des Plugins finden sich in dessen eigener Dokumentation (``user_doc.rst``).

