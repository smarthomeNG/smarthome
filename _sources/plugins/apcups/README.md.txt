# APC UPS

## Requirements

A running **apcupsd** with configured netserver (NIS). The plugin retrieves the information via network from the netserver. No local apcupsd is required.
The apcupsd package must be installed also on the local system (running daemon is not required). The plugin uses the **apcaccess** helper tool from the package.

If running the daemon locally and using the netserver, then the ``/etc/apcupsd/apcupsd.conf`` should contain additionally the following entries:

```
NETSERVER on
NISPORT 3551
NISIP 127.0.0.1
```

## Supported Hardware

Should work on all APC UPS devices. Tested only on a "smartUPS".

## Configuration

### plugin.yaml

Add the following lines to activate the plugin:

```yaml
ApcUps:
    plugin_name: apcups
    host: localhost
    port: 3551
```

Description of the attributes:

* __host__: ip address of the NIS (optional, default: localhost)
* __port__: port of the NIS (optional, default: 3551)
* __cycle__: time to update the items with values from apcaccess

### items.yaml

There is only one attribute: **apcups**

For a list of values for this attribute call "apcaccess" on the command line. This command will give back a text block containing a list of ``statusname : value`` entries like the following:

```
APC      : 001,050,1127
DATE     : 2017-11-02 07:59:15 +0100
HOSTNAME : sh11
VERSION  : 3.14.12 (29 March 2014) debian
UPSNAME  : UPS_IDEN
CABLE    : Ethernet Link
DRIVER   : PCNET UPS Driver
UPSMODE  : Stand Alone
STARTTIME: 2017-11-02 07:59:11 +0100
MODEL    : Smart-UPS 1400 RM
STATUS   : ONLINE
LINEV    : 227.5 Volts
LOADPCT  : 31.2 Percent
BCHARGE  : 100.0 Percent
TIMELEFT : 30.0 Minutes
MBATTCHG : 10 Percent
MINTIMEL : 5 Minutes
MAXTIME  : 0 Seconds
MAXLINEV : 227.5 Volts
MINLINEV : 226.0 Volts
OUTPUTV  : 227.5 Volts
SENSE    : High
DWAKE    : 0 Seconds
DSHUTD   : 120 Seconds
DLOWBATT : 2 Minutes
LOTRANS  : 208.0 Volts
HITRANS  : 253.0 Volts
RETPCT   : 0.0 Percent
ITEMP    : 25.6 C
ALARMDEL : Low Battery
BATTV    : 27.7 Volts
LINEFREQ : 49.8 Hz
LASTXFER : Line voltage notch or spike
NUMXFERS : 0
TONBATT  : 0 Seconds
CUMONBATT: 0 Seconds
XOFFBATT : N/A
SELFTEST : NO
STESTI   : 336
STATFLAG : 0x05000008
REG1     : 0x00
REG2     : 0x00
REG3     : 0x00
MANDATE  : 08/16/00
SERIALNO : GS0034003173
BATTDATE : 06/20/15
NOMOUTV  : 230 Volts
NOMBATTV : 24.0 Volts
EXTBATTS : 0
FIRMWARE : 162.3.I
END APC  : 2017-11-02 08:00:39 +0100
```

The plugin will check the items type. If the type is a string, then the value will we returned as a string (e.g. status "ONLINE").
If it is of type num, then the item will be set to a float. To convert to a float, the returned string will be cut after first space and the converted (e.g. 235 Volt = 235).

### Example

The example below will read the keys **LINEV**, **STATUS** and **TIMELEFT** and returns their values.

```yaml
# items/apcups.yaml
serverroom:

    apcups:

        linev:
            visu_acl: ro
            type: num
            apcups: linev

        status:
            # will be 'ONLINE', 'ONBATT', or in case of a problem simply empty
            visu_acl: ro
            type: str
            apcups: status

        timeleft:
            visu_acl: ro
            type: num
            apcups: timeleft
```

**type** depends on the values.

### Status Report Fields

Due to a look into this http://apcupsd.org/manual/manual.html#configuration-examples file the meaning of the above variables are as follows

