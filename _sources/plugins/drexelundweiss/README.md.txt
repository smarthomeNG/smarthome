# Drexel & Weiss

This plugin uses the D&W USB service interface for connection, so you don't need the additional modbusadapter. Be careful not to configure wrong parameters, otherwise the function of your device may be damaged. The D&W warranty is not including this case of damage!

## Changelog

1.5.3:
* Improve line ending handling
* Add possibility to use PANEL PCB (for room temperature, etc.)
* Minor improvements for logging, etc.
* Web documentation instead of README

1.5.2:
* Added aerosilent exos
* Updated README

1.5.1:
* Adapted plugin to use newer functions and logging parameters

1.3.0:
* Ignore wrong device info and use backup device id (set correct number for your DuW device from list below)
* Retry reading lines to prevent wrong data (set value in conf file)
* Catch division by zero errors
* expanded config file for x2 plus. See http://filter.drexel-weiss.at/HP/Upload/Dateien/900.6667_00_TI_Modbus_Parameter_V4.01_DE.pdf for further parameters
* Plugin is smart so you can use seperate logging level in logging.yaml
* Fixed some code
* Added example config file in plugins folder


## Supported Devices

The plugin detects the connected device type automatically:

   * aerosilent bianco: 13
   * aerosilent business: 15
   * aerosilent centro: 8
   * aerosilent exos: 25
   * aerosilent micro: 3
   * aerosilent primus: 1
   * aerosilent stratos: 17
   * aerosilent topo: 2
   * aerosmart l: 6
   * aerosmart m: 5
   * aerosmart s: 4
   * aerosmart mono: 11
   * aerosmart xls: 7
   * termosmart sc: 9
   * X²: 10
   * X² Plus: 14

## Configuration

### plugin.yaml

```yaml
DuW:
    class_name: DuW
    class_path: plugins.drexelundweiss
    tty: /dev/ttyUSB0
    # Busmonitor: 1
    # LU_ID: 130
    # WP_ID: 140
    # device: 14 # x2 plus as standard device
    # retrylimit: 100 # number of retries to get answer right
```

You have to adapt the tty to your local environment and change LU_ID and WP_ID if not D&W default is used.
Busmonitor mode will output all activity on Service Interface to smarthome.py log if started in debug mode, default is Busmonitor off.

### items.yaml

#### DuW_LU_register / DuW_WP_register

With these attributes you could specify the D&W register ID found in the modbus documentation of D&W (900.6666_00_TI_Modbus_Parameter_DE.pdf)
Depending on which PCB you want to address use WP or LU attribute. The Plugin will ignore write attempts on read only registers.
If the value of the item is getting out of the configured register range, then the value will be ignored by the plugin.
Values are calculated automatically regarding the register depending divisor and comma setting, e.g. DuW_LU_register = 200 will result in a item value = 18,5

#### Example

```yaml
KWL:

    MODE:
        name: Betriebsart
        visu_acl: rw
        type: num
        DuW_LU_register: 5002
        sv_widget: "{{ basic.slider('item', 'item', 0, 5, 1) }}"
```

A full .yaml file example can be found in plugin folder.

## Functions

None so far
