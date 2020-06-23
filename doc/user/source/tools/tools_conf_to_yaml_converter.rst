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

   conf_to_yaml_converter.py - tool to convert shng .conf files to yaml

   converting .conf-files from the following directories:
   - item-directory  : /usr/local/smarthome/items
   - config-directory: /usr/local/smarthome/etc

   Convert item files (y/n)?: y
   Convert config files (y/n)?:
