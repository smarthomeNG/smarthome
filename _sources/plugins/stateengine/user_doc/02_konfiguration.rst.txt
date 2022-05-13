
.. index:: Stateengine; Konfiguration

=============
Konfiguration
=============

.. important::

      Detaillierte Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/stateengine` zu finden.

Pluginkonfiguration
-------------------

.. code-block:: yaml

   #etc/plugin.yaml
   stateengine:
       plugin_name: stateengine
       plugin_enabled: True
       #startup_delay_default: 10
       #suspend_time_default: 3600
       #log_level: 0
       #log_directory: var/log/StateEngine/
       #log_maxage: 0

Aktivieren
----------

Um für ein Item das Stateengine Plugin zu aktivieren, ist das Attribut ``se_plugin``
auf ``active`` zu setzen. Dies ist in der generellen struct Vorlage bereits
hinterlegt, muss aber manuell gesetzt werden, falls das ``struct: stateengine.general``
nicht eingesetzt wird.

.. code-block:: yaml

  #items/item.yaml
  raffstore1:
      automatik:
          rules:
             se_plugin: active
             se_log_level: 2

Logging
-------

Es gibt zwei Möglichkeiten, den Output des Plugins zu loggen:
**intern**
Hierbei werden, sofern das Loglevel 1 oder 2 beträgt, sämtliche Logeinträge in
eigene Dateien in einem selbst definierten Verzeichnis geschrieben. Das Loglevel
kann sowohl global in der etc/plugin.yaml Datei deklariert, als auch individuell
pro Item mittels ``se_log_level`` (dort wo auch se_plugin: active steht) überschrieben werden.

**logging.yaml**
Sowohl der Output des Plugins generell, als auch der Einträge für bestimmte Items
können in der logging.yaml Datei wie folgt deklariert werden:

.. code-block:: yaml

  #etc/logging.yaml
  filters:
      notfound:
          (): lib.logutils.Filter
          msg: "(.*)Item (.*) not found!"

  handlers:
      stateengine_licht_file:
          class: logging.handlers.TimedRotatingFileHandler
          formatter: shng_simple
          level: DEBUG
          utc: false
          when: midnight
          backupCount: 2
          filename: ./var/log/stateengine_licht.log
          encoding: utf8
          filters: [notfound]

      stateengine_all_file:
          class: logging.handlers.TimedRotatingFileHandler
          formatter: shng_simple
          level: DEBUG
          utc: false
          when: midnight
          backupCount: 2
          filename: ./var/log/stateengine.log
          encoding: utf8

  loggers:
      plugins.stateengine:
          # Default logger for SmartHomeNG plugins
          handlers: [shng_details_file]
          level: INFO

      stateengine.licht:
          # Default logger for SmartHomeNG plugins
          handlers: [stateengine_licht_file]
          level: DEBUG

      stateengine:
          # Default logger for SmartHomeNG plugins
          handlers: [stateengine_all_file]
          level: WARNING

Das obige Beispiel würde in die Datei var/log/stateengine_licht.log sämtliche
Debug Information schreiben, die für das Item "licht" und dessen Unteritems
relevant sind. Aufgrund des aktiven Filters "notfound" werden sämtliche
Einträge zu nicht gefundenen Items ignoriert.

Zusätzlich werden alle Fehler von StateEngine Items in die Datei
stateengine.log geschrieben. Da der Filter hier nicht aktiv ist,
werden auch Informationen zu nicht gefundenen Items geloggt.

Generelle Informationen und Warnungen unabhänging von den StateEngine Items
(z.B. zum Standardloglevel, maximalen Alter, etc.) werden in das
smarthome-details.log geschrieben.
