.. index:: Plugins; drexelundweiss
.. index:: drexelundweiss

==============
drexelundweiss
==============

Einführung
==========

Dieses Plugin ermöglicht es, Drexel und Weiß Geräte (Wärmepumpen) direkt über USB ohne Modbusadapter zu steuern.

.. important::

    Vorsicht vor falsch eingestellten Parametern! Das Gerät könnte beschädigt werden und die Garantie wird etwaige Schäden nicht decken!

Folgende Geräte werden unterstützt. Sie sollten generell automatisch erkannt werden. Falls dies nicht klappt, ist die entsprechende Device Nummer in der Pluginkonfiguration anzugeben.

- aerosilent bianco: 13
- aerosilent business: 15
- aerosilent centro: 8
- aerosilent exos: 25
- aerosilent micro: 3
- aerosilent primus: 1
- aerosilent stratos: 17
- aerosilent topo: 2
- aerosmart l: 6
- aerosmart m: 5
- aerosmart s: 4
- aerosmart mono: 11
- aerosmart xls: 7
- termosmart sc: 9
- X²: 10
- X² Plus: 14


Konfiguration
=============

.. important::

      Detaillierte Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/drexelundweiss` zu finden.


.. code-block:: yaml

    # etc/plugin.yaml
    drexelundweiss:
        plugin_name: drexelundweiss
        tty: /dev/ttyUSB0
        #PANEL_ID: 120
        #LU_ID: 130
        #WP_ID: 140
        #device: 0
        #busmonitor: false
        #retrylimit: 100

Der Busmonitor Modus schreibt alle Aktivitäten am Service Interface in ein Logfile, sofern Smarthome im Debugmodus gestartet wurde.


Items Attribute
===============

Die möglichen Itemattribute sind:

- DuW_LU_register
- DuW_WP_register
- DuW_PANEL_register

Damit wird spezifiziert, welche Register ID laut Modbus Dokumentation genutzt werden soll. LU sollte für Adressen bezüglich Lüftung, WP für die Wärmepumpe und PANEL für ein Wandpanel genutzt werden.

Das Plugin wird Schreibversuche auf reine Read Only Register ignorieren, ebenso Schreibversuche von Werten, die sich außerhalb der konfigurierten Registerspanne befinden.

Werte werden automatisch auf Basis der Divisor und Comma Einstellungen im entsprechenden Textfile berechnet und formatiert. Beispiel DuW_LU_register = 200 erhält beispielsweise den Wert 18,5.

Beispiel:

.. code-block:: yaml

    # items/my.yaml
    KWL:
        MODE:
            name: Betriebsart
            visu_acl: rw
            type: num
            DuW_LU_register: 5002
