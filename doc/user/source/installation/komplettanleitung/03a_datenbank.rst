
.. index:: Datenbank installieren
.. index:: MySQL installieren
.. index:: MariaDB installieren
.. index:: PostgreSQL installieren
.. index:: TimescaleDB installieren

.. role:: bluesup
.. role:: redsup

=========================================
Datenbank installieren :bluesup:`Neu`
=========================================

Das ``database`` Plugin speichert Itemwerte über die Zeit und unterstützt dafür drei Datenbanken:
SQLite3, MySQL/MariaDB und PostgreSQL, letzteres optional erweitert um die
`TimescaleDB <https://www.tigerdata.com>`__ Erweiterung. Standardmäßig wird SQLite3 genutzt, dafür
ist **keine** zusätzliche Installation notwendig - dieses Kapitel kann dann übersprungen werden.

Wer stattdessen MySQL/MariaDB oder PostgreSQL+TimescaleDB nutzen möchte, findet hier die
Installation und Grundeinrichtung des jeweiligen Datenbankservers. Die eigentliche Konfiguration
des Plugins (``plugin.yaml``, Treiberauswahl, Item Attribute) ist danach unter
:doc:`database Plugin </plugins_doc/config/database>` beschrieben.

.. contents:: Schritte der Installation
   :local:


Auswahl der Datenbank
======================

Alle drei Datenbanken speichern die gleichen Daten im gleichen Schema; das Plugin verhält sich
aus Sicht der Items identisch. Der Unterschied liegt im Installationsaufwand und darin, was mit
großen Datenmengen passiert:

+------------------------+--------------------------------+--------------------------------+--------------------------------------+
|                        | SQLite3                        | MySQL/MariaDB                  | PostgreSQL+TimescaleDB               |
+========================+================================+================================+======================================+
| Installationsaufwand   | keiner (in Python enthalten)   | Serverpaket installieren und   | Serverpaket installieren, optional   |
|                        |                                | einrichten                     | zusätzlich TimescaleDB-Paketquelle   |
|                        |                                |                                | einrichten                           |
+------------------------+--------------------------------+--------------------------------+--------------------------------------+
| Datenhaltung           | eine einzelne Datei            | eigener Datenbankserver        | eigener Datenbankserver              |
|                        |                                | (Client/Server)                | (Client/Server)                      |
+------------------------+--------------------------------+--------------------------------+--------------------------------------+
| Gut geeignet für       | kleine bis mittlere            | einen bereits vorhandenen      | sehr große Logbestände (Millionen    |
|                        | Installationen                 | MySQL/MariaDB-Server mitnutzen | Zeilen), native Kompression und      |
|                        |                                |                                | Aggregation direkt auf dem           |
|                        |                                |                                | Datenbankserver                      |
+------------------------+--------------------------------+--------------------------------+--------------------------------------+
| Standard im Plugin     | ja (``driver: sqlite3``)       | nein                           | nein                                 |
+------------------------+--------------------------------+--------------------------------+--------------------------------------+

.. note::

   PostgreSQL kann auch **ohne** die TimescaleDB Erweiterung genutzt werden - dann verhält es sich
   funktional wie MySQL/MariaDB, nur mit einem anderen Server. TimescaleDB lohnt sich vor allem bei
   sehr großen Datenmengen; Details dazu (Kompression, native Aggregation, native Aufbewahrungsfristen)
   sind im Abschnitt "PostgreSQL+TimescaleDB Unterstützung" des
   :doc:`database Plugins </plugins_doc/config/database>` beschrieben.

Im Zweifel ist SQLite3 der einfachste Einstieg und für die meisten Installationen ausreichend.


Datenbankserver installieren
==============================

