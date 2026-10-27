.. index:: upgrade_check.py
.. index:: Tools; upgrade_check.py

upgrade_check.py
================

Dieses Skript prüft die Konfiguration einer Installation auf Änderungen, die für SmartHomeNG 2.0 nötig sind, und
kann die meisten davon selbst durchführen. Ohne die Option ``--fix`` wird nichts verändert. Mit ``--fix`` wird jede
geänderte Datei vorher nach ``etc/upgrade_check_backup/<Zeitstempel>/`` kopiert.

Es werden die Dateien ``etc/plugin.yaml``, die Item- und Struct-Dateien, die Logiken, die Userfunctions und die
Szenen geprüft. Liegen die Verzeichnisse noch im Hauptverzeichnis (``items``, ``logics`` usw.), werden sie dort
gefunden.

.. code::

   smarthome$ python3 tools/upgrade_check.py
   removed-api: removed sh.* methods (sh.return_item, sh.now, sh.base_dir, sh.tools, ...)
     [fixable] etc/logics/cal.py:4: sh.now -> sh.shtime.now
     [fixable] etc/structs/rollo.yaml:130: sh.return_item -> sh.items.return_item

   2 findings, 2 can be fixed with --fix.
   smarthome$ python3 tools/upgrade_check.py --fix

Die Prüfungen:

+-------------------+-------------------------------------------------------------------------------------------------+
| ``instances``     | Instanznamen von Plugins, die mehrfach eingebunden sind: Seit 2.0 ist der Name des Abschnitts   |
|                   | in der ``plugin.yaml`` der Instanzname. Ein Abschnitt ohne ``instance:`` erhält ``instance:     |
|                   | default`` und behält damit die leere Instanz. Item-Attribute ``attr@alt`` werden auf den neuen  |
|                   | Instanznamen umgestellt (bei einem nur einmal eingebundenen Plugin entfällt das ``@alt``).      |
+-------------------+-------------------------------------------------------------------------------------------------+
| ``plugin-alias``  | ``sh.<Abschnitt>`` wird zu ``sh.plugins.<Abschnitt>`` (in Logiken, Userfunctions und in Items). |
|                   | Heißt ein Plugin-Abschnitt wie ein Top-Level Item, wird er nur gemeldet.                        |
+-------------------+-------------------------------------------------------------------------------------------------+
| ``plugin-class``  | ``class_name`` und ``class_path`` in der ``plugin.yaml`` werden zu ``plugin_name`` (und bei     |
|                   | einer älteren Plugin-Version zu ``plugin_version``). Plugins außerhalb des Verzeichnisses       |
|                   | ``plugins`` werden nur gemeldet.                                                                |
+-------------------+-------------------------------------------------------------------------------------------------+
| ``removed-api``   | Entfernte Methoden des ``sh`` Objekts, z.B. ``sh.return_item()`` wird zu                        |
|                   | ``sh.items.return_item()`` und ``sh.now()`` zu ``sh.shtime.now()``. Für ``sh.tools``,           |
|                   | ``sh.string2bool`` und Importe von ``lib.tools`` wird nur die Ersetzung genannt, da dafür ein   |
|                   | Import nötig ist.                                                                               |
+-------------------+-------------------------------------------------------------------------------------------------+
| ``scenes``        | Szenen im alten ``.conf`` Format werden zu ``.yaml`` Dateien.                                   |
+-------------------+-------------------------------------------------------------------------------------------------+
| ``conf-files``    | Item-Dateien (``items/*.conf``) und Konfigurationsdateien (``etc/*.conf``) im alten ``.conf``   |
|                   | Format werden nicht mehr gelesen und werden gemeldet (Umwandlung mit                            |
|                   | ``tools/conf_to_yaml_converter.py``).                                                           |
+-------------------+-------------------------------------------------------------------------------------------------+
| ``module-params`` | Parameter in ``etc/module.yaml``, die es in den Modulen nicht mehr gibt (admin:                 |
|                   | ``websocket_host``, ``websocket_port``, ``pypi_timeout``), werden entfernt.                     |
+-------------------+-------------------------------------------------------------------------------------------------+
| ``password-hash`` | Ungesalzene SHA-512 Passwort-Hashes (``hashed_password`` und ``service_hashed_password`` des    |
|                   | http Moduls, ``hashed_password`` des cli Plugins) werden gemeldet. Sie funktionieren weiter,    |
|                   | sollten aber durch einen gesalzenen Hash von ``tools/hash_password.py`` ersetzt werden.         |
+-------------------+-------------------------------------------------------------------------------------------------+

Optionen:

.. code::

   --base DIR   Verzeichnis der Installation (Standard: das Verzeichnis dieses SmartHomeNG)
   --fix        Änderungen durchführen (Sicherungen in etc/upgrade_check_backup)
   --only NAME  nur diese Prüfung ausführen (mehrfach möglich)
   --list       die Prüfungen auflisten
   --json       die Ergebnisse als JSON ausgeben

Der Rückgabewert ist 0, wenn nichts mehr zu tun ist, sonst 1.
