.. role:: redsup

.. index:: Datenbank Migrations Tool
.. index:: Tools; Datenbank Migrations Tool

db_migrate.py :redsup:`Neu`
===========================

Dieses Skript migriert das Schema des database Plugins (Tabellen ``item``/``log``) zwischen
zwei beliebigen der unterstützten Datenbank-Backends: SQLite3, MySQL/MariaDB und
PostgreSQL+TimescaleDB - in beliebiger Richtung.

.. attention::

   Das Skript muss bei gestopptem SmartHomeNG ausgeführt werden. Es verweigert den Start,
   solange eine laufende Instanz erkannt wird.

Quelle und Ziel können auf drei Arten angegeben werden: über den Namen einer bereits in
``etc/plugin.yaml`` konfigurierten Plugin-Instanz (``--source-instance``/``--dest-instance``),
über explizite Treiber-/Verbindungsparameter (``--source-driver``/``--source-connect`` bzw.
``--dest-driver``/``--dest-connect``), oder interaktiv über Rückfragen (``--interactive``).

Der Migrationslauf ist fortsetzbar: bereits auf dem Ziel vorhandene Items werden übersprungen,
sofern nicht ``--force`` für dieses Item angegeben wird. Mit ``--dry-run`` lässt sich der
geplante Ablauf ohne tatsächliche Schreibvorgänge prüfen.

.. note::

   Stammt die Quelle von einer PostgreSQL+TimescaleDB-Instanz mit aktivierter
   ``timescale_native_aggregation``, verweigert das Skript standardmäßig die Migration: Es
   liest ausschließlich die Rohdaten-Tabelle ``log``, nicht die serverseitig berechneten
   Continuous Aggregates - bereits durch ``timescale_native_retention`` entfernte Rohdaten
   würden sonst stillschweigend fehlen. Mit ``--force <item ...>`` lässt sich dies bewusst
   übergehen (migriert dann nur die noch vorhandenen Rohdaten).

.. code::

   smarthome@<yourcomputer>:/usr/local/smarthome$ python3 tools/db_migrate.py -h

   usage: db_migrate.py [-h] [--etc-dir ETC_DIR] [--interactive] [--dry-run]
                        [--bulk] [--batch-size BATCH_SIZE]
                        [--force ITEM [ITEM ...]] [--source-instance NAME]
                        [--source-driver SOURCE_DRIVER] [--source-connect JSON]
                        [--source-password SOURCE_PASSWORD]
                        [--source-prefix SOURCE_PREFIX] [--dest-instance NAME]
                        [--dest-driver DEST_DRIVER] [--dest-connect JSON]
                        [--dest-password DEST_PASSWORD]
                        [--dest-prefix DEST_PREFIX]

   Migrate the database plugin schema (item/log tables) between sqlite3/MySQL-
   MariaDB/PostgreSQL. Must be run with SmartHomeNG stopped.

   options:
     -h, --help            show this help message and exit
     --etc-dir ETC_DIR     etc/ directory to read plugin.yaml from
     --interactive         prompt for any side not fully specified via flags
     --dry-run             report what would happen, write nothing
     --bulk                use multi-row bulk inserts instead of row-by-row
                           (default)
     --batch-size BATCH_SIZE
                           rows per commit (default 20000)
     --force ITEM [ITEM ...]
                           redo these items even if already migrated; also the
                           required override to proceed when the source has
                           native continuous aggregates (see
                           source_has_native_cagg)
     --source-instance NAME
                           source: plugin.yaml instance name
     --source-driver SOURCE_DRIVER
                           source: driver (sqlite3/pymysql/psycopg2), manual
                           config
     --source-connect JSON
                           source: connect params as a JSON object
     --source-password SOURCE_PASSWORD
                           source: password (prompted via getpass if omitted and
                           needed)
     --source-prefix SOURCE_PREFIX
                           source: table prefix
     --dest-instance NAME  destination: plugin.yaml instance name
     --dest-driver DEST_DRIVER
                           destination: driver (sqlite3/pymysql/psycopg2), manual
                           config
     --dest-connect JSON   destination: connect params as a JSON object
     --dest-password DEST_PASSWORD
                           destination: password (prompted via getpass if omitted
                           and needed)
     --dest-prefix DEST_PREFIX
                           destination: table prefix

Beispiel: Migration einer lokalen SQLite3-Instanz nach PostgreSQL+TimescaleDB, unter
Verwendung zweier bereits in ``etc/plugin.yaml`` konfigurierter Instanzen:

.. code-block:: bash

   python3 tools/db_migrate.py --source-instance database --dest-instance database_timescale
