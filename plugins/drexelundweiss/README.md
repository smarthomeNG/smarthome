# Drexel & Weiss

This plugin uses the D&W USB service interface for connection, so you don't need the additional modbusadapter. Be careful not to configure wrong parameters, otherwise the function of your device may be damaged. The D&W warranty is not including this case of damage!

Supported Devices
============

The plugin detects the connected device type automatically:

   * aerosilent bianco
   * aerosilent business
   * aerosilent centro
   * aerosilent micro
   * aerosilent primus
   * aerosilent stratos
   * aerosilent topo
   * aerosmart l
   * aerosmart m
   * aerosmart s
   * aerosmart mono
   * aerosmart xls
   * termosmart sc
   * X²
   * X² Plus


Configuration
=============

plugin.conf
-----------
<pre>
[DuW]
   class_name = DuW
   class_path = plugins.drexelundweiss
   tty = /dev/ttyUSB0
#   Busmonitor = 1
#   LU_ID = 130
#   WP_ID = 140
</pre>

You have to adapt the tty to your local environment and change LU_ID and WP_ID if not D&W default is used.
Busmonitor mode will output all activity on Service Interface to smarthome.py log if started in debug mode, default is Busmonitor off.

items.conf
--------------

#### DuW_LU_register
#### DuW_WP_register

With this attributes you could specify the D&W register ID found in the modbus documentation of D&W (900.6666_00_TI_Modbus_Parameter_DE.pdf)
Depending on which PCB you want to address use WP or LU attribute. The Plugin will ignore write attempts on read only registers.
If the value of the item is getting out of the configured register range, then the value will be ignored by the plugin.
Values are calculated automatically regarding the register depending divisor and comma setting, e.g. DuW_LU_register = 200 will result in a item value = 18,5

# Example
<pre>
[KWL]
    [[MODE]]
        name = Betriebsart
        visu_acl = rw
        type = num
        DuW_LU_register = 5002
        sv_widget = {{ basic.slider('item', 'item', 0, 5, 1) }}
</pre>


Functions
=========

......
