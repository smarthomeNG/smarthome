# miflora

## Requirements
This plugin requires lib miflora in version 0.4 or above. You can install this lib with:

```
sudo pip3 install miflora --upgrade
```
Depending on the used library, you will also need the following packages (requirements.txt sets all of them):
```
pip3 install bluepy
pip3 install pygatt
```

Due to the miflora package, currently all firmwares up to 2.6.6 are supported.

Forum thread to the plugin: https://knx-user-forum.de/forum/supportforen/smarthome-py/1027133-plugin-xiaomi-mi-plant-flowers-tester-light-monitor

## Supported Hardware

* Xiaomi MiFlora Plant Flowers Tester Light Monitor

## Configuration

### plugin.yaml

```yaml
miflora:
    plugin_name: miflora
    bt_library: bluepy
    bt_addr: C4:7C:7E:21:F3:2B
    cycle: 300
    instance: miflora
```

#### Attributes
  * `bt_addr`: The Bluetooth address of your xiaomi miflora plant sensor. Find e.g. with hcitool lescan
  * `bt_library`: The bluetooth library to use: gatttool (deprecated), bluepy (recommended), pygatt.
  * `cycle`: Cycle interval for data retrieval
  * `instance`: Instance name in case multi-instance use is needed (one instance can handle one sensor)

### items.yaml

#### miflora_data_type

The miflora_data_type is needed to provide information to the plugin, which values shall be stored in the item.
Possible miflora_data_type's are temperature, light, moisture, conductivity, name, firmware and battery.

#### Example

```yaml
plants:

    sensor_office:

        temperature:
            type: num
            miflora_data_type@miflora: temperature

        light:
            type: num
            miflora_data_type@miflora: light

        moisture:
            type: num
            miflora_data_type@miflora: moisture

        conductivity:
            type: num
            miflora_data_type@miflora: conductivity

        name:
            type: str
            miflora_data_type@miflora: name

        firmware:
            type: str
            miflora_data_type@miflora: firmware

        battery:
            type: num
            miflora_data_type@miflora: battery
```
