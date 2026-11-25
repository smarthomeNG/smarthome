.. index:: Plugins; co2meter (CO2Meter Kohlendioxidmessgerät)
.. index:: co2meter

========
co2meter
========

Das co2meter-Plugin liest Messwerte eines Dostmann TFA AirCO2ntrol Kohlendioxid-Messgeräts über die
USB-Schnittstelle aus.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/co2meter` beschrieben.

Item-Attribute
--------------

**co2meter_data_type** legt fest, welcher Messwert in das Item geschrieben wird. Gültige Werte sind
**temperature** und **co2**.


Beispiele
=========

::

    co2:

        temperature:
            type: num
            co2meter_data_type: temperature

        co2:
            type: num
            co2meter_data_type: co2
