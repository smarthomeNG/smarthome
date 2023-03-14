

### Items



### items.yaml


```

The optional ref_level parameter defines default dim value when dimmer is switched on via the regular "on"" command.

## Functions
### Learning Mode

Devices that shall receive commands from the SmarthomeNG plugin must be subscribed (tought-in) first.
Generally follow the teach-in procedure as described by EnOcean:
1. Set the EnOcean device/actor into learn mode. See the manual of the respective EnOcean device for detailed information on how to enter learn mode.
2. While being in learn mode, trigger the learn telegram from SmarthomeNG (via webinterface or via interactive SmarthomeNG console)
3. Exit the learn mode of the actor

The SmarthomeNG interactive console can be reached via:

```bash
cd /usr/local/smarthome/bin
sudo systemctl stop smarthome
sudo ./smarthome.py -i
```
The learn message is issued by the following command:
```python
sh.enocean.send_learn_protocol(id_offset, device)
```
The teach-in commands vary for different EnOcean sensor/actors. The following classes are currently supported:

With device are different actuators defined:

- 10: Eltako Switch FSR61, Eltako FSVA-230V
- 20: Eltako FSUD-230V
- 21: Eltako FHK61SSR dim device (EEP A5-38-08)
- 22: Eltako FRGBW71L RGB dim devices (EEP 07-3F-7F)
- 30: Radiator Valve
- 40: Eltako shutter actors FSB61NP-230V, FSB14, FSB61, FSB71

Examples are:
```python
sh.enocean.send_learn_protocol() or sh.enocean.send_learn_protocol(0,10)
sh.enocean.send_learn_protocol(id_offset,20)
```

Where `id_offset`, range (0-127), specifies the sending ID-offset with respect to the Base-ID.
Later, the ID-offset is specified in the <item.yaml> for every outgoing send command, see the examples above.

Use different ID-offsets for different groups of actors.
After complete the teach-in procedure, leave the interactive console by `STRG+C` and add the applied id_offset to the respective EnOcean send item (enocean_tx_id_offset = ID_Offset).

### UTE teach-in

UTE stands for "Universal Uni- and Bidirectional Teach in".
When being activated on an EnOcean device the device will send a `D4` teach-in request. SmarthomeNG will answer within 500 ms with a telegram to complete the teach-in process.
To do so enable the UTE learn mode prior to the activation on the device. Again, enabling the UTE mode can be achieved via
a) The plugin webinterface
b) SmarthomeNG's interactive console - see above - and the following command `sh.enocean.start_UTE_learnmode(ID_Offset)`
