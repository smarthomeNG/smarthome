.. index:: Plugins; helios
.. index:: helios

======
helios
======

Das Plugin steuert Lüftungsgeräte vom Typ Helios EC x00 Pro bzw. Vallox xx SE über eine serielle
Schnittstelle an und liest deren Status- und Fehlerwerte aus.


Voraussetzungen
================

Für die Kommunikation mit dem Lüftungsgerät wird eine serielle Verbindung (RS232 oder USB-Adapter)
benötigt, deren Port über den Parameter **tty** konfiguriert wird.

Ausführliche Dokumentation und Troubleshooting-Hinweise bietet das
`Wiki des Plugins <https://github.com/Tom-Bom-badil/helios/wiki>`_.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/helios` beschrieben.

Das Plugin liefert im Verzeichnis ``helios/files/`` fertige Vorlagen für Items (``helios.yaml``) und
Logiken (``helios_logics.py``), die nach ``items`` bzw. ``logics`` kopiert und dort angepasst werden
können.


Beispiele
=========

Logik-Einbindung
-----------------

Für die mitgelieferten Logiken müssen in ``etc/logic.yaml`` passende Einträge angelegt werden::

    fanspeed_uzsu_logic:
        filename: helios_logics.py
        watch_item: ventilation.fanspeed.fanspeed_uzsu

    booster_logic:
        filename: helios_logics.py
        watch_item: ventilation.booster_mode.logics.switch

**watch_item** verweist jeweils auf das Item, dessen Änderung die Logik auslöst.
