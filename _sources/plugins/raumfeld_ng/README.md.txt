# Sample Plugin <- put the name of your plugin here

#### Version 1.x.y

The plugin connects the raumfeld node-raumserver to smarthome.py. It ist possible to control a raumfeld/teufel multiroom speaker setup.

## Change history

2019 intial and final :)

## Requirements

The plugin needs a running node-raumserver instance on the same or another host.

### Needed software

* https://github.com/ChriD/node-raumserver

### Supported Hardware

* Raumfeld / Teufel multiroom speaker

## Configuration

### plugin.yaml

```yaml
raumfeld_ng:
    class_name: raumfeld_ng
    class_path: plugins.raumfeld_ng
    rf_HostIP: '127.0.0.1'
    rf_HostPort: '8080'
```

This plugin needs an hostIP attribute and a port attribute.

### items.yaml

There are two groups of item attributes. One for devices (aka 'speaker'), one for zones (aka 'group of speaker').
Zoneconfig cant be change with the plugin.

#### device attributes


raumfeld:
    kueche:    
        # read / write the powerstate of the device
        rf_power_state_kueche:
            type: bool
            rf_renderer_name: "Kueche"
            rf_attr: power_state
            rf_scope: room
            initial_value: False
            enforce_updates: 'yes'

        # read / write the volume of the device
        rf_volume_kueche:
            type: num
            rf_renderer_name: "Kueche"
            rf_attr: set_volume
            rf_scope: room
            mode: absolute
            initial_value: 30
            enforce_updates: 'yes'

        # write only - mute / unMute / toggleMute
        rf_set_mute_kueche:
            type: str
            rf_renderer_name: "Kueche"
            rf_attr: set_mute
            rf_scope: room
            enforce_updates: 'yes'


#### zone attributes

    zone_kueche:
        # read / writei the play state of the zone
        rf_play_state_kueche:
            type: str
            rf_renderer_name: "Kueche"
            rf_attr: play_state
            rf_scope: zone
            enforce_updates: 'yes'

        # write only list ["playlist", tracknum], without tracknum start first track (zone)
        rf_load_playlist_kueche:
            type: list
            rf_renderer_name: "Kueche"
            rf_attr: load_playlist
            rf_scope: zone
            enforce_updates: 'yes'

        # write only the track to play
        rf_load_track_kueche:
            type: num
            rf_renderer_name: "Kueche"
            rf_attr: load_track
            rf_scope: zone
            enforce_updates: 'yes'
    
        # read only the zone mediainfo
        rf_mediainfo_kueche:
            type: list
            rf_renderer_name: "Kueche"
            rf_attr: get_mediainfo
            rf_scope: zone
            enforce_updates: 'yes'




### logic.yaml


## Methods

