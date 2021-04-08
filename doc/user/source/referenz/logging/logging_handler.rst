
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

Der **TimedRotatingFileHandler** benennt die Backaup Versionen einer Log Datei in einer Art und Weise um, die
im Handling umständlich sein kann, da die Datei dabei die normale Extension **.log** verliert:

    smarthome-warnings.log  -->  smarthome-warnings.log.2021-04-06

Der **ShngTimedRotatingFileHandler** hat die gleiche Funktionalität und Konfigurierbarkeit wie der
**TimedRotatingFileHandler**, bildet den Namen für die Backup Dateien jedoch anders. Der Timestamp (2021-04-06)
wird nicht an das Ende des Dateinamens angefügt, sondern vor der Extenstion **.log** eingefügt:

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


**ShngMemLogHandler** hat zwei Parameter:

    - ``logname:`` - Legt den Namen fest, unter dem das Memory Log aus der smartVISU oder dem **cli** Plugin
      angesprochen werden kann.
    - ``maxlen:`` - Legt fest, wie viele Einträge ein Memory Log aufnehmen kann, bevor der älteste Eintrag
      gelöscht wird.

|

Um den Handler im Python Logging zu nutzen, wird es anschließend der Handler zum gewünschten Logger hinzu
gefügt.

.. code-block:: yaml

    loggers:
        heizung:
            handlers: [shng_heizung_file, memory_heizung]

