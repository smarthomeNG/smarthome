
.. index:: Konfiguration; Sichern und Wiederherstellen

.. role:: redsup
.. role:: bluesup

==========================================
Konfiguration Sichern und Wiederherstellen
==========================================

.. index:: Backup; Kommandozeile
.. index:: Sichern; Kommandozeile
.. index:: Konfiguration; Backup

-------
Sichern
-------

Die Konfiguration von SmartHomeNG kann in ein zip-Archiv gesichert werden und aus einem solchen Archiv wiederhergestellt
werden. Dieses kann sowohl von der Kommandozeile aus, als auch über das Administrationsinterface erfolgen.

Von der Kommandozeile wird ein Backup erstellt, indem SmartHomeNG mit der Option **-cb** bzw. **--create_backup**
gestartet wird. Das zip-Archiv mit dem Backup wird im Verzeichnis **/var/backup** abgelegt und hat den Namen
**shng_config_backup.zip**.

Wenn beim Backup der Dateiname den Zeitpunkt des Backups enthalten soll, muss SmartHomeNG mit der Option **-cbt** bzw.
**--create_backup_t** aufgerufen werden. Dann wird der Dateiname um Datum und Zeit der Erstellung des Backups ergänzt.
Der Dateiname hat dann die Form **shng_config_backup_YYYY-MM-TT_hh-mm-ss.zip**.

Die Sicherung von der Kommandozeile aus kann durchgeführt werden, während eine Instanz von SmartHomeNG läuft. Es ist
nicht notwendig ein laufendes SmartHomeNG vorher zu beenden.

.. attention::

   Es werden keine Konfigurationsdateien des alten .CONF Formats gesichert, sondern ausschließlich YAML Dateien.


.. index:: Restore; Kommandozeile
.. index:: Wiederherstellen; Kommandozeile
.. index:: Konfiguration; Restore

----------------
Wiederherstellen
----------------

Zum Wiederherstellen eines Konfigurations-Backups von der Kommandozeile, muss das Backup-Archiv in das Verzeichnis
**/var/restore** gelegt werden. Es darf einen beliebigen Namen tragen und muss die einzige Datei in diesem Verzeichnis
sein. Anschließend muss SmartHomeNG mit der Option **-rb** bzw. **--restore_backup** gestartet werden.

Die Wiederherstellung von der Kommandozeile aus kann durchgeführt werden, während eine Instanz von SmartHomeNG läuft.
Es ist nicht notwendig ein laufendes SmartHomeNG vorher zu beenden. Allerdings muss nach der Wiederherstellung die
laufende Instanz beendet und neu gestartet werden, damit die wiederhergestellte Konfiguration verwendet wird.

Falls die Wiederherstellung mit der Admin GUI durchgeführt wird, startet SmartHomeNG anschließend automatisch neu.


--------------------
Umfang der Sicherung
--------------------

Beim sichern werden folgende Daten in das zip-Archiv übernommen:

  - /etc

    - holidays.yaml
    - logging.yaml
    - logic.yaml
    - module.yaml
    - plugin.yaml
    - smarthome.yaml
    - struct.yaml
    - struct\_\*.yaml
    - \*.cer
    - \*.pem
    - \*.key
  - /functions

    - \*.*
  - /items

    - items\*.yaml
    - items\*.conf
  - /logic

    - \*.yaml
  - /scenes

    - *.yaml
    - *.conf
  - /structs

    - \*.yaml

.. attention::

    Zertifikats- und Key Dateien (\*.cer, \*.pem und \*.key) für tls/https werden erst ab SmartHomeNG v1.7 gesichert.


Falls SmartHomeNG mit der Option **-c** bzw. **--config_dir** gestartet wurde, so wird dieses beim Sichern und
Wiederherstellen berücksichtigt.


.. warning::

    Es werden nur **Konfigurationsdaten** gesichert.

    Ganz ausdrücklich werden **keine** Daten aus dem Unterverzeichnis ``var`` gesichert.
    Also keine Datenbank aus ``var/db`` oder ``var/rrd``, keine Logfiles aus ``log`` und auch keine Cache Daten
    aus ``var/cache`` die via Attribut ``cache: True`` befüllt werden.

    Sollen diese Daten gesichert werden, so muß SmartHomeNG zuerst beendet und danach die gewünschten Dateie manuell
    gesichert werden.

