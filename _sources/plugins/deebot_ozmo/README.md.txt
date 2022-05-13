# Plugin for Deebot Ozmo 920 / 950 / 960

#### Version 1.7.2
This plugin can control and monitor an Ecovacs Deebot Ozmo series vaccum cleaner robot.

## Change history
This plugin is work in progress. Change history will be recorded starting with first release not marked as "dev" version.


## Requirements
This plugin itself does not have any other requirement except the listed library and, obviously, a robot hardware.

### Needed software
- [deebotozmo package](https://pypi.org/project/deebotozmo/)

### Supported Hardware
This plugin is supposed to work with the [Ecovacs Deebot Ozmo series](https://www.ecovacs.com/de/deebot-robotic-vacuum-cleaner?filter=28).
Is has been successfully tested and used with a Deebot Ozmo 950.
According to the author of the underlying lib, it should work with the Deebot Ozmo 920 / 950  960.

## Configuration

### plugin.yaml
Please refer to the documentation generated from plugin.yaml metadata.


### items.yaml
Please refer to the documentation generated from plugin.yaml metadata.


### logic.yaml
Please refer to the documentation generated from plugin.yaml metadata.


## Methods
Please refer to the documentation generated from plugin.yaml metadata.


## Examples
As this plugin offers struct items, using it in your own `items.yaml` is easy.
The following example includes ALL of the available items into your SHNG.
```
deebot:
    general:
        struct: deebot_ozmo.general
    settings:
        struct: deebot_ozmo.settings
    components:
        struct: deebot_ozmo.components
    maps:
        struct: deebot_ozmo.maps
    history:
        struct: deebot_ozmo.history
    controls:
        struct: deebot_ozmo.controls
```
