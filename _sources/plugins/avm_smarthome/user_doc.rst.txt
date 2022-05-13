.. index:: avm_smarthome plugin
.. index:: Plugins; avm_smarthome

=============
avm_smarthome
=============

Das Plugin dienst zur Steuerung Smarthome Devices von AVM, die mit einer Fritzbox verbunden sind und über DECT kommunizieren.
Verwendet wird das AHA-Protokoll. siehe (http://avm.de/service/schnittstellen/)


.. attention::

    Das Plugin kann parallel zum avm-Plugin verwendet werden

Reguirements
============
Das Plugin nutzt die Python Bilbliothek pyfritzhome.
Es wird die Version 0.5.1 als Minimum benötigt.
Eine händliche Installtion des aktuellen Mastern funktioniert mit:

pip3 install git+https://github.com/hthiery/python-fritzhome


Konfiguration
=============

Für die Nutzung eines avm_smarthome Devices müssen in dem entsprechenden Item die zwei Attribute ``avm_ain`` und
``avm_smarthome_data`` konfiguriert werden, wie im folgenden Beispiel gezeigt:

.. code-block:: yaml

    avm:
        smarthome:
            hkr_bathroom_og:
                name:
                    type: str
                    avm_ain: '00000 0000000'  # AIN muss mit Leerstelle angegeben werden
                    avm_smarthome_data: name

            hkr_bathroom_ug:
                type: foo
                avm_ain: '00000 0000000'  # AIN muss mit Leerstelle angegeben werden
                struct:
                  - avm_smarthome.general
                  - avm_smarthome.hkr
                  - avm_smarthome.temperatur_sensor


Dabei kann das Attribut ``avm_ain`` entweder beim Item selbst gesetzt werden oder aber einmalig beim Parent-Item, wobei das Attribut auf alle Kinder-Item vererbt wird.
Zusätzlich bringt das Plugin structs mit, die für alle Eigenschaftes der Gerätetypen "general", "hkr", "temperatur_sensor", "alert" und "switch" ein entsprechendes Item erstellt.


Historie
========

* Version 1.0.0 getestet mit FRITZ!Box 7490 (FRITZ!OS 07.12) a FRITZ!Box 7530 (FRITZ!OS 07.12) und DECT Heizkörperthermostaten


Web Interface des Plugins
=========================

Items
-----

Das Webinterface zeigt die Items an, für die eine AIN und damit ein AVM_Smarthome Device konfiguriert ist.


Devices
-------

Das Webinterface zeigt Informationen zu allen gefundenen AVM_Smarthome Devices an.


Thermostat
----------

Das Webinterface zeigt Informationen zu allen gefundenen Thermostaten an.


Relais
----------

Das Webinterface zeigt Informationen zu allen gefundenen Relais an.


Alarm
----------

Das Webinterface zeigt Informationen zu allen gefundenen Alarmgeräten an.




