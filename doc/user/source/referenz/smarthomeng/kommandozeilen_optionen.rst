
Kommandozeilen-Optionen
=======================

smarthome.py kann mit folgenden Kommandozeilen Optionen gestartet werden:

+------------+----------------------+--------------------------------------------------------------------------------+
| **Option** | **Option (lang)**    | **Beschreibung**                                                               |
+------------+----------------------+--------------------------------------------------------------------------------+
| -p         | --pip3_command       | Setzt den Pfad des pip3 Kommandos (notwendig falls es nicht autmatisch         |
|            |                      | gefunden wird)                                                                 |
+------------+----------------------+--------------------------------------------------------------------------------+
| -i         | --interactive        | Eine interaktive Shell öffnen (mit Tab Vervollständigung). Das Logging erfolgt |
|            |                      | gemäß ``logging.yaml``.                                                        |
+------------+----------------------+--------------------------------------------------------------------------------+
| -l         | --logics             | Alle Logiken neu laden                                                         |
+------------+----------------------+--------------------------------------------------------------------------------+
| -r         | --restart            | SmartHomeNG neu starten                                                        |
+------------+----------------------+--------------------------------------------------------------------------------+
| -R         | --restart_pid0       | SmartHomeNG neu starten, ohne die PID-0-Warnung anzuzeigen                     |
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
| -u         | --var_dir            | Ein externes var-Verzeichnis benutzen (Cache, Logs, PID-Datei, Datenbanken und |
|            |                      | andere Laufzeitdaten). Standard: ``var/`` unterhalb des SmartHomeNG-Verzeich-  |
|            |                      | nisses. Relative ``var/...``-Pfade in der ``logging.yaml`` folgen dieser       |
|            |                      | Option. Beim Stoppen/Neustarten (``-s``, ``-r``) muss dieselbe Option          |
|            |                      | angegeben werden.                                                              |
+------------+----------------------+--------------------------------------------------------------------------------+
| -e         | --config_etc         | Die Verzeichnisse mit benutzerdefinierter Konfiguration (items, structs,       |
|            |                      | logics, scenes, uf) unterhalb von etc suchen                                   |
|            |                      | (``etc/items/`` statt ``items/``, ``etc/structs/`` statt ``structs/`` usw.)    |
+------------+----------------------+--------------------------------------------------------------------------------+
| -d         | --debug              | Im Vordergrund bleiben mit Debug-Logging. ``logging.yaml`` wird dabei komplett |
|            |                      | ignoriert: Alle SmartHomeNG-Logger (lib, modules, plugins, logics, items,      |
|            |                      | functions) loggen auf Level DEBUG, alle anderen auf INFO, jeweils auf die      |
|            |                      | Konsole und in die Datei ``var/log/smarthome-debug.log``.                      |
+------------+----------------------+--------------------------------------------------------------------------------+
| -f         | --foreground         | Im Vordergrund bleiben                                                         |
+------------+----------------------+--------------------------------------------------------------------------------+
