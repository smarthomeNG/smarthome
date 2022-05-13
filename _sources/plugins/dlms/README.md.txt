# DLMS

## Requirements

* smartmeter using DLMS (Device Language Message Specification) IEC 62056-21
* USB IR-Reader e.g. from volkszaehler.org

install with
```
sudo python3 -m pip install pyserial
```

make sure the serial port can be used by the user executing smarthome.py

Example for a recent version of the Volkszaehler IR-Reader, please adapt the vendor- and product-id for your own readers:

```
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", ATTRS{serial}=="0092C9FE", MODE="0666", GROUP="dialout", SYMLINK+="dlms0"' > /etc/udev/rules.d/11-dlms.rules
udevadm trigger
```

If you like, you can also give the serial port a descriptive name with this.

### Optional:

A script ``get_manufacturer_ids.py`` is provided. Upon execution within the directory of ``plugins/dlms`` this script 
loads an XLSX file with list of known manufacturers from 
``https://www.dlms.com/srv/lib/Export_Flagids.php``, reads the ids and the corresponding manufacturer for convenience 
and finally write a YAML file to ``manufacturer.yaml``

The main module will use the ``manufacturer.yaml`` if it's existing to output more information for debug purposes


### Supported Hardware

* smart meters using using DLMS (Device Language Message Specification) IEC 62056-21
* e.g. Landis & Gyr ZMD120

## Configuration

### plugin.yaml

```
dlms:
    class_name: DLMS
    class_path: plugins.dlms
    serialport: /dev/dlms0
    update_cycle: 900
    # SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"10c4\", ATTRS{idProduct}==\"ea60\", ATTRS{serial}==\"0092C9FE\", MODE=\"0666\", GROUP=\"dialout\", SYMLINK+=\"dlms0\"
```

Description of the attributes:

* __serialport__: gives the serial port for the dlms query
* __update_cycle__: interval in seconds how often the data is read from the meter - be careful not to set a shorter interval than a read operation takes (default: 300)


### Setup procedure:

Start the plugin in **standalone mode** with a shell from the plugins directory e.g. **/usr/local/smarthome/plugins/dlms** with
**python3 dlms.py _serialport_**

Copy the given obis codes to your item configuration to help generate items as needed

### items.yaml

You can use all obis codes available by the meter.

Attributes:
* __dlms_obis_code__: obis code such as 'x.y', 'x.y.z' or 'x.y.z*q' plus a specifier which value to read, the type must match the conversion from OBIS value (str, num, foo)
* __dlms_obis_readout__: value irrelevant, the item will need to be of ``type: str`` at it receives the full readout of the smartmeter

## Some background information on OBIS Codes

OBIS codes are a combination of six value groups, which describe in a hierarchical way 
the exact meaning of each data item

| value group | meaning |
| --- | --- |
| A | characteristic of the data item to be identified (abstract data, electricity-, gas-, heat-, water-related data)
| B | channel number, i.e. the number of the input of a metering equipment having several inputs for the measurement of energy of the same or different types (e.g. in data concentrators, registration units). Data from different sources can thus be identified. The definitions for this value group are independent from the value group A.
| C | abstract or physical data items related to the information source concerned, e.g. current , voltage , power, volume, temperature. The definitions depend on the value of the value group A .  Measurement, tariff processing and data storage methods of these quantities are defined by value groups D, E and F For abstract data, the hierarchical structure of the 6 code fields is not applicable. |
| D | types, or the result of the processing of physical quantities identified with the value groups A and C, according to various specific algorithms. The algorithms can deliver energy and demand quantities as well as other physical quantities.
| E | further processing of measurement results identified with value groups A to D to tariff registers, according to the tariff(s) in use. For abstract data or for measurement results for which tariffs are not relevant, this value group can be used for further classification.
| F | the storage of data, identified by value groups A to E, according to different billing periods. Where this is not relevant, this value group can be used for further classification.
 
A sample single line may look like ``A-B:C.D.E*F(Value*Unit)(another Value)``.  
Parts **A** and **B** are optional as well as **E** and **F**. The second value may be omitted as well as the unit from the first value.
Every smartmeter readout will look different. The way how to interpret the values is not prescribed in
the file itself. It's in the smartmeters specification but one can guess also which is the best fit. 

See the follwing examples to get an idea about the differences:

### OBIS code example A
Some first lines of a sample OBIS Code readout for a **Landis & Gyr ZMD 310** Smartmeter for industrial purposes
```
1-1:F.F(00000000)
1-1:0.0.0(50871031)
1-1:0.0.1(50871031)
1-1:0.9.1(155420)
1-1:0.9.2(170214)
1-1:0.1.2(0000)
1-1:0.1.3(170201)
1-1:0.1.0(18)
1-1:1.2.1(0451.17*kW)
1-1:1.2.2(0451.17*kW)
1-1:2.2.1(0060.24*kW)
1-1:2.2.2(0060.24*kW)
1-1:1.6.1(27.19*kW)(1702090945)
1-1:1.6.1*18(28.74)(1701121445)
1-1:1.6.1*17(28.95)(1612081030)
1-1:1.6.1*16(25.82)(1611291230)
1-1:1.8.0(00051206*kWh)
1-1:1.8.0*18(00049555)
1-1:1.8.0*17(00045862)
...
```

