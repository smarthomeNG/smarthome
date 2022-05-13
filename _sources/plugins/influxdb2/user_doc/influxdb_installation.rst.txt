
.. index:: InfluxDB; Installation

InfluxDB Installation
=====================

Hier wird kurz beschrieben, wie die InfluxDB Software auf einem Debian Linux System installiert wird.
Die vollständige Installationsdokumentation ist auf der
`Website von Influxdata <https://docs.influxdata.com/influxdb/v2.1/install/>`__ zu finden.
Dort wird auch beschrieben, wie InfluxDB auf anderen Betriebssystemen zu installieren ist.

Die folgende Beschreibung installiert die Version 2.1.1 der InfluxDB Software für x86 Prozessoren (amd64).

.. code-block:: bash

   wget https://dl.influxdata.com/influxdb/releases/influxdb2-2.1.1-amd64.deb
   sudo dpkg -i influxdb2-2.1.1-amd64.deb

Das Installationspaket installiert auch einen Service, der InfluxDB bei einem Systemstart startet. Ohne zum
jetzigen Zeitpunkt das System neu starten zu müssen, kann InfluxDB mit dem folgenden Kommando gestartet werden:

.. code-block:: bash

   sudo service influxdb start

Ab jetzt kann mit einem Browser auf InfluxDB zugegriffen werden. Dazu im Browser als
Url ``http://<IP des Servers>:8086`` eingeben.

Falls das Commandline Interface von InfluxDB genutzt werden soll, kann dieses folgendermaßen installiert werden:

.. code-block:: bash

   wget https://dl.influxdata.com/influxdb/releases/influxdb2-client-2.2.0-linux-amd64.tar.gz
   tar xvzf path/to/influxdb2-client-2.2.0-linux-amd64.tar.gz

   sudo cp influxdb2-client-2.2.0-linux-amd64/influx /usr/local/bin/


...
