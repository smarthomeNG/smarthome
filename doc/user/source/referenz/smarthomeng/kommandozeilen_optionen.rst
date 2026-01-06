
Kommandozeilen-Optionen
=======================

smarthome.py kann mit folgenden Kommandozeilen Optionen gestartet werden:

+------------+----------------------+--------------------------------------------------------------------------------+
| **Option** | **Option (lang)**    | **Beschreibung**                                                               |
+------------+----------------------+--------------------------------------------------------------------------------+
| -p         | --pip3_command       | Setzt den Pfad des pip3 Kommandos (notwendig falls es nicht autmatisch         |
|            |                      | gefunden wird)                                                                 |
+------------+----------------------+--------------------------------------------------------------------------------+
| -i         | --interactive        | Eine interactive Shell öffen (mit Tab Vervollständigung und ausführlichem      |
|            |                      | Logging)                                                                       |
+------------+----------------------+--------------------------------------------------------------------------------+
| -l         | --logics             | Alle Logiken neu laden                                                         |
+------------+----------------------+--------------------------------------------------------------------------------+
| -r         | --restart            | SmartHomeNG neu starten                                                        |
+------------+----------------------+--------------------------------------------------------------------------------+
| -s         | --stop               | SmartHomeNG beenden                                                            |
+------------+----------------------+--------------------------------------------------------------------------------+
| -V         | --version            | Die Version von SmartHomeNG anzeigen                                           |
+------------+----------------------+--------------------------------------------------------------------------------+
|            | --start              | SmartHomeNG beim Start in den Hintergrund bringen (Default)                    |
+------------+----------------------+--------------------------------------------------------------------------------+
| -cb        | --create_backup      | Ein Backup der Konfiguration von SmartHomeNG erzeugen (nur die YAML Dateien)   |
+------------+----------------------+--------------------------------------------------------------------------------+
| -cbt       | --create_backup_t    | Ein Backup der Konfiguration von SmartHomeNG erzeugen (nur die YAML Dateien)   |
|            |                      | mit Zeitstempel im Dateinamen                                                  |
+------------+----------------------+--------------------------------------------------------------------------------+
| -rb        | --restore_backup     | Ein vorher erzeugtes Konfigurations-Backup wieder einspielen                   |
+------------+----------------------+--------------------------------------------------------------------------------+
| -c         | --config_dir         | Ein externes Konfigurations-Verzeichnis benutzen. Dieses Verzeichnis sollte    |
|            |                      | die Unter-Verzeichnisse "etc", "items", "logics" and "scenes" enthalten.       |
+------------+----------------------+--------------------------------------------------------------------------------+
| -e         | --config_etc         | Die Verzeichnisse mit benutzerdefinierter Konfiguration (items, structs,       |
|            |                      | logics, scenes, uf) unterhalb von etc suchen                                   |
|            |                      | (/etc/items/ statt /items/, /etc/structs/ statt /structs/ usw.)                |
+------------+----------------------+--------------------------------------------------------------------------------+
| -v         | --verbose            | Ausführliches Logging - DEPRECATED bitte die Logging-Konfiguration benutzen    |
+------------+----------------------+--------------------------------------------------------------------------------+
| -d         | --debug              | Im Vordergrund bleiben mit ausführlichem Logging - DEPRECATED bitte die        |
|            |                      | Logging-Konfiguration benutzen                                                 |
+------------+----------------------+--------------------------------------------------------------------------------+
| -f         | --foreground         | Im Vordergrund bleiben                                                         |
+------------+----------------------+--------------------------------------------------------------------------------+
| -q         | --quiet              | Reduziertes Logging - DEPRECATED bitte die Logging-Konfiguration benutzen      |
+------------+----------------------+--------------------------------------------------------------------------------+

Die als DEPRECATED gekennzeichneten Optionen werden in einem der nächsten Releases entfernt werden.


