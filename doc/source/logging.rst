=====================
 Logging
=====================

Konfiguration 
=============
Das SmartHomeNG Logging wird in der Datei etc/logging.yaml konfiguriert.
Die Datei ist im YAML Format.

Die Logging Konfiguration in Python kann unter der URL:  https://docs.python.org/3/howto/logging.html nachgelesen werden.


Beispiel:

.. raw:: html

   <pre>
   <code>
   version: 1
   disable_existing_loggers: False
   formatters:
     simple:
       format: '%(asctime)s %(levelname)-8s %(threadName)-12s %(message)s'
       datefmt: '%Y-%m-%d  %H:%M:%S'
     detail:
       format: '%(asctime)s %(levelname)-8s %(module)-12s %(threadName)-12s %(message)s -- %(filename)s:%(funcName)s:%(lineno)d'
       datefmt: '%Y-%m-%d %H:%M:%S'

   handlers:
     console:
       class: logging.StreamHandler
       formatter: simple
       stream: ext://sys.stdout
     file:
       class: logging.handlers.TimedRotatingFileHandler
       level: DEBUG
       formatter: detail
       when: midnight
       backupCount: 7
       filename: ./var/log/smarthome.log
   loggers:
     plugins.knx:
       handlers: [file, console]
       level: DEBUG
   #   lib.scheduler:
   #    handlers: [file, console]
   #    level: DEBUG
   #  plugins.cli:
   #    handlers: [console]
   #    level: DEBUG
   root:
       level: INFO
       handlers: [file, console]
   </code>
   </pre>

format
------
Der Parameter format bschreibt das Aussehen der Logeinträge.

 

Level
-----
DEBUG
INFO
WARNING
ERROR
CRITICAL

Logging einzelner Plugins
-------------------------
Innerhalb der Logger können logging Konfigurationen für einzelne Plugins, Logiken und Libs  separat gesteuert werden.


.. raw:: html

   <pre>
   <code>
   loggers:
     plugins.knx:
       handlers: [file, console]
       level: DEBUG
   </code>
   </pre>

Configuration
=============
SmartHomeNG logging can be configured in a file in YAML format. 
The configuration file is located in the main configuration directory etc/ and is called logging.yaml
 
For configuration details see: https://docs.python.org/3/howto/logging.html 
     and https://docs.python.org/3/howto/logging.html#useful-handlers

format
------



level
-----

System
------

.. raw:: html

   <pre>
   <code>
   version: 1
   disable_existing_loggers: False
   formatters:
     simple:
       format: '%(asctime)s %(levelname)-8s %(threadName)-12s %(message)s'
       datefmt: '%Y-%m-%d  %H:%M:%S'
     detail:
       format: '%(asctime)s %(levelname)-8s %(module)-12s %(threadName)-12s %(message)s -- %(filename)s:%(funcName)s:%(lineno)d'
       datefmt: '%Y-%m-%d %H:%M:%S'

   handlers:
     console:
       class: logging.StreamHandler
       formatter: simple
       stream: ext://sys.stdout
     file:
       class: logging.handlers.TimedRotatingFileHandler
       level: DEBUG
       formatter: detail
       when: midnight
       backupCount: 7
       filename: ./var/log/smarthome.log
   loggers:
     plugins.knx:
       handlers: [file, console]
       level: DEBUG
   #   lib.scheduler:
   #    handlers: [file, console]
   #    level: DEBUG
   #  plugins.cli:
   #    handlers: [console]
   #    level: DEBUG
   root:
       level: INFO
       handlers: [file, console]
   </code>
   </pre>

