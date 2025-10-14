
.. index:: Node.js installieren

.. role:: bluesup
.. role:: redsup

=====================
Node.js :redsup:`new`
=====================

Einige Software Pakete, die zusätzlich installiert werden um z.B.  das Zigbee2Mqtt Gateway oder das MobileAlerts
Gateway zu unterstützen, benötigen node.js. Deshalb wird für diejenigen, die es benötigen, im folgenden die
Installation von Node.js und Node Packet Manager (npm) beschrieben.

.. contents:: Schritte der Installation
   :local:

Node.js Installation
====================

Vor der Installation von Node.js und nvm sollte das Betriebssystem auf den aktuellen Stand gebracht werden.
Dazu sollten die System Repositories auf den aktuellen Stand gebracht werden:

.. code-block:: bash

    sudo apt update


Anschließend sollten die Pakete auf die aktuellste Version gebracht werden:

.. code-block:: bash

    sudo apt upgrade

|

Anschließend können mit dem folgenden Kommando node.js und npm installiert werden:

.. code-block:: bash

    sudo apt install nodejs npm -y

|

Anschließend kann die Installation mit den folgenden Kommandos überprüft werden, die die Versionen von node.js und npm
ausgeben:

.. code-block:: bash

    node -v

und

.. code-block:: bash

    npm -v

|

Zigbee2MQTT Gateway installieren
================================

...
Dieser Abschnitt muss noch vervollständigt werden
...

.. code-block:: bash

    # Install pnpm
    wget -qO- https://get.pnpm.io/install.sh | sh -

    # Create a directory for zigbee2mqtt and set your user as owner of it
    sudo mkdir /opt/zigbee2mqtt
    sudo chown -R ${USER}: /opt/zigbee2mqtt

    # Clone Zigbee2MQTT repository
    git clone --depth 1 https://github.com/Koenkk/zigbee2mqtt.git /opt/zigbee2mqtt

    # Install dependencies (as user "smarthome")
    cd /opt/zigbee2mqtt
    pnpm install --frozen-lockfile

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

