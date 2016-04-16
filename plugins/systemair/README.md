# Systemair

# Requirements

 1. One of the following Systemair residential air units:
    
    VR400
    VR700
    VR700DK
    VR400DE
    VTC300
    VTC700
    VTR150K
    VTR200B
    VSR300
    VSR500
    VSR150
    VTR300
    VTR500
    VSR300DE
    VTC200
 
 2. Python3 package 'minimalmodbus-0.7' or later. (install it with pip3 or easy_setup).
 3. Python3 package 'pyserial-3.0.1' or later. (install it with pip3 or easy_setup).
 
 If you use a virtual serial device like /dev/ttyVUSB0, sometimes an error occurs:
 
    ...
    File "/usr/local/lib/python3.2/site-packages/serial/serialposix.py", line 605, in _update_dtr_state
    fcntl.ioctl(self.fd, TIOCMBIS, TIOCM_DTR_str)
    IOError: [Errno 22] Invalid argument
    ...
    
 Due to a bug in the current pyserial implementation, you have to change the 'minimalmodbus.py' code and change
 following line:
 
    self.serial = _SERIALPORTS[port] = serial.Serial(port=port, baudrate=BAUDRATE, parity=PARITY, bytesize=BYTESIZE, 
    stopbits=STOPBITS, timeout=TIMEOUT)
 
 to 
    
    self.serial = _SERIALPORTS[port] = serial.Serial(port=port, baudrate=BAUDRATE, parity=PARITY, bytesize=BYTESIZE, 
    stopbits=STOPBITS, timeout=TIMEOUT, rtscts=True, dsrdtr=True)

 Normally, you can find the file in '/usr/local/lib/python3.2/site-packages/minimalmodbus.py'. (It depends on your 
 python installation, maybe you have to change the python version 3.2 to your needs.)


## Supported Hardware

 Should be working for all Systemair air handling units. Successfully tested on Systemair VTR 200/B.

 ATTENTION: some of the values provides write access to the air handling unit. BE CAREFUL. You can harm your device.
 You use this plugin at your own risk. Please check the official Modbus document on Systemair's website:
 
 https://www.systemair.com/globalassets/documentation/40903.pdf


# Configuration


## plugin.conf

    [Systemair]
        class_name = systemair 
        class_path = plugins.systemair
        serialport = /dev/ttyUSB0 # serial port of modbus device
        # slave_address = 1 # default: 1
        # update_cycle = 30 # default: 30sec


## items.conf

The example below contains not all possible modbus register. Many of these values are not necessary for daily use. 
To get all possible register open the 'systemair.conf' in the plugin folder. Every item marked with 'mod_write = true' 
is a writeable register.

### Example

    [[Lueftergeschwindigkeit]]
        # read/write
        # 0: Aus
        # 1: Langsame Geschwindigkeit
        # 2: Mittlere Geschwindigkeit 
        # 3: Schnelle Geschwindigkeit
        type = num
        systemair_regaddr = 101

    [[Luefterdrehzahl_Zuluft]]
        # in Umdrehung pro Minute
        # read
        type = num
        systemair_regaddr = 111

    [[Luefterdrehzahl_Abluft]]
        # in Umdrehung pro Minute
        # read
        type = num
        systemair_regaddr = 112


    [[Frostschutzlevel]]
        # read/write
        # Frotschutzlevel, erlaubte Werte: 70,80,90,100,110,120 = 7,8,9,10,11,12°C
        type = num
        systemair_regaddr = 206

    [[Temperatursensor_1]]
        # read
        type = num
        systemair_regaddr = 214
        eval = value / 10 #to get Celsius

    [[Temperatursensor_2]]
        # read
        type = num
        systemair_regaddr = 215
        eval = value / 10 #to get Celsius

    [[Temperatursensor_3]]
        # read
        type = num
        systemair_regaddr = 216
        eval = value / 10 #to get Celsius

    [[Temperatursensor_4]]
        # read
        type = num
        systemair_regaddr = 217
        eval = value / 10 #to get Celsius

    [[Temperatursensor_5]]
        # read
        type = num
        systemair_regaddr = 218
        eval = value / 10 #to get Celsius

    [[Wochenprogramm_Aktiv]]
        # read
        # 0: aus, 1: ein
        type = num
        coil_regaddr = 6401

    [[Filter_Wechselzeitraum]]
        # read/write
        # Wert in Monaten
        type = num
        systemair_regaddr = 601

    [[Filter_Verbrauchte_Zeit]]
        # read/write
        # Wert in Tagen
        type = num
        systemair_regaddr = 602


    [[Defroster_Status]]
        # read
        # Werte:
        # 0: No defrosting ongoing, 1: Reduced flow defrosting, 2: Bypass defrosting, 3: Stop defrosting
        type = num
        systemair_regaddr = 651

    [[Alarm_Filter]]
        # read
        # Werte:
        # 0: Alarm nicht aktiv, 1: Alarm aktiv
        type = num
        systemair_coiladdr = 12801

    [[Alarm_Luefter]]
        # read
        # Werte
        # 0: Alarm nicht aktiv, 1: Alarm aktiv
        type = num
        systemair_coiladdr = 12802

    [[Alarm_Rotor]]
        # read
        # Werte
        # 0: Alarm nicht aktiv, 1: Alarm aktiv
        type = num
        systemair_coiladdr = 12804

    [[Alarm_Frost]]
        # read
        # Werte
        # 0: Alarm nicht aktiv, 1: Alarm aktiv
        type = num
        systemair_coiladdr = 12805

    [[Alarm_PCU]]
        # read
        # Werte
        # 0: Alarm nicht aktiv, 1: Alarm aktiv
        type = num
        systemair_coiladdr = 12806

    [[Alarm_Temperatursensor]]
        # read
        # Werte
        # 0: Alarm nicht aktiv, 1: Alarm aktiv
        type = num
        systemair_coiladdr = 12807

    [[Alarm_Notfallthermostat]]
        # read
        # Werte
        # 0: Alarm nicht aktiv, 1: Alarm aktiv
        type = num
        systemair_coiladdr = 12808

    [[Alarm_Lueftungsklappe]]
        # read
        # Werte
        # 0: Alarm nicht aktiv, 1: Alarm aktiv
        type = num
        systemair_coiladdr = 12809

    [[Alarm_Relais_Aktiv]]
        # read
        # Werte
        # 0: Relais nicht aktiv, 1: Relais aktiv
        type = num
        systemair_coiladdr = 12817


        
## logic.conf

no logics

## Methodes

no methods