### OBIS code example B

Sample OBIS Code readout from a relative simple **Pafal 12EC3g** smartmeter
```
0.0.0(72044837)(72044837)
0.0.1(PAF)(PAF)
F.F(00)(00)
0.2.0(1.29)(1.29)
1.8.0*00(000783.16)(000783.16)
2.8.0*00(000045.38)(000045.38)
C.2.1(000000000000)(                                                )(000000000000)(                                                )
0.2.2(:::::G11)!(:::::G11)(!)
```

### Getting Values from Codelines

Comparing the above examples it is obvious that the basically same OBIS Code has different appearances. 

| Example A | Example B |
| :---: | :---: |
| 1-1:F.F(00000000) | F.F(00)(00) |
| 1-1:1.8.0(00051206*kWh) | 1.8.0*00(000783.16)(000783.16) |

To get the value from ``1-1:1.8.0(00051206*kWh)`` into the item we write in the items config file 
```
dlms_obis_code: 
    - '1-1:1.8.0'
    - 0
    - 'Value'
    - 'num'
```
This will get the first value in parentheses and cast it into a numeric value.

To get the value from ``1.8.0*00(000783.16)(000783.16)`` into the item we write in the items config file 
```
dlms_obis_code: 
    - '1.8.0*00'
    - 0
    - 'Value'
    - 'num'
```
This will too get the first value in parentheses and cast it into a numeric value.

To get the unit from ``1-1:1.8.0(00051206*kWh)`` into another item we write 
```yaml
dlms_obis_code: 
    - '1-1:1.8.0'
    - 0
    - 'Unit'
    - 'str'
``` 

into the item.yaml.


A sample item.yaml for example **A** might look like following:

```yaml
Stromzaehler:
    Auslesung:
        type: str
        dlms_obis_readout: yes
    Seriennummer:
        type: str
        dlms_obis_code: 
            - '1-1:0.0.0
            - 0
            - 'Value' 
            - 'str'

    Ablesung:
        # Datum und Uhrzeit der letzten Ablesung
        Uhrzeit:
            type: foo
            dlms_obis_code: 
              - '1-1:0.9.1'
              - 0
              - 'Value'
              - 'Z6'
        Datum:
            type: foo
            dlms_obis_code: 
              - '1-1:0.9.2'
              - 0
              - 'Value'
              - 'D6'
        Datum_Aktueller_Abrechnungsmonat:
            type: foo
            dlms_obis_code: 
              - '1-1:0.1.3'
              - 0
              - 'Value'
              - 'D6'
        Monatszaehler:
            # Billing period counter
            type: num
            dlms_obis_code: 
              - '1-1:0.1.0'
              - 0
              - 'Value'
              - 'num'
            
    Bezug:
        Energie:
            type: num
            sqlite: yes
            dlms_obis_code: 
              - '1-1:1.8.1'
              - 0
              - 'Value'
              - 'num'
              
        Energie_Einheit:
            type: str
            sqlite: yes
            dlms_obis_code: 
              - '1-1:1.8.1'
              - 0
              - 'Unit'
              - 'str'

    Lieferung:
        Energie:
            type: num
            sqlite: yes
            dlms_obis_code: 
              - '1-1:2.8.1'
              - 0
              - 'Value'
              - 'num'

        Energie_Einheit:
            type: str
            sqlite: yes
            dlms_obis_code: 
              - '1-1:2.8.1'
              - 0
              - 'Unit'
              - 'str'
```
The basic syntax of the **dlms_obis_code** attributes value is
```
dlms_obis_code: 
    - 1-1:1.6.2*01
    - Index
    - 'Value' or 'Unit'
    - Value Type
```
where

* __Index__ is the number of the value group you want to read
* __Value__ or __Unit__  whether you are interested in the value (mostly) or the unit like **kWh**
* __Value Type__ can be one of 
    * __Z6__ (time coded with hhmmss), 
    * __Z4__ (time coded with hhmm), 
    * __D6__ (date coded with YYMMDD),
    * __ZST10__ (date and time coded with YYMMDDhhmm),
    * __ZST12__ (date and time coded with YYMMDDhhmmss), 
    * __str__, a string
    * __float__, a floating point number
    * __int__ an integer
    * __num__ a number either float or int
    
For any Value Type with ``time`` or ``date`` the python datetime will be used. 
That implies that you use ``type: foo`` for the items attribute in the respective item.yaml
 
| OBIS A | meaning |
| --- | --- |
|0 | Abstract Objects |
|1 | Electricity related objects|



