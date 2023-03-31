# Bose Soundtouch Plugin

#### Version 1.0.1

- Improved error handling.

#### Version 1.0.0

This plugin integrates [Bose Soundtouch](https://www.bose.de/de_de/products/speakers/smart_home/soundtouch_family.html) devices into the [SmartHomeNG](https://www.smarthomeng.de/) infrastructure. Currently the following use cases are implemented:

- Control basic functions (Power On / Off, Play, Pause, Mute, Next / Previous Track, ...)
- Control volume
- Get status information (Current Song, Artwork, Source,...)
- Get preset information and select preset


Limitations

- Only one Bose Soundtouch device is supported at the moment
- Zone / multi-room support is missing

## Change history

### Changes Since version 1.0.0

- n/a

## Requirements

### Needed software

* SmartHomeNG V1.6 or later
* Python modules: see requirements.txt

### Supported Hardware

* Bose Soundtouch (see official homepage for a [list of available devices](https://www.bose.de/de_de/products/speakers/smart_home/soundtouch_family.html))

## Configuration

### plugin.yaml
The plugin can be configured with the following parameters:

| Parameter  | Description | Required
| ------------- | ------------- | ------------- |
| ip  | IP address of Bose Soundtouch system. e.g. `192.168.2.28`  | Yes  |
| port  | Port of Bose Soundtouch system. e.g. `8090`  | -  |
| cycle_time  | Bose Soundtouch system will we queried every X seconds. e.g. `10`  | - |

The following example can be used to setup a device:

```yaml
bose_soundtouch:
    plugin_name: bose_soundtouch
    ip: 192.168.2.28
```

### items.yaml

The plugin provides ready to use structs for easy integration into your item configuration.

| Item  | Description |
| ------------- | ------------- |
| actions  | These items trigger basic control functions (Power On / Off, Play, Pause, Mute, Next / Previous Track, ...).  |
| presets  | (read only) Get information about the presets  |
| status  | (read only) Get information about the status (Current Song, Artwork, Source,...)   |
| volume  | Control volume of the device.   |

Please see the following example:

```yaml
BoseSoundtouch:
  actions:
    struct: bose_soundtouch.actions
  presets:
    struct: bose_soundtouch.presets
  status:
    struct: bose_soundtouch.status
  volume:
    struct: bose_soundtouch.volume
```

## Methods
n/a

# Appendix
- [Bose SoundTouch API Reference](https://developer.bose.com/guides/bose-soundtouch-api/bose-soundtouch-api-reference)
- [Libsoundtouch’s documentation](https://libsoundtouch.readthedocs.io/en/latest/)


