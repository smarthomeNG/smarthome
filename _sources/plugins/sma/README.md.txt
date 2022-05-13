# SMA

## Requirements

bluez

install by

```bash
$ apt-get install bluez python-gobject python-dbus
$ hcitool scan
Scanning ...
        <bt-addr>       <name of your inverter, e.g. 'SMA001d SN: 213000xxxx SN213000xxxx'>
$ bluez-simple-agent hci0 <bt-addr>
RequestPinCode (/org/bluez/3070/hci0/dev_bt_addr_underscores)
Enter PIN Code: <pin-code>
Release
New device (/org/bluez/3070/hci0/dev_bt_addr_underscores)
$ bluez-test-device trusted <bt-addr> yes
$ bluez-test-device list
```

### Supported Hardware

Tested with:
* SMA SunnyBoy 5000TL-21
* SMA Sunny Tripower 8000TL-10
* SMA Sunny Tripower 12000TL-10

Should work with other SMA inverters as well - please let me know!

## Configuration

### plugin.yaml

```yaml
sma:
    class_name: SMA
    class_path: plugins.sma
    bt_addr: 00:80:25:21:7F:58
    # password = 0000
    # update_cycle = 60
    # allowed_timedelta = 10
```

Description of the attributes:

* __bt_addr__: MAC-address of the inverter (find out with 'hcitool scan')
* __password__: password for accessing the inverter in user-mode (default 0000)
* __update_cycle__: interval in seconds how often the data is read from the inverter (default 60)
* __allowed_timedelta__: allowed difference of inverter to system time - if above, inverter is set to system time - set to -1 to disable (default 60)

### items.yaml

The item having ``sma = PLUGIN_ACTIVE`` can be set to True/False in order to connect/disconnect to the inverter during night.

```yaml
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

    Serial_Number:
        type: num
        sma: INV_SERIAL

    MAC_Address:
        type: str
        sma: INV_ADDRESS

    Last_Update_Of_Data:
        type: str
        sma: LAST_UPDATE

    DC_Power_String1_in_W:
        type: num
        sma: DC_STRING1_P

    DC_Power_String2_in_W:
        type: num
        sma: DC_STRING2_P

    DC_Voltage_String1_in_V:
        type: num
        sma: DC_STRING1_U

    DC_Voltage_String2_in_V:
        type: num
        sma: DC_STRING2_U

    DC_Current_String1_in_A:
        type: num
        sma: DC_STRING1_I

    DC_Current_String2_in_A:
        type: num
        sma: DC_STRING2_I

    Operating_Time_in_s:
        type: num
        sma: OPERATING_TIME

    Feeding_Time_in_s:
        type: num
        sma: FEEDING_TIME

    Grid_Frequency_in_Hz:
        type: num
        sma: GRID_FREQUENCY

    Inverter_Status:
        type: str
        sma: STATUS

    Relais_Status:
        type: str
        sma: GRID_RELAY

    Software_Version:
        type: str
        sma: SW_VERSION
```
