
.. index:: knxd installieren

.. role:: bluesup
.. role:: redsup

=================
knxd installieren
=================

Der knxd implementiert Zugriffe auf verschiedenste Schnittstellen zum KNX Bus (z.B. IP-Router, IP-Schnittstelle,
USB-Schnittstelle, etc.) und bietet dafür eine dokumentierte Softwareschnittstelle für Programme an.

SmartHomeNG nutzt den knxd über seine tcp Schnittstelle um Daten auf den KNX Bus zu schreiben oder zu lesen.
Wer KNX nicht verwendet, kann diesen Installationsschritt überspringen.

.. contents:: Schritte der Installation
   :local:


knxd unter Debian installieren
==============================

Ab Debian 10 (Buster) ist knxd als Installationspaket in der Distribution enthalten.

Das fertige knxd Paket kann mit folgenden Kommandos installiert werden:


.. code-block:: bash

    sudo apt-get update
    sudo apt-get install knxd knxd-tools

knxd konfigurieren
==================

Als nächstes muss die Konfiguration des knxd für die zu verwendende
Schnittstelle angepasst werden. Dazu wird bei Systemen mit systemd die
Datei **/etc/knxd.conf** bearbeitet:

.. code-block:: bash

    sudo nano /etc/knxd.conf

Die Originalzeile ``KNXD_OPTS="-e 0.0.1 -E 0.0.2:8 -u /tmp/eib -b ip:"`` 
am besten mit einem ``#`` zum Kommentar machen und in der Zeile darunter dann die
gewählten Parameter eintragen.

Details zu Schnittstellen finden sich auf der `Github-Seite vom knxd <https://github.com/knxd/knxd>`__.
Der Parameter **-c** stellt den knxd so ein, das er einen Cache nutzt.
Danach folgen die Optionen für die Verwendung der eingesetzten physikalischen Schnittstelle:

-  IP Schnittstelle: ``KNXD_OPTS="-e 0.0.1 -E 0.0.2:8 -c -b ipt:<IP der knx Schnittstelle>"``
-  IP Router: ``KNXD_OPTS="-e 0.0.1 -E 0.0.2:8 -c -b ip:<Multicast IP>"``
-  TP UARTS: ``KNXD_OPTS="-e 0.0.1 -E 0.0.2:8 -c -b tpuarts:/dev/knx"``
-  USB-Interface: Bitte `Wiki zum knxd <https://github.com/knxd/knxd/wiki>`__ konsultieren.


Es kann sein, das bei ``KNXD_OPTS`` hinter dem **-c** bei einigen Interfaces noch ein ``--send-delay=30`` eingefügt
werden muß um Telegrammverlust bei hohen Lasten zu minimieren. Die 30 bedeutet dabei eine zusätzliche Wartezeit
von 30msec. Es wird damit zwischen den Paketen eine kleine Pause eingelegt um ein überfahren der Schnittstelle
zu vermeiden. Der Parameter **--no-tunnel-client-queuing** ist obsolet und sollte nicht mehr eingesetzt werden.

.. note::

   Einige IP Schnittstellen (besonders ältere) unterstützen nur einen Tunnel. Das bedeutet, dass z.B. ETS und
   knxd (SmartHomeNG) nicht gleichzeitig an solchen Schnittstellen betrieben werden können.

knxd testen
============

Nachdem knxd installiert, konfiguriert und der Dienst gestartet ist, kann mit folgendem Kommando geprüft
werden, ob eine funktionsfähige Verbindung zum KNX Bus besteht. Dazu das folgende Kommando eingeben:

.. code-block:: bash

    knxtool groupsocketlisten ip:localhost

Damit protokolliert knxtool mit, welche Pakete auf dem Bus übertragen werden. Die Ausgabe sieht dann so
ähnlich aus:

.. code-block::

    Write from 1.1.202 to 3/3/6: 01 43
    Write from 1.1.203 to 2/6/25: 02 2E
    Write from 1.1.204 to 2/6/32: 00 0B
    Write from 1.1.203 to 2/6/16: 01 BF
    Write from 1.1.204 to 2/6/34: 02 04
    Write from 1.1.191 to 0/7/3: C0 C3 F2 FB
    Write from 0.0.8 to 2/5/14: 7E
    Write from 1.1.243 to 12/3/13: 45 31 60 00

