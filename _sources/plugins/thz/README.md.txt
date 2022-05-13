# THZ

Plugin for Stiebel Eltron and Tecalor integrated heatpumps LWZ/THZ 30x/40x.


## Requirements

* pySerial (sudo apt-get install python-serial)
* Serial port connected to the LWZ/THZ maintenance port.
  The wiring description is provided at:
  http://robert.penz.name/heat-pump-lwz

## Supported Hardware

Tested with:
* THZ 404 SOL, software version 5.39, software IDs 5993 & 7278
* THZ 303i, software version 4.39

According to the FHEM forum (http://forum.fhem.de/index.php/topic,13132.0.html) the original Perl code also works with other heatpump models (303, 304, 403). 

## Configuration

### plugin.yaml

```
thz:
    class_name: THZ
    class_path: plugins.thz
    serial_port: /dev/ttyUSB0
    baudrate: 115200
    poll_period: 30
    min_update_period: 300
    max_update_period: 43200
```

Description of the attributes:

* __serial_port__: serial port connected to the heatpump
* __baudrate__: port speed, recent models use 115200 bps, older heatpumps may use 57600 bps or even 9600 bps
* __poll_period__: interval in seconds how often the data is read from the heatpump
* __min_update_period__: interval in seconds for updating the values changing frequently (e.g. temperature), it should be higher than the poll period
* __max_update_period__: interval in seconds for updating the values with infrequent changes (e.g. counters updated once per day)

### items.yaml

There are read-only parameters and read-write parameters.
Temperature values are in °C.
Heat and power values are provided in kWh.
For the description of the read-write parameters refer to the heatpump manual.
The parameter name includes the parameter number (i.e. the prefix pXX) described in the manual.

.. literalinclude:: thz.yaml
    :linenos:
    :language: python
    :lines: 1, 3-5
    :start-after: 3
    :end-before: 5

### Release history

* Version overhauled to be a SmartPlugin to 0.2.2

* Version renamed to 0.2.1

* beta1, Dec 17, 2016
  + new status parameters
      iconCooling
      iconService
  + new read/write parameters:
      p32hystDHW
      p34BoosterDHWTempAct
      p35PasteurisationInterval
      p35PasteurisationTemp
      p76RoomThermCorrection
      p77OutThermFilterTime
      p89DHWeco
      p99DHWmaxFlowTemp
      p99startUnschedVent
      pClockDay
      pClockMonth
      pClockYear
      pClockHour
      pClockMinute
  - removed parameters:
      p99CoolingRtDay (redundant, see p01-p03 summer mode)
      p99CoolingRtNight (redundant, see p01-p03 summer mode)

* alpha6, Aug 5, 2016
  + new read/write parameters:
      p99CoolingRtDay
      p99CoolingRtNight
      p99CoolingSwitch
  + new status parameters
      inputVentSpeed
      outputVentSpeed
      inputAirFlow
      outputAirFlow

* alpha5, Jan 31, 2015

* alpha4, Jan 25, 2015

* alpha3, Jan 5, 2015

* alpha2, Dec 26, 2014

* alpha1, Dec 19, 2014

