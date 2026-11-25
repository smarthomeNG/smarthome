.. index:: Plugins; comfoair
.. index:: comfoair

========
comfoair
========

Das Plugin verbindet SmartHomeNG mit einer Zehnder ComfoAir Lüftungsanlage mit Wärmerückgewinnung
(KWL) und liest bzw. schreibt deren Parameter. Primär unterstützt wird die ComfoAir 350. Baugleiche
Anlagen anderer Hersteller mit identischem Protokoll (u.a. Wernig G90-380, teilweise Paul Lüftung)
funktionieren ebenfalls. Die Unterstützung für die ComfoAir 500 wurde ergänzt, das Protokoll ist
dafür aber noch nicht vollständig untersucht.

Die Verbindung zur Anlage erfolgt entweder per TCP (über einen TCP-zu-Seriell-Konverter, RS232 bei
der ComfoAir 350 bzw. RS485 bei der ComfoAir 500) oder über eine direkte serielle Schnittstelle am
SmartHomeNG-Host.

.. important::

   Das CC Ease Bedienpanel darf nicht parallel zum Plugin verwendet werden. Beide würden gleichzeitig
   mit der ComfoAir kommunizieren, was im schlimmsten Fall die Konfiguration der Anlage beschädigen
   kann.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/comfoair` beschrieben.

Welche Kommandos zu welchem Zeitpunkt gesendet oder gelesen werden, wird vollständig über die
Item-Attribute in der Item-Konfiguration festgelegt.

Beispiel
========

::

    kwl:
        level:
            type: num
            comfoair_send: WriteVentilationLevel
            comfoair_read: ReadCurrentVentilationLevel
            comfoair_read_afterwrite: 1 # seconds
            comfoair_trigger: ReadSupplyAirRPM
            comfoair_trigger_afterwrite: 6 # seconds
            comfoair_init: true
        supplyair:
            rpm:
                type: num
                comfoair_read: ReadSupplyAirRPM
                comfoair_read_cycle: 60 # seconds
                comfoair_init: true
        temp:
            comfort:
                type: num
                comfoair_send: WriteComfortTemperature
                comfoair_read: ReadComfortTemperature
                comfoair_read_cycle: 60 # seconds
                comfoair_init: true
            supplyair:
                type: num
                comfoair_read: ReadSupplyAirTemperature
                comfoair_read_cycle: 60 # seconds
                comfoair_init: true
            extractair:
                type: num
                comfoair_read: ReadExtractAirTemperature
                comfoair_read_cycle: 60 # seconds
                comfoair_init: true
        heatpreparationratio:
            type: num
            eval: (sh.kwl.temp.supplyair() - sh.kwl.temp.freshair()) / (sh.kwl.temp.extractair() - sh.kwl.temp.exhaustair()) * 100
            eval_trigger:
              - kwl.temp.supplyair
              - kwl.temp.freshair
              - kwl.temp.extractair
              - kwl.temp.exhaustair

Das Item **level** sendet bei einer Änderung das Kommando **WriteVentilationLevel** und liest eine
Sekunde später den neuen Wert mit **ReadCurrentVentilationLevel** zurück. Zusätzlich wird 6 Sekunden
nach der Änderung **ReadSupplyAirRPM** ausgelöst, um die aktualisierte Zulüfter-Drehzahl abzurufen.
Das Item **heatpreparationratio** berechnet den Wärmebereitstellungsgrad direkt aus anderen Items
und benötigt kein eigenes **comfoair**-Attribut.