.. tab-set::

    .. tab-item:: SQLite3 (Standard)

        SQLite3 ist Teil der Python Standardbibliothek und damit bereits vorhanden, sobald Python
        selbst installiert ist (siehe :doc:`Debian Linux installieren <01_debian>`). Es ist keine
        weitere Installation notwendig.

        Zur Kontrolle kann geprüft werden, ob das Python Modul verfügbar ist und welche
        SQLite3-Version mitgebracht wird:

        .. code-block:: bash

           python3 -c "import sqlite3; print(sqlite3.sqlite_version)"

        Das Plugin legt die Datenbankdatei beim ersten Start selbstständig an, eine manuelle
        Einrichtung ist nicht erforderlich. Die passende Konfiguration ist bereits in der
        mitgelieferten ``plugin.yaml.default`` enthalten (siehe
        :doc:`SmartHomeNG installieren <03_smarthomeng>`).


    .. tab-item:: MySQL/MariaDB

        Debian trixie liefert MariaDB als Standard-Implementierung von MySQL im eigenen Repository
        aus, eine zusätzliche Paketquelle ist nicht notwendig:

        .. code-block:: bash

           sudo apt-get install mariadb-server

        Mit dem folgenden Befehl kann kontrolliert werden, ob der Server läuft:

        .. code-block:: bash

           systemctl status mariadb

        .. code-Block:: bash

            ● mariadb.service - MariaDB 11.8.3 database server
                 Loaded: loaded (/usr/lib/systemd/system/mariadb.service; enabled; preset: enabled)
                 Active: active (running) since ...
                   Docs: man:mariadbd(8)
                         https://mariadb.com/kb/en/library/systemd/

        Der Server ist nach der Installation sofort einsatzbereit, der lokale **root**-Zugriff
        erfolgt standardmäßig passwortlos über den Unix-Socket (``sudo mariadb``), nicht über ein
        gesetztes Passwort. Zum Absichern der Installation (u.a. Testdatenbank entfernen, anonyme
        Nutzer entfernen) kann optional

        .. code-block:: bash

           sudo mariadb-secure-installation

        ausgeführt werden. Der Assistent fragt dabei unter anderem, ob die Unix-Socket-Authentifizierung
        für root beibehalten werden soll - diese Frage kann mit **Ja** beantwortet werden, sofern kein
        root-Passwort gewünscht ist.

        Anschließend wird eine Datenbank und ein eigener Benutzer für SmartHomeNG angelegt (Passwort
        bitte durch ein eigenes ersetzen):

        .. code-block:: bash

           sudo mariadb -e "CREATE DATABASE shng CHARACTER SET utf8mb4;"
           sudo mariadb -e "CREATE USER 'shng'@'localhost' IDENTIFIED BY 'shng_password';"
           sudo mariadb -e "GRANT ALL PRIVILEGES ON shng.* TO 'shng'@'localhost';"
           sudo mariadb -e "FLUSH PRIVILEGES;"

        .. hint::

           Soll auch von einem anderen Rechner im Netzwerk auf den Server zugegriffen werden, muss
           statt ``'shng'@'localhost'`` z.B. ``'shng'@'%'`` (oder eine feste IP-Adresse) verwendet
           werden, und in ``/etc/mysql/mariadb.conf.d/50-server.cnf`` die Zeile ``bind-address``
           entsprechend angepasst bzw. entfernt werden.

        Das Plugin greift über das Python-Modul ``pymysql`` auf MySQL/MariaDB zu. Dieses Modul ist
        nicht Teil der Grundinstallation und muss nachinstalliert werden. Da das virtuelle Python
        Environment, das ``tools/postinstall`` angelegt hat, bei der Anmeldung des Users
        **smarthome** automatisch aktiviert wird (siehe :doc:`SmartHomeNG installieren
        <03_smarthomeng>`), genügt dazu das normale ``pip3``:

        .. code-block:: bash

           pip3 install pymysql

        Die eigentliche Plugin-Konfiguration (``driver: mariadb``, Verbindungsdaten) ist unter
        :doc:`database Plugin </plugins_doc/config/database>` beschrieben.


    .. tab-item:: PostgreSQL + TimescaleDB

        PostgreSQL selbst ist Teil des Debian trixie Standard-Repositories (Version 17) und wird
        wie folgt installiert:

        .. code-block:: bash

           sudo apt-get install postgresql postgresql-contrib

        Mit dem folgenden Befehl kann kontrolliert werden, ob der Server läuft:

        .. code-block:: bash

           systemctl status postgresql

        Anschließend wird eine Datenbank und ein eigener Benutzer für SmartHomeNG angelegt (Passwort
        bitte durch ein eigenes ersetzen):

        .. code-block:: bash

           sudo -u postgres psql -c "CREATE USER shng WITH PASSWORD 'shng_password';"
           sudo -u postgres psql -c "CREATE DATABASE shng OWNER shng;"

        .. important::

           Die TimescaleDB Paketquelle veröffentlicht zum Zeitpunkt der Erstellung dieser Anleitung
           noch keine Pakete für Debian trixie (13), sondern nur bis einschließlich bookworm
           (Debian 12). Wer nur PostgreSQL ohne TimescaleDB nutzen möchte, kann diesen Abschnitt
           überspringen - das Plugin funktioniert auch mit einem reinen PostgreSQL-Server, nur ohne
           die in "PostgreSQL+TimescaleDB Unterstützung" beschriebenen Zusatzfunktionen.

           Bis eine offizielle trixie-Unterstützung existiert, kann die bookworm-Paketquelle genutzt
           werden - die Pakete sind gegen die jeweilige PostgreSQL-Hauptversion gebaut, nicht fest an
           eine Debian-Version gebunden. Dies ist ein inoffizieller Workaround, keine von TimescaleDB
           offiziell unterstützte Konfiguration. Vor der praktischen Nutzung sollte auf
           `der offiziellen Installationsseite <https://www.tigerdata.com/docs/get-started/choose-your-path/install-timescaledb>`__
           geprüft werden, ob sich daran etwas geändert hat.

        Einrichtung der Paketquelle (mit explizit gesetztem ``bookworm`` statt der über
        ``lsb_release`` ermittelten trixie-Kennung, siehe Hinweis oben):

        .. code-block:: bash

           sudo apt-get install gnupg postgresql-common apt-transport-https lsb-release wget
           echo "deb https://packagecloud.io/timescale/timescaledb/debian/ bookworm main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
           wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg
           sudo apt-get update

        Im Regelfall genügt der einfache Befehl:

        .. code-block:: bash

           sudo apt-get install timescaledb-2-postgresql-17

        .. hint::

           Weil die TimescaleDB-Pakete gegen bookworm gebaut sind, das System aber bereits die neueren
           trixie-Versionen von ``postgresql-17``/``libpq5`` installiert hat (oder installieren würde),
           kann ``apt`` beim einfachen Befehl oben in seltenen Fällen mit nicht auflösbaren
           Abhängigkeiten scheitern, weil der Resolver bookworm- und trixie-Versionen der beteiligten
           Pakete mischen will. In diesem Fall hilft es, alle betroffenen Pakete in einem Kommando und
           mit ``-t`` explizit auf die eigene (trixie-)Paketquelle festgelegt zu installieren:

           .. code-block:: bash

              sudo apt-get install -t trixie postgresql-17 postgresql-client-17 libpq5 timescaledb-2-postgresql-17

           Ein solcher Konflikt wurde auf Devuan excalibur (dem trixie-Gegenstück von Devuan)
           beobachtet und dort mit ``-t excalibur-security`` statt ``-t trixie`` behoben. Auf einem
           frisch aufgesetzten, echten Debian trixie (getestet in einem Container, arm64) trat der
           Konflikt dagegen **nicht** auf - der einfache Befehl oben installierte dort ohne Probleme.
           Ob der Konflikt auftritt, scheint also vom bereits vorhandenen Systemzustand abzuhängen
           (z. B. weitere aktive Paketquellen, bereits vorgenommene Teil-Upgrades). Zuerst den
           einfachen Befehl versuchen, bei einer Fehlermeldung zu nicht auflösbaren Abhängigkeiten auf
           den ``-t trixie`` Befehl ausweichen; sollte das nicht ausreichen, probeweise
           ``-t trixie-security`` verwenden.

        Anschließend passt ``timescaledb-tune`` die PostgreSQL-Konfiguration automatisch an die
        vorhandene Hardware an (Arbeitsspeicher etc.) und der Server wird neu gestartet:

        .. code-block:: bash

           sudo timescaledb-tune --quiet --yes
           sudo systemctl restart postgresql

        Die Erweiterung muss abschließend pro Datenbank aktiviert werden:

        .. code-block:: bash

           sudo -u postgres psql -d shng -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"

        Das Plugin greift über das Python-Modul ``psycopg2-binary`` auf PostgreSQL zu. Dieses Modul
        ist nicht Teil der Grundinstallation und muss nachinstalliert werden. Da das virtuelle Python
        Environment, das ``tools/postinstall`` angelegt hat, bei der Anmeldung des Users
        **smarthome** automatisch aktiviert wird (siehe :doc:`SmartHomeNG installieren
        <03_smarthomeng>`), genügt dazu das normale ``pip3``:

        .. code-block:: bash

           pip3 install psycopg2-binary

        Die eigentliche Plugin-Konfiguration (``driver: timescaledb``, Verbindungsdaten,
        ``timescale_hypertable`` und die weiteren TimescaleDB-spezifischen Parameter) ist unter
        :doc:`database Plugin </plugins_doc/config/database>`, Abschnitt "PostgreSQL+TimescaleDB
        Unterstützung", beschrieben.