```
APC
    Header record indicating the STATUS format revision level, the number of records that follow the APC statement, and the number of bytes that follow the record.
DATE
    The date and time that the information was last obtained from the UPS.
HOSTNAME
    The name of the machine that collected the UPS data.
UPSNAME
    The name of the UPS as stored in the EEPROM or in the UPSNAME directive in the configuration file.
VERSION
    The apcupsd release number, build date, and platform.
CABLE
    The cable as specified in the configuration file (UPSCABLE).
MODEL
    The UPS model as derived from information from the UPS.
UPSMODE
    The mode in which apcupsd is operating as specified in the configuration file (UPSMODE)
STARTTIME
    The time/date that apcupsd was started.
STATUS
    The current status of the UPS (ONLINE, ONBATT, etc.)
LINEV
    The current line voltage as returned by the UPS.
LOADPCT
    The percentage of load capacity as estimated by the UPS.
BCHARGE
    The percentage charge on the batteries.
TIMELEFT
    The remaining runtime left on batteries as estimated by the UPS.
MBATTCHG
    If the battery charge percentage (BCHARGE) drops below this value, apcupsd will shutdown your system. Value is set in the configuration file (BATTERYLEVEL)
MINTIMEL
    apcupsd will shutdown your system if the remaining runtime equals or is below this point. Value is set in the configuration file (MINUTES)
MAXTIME
    apcupsd will shutdown your system if the time on batteries exceeds this value. A value of zero disables the feature. Value is set in the configuration file (TIMEOUT)
MAXLINEV
    The maximum line voltage since the UPS was started, as reported by the UPS
MINLINEV
    The minimum line voltage since the UPS was started, as returned by the UPS
OUTPUTV
    The voltage the UPS is supplying to your equipment
SENSE
    The sensitivity level of the UPS to line voltage fluctuations.
DWAKE
    The amount of time the UPS will wait before restoring power to your equipment after a power off condition when the power is restored.
DSHUTD
    The grace delay that the UPS gives after receiving a power down command from apcupsd before it powers off your equipment.
DLOWBATT
    The remaining runtime below which the UPS sends the low battery signal. At this point apcupsd will force an immediate emergency shutdown.
LOTRANS
    The line voltage below which the UPS will switch to batteries.
HITRANS
    The line voltage above which the UPS will switch to batteries.
RETPCT
    The percentage charge that the batteries must have after a power off condition before the UPS will restore power to your equipment.
ITEMP
    Internal UPS temperature as supplied by the UPS.
ALARMDEL
    The delay period for the UPS alarm.
BATTV
    Battery voltage as supplied by the UPS.
LINEFREQ
    Line frequency in hertz as given by the UPS.
LASTXFER
    The reason for the last transfer to batteries.
NUMXFERS
    The number of transfers to batteries since apcupsd startup.
XONBATT
    Time and date of last transfer to batteries, or N/A.
TONBATT
    Time in seconds currently on batteries, or 0.
CUMONBATT
    Total (cumulative) time on batteries in seconds since apcupsd startup.
XOFFBATT
    Time and date of last transfer from batteries, or N/A.
SELFTEST

    The results of the last self test, and may have the following values:

        OK: self test indicates good battery
        BT: self test failed due to insufficient battery capacity
        NG: self test failed due to overload
        NO: No results (i.e. no self test performed in the last 5 minutes)

STESTI
    The interval in hours between automatic self tests.
STATFLAG
    Status flag. English version is given by STATUS.
DIPSW
    The current dip switch settings on UPSes that have them.
REG1
    The value from the UPS fault register 1.
REG2
    The value from the UPS fault register 2.
REG3
    The value from the UPS fault register 3.
MANDATE
    The date the UPS was manufactured.
SERIALNO
    The UPS serial number.
BATTDATE
    The date that batteries were last replaced.
NOMOUTV
    The output voltage that the UPS will attempt to supply when on battery power.
NOMINV
    The input voltage that the UPS is configured to expect.
NOMBATTV
    The nominal battery voltage.
NOMPOWER
    The maximum power in Watts that the UPS is designed to supply.
HUMIDITY
    The humidity as measured by the UPS.
AMBTEMP
    The ambient temperature as measured by the UPS.
EXTBATTS
    The number of external batteries as defined by the user. A correct number here helps the UPS compute the remaining runtime more accurately.
BADBATTS
    The number of bad battery packs.
FIRMWARE
    The firmware revision number as reported by the UPS.
APCMODEL
    The old APC model identification code.
END APC
    The time and date that the STATUS record was written.
```
