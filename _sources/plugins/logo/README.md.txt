# logo

## Requirements
Siemens LOGO PLC

libnodave - a free library to communicate to Siemens S7 PLCs
used version: 0.8.4.6

raspberry.pi: copy the file 'libnodave.so' to '/lib/libnodave.so'
sudo cp /usr/smarthome/plugins/logo/libnodave.so /lib/libnodave.so

other machines: download the library  and run 'make'
http://libnodave.sourceforge.net/

NOTE: The library libnodave runs only on 32-bit machines!!

Version 1.2.1
The version is not tested with new multi-instance functionality of SmartHomeNG.

There is a new plugin in development which uses snap7. Details can be found 
in support thread at https://knx-user-forum.de/forum/supportforen/smarthome-py/36372-plugin-siemens-logo-0ba7

## Supported Hardware

Siemens LOGO version 0BA7
Siemens LOGO version 0BA8

## Configuration

### plugin.yaml

Sample configuration file for two instances of the logo plugin.

```yaml
logo1:
    class_name: LOGO
    class_path: plugins.logo
    host: 10.10.10.99
    instance: logo1
    # port: 102
    # io_wait: 5
    # version: 0BA8
logo2:
    class_name: LOGO
    class_path: plugins.logo
    host: 10.10.10.100
    version: 0BA8
    instance: logo2
    # port: 102
    # io_wait: 5
```

This plugin needs an host attribute and you could specify a port attribute

'instance' = give the instance a name (e.g.'logo1') for multiinstance

* 'io_wait' = timeperiod between two read requests. Default 5 seconds.

* 'version' = Siemens Hardware Version. Default 0BA7

### items.yaml

#### logo_read@logo1
Input, Output, Mark to read from Siemens Logo
@logo1 instancename

#### logo_write@logo1
Input, Output, Mark to write to Siemens Logo
@logo1 instancename

* 'I' Input bit to read I1, I2 I3,.. (max I24)
* 'Q' Output bit to read/write Q1, Q2, Q3,.. (0BA7 max Q16; OBA8 max Q20)
* 'M' Mark bit to read/write M1, M2 M3,.. (0BA7 max M27; OBA8 max M64)
* 'AI' Analog Input(word) to read AI1, AI2, AI3,.. (max AI8)
* 'AQ' Analog Output(word) to read/write AQ1, AQ2,.. (0BA7 max AQ2; OBA8 max AQ8)
* 'AM' Analog Mark(word) to read/write AM1, AM2, AM3,.. (0BA7 max AM16; OBA8 max AM64)
* 'NI' Network Input bit to read NI1, NI2,.. (OBA8 max NI64)
* 'NAI' Network Analog Input (word) to read NAI1, NAI2,.. (OBA8 max NAI32)
* 'NQ' Network Output bit to read NQ1, NQ2,.. (OBA8 max NQ64)
* 'NAQ' Network Analog Output (word) to read NAQ1, NAQ2,.. (OBA8 max NAQ16)
* 'VM' VM-Byte to read/write VM0, VM1, VM3,.. VM850
* 'VMx.x' VM-Bit to read/write VM0.0, VM0.7, VM3.4,.. VM850.7
* 'VMW' VM-Word to read/write VMW0, VM2, VMW4,.. VM849

```yaml
myroom:

    status_I1:
        typ: bool
        logo_read@logo1: "I1    ## read the Input I1 from Logo-Instance 'logo1'"
        logo_read@logo2: "I1    ## read the Input I1 from Logo-Instance 'logo2'"

    lightM1:
        typ: bool
        knx_dpt: 1
        knx_listen: 1/1/3
        knx_init: 1/1/3
        logo_write@logo1: "M4    ## write the Mark M4 to Logo-Instance 'logo1'"

    temp_measure:
        typ: num
        eval: value/10
        visu: 'yes'
        sqlite: 'yes'
        logo_read@logo1: "AI1    ## read the Analog Input AI1 from Logo-Instance 'logo1'"

    temp_set:
        typ: num
        visu: 'yes'
        logo_write@logo1: "VMW4    ## write the VM-Word VM4 to Logo-Instance 'logo1'"
```
