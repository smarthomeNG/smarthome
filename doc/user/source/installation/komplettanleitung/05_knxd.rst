
.. index:: knxd installieren

.. role:: bluesup
.. role:: redsup

===================================
knxd installieren :bluesup:`update`
===================================

Der knxd implementiert Zugriffe auf verschiedenste Schnittstellen zum KNX Bus (z.B. IP-Router, IP-Schnittstelle,
USB-Schnittstelle, etc.) und bietet dafür eine dokumentierte Softwareschnittstelle für Programme an. SmartHomeNG
nutzt den knxd über seine tcp Schnittstelle um Daten auf den KNX Bus zu schreiben oder zu lesen. Wer keinen KNX-Bus
einsetzt, kann diesen Installationsschritt überspringen.

.. contents:: Schritte der Installation
   :local:


Grundsätzlich findet sich auf der `knxd-Seite <https://github.com/knxd/knxd>`__ die Anleitung für die
Installation. Auf der Github Seite kann unter **Code** immer der Branch ausgewählt werden. Jeder Branch
hat sein eigenes Read.me.

.. important::

    Der knxd wird derzeit aktiv weiterentwickelt. Ab
    Version 0.12.x ist pthsem nicht mehr notwendig und es wird libev
    eingesetzt. Wer genügend Wissen zum Testen hat ist herzlich
    eingeladen hier mitzuhelfen oder zu spenden. Auch bitte **vor** der
    Installation hier noch einen Blick auf
    `knxd-Seite <https://github.com/knxd/knxd>`__ werfen um aktuelles
    nicht zu verpassen.

    Diese Anleitung wird zwar in regelmäßigen Abständen aktualisiert
    aber eben nicht unbedingt wöchentlich oder gar täglich.

Die folgenden Installationsschritte beziehen sich auf Version **0.14**.


knxd unter Debian Buster installieren
=====================================

Ab dem Buster Release, ist knxd als Installationspaket in der Distribution enthalten. Die in Buster enthaltene knxd
Version ist 0.14.

Das fertige knxd Paket kann mit folgenden Kommandos installiert werden:


.. code-block:: bash

    sudo apt-get update
    sudo apt-get install -t buster knxd knxd-tools

Anschließend mit der Konfiguration gemäß Abschnitt `knxd konfigurieren <#knxd-konfigurieren>`__ fortfahren.


knxd unter älteren Debian Versionen installieren
================================================

In älteren Debian Linux Versionen ist kein Installationspaket für knxd enthalten. Unter diesen Versionen muss knxd
zuerst aus dem Quellcode compiliert werden.


zusätzliche Pakete zum Bau installieren
---------------------------------------

Zunächst müssen für den Bau einige grundlegende Tools installiert
werden:

.. code-block:: bash

    sudo apt-get install git-core build-essential dh-systemd autoconf libtool libusb-1.0-0-dev pkg-config libsystemd-dev libev-dev cmake


Quellcode laden, compilieren und ein Paket schnüren
---------------------------------------------------

Zunächst den Quellcode für den knxd vom github laden und sicherstellen,
das der 0.14 branch gewählt wird:

.. code-block:: bash

    git clone https://github.com/knxd/knxd.git
    cd knxd
    git checkout v0.14

Im Unterverzeichnis ``tools``\ findet sich ein Skript was benötigt wird
um libfmt herunterzuladen und zu bauen

.. code-block:: bash

    tools/get_libfmt

Dann übersetzen und das Paket schnüren:

.. code-block:: bash

    dpkg-buildpackage -b -uc

Wichtig ist, das am Ende der Paketerstellung keine Fehler gemeldet
wurden.

Sollte die Paketerstellung fehlerfrei ablaufen, dann kann das Paket nun
noch installiert werden mit:

.. code-block:: bash

    cd ..
    sudo dpkg -i knxd_*.deb knxd-tools_*.deb


knxd konfigurieren
==================

Als nächstes muß die Konfiguration des knxd für die zu verwendende
Schnittstelle angepasst werden. Dazu muß bei Systemen mit systemd die
Datei **/etc/knxd.conf** bearbeitet werden:

.. code-block:: bash

    sudo nano /etc/knxd.conf

Die Originalzeile ``KNXD_OPTS="-e 0.0.1 -E 0.0.2:8 -u /tmp/eib -b
ip:"`` am besten auskommentieren und in der Zeile darunter dann die
gewählten Parameter eintragen.

Details zu Schnittstellen finden sich auf der `Github-Seite vom knxd <https://github.com/knxd/knxd>`__.
Der Parameter **-c** stellt den knxd so ein, das er einen Cache nutzt. Danach folgen die Optionen für
die Verwendung der Schnittstelle:

-  IP Schnittstelle: ``KNXD_OPTS="-e 0.0.1 -E 0.0.2:8 -c -b ipt:<IP der knx Schnittstelle>"``
-  IP Router: ``KNXD_OPTS="-e 0.0.1 -E 0.0.2:8 -c -b ip:<IP des knx Routers>"``
-  USB-Interface: Bitte `Wiki zum knxd <https://github.com/knxd/knxd/wiki>`__ konsultieren.

Es kann sein, das bei ``KNXD_OPTS`` hinter dem **-c** bei einigen Interfaces noch ein ``--send-delay=30`` eingefügt
werden muß um Telegrammverlust bei hohen Lasten zu minimieren. Die 30 bedeutet dabei eine zusätzliche Wartezeit
von 30msec. Es wird damit zwischen den Paketen eine kleine Pause eingelegt um ein überfahren der Schnittstelle
zu vermeiden. Der Parameter **--no-tunnel-client-queuing** ist obsolet und sollte nicht mehr eingesetzt werden.

.. note::

   Einige IP Schnittstellen (besonders ältere) unterstützen nur einen Tunnel. Das bedeutet, dass z.B. ETS und
   knxd (SmartHomeNG) nicht gleichzeitig an solchen Schnittstellen betrieben werden können.


knxd und systemd
================

Um die Änderungen wirksam werden zu lassen, muß der knxd die neue
Konfiguration noch berücksichtigen dazu muß er ggf. beendet und neu
gestartet werden. Der knxd hat dazu zwei Einträge, zum einen
``knxd.socket`` der die normalerweise die Kommunikation über der Port
6720 übernimmt und der ``knxd.service`` der die restlichen Aufgaben
übernimmt.

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

Auch hier ist die Reihenfolge wichtig: Starten wir erst den Service,
werden dem knxd die Sockets nicht vom systemd übergeben.

Mit den folgenden Kommandos kann geprüft werden, ob die beiden Einträge
ordnungsgemäßt funktionieren:

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

Die Funktion des knxd läßt sich z.B. testen mit einer Gruppenadresse
(hier: 1/0/170) für einen Schaltaktor mit 1 oder 0.

.. code-block:: bash

    knxtool groupswrite ip:localhost 1/0/170 1

Sollte sich jetzt nichts tun, dann gibt es irgendwo einen Fehler und
alles muß noch einmal geprüft werden. Vielleicht ist der Neustart des
knxd vergessen oder ein Build-Fehler übersehen worden.

.. note::

   Der Befehl zum testen ist **knxtool groupswrite** und nicht **knxtool groupwrite**!


SmartHomeNG Plugin konfigurieren
================================

Damit das KNX-Plugin von SmartHomeNG genutzt werden kann, muß in der
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
