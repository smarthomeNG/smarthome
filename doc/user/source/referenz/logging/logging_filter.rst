
.. index:: Referenz; Logging Filter
.. Index:: Logging Filter; Referenz

.. role:: bluesup
.. role:: redsup


==============
Logging Filter
==============

Mit der Hilfe von Logging Filtern kann innerhalb eines Handlers gesteuert werden, ob ein Log Record erzeugt
werden soll, oder ob die Information verworfen werden soll.

SmartHomeNG bringt einige Logging Filter mit.

|

CherryPyFilter
==============

Das im http Modul von SmartHomeNG genutzte CherryPy Modul erzeugt leider unerwartete/unerwünschte Log Einträge,
die in einigen Logs auftreten können. Um diese Log Einträge zu unterdrücken, kann der **CherryPyFilter**
genutzt werden, den das http Modul mitbringt.

Benutzung des Filters
---------------------

In der Datei ``../etc/logging.yaml`` wird der **CherryPyFilter** im Abschnitt ``filters:`` zur Nutzung
konfiguriert.

.. code-block:: yaml

    filters:
        cherrypy_filter:
            (): modules.http.CherryPyFilter

Um den Filter in einem Log-Handler anzuwenden, muss der Filter noch in der Konfiguration des entsprechenden
Handlers im Abschnitt ``handlers:`` konfiguriert werden:

.. code-block:: yaml

    handlers:
        shng_details_file:
            (): lib.log.ShngTimedRotatingFileHandler
            formatter: shng_simple
            level: DEBUG
            utc: false
            when: midnight
            backupCount: 7
            filename: ./var/log/smarthome-details.log
            encoding: utf8
            filters: [cherrypy_filter]

|

DuplicateFilter
===============

Manchmal ist es wünschenswert mehrere gleich lautende Logeinträge, die direkt aufeinander folgen zu unterdrücken
und nur den ersten Log Eintrag wirklich in das Log zu schreiben. Diese Aufgabe erfüllt der **DuplicateFilter**.

Benutzung des Filters
---------------------

In der Datei ``../etc/logging.yaml`` wird der **DuplicateFilter** im Abschnitt ``filters:`` zur Nutzung
konfiguriert.

.. code-block:: yaml

    filters:
        duplicatefilter:
            (): lib.logutils.DuplicateFilter

Um den Filter in einem Log-Handler anzuwenden, muss der Filter noch in der Konfiguration des entsprechenden
Handlers im Abschnitt ``handlers:`` konfiguriert werden.

|

Filter
======

**Filter** ist ein recht universeller Filter, der über eine Reihe von Parametern konfiguriert werden kann:

  - **name**: Name des Loggers (regex)
  - **module**: Loggendes Module (regex)
  - **msg**: Log Message (regex)
  - **timestamp**: Zeitpunkt des Logeintrages (regex)
  - **invert**: False/True. Über **invert** kann das durch die obigen Parameter erzeugte Filter Ergebnis invertiert werden

Bis auf **invert** können alle Parameter Listen von Regular Expressions sein.

Benutzung des Filters
---------------------

In der Datei ``../etc/logging.yaml`` wird der **Filter** im Abschnitt ``filters:`` zur Nutzung
konfiguriert. Dabei ist die erste Zeile `(): lib.logutils.Filter` zwingend anzugeben,
außerdem zumindest eine der darauffolgenden Zeilen (module, msg, timestamp). Die Angaben
sind dabei als reguläre Ausdrücke anzugeben und können sogar in Listenform erfolgen.
Bei Modulen wie item, metadata, etc. ist KEIN voranstehendes `lib.` anzugeben. 

.. code-block:: yaml

    filters:
        examplefilter:
            (): lib.logutils.Filter
            name: []
            module: []
            msg: []
            timestamp: []
            invert: False

Um den Filter in einem Log-Handler anzuwenden, muss der Filter noch in der Konfiguration des entsprechenden
Handlers im Abschnitt ``handlers:`` konfiguriert werden.

|
