
.. index:: Referenz; Logging
.. Index:: Logging; Referenz

.. role:: bluesup
.. role:: redsup


===============
Logging Handler
===============

Zusätzlich zu den Logging Handlern, die im Standard Logging Modul von Python definiert, bringt SmartHomeNG
weitere Handler mit, die bei der Konfiguration in ../etc/logging.yaml verwendet werden können.

|

ShngTimedRotatingFileHandler
============================

Der **ShngTimedRotatingFileHandler** ist eine Variante des **TimedRotatingFileHandler**, der im Python
Logging Modul vorhanden ist (logging.handlers.TimedRotatingFileHandler).

Der **TimedRotatingFileHandler** benennt die Backup Versionen einer Log Datei in einer Art und Weise um, die
im Handling umständlich sein kann, da die Datei dabei die normale Extension **.log** verliert:

    smarthome-warnings.log  -->  smarthome-warnings.log.2021-04-06

Der **ShngTimedRotatingFileHandler** hat die gleiche Funktionalität und Konfigurierbarkeit wie der
**TimedRotatingFileHandler**, bildet den Namen für die Backup Dateien jedoch anders. Der Timestamp (2021-04-06)
wird nicht an das Ende des Dateinamens angefügt, sondern vor der Extension **.log** eingefügt:

    smarthome-warnings.log  -->  smarthome-warnings.2021-04-06.log

Dadurch bleibt die normale Extension des Dateinamens erhalten und die Dateien können z.B. durch Doppel-Klick
in der GUI eines Betriebssystems geöffnet werden.

Benutzung des Handlers
----------------------

In der Datei ``../etc/logging.yaml`` wird der Handler als Ersatz für **TimedRotatingFileHandler** eingesetzt.
Dort wo im Abschnitt ``handler:`` bisher der Handler **TimedRotatingFileHandler** konfiguriert ist:

.. code-block:: yaml

    handler:
        shng_warnings_file:
            class: logging.handlers.TimedRotatingFileHandler
            formatter: shng_simple
            level: WARNING
            utc: false
            when: midnight
            backupCount: 7
            filename: ./var/log/smarthome-warnings.log
            encoding: utf8

wird anstelle des ``class:`` Attributes der Handler **ShngTimedRotatingFileHandler** folgendermaßen konfiguriert:

.. code-block:: yaml

    handler:
        shng_warnings_file:
            (): lib.log.ShngTimedRotatingFileHandler
            formatter: shng_simple
            level: WARNING
            utc: false
            when: midnight
            backupCount: 7
            filename: ./var/log/smarthome-warnings.log
            encoding: utf8

Mögliche Angaben für ``when:`` sind:

- 'S': jede Sekunde
- 'M': jede Minute
- 'H': jede Stunde
- 'D': täglich
- 'W0', 'W1', ..., 'W6': Tag der Woche (0 = Montag, 1 = Dienstag, ..., 6 = Sonntag)
- 'midnight': Mitternacht, gleich wir 'D', also täglich

|

DateTimeRotatingFileHandler
===========================

Dieser Handler ermöglicht wie das operationlog und datalog Plugin, die Logdateien
entsprechend der aktuellen Uhrzeit zu benennen. Gleich wie beim oben beschriebenen
ShngTimedRotatingFileHandler kann angegeben werden, in welchem zeitlichen Abstand
eine neue Datei erstellt werden soll und wieviele Backup-Versionen erhalten bleiben.
Dabei sind zusätzlich mögliche Angaben für ``when:``:

- 'W': jede Woche, also jeden Montag mitternachts, identisch zu W0
- 'MO': monatlich, also jeden 1. eines Monats mitternachts
- 'Y': jährlich, also jedes Jahr am 1. Jänner mitternachts

Der Handler stellt mehrere Platzhalter für Dateinamen und Ordner zur Verfügung.
Monat, Tag, Stunde und Minute werden im Normalfall mit einer Ziffer
ohne vorgestellter 0 geschrieben, außer man setzt dezidiert ein ``:02`` hinten dran.
Durch ``{month:02}`` wird z.B. der März als 03 geschrieben,
während der März bei ``{month}`` als 3 geschrieben wird.

