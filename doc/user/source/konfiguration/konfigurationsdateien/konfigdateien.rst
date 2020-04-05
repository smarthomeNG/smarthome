=====================
Konfigurationsdateien
=====================

Für die Konfiguration sind die Verzeichnisse ***../etc***, ***../items***, ***../scenes*** und ***../logics*** wichtig.
In diesen Verzeichnissen wird die Konfiguration gespeichert und gepflegt. Im folgenden sind
die Konfigurationsdateien beschrieben, die in diesen Verzeichnissen gespeichert werdeen.

Die Konfiguration erfolgt im weit verbreiteten `yaml <https://en.wikipedia.org/wiki/YAML>`_ Format.

Ältere Versionen von smarthome.py und SmartHomeNG benutzten das `configobj <http://www.voidspace.org.uk/python/articles/configobj.shtml>`_
Dateiformat, welches ähnlich zum bekannten `ini-file <https://en.wikipedia.org/wiki/INI_file>`_ Format
ist, jedoch die Möglichkeit hat, Abschnitte mit Unterstrukturen in Multilevel Strukturen anzulegen.
Dieses Dateiformat ist von SmartHomeNG noch unterstützt. Es ist jedoch veraltet und wird nur für Umsteiger aus
älteren Versionen beschrieben. Dieses Dateiformat wird in zukünftigen Versionen von SmartHomeNG
nicht mehr unterstützt werden. Ab welcher Version die Unterstützung entfallen wird, ist noch nicht festgelegt.

Wenn das Backend-Plugin konfiguriert ist, können damit Abschnitte des alten .conf Dateiformats in das yaml Format
überführt werden.

Es gibt außerdem ein Service Tool im Verzeichnis ***../tools***, welches dazu dient, die gesamte Konfiguration zu
konvertieren. Hierbei kann gewählt werden, ob die Inhalte des ***../etc*** Verzeichnisses, des ***../items*** Verzeichnisses
oder beide konvertiert werden sollen.

Genaueres bitte unter :doc:`../../tools/tools` nachlesen.


---------------------------------------------
Konfigurationsdateien im Verzeichnis *../etc*
---------------------------------------------

- smarthome.yaml
- holidays.yaml
- module.yaml
- plugin.yaml
- logic.yaml
- logging.yaml
- struct.yaml


-------------------------------------------------
Item Definitionsdateien im Verzeichnis *../items*
-------------------------------------------------

- \*.yaml


----------------------------------------------------
Szenen Definitionsdateien im Verzeichnis *../scenes*
----------------------------------------------------

- \*.yaml


-------------------------------------
Logik Code im Verzeichnis *../logics*
-------------------------------------

- \*.py
- \*.blockly


.. toctree::
   :maxdepth: 4
   :hidden:

   aufbau.md
   yaml_syntax.rst
   smarthome.rst
   holidays.rst
   module.rst
   plugin.rst
   logic.rst
   logging.rst
   items.rst
   struct.rst
   logics.rst
   scenes.rst
