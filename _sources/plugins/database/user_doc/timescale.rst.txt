
.. index:: database; PostgreSQL installieren
.. index:: database; TimescaleDB installieren

.. role:: redsup

=================================================
PostgreSQL/TimescaleDB Installation :redsup:`neu`
=================================================

Diese Seite beschreibt die Installation und Grundeinrichtung eines PostgreSQL Servers, optional
erweitert um die `TimescaleDB <https://www.tigerdata.com>`__ Extension, für die Nutzung mit dem
``database`` Plugin.

.. note::

   PostgreSQL kann auch **ohne** die TimescaleDB Erweiterung genutzt werden - dann verhält es sich
   funktional wie MySQL/MariaDB, nur mit einem anderen Server. Details zu den TimescaleDB
   Zusatzfunktionen (Kompression, native Aggregation, native Aufbewahrungsfristen) sind im
   Abschnitt "PostgreSQL+TimescaleDB Unterstützung" in :doc:`../user_doc` beschrieben.

PostgreSQL installieren
========================

PostgreSQL selbst ist auf aktuellen Debian- und Ubuntu-Versionen im Standard-Repository enthalten
und wird wie folgt installiert:

.. code-block:: bash

   sudo apt-get install postgresql postgresql-contrib

Mit dem folgenden Befehl kann kontrolliert werden, ob der Server läuft:

.. code-block:: bash

   systemctl status postgresql

Anschließend wird eine Datenbank und ein eigener Benutzer für SmartHomeNG angelegt (Passwort bitte
durch ein eigenes ersetzen):

.. code-block:: bash

   sudo -u postgres psql -c "CREATE USER shng WITH PASSWORD 'shng_password';"
   sudo -u postgres psql -c "CREATE DATABASE shng OWNER shng;"

Wer nur PostgreSQL ohne TimescaleDB nutzen möchte, kann den folgenden Abschnitt überspringen - das
Plugin funktioniert auch mit einem reinen PostgreSQL-Server, nur ohne die oben verlinkten
TimescaleDB-Zusatzfunktionen.

TimescaleDB Erweiterung installieren
======================================

.. important::

   Die TimescaleDB Paketquelle enthält Pakete für Debian bookworm (12) und trixie (13), jeweils für
   amd64 und arm64 (geprüft am 06.10.2026 anhand des Paketindex der Paketquelle; für
   ``timescaledb-2-postgresql-17`` unter trixie z.B. Version 2.30.2).

   Als Distributions-Name muss die Debian-Bezeichnung eingetragen werden. Auf Derivaten wie Devuan
   (excalibur entspricht Debian trixie) kennt die Paketquelle den von ``lsb_release`` gelieferten
   Namen nicht - dort also ``trixie`` verwenden, nicht den Namen der eigenen Distribution.

Einrichtung der Paketquelle (hier für Debian trixie bzw. Devuan excalibur; für Debian bookworm
``trixie`` durch ``bookworm`` ersetzen):

.. code-block:: bash

   sudo apt-get install gnupg postgresql-common apt-transport-https lsb-release wget
   echo "deb https://packagecloud.io/timescale/timescaledb/debian/ trixie main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
   wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/timescaledb.gpg
   sudo apt-get update

Im Regelfall genügt der einfache Befehl (Versionsnummer ggf. an die installierte PostgreSQL
Version anpassen):

.. code-block:: bash

   sudo apt-get install timescaledb-2-postgresql-17

.. hint::

   Scheitert ``apt`` beim einfachen Befehl oben in seltenen Fällen mit nicht auflösbaren
   Abhängigkeiten, weil der Resolver Pakete unterschiedlicher Debian-Versionen mischen will, hilft
   es, alle betroffenen Pakete in einem Kommando und mit ``-t`` explizit auf die eigene
   Paketquelle (z.B. ``trixie``) festgelegt zu installieren:

   .. code-block:: bash

      sudo apt-get install -t trixie postgresql-17 postgresql-client-17 libpq5 timescaledb-2-postgresql-17

   Ein solcher Konflikt wurde mit der früher hier beschriebenen bookworm-Paketquelle auf Devuan
   excalibur beobachtet und dort mit ``-t excalibur-security`` statt ``-t trixie`` behoben; auf
   einem frisch aufgesetzten Debian trixie (Container, arm64) trat er nicht auf. Ob er auftritt,
   hängt offenbar vom vorhandenen Systemzustand ab (weitere aktive Paketquellen, bereits
   vorgenommene Teil-Upgrades). Zuerst den einfachen Befehl versuchen, bei einer Fehlermeldung zu
   nicht auflösbaren Abhängigkeiten auf den ``-t``-Befehl ausweichen; sollte das nicht ausreichen,
   probeweise ``-t trixie-security`` verwenden.

Anschließend passt ``timescaledb-tune`` die PostgreSQL-Konfiguration automatisch an die vorhandene
Hardware an (Arbeitsspeicher etc.) und der Server wird neu gestartet:

.. code-block:: bash

   sudo timescaledb-tune --quiet --yes
   sudo systemctl restart postgresql

Die Erweiterung muss abschließend pro Datenbank aktiviert werden:

.. code-block:: bash

   sudo -u postgres psql -d shng -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"

Python-Modul installieren
===========================

Das Plugin greift über das Python-Modul ``psycopg2-binary`` auf PostgreSQL zu. Dieses Modul ist
nicht Teil der Grundinstallation und muss im für SmartHomeNG verwendeten virtuellen Python
Environment (siehe :doc:`/referenz/python/virtual_environments`) nachinstalliert werden:

.. code-block:: bash

   pip3 install psycopg2-binary

Die eigentliche Plugin-Konfiguration (``driver: timescaledb``, Verbindungsdaten) ist unter
:doc:`/plugins_doc/config/database` beschrieben, die TimescaleDB-spezifischen Parameter
(``timescale_hypertable`` und weitere) im Abschnitt "PostgreSQL+TimescaleDB Unterstützung" von
:doc:`../user_doc`.
