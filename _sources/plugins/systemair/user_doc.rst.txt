.. index:: Plugins; systemair
.. index:: systemair

=========
systemair
=========

Das Plugin verbindet SmartHomeNG per Modbus mit einer Systemair Wohnraumlüftungsanlage und liest
bzw. schreibt deren Register.

Voraussetzungen
================

Unterstützt werden die Systemair Wohnraumlüftungsanlagen VR400, VR700, VR700DK, VR400DE, VTC300,
VTC700, VTR150K, VTR200B, VSR300, VSR500, VSR150, VTR300, VTR500, VSR300DE und VTC200. Das Plugin
sollte grundsätzlich mit allen Systemair Lüftungsanlagen funktionieren, erfolgreich getestet wurde
es mit der VTR 200/B.

Für die Modbus-Kommunikation werden die Python3-Pakete **minimalmodbus** (ab Version 0.7) und
**pyserial** (ab Version 3.0.1) benötigt.

.. important::

   Einige Register erlauben Schreibzugriff auf die Lüftungsanlage. Falsche Werte können das Gerät
   beschädigen. Vor dem Schreibzugriff sollte die offizielle Modbus-Dokumentation von Systemair
   konsultiert werden: https://www.systemair.com/globalassets/documentation/40903.pdf

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/systemair` beschrieben.

Item-Attribute
--------------

**systemair_regaddr**, **mod_write** und **systemair_coiladdr** sind unter
:doc:`/plugins_doc/config/systemair` beschrieben. Eine vollständige Liste aller bekannten Register
als vorgefertigte Item-Definitionen liegt der Plugin-Installation als ``systemair.yaml`` bei.

Beispiel
========

::

    Lueftergeschwindigkeit:
        # read/write
        # 0: Aus, 1: Langsame Geschwindigkeit, 2: Mittlere Geschwindigkeit, 3: Schnelle Geschwindigkeit
        type: num
        systemair_regaddr: 101
        mod_write: 'true'

    Luefterdrehzahl_Zuluft:
        # in Umdrehungen pro Minute, read
        type: num
        systemair_regaddr: 111

    Alarm_Filter:
        # 0: Alarm nicht aktiv, 1: Alarm aktiv, read
        type: num
        systemair_coiladdr: 12801

Weitere Beispiele für gängige Register finden sich in der ``systemair.yaml`` im Plugin-Verzeichnis.