Das Protokollieren kann mit Ctrl-C beendet werden.

knxd und systemd
================

Um die Änderungen wirksam werden zu lassen wird der knxd neu gestartet.
Der knxd ist im systemd zum einen über ``knxd.socket`` der die normalerweise die Kommunikation über der Port
6720 übernimmt und den ``knxd.service`` der die restlichen Aufgaben
übernimmt bereitgestellt. Beide müssen neu gestartet werden.

Zunächst beenden des knxd:

.. code-block:: bash

    sudo systemctl stop knxd.socket
    sudo systemctl stop knxd.service

Die Reihenfolge ist wichtig: beenden wir erst den knxd, kann ein Prozess
genau dann einen Socket öffnen und der systemd startet ihn sofort
wieder.

Um sicher zu gehen, das der knxd mit dem Systemstart auch gestartet wird
muß dem systemd mitgeteilt werden das diese beiden Einträge auch
eingeschaltet also ``enabled`` sind.

.. code-block:: bash

    sudo systemctl enable knxd.service
    sudo systemctl enable knxd.socket

Jetzt können wir den knxd starten mit

.. code-block:: bash

    sudo systemctl start knxd.socket
    sudo systemctl start knxd.service

Auch hier ist die Reihenfolge wichtig: Startet man erst den Service,
werden dem knxd die Sockets nicht vom systemd übergeben.

Mit den folgenden Kommandos kann geprüft werden, ob die beiden Einträge
ordnungsgemäß funktionieren:

.. code-block:: bash

    sudo systemctl status knxd.socket
    sudo systemctl status knxd.service

Wenn alles ok ist, dann sieht das etwa so aus:

.. code-block:: bash

   $ sudo systemctl status knxd.socket
   ● knxd.socket - KNX Daemon (socket)
   Loaded: loaded (/lib/systemd/system/knxd.socket; enabled; vendor preset: enabled)
   Active: active (running) since Sun 2019-03-31 19:07:49 CEST; 1 weeks 6 days ago
   Listen: /var/run/knx (Stream)
           [::]:6720 (Stream)

   ● knxd.service - KNX Daemon
   Loaded: loaded (/lib/systemd/system/knxd.service; enabled; vendor preset: enabled)
   Active: active (running) since Sun 2019-03-31 19:08:10 CEST; 1 weeks 6 days ago
   Main PID: 865 (knxd)
   Tasks: 1 (limit: 4915)
   CGroup: /system.slice/knxd.service
           └─865 /usr/bin/knxd -e 7.0.99 -E 0.0.2:8 -c -b ipt:192.168.x.y

Die Funktion des knxd lässt sich z.B. testen mit einer Gruppenadresse
(hier: 1/0/170) für einen Schaltaktor mit 1 oder 0.

.. code-block:: bash

    knxtool groupswrite ip:localhost 1/0/170 1

Sollte sich jetzt nichts tun, dann gibt es irgendwo einen Fehler und
alles muss noch einmal geprüft werden. Vielleicht ist der Neustart des
knxd vergessen oder ein Build-Fehler übersehen worden.

.. note::

   Der Befehl zum testen ist **knxtool groupswrite** und nicht **knxtool groupwrite**!


SmartHomeNG Plugin konfigurieren
================================

Damit das KNX-Plugin von SmartHomeNG genutzt werden kann, muss in der
**../etc/plugin.yaml** noch folgendes eingefügt werden:

.. code-block:: yaml

    knx:
        plugin_name: knx
        # host: 127.0.0.1    # host, falls knxd auf einem anderen System läuft als SmartHomeNG
        # port: 6720         # port zur Kommunikation mit knxd, default 6720
        # send_time: 600     # update date/time every 600 seconds, default none
        # time_ga: 11/1/1    # time GA (default none)
        # date_ga: 11/1/0    # date GA (default none)
        # busmonitor: 'on'

Alternativ kann dazu natürlich auch das Admin Interface genutzt werden.