* {year}: Das aktuelle Jahr im Format YYYY, z.B. 2023
* {month}: Der aktuelle Monat im Format (M)M, z.B. (0)3 für März oder 10 für Oktober
* {day}: Der aktuelle Tag im Format (D)D, z.B. (0)1 für den 1. oder 10 für den 10. des Monats
* {hour}: Die aktuelle Stunde im Format (H)H, z.B. 22 für zehn Uhr abends oder (0)1 für ein Uhr nachts
* {minute}: Die aktuelle Minute im Format , z.B. 22 für zehn Uhr abends oder 1 für ein Uhr nachts
* {stamp}: Der aktuelle Unix Timestamp, z.B. 1699220771.133886
* {intstamp}: Der aktuelle Unix Timestamp als Integer, z.B. 1699220771

Das folgende Beispiel erstellt eine CSV Datei mit Namen "test" und dem aktuellen Datum im Format Tag.Monat.Jahr_Stunde im Ordner smarthome/<aktuelles Jahr>.
Jede volle Stunde wird eine neue Logdatei mit dem gleichen Muster erstellt. Es werden
zwei Backup-Dateien behalten, ältere Dateien werden zur vollen Stunde gelöscht.

Hinweis: Ist {hour} nicht Bestandteil des Dateinamens, wird die selbe Datei für den jeweiligen Tag überschrieben, erst am nächsten Tag wird eine neue Datei erstellt.

.. code-block:: yaml

    handler:
        csv_file:
            (): lib.log.DateTimeRotatingFileHandler
            formatter: shng_simple
            filename: ./{year}/test_{day}.{month}.{year}_{hour}.csv
            when: 'H'
            interval: 1
            backupCount: 2

Wird beim Anlegen des Handlers kein Platzhalter im Dateinamen genutzt,
kommt die standardmäßige Benennung, bei der zwischen Dateinamen und Dateierweiterung
die aktuelle minimale Zeitinformation eingefügt wird, zu tragen.

Das folgende Beispiel erstellt im Log-Ordner alle 10 Minuten eine Datei namens
``test.<Jahr>-<Monat>-<Tag>-<Stunde>.<Minute>.txt``. Wird die Logrotation auf
"jeden xten Tag" gestellt, also ``when: 'D'``, wird die Datei
``test.<Jahr>-<Monat>-<Tag>.txt`` benannt.

.. code-block:: yaml

    handler:
        txt_file:
            (): lib.log.DateTimeRotatingFileHandler
            formatter: shng_simple
            filename: ./var/log/test.txt
            when: 'M'
            interval: 10

|

ShngMemLogHandler
=================

In SmartHomeNG ist seit je her standardmäßig ein Memory Log konfiguriert. Dieses Memory Log ist bisher
völlig losgelöst vom Python Logging System. Das memory Log trägt den Namen 'env.core.log' und wird dazu verwendet
in der smartVISU auf der Konfigurationsseite unter 'SmartHomeNG' Log Einträge anzuzeigen. Das Memory Log
'env.core.log' kann auch mit Hilfe des **cli** Plugins angezeigt werden.

Weitere Memory Logs (die bisher mit dem **memlog** Plugin angelegt werden konnten/mussten) können in der smartVISU
mit Hilfe der Widgets **status.log** und des **cli** Plugins angezeigt werden.

Mit Hilfe des **ShngMemLogHandler** können nun normale Log Einträge, die über das Standard Python Logging erzeugt
werden, in ein Memory Log geloggt werden. Der **ShngMemLogHandler** legt dazu ein entsprechendes Memory Log an
und der Handler wird in den konfigurierten Loggern als (zusätzlicher) Logger konfiguriert.

Benutzung des Handlers
----------------------

In der Datei ``../etc/logging.yaml`` wird der **ShngMemLogHandler** im Abschnitt ``handler:`` konfiguriert.

.. code-block:: yaml

    handler:
        memory_heizung:
            (): lib.log.ShngMemLogHandler
            logname: mem_heiz
            maxlen: 60
            level: INFO
            cache: True


**ShngMemLogHandler** hat vier Parameter:

    - ``logname:`` - Legt den Namen fest, unter dem das Memory Log aus der smartVISU oder dem **cli** Plugin
      angesprochen werden kann.
    - ``maxlen:`` - Legt fest, wie viele Einträge ein Memory Log aufnehmen kann, bevor der älteste Eintrag
      gelöscht wird.
    - ``level:`` - Legt den minimalen Log Level fest, der in das Memory Log geschrieben wird
    - ``cache:`` - Ist dieser Parameter True, werden die Einträge im cache Ordner gesichert und beim Neustart geladen

|

Um den Handler im Python Logging zu nutzen, wird es anschließend der Handler zum gewünschten Logger hinzu
gefügt.

.. code-block:: yaml

    loggers:
        heizung:
            handlers: [shng_heizung_file, memory_heizung]
