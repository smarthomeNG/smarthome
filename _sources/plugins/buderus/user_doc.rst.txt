.. index:: Plugins; buderus
.. index:: buderus

=======
buderus
=======

Das Plugin steuert Buderus Heizungsanlagen über ein Logamatic web KM200 Gateway-Modul an und liest
deren Betriebs- und Sensordaten aus.

.. important::

   Das Plugin befindet sich noch in der Entwicklung. Urlaubsprogramme werden aktuell nicht
   unterstützt, und die Schaltprogramme der Heizkreise können über das Plugin nicht verändert werden.


Voraussetzungen
================

Unterstützt wird das Buderus Gateway KM200. Die Module KM50 und KM300 sollten ebenfalls
funktionieren, wurden aber nicht getestet.

Für den Parameter **key** wird ein Sicherheitsschlüssel benötigt, der aus dem auf dem KM200
aufgedruckten Gerätepasswort und dem in der EasyControl-App gesetzten Benutzerpasswort erzeugt wird,
unter https://ssl-account.com/km200.andreashahn.info/.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/buderus` beschrieben.


Beispiele
=========

Das Plugin liefert fertige Item-Structs für Gateway, Heizsystem, Heizkreise und Warmwasserkreise mit.
Diese werden wie folgt in die eigene Item-Konfiguration eingebunden::

    Buderus:
      gateway:
        struct: buderus.gateway
      heating_system:
        struct: buderus.heating_system
      heating_circuit_01:
        struct: buderus.heating_circuit_01
      hot_water_circuit_01:
        struct: buderus.hot_water_circuit_01
