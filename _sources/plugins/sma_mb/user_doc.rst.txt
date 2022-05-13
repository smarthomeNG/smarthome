.. index:: Plugins; sma_mb (SMA-Modbus)
.. index:: sma_mb

======
sma_mb
======

Dieses Plugin liest die aktuellen Werte eines SMA-Wechselrichters per SMA Speedwire Feldbus/Modbus aus.


Anforderungen
=============

Im Wechselrichter das Modbusprotokol aktivieren (ist normalerweise Standardeinstellung).

Infos zum SMA-Modbus-Interface sind auf der
`Herstellerseite <https://my.sma-service.com/s/article/SMA-Modbus-Interface-SMA-SunSpec-Modbus-Interface>`_
zu finden


Notwendige Software
-------------------

Folgende Python Packages werden benötigt:

* pymodbus >= 2.3.0


Unterstützte Geräte
-------------------

Folgende Hardware wird durch das Plugin unterstützt:

* SMA Wechselrichter Sunny Boy SB3000TL-21


Konfiguration
=============

Die Konfiguration kann über die Admin GUI vorgenommen werden. (Bitte daran denken, das Plugin auf **enabled** zu setzen)

Die Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind unter
:doc:`/plugins_doc/config/sma_mb` beschrieben.


plugin.yaml
-----------

.. code-block:: yaml

    SMAModbus:
        plugin_name: sma_mb
        #instance: si44    # Name des Wechselrichters, nur bei mehreren laufenden Plugin Instanzen angeben
        host: <IP Adresse reinschreiben>    # z.B.: 192.168.xxx.xxx
        # port: 502        # optional: Port nummer auf dem Host
        # cycle: 150       # optional: Zyklus Zeit zur Abfrage in Sekunden


items.yaml
----------

.. code-block:: yaml

    sb3000tl:

        serialnumber:
            type: num
            visu_acl: ro
            smamb_register: 30057
            smamb_datatype: U32

        status:
            type: num
            visu_acl: ro
            smamb_register: 30201
            smamb_datatype: U32

        iso:
            type: num
            visu_acl: ro
            smamb_register: 30225
            smamb_datatype: U32

        relais:
            type: num
            visu_acl: ro
            smamb_register: 30217
            smamb_datatype: U32

        ac_energy_total:
            type: num
            visu_acl: ro
            smamb_register: 30529
            smamb_datatype: U32

        ac_energy_day:
            type: num
            visu_acl: ro
            smamb_register: 30535
            smamb_datatype: U32

        time_work:
            type: num
            visu_acl: ro
            smamb_register: 30541
            smamb_datatype: U32

        power:
            type: num
            visu_acl: ro
            smamb_register: 30775
            smamb_datatype: S32
