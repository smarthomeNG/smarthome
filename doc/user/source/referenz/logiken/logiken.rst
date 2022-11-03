:tocdepth: 5

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup


.. index:: Referenz; Logiken
.. Index:: Logiken; Referenz

#######
Logiken
#######

Logiken dienen dazu, komplexere Zustände und Abläufe zu steuern, die über Item Attribute nicht abgebildet werden
können. Logiken für SmartHomeNG sind Python Skripte. Zur Erstellung von Logiken müssen Sie über Kenntnisse
der Programmiersprache Python verfügen.

In diesem Abschnitt wird die grundlegende Struktur einer Logik, sowie deren Konfiguration beschrieben. Weiterhin
werden die definierten Objekte und Methoden, sowie die zur Verfügung stehenden Pythom Module erläutert. Im weiteren
wird beschrieben, wie auf Items zugegriffen wird.

Das mqtt Modul bietet einen Support für Logiken, der auch in diesem Abschnitt dokumentiert ist.

Außerdem werden die Prinzipien der Nutzung von Plugin Funktionen beschrieben (falls das jeweilige Plugin Funktionen
definiert hat).

.. toctree::
   :maxdepth: 5
   :hidden:

   logiken_grundstruktur
   logiken_konfiguration
   logiken_logic_objekt
   logiken_logging

   logiken_python_module
   logiken_smarthomeng_methoden
   logiken_plugin_funktionen

   logiken_persistente_vars
   logiken_items
   logiken_funktionen
   logiken_mqtt
   logiken_exceptions


