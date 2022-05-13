# PLUGGIT

## Requirements

This plugin is based on the lib pymodbus (branch python3):
https://github.com/bashwork/pymodbus
https://github.com/bashwork/pymodbus/tree/python3

## Supported Hardware

It is currently working and tested with:

  * Pluggit AP310

## Configuration

### plugin.yaml

The plugin can be configured like this:

```yaml
pluggit:
    class_name: Pluggit
    class_path: plugins.pluggit
    host: 192.168.0.222
    # cycle: 300
```

This plugin retrieves data from the KWL Pluggit AP310 based on the modbus register description from the official pluggit homepage ( http://www.pluggit.com/portal/de/faq/bms-building-management-system/verbindung-mit-building-management-system-9737 )

The data retrieval is done by establishing a modbus tcp network connection via modbus port 502.
You need to configure the host (or IP) address of your pluggit KWL.

The cycle parameter defines the update interval and defaults to 300 seconds.

### items.yaml

#### pluggit

This attribute references the information to retrieve by the plugin.
The following list of information can be specified:

  * prmRamIdxUnitMode: Active Unit mode> 0x0004 Manual Mode; 0x0008 WeekProgram
  * prmNumOfWeekProgram: Number of the Active Week Program (for Week Program mode)
  * prmRomIdxSpeedLevel: Speed level of Fans in Manual mode; shows a current speed level [4-0]; used for changing of the fan speed level
  * prmFilterRemainingTime: Remaining time of the Filter Lifetime (Days)
  * prmRamIdxT1: Frischluft temperature in degree
  * prmRamIdxT2: Zuluft temperature in degree
  * prmRamIdxT3: Abluft temperature in degree
  * prmRamIdxT4: Fortluft temperature in degree
  * prmRamIdxBypassActualState: Bypass state> Closed 0x0000; In process 0x0001; Closing 0x0020; Opening 0x0040; Opened 0x00FF
  * activatePowerBoost: bool variable that changes the Unit Mode to manual mode and sets the fan speed level to the highest level (4)

#### Example

Example configuration which shows the current unit mode, the actual week program, the fan speed, the remaining filter lifetime and the bypass state.

```yaml
pluggit:
    type: foo

    unitMode:
        type: str
        visu_acl: ro
        enforce_updates: 'true'
        pluggit_listen: prmRamIdxUnitMode

    weekProgram:
        type: num
        visu_acl: ro
        enforce_updates: 'true'
        pluggit_listen: prmNumOfWeekProgram

    fanSpeed:
        type: num
        visu_acl: ro
        enforce_updates: 'true'
        pluggit_listen: prmRomIdxSpeedLevel

    remainingFilterLifetime:
        type: num
        visu_acl: ro
        enforce_updates: 'true'
        pluggit_listen: prmFilterRemainingTime

    frischluft:
        type: num
        visu_acl: ro
        enforce_updates: 'true'
        pluggit_listen: prmRamIdxT1

    zuluft:
        type: num
        visu_acl: ro
        enforce_updates: 'true'
        pluggit_listen: prmRamIdxT2

    abluft:
        type: num
        visu_acl: ro
        enforce_updates: 'true'
        pluggit_listen: prmRamIdxT3

    fortluft:
        type: num
        visu_acl: ro
        enforce_updates: 'true'
        pluggit_listen: prmRamIdxT4

    bypassState:
        type: str
        visu_acl: ro
        enforce_updates: 'true'
        pluggit_listen: prmRamIdxBypassActualState

    activatePowerBoost:
        type: bool
        visu_acl: rw
        enforce_updates: 'true'
        pluggit_send: activatePowerBoost
```

## logic.yaml

No logic related stuff implemented.

## Methods

No methods provided currently.
