Logging
=======

Configuration
-------------

Logging for SmartHomeNG is configured in ``etc/logging.yaml``. This file is in YAML format.
The way to configure logging within Python is described `here <https://docs.python.org/3/howto/logging.html>`_.

A `Best Practices` description for logging in SmartHomeNG can be found `in the Wiki <https://github.com/smarthomeNG/smarthome/wiki/Logging----Best-Practices>`_ (in German).


.. code-block:: YAML
   :caption: Example for `etc/logging.yaml`

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


format
------

The parameter format describes the appearance of the log entries.


Level
-----
The logging level can be one of:

- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

Logging of single plugins
-------------------------
Within the logging the configuration can be set separately for single plugins, logics and libs.

.. code-block:: YAML
   :caption: Sample for knx plugin

   loggers:
       plugins.knx:
       handlers: [file, console]
       level: DEBUG
