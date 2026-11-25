.. index:: CONF zu YAML Konverter
.. index:: YAML; CONF zu YAML Konverter
.. index:: Tools; CONF zu YAML Konverter
.. index:: Konfigurationsdateien; CONF zu YAML Konverter

conf_to_yaml_converter.py
=========================

Für Nutzer älterer Versionen, die das CONF Dateiformat für die Konfiguration von Smarthome.py
bzw. SmartHomeNG nutzen steht ein Tool zur Verfügung, welches die Konvertierung der
Konfigurationsdateien vom **CONF** Format in das **YAML** Format übernimmt.

.. note:: 

   Da Szenen ein Dateiformat verwenden, welches vom sonst in SmartHomeNG genutzten CONF Dateiformat
   abweicht, wird die Konvertierung von Szenen Konfigurationen in das YAML Format von diesem
   Konvertierungs-Tool nicht unterstützt.


.. code::

   smarthome$ python3 tools/conf_to_yaml_converter.py

   conf_to_yaml_converter.py - Tool zur Konvertierung von shng .conf-Dateien ins yaml-Format

   Dateien im Verzeichnis items konvertieren (j/n)? j
   Konvertiere Dateien in items:

   Dateien im Verzeichnis etc konvertieren (j/n)? j
   Konvertiere Dateien in etc:
