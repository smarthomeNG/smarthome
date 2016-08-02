=====================
 Logging
=====================

Configuration 
=============
Logging for SmartHomeNG Logging will be configured within `etc/logging.yaml`
The file is in YAML format.

The logging configuration of Python may be obtained at `https://docs.python.org/3/howto/logging.html <https://docs.python.org/3/howto/logging.html>`.

Example:

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

The parameter format describes the appearance of the log entries.


Level
-----
DEBUG
INFO
WARNING
ERROR
CRITICAL

Logging of single plugins
-------------------------
Within the logging the configuration can be set seperately for single plugins, logics and libs.


.. raw:: html

   <pre>
   <code>
   loggers:
     plugins.knx:
       handlers: [file, console]
       level: DEBUG
   </code>
   </pre>
