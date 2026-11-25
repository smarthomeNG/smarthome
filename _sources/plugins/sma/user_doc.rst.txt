.. index:: Plugins; sma
.. index:: sma

===
sma
===

Das Plugin liest Messwerte von SMA-Wechselrichtern über Bluetooth aus.

Getestet wurde es mit folgenden Geräten:

- SMA SunnyBoy 5000TL-21
- SMA Sunny Tripower 8000TL-10
- SMA Sunny Tripower 12000TL-10

Andere SMA-Wechselrichter mit Bluetooth-Schnittstelle sollten ebenfalls funktionieren.


Voraussetzungen
================

Für die Bluetooth-Kommunikation wird ``bluez`` benötigt::

    apt-get install bluez python-gobject python-dbus

Der Wechselrichter muss einmalig mit dem System gekoppelt werden::

    hcitool scan
    # Scanning ...
    #     <bt-addr>    <Name des Wechselrichters, z.B. 'SMA001d SN: 213000xxxx SN213000xxxx'>
    bluez-simple-agent hci0 <bt-addr>
    # RequestPinCode (...)
    # Enter PIN Code: <PIN>
    bluez-test-device trusted <bt-addr> yes
    bluez-test-device list


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/sma` beschrieben.


Beispiele
=========

::

    Inverter:

        Plugin_active:
            type: bool
            sma: PLUGIN_ACTIVE

        Feeding_Power_in_W:
            type: num
            sma: AC_P_TOTAL

        Daily_Yield_in_Wh:
            type: num
            sma: E_DAY

        Total_Yield_in_Wh:
            type: num
            sma: E_TOTAL

        Inverter_Status:
            type: str
            sma: STATUS

Das Item mit dem Attribut ``sma: PLUGIN_ACTIVE`` kann auf ``True``/``False`` gesetzt werden, um die
Verbindung zum Wechselrichter z.B. nachts zu trennen und wieder herzustellen.
