# Raumfeld
Thanks to tfeldmann for his raumfeld code: https://github.com/tfeldmann/python-raumfeld

This is a prototyp for a simple raumfeld integration. The current version
supports start and stop playing stream in a specific zone.

## Requirements

Plugin for Teufel Raumfeld compontents. See https://www.raumfeld.com/

## Supported Hardware

* all Raumfeld Speaker

## Configuration

### plugin.yaml

```yaml
raumfeld:
    class_name: Raumfeld
    class_path: plugins.raumfeld
```


### items.yaml

```yaml
raumfeld:

    bad:
        type: bool
        name: Badezimmer Musik
        device_name: Bad
        stream_url: http://rb-mp3-m-bremenvier.akacast.akamaistream.net/7/23/234437/v1/gnl.akacast.akamaistream.net/rb-mp3-m-bremenvier
        enforce_updates: 'true'
        knx_dpt: 1
        knx_listen: 1/0/18
        knx_send: 1/0/18
        knx_init: 1/0/20
        knx_reply: 1/0/20

    kueche:
        type: bool
        name: Küche Musik
        device_name: Kueche
        stream_url: http://rb-mp3-m-bremenvier.akacast.akamaistream.net/7/23/234437/v1/gnl.akacast.akamaistream.net/rb-mp3-m-bremenvier
        enforce_updates: 'true'
        knx_dpt: 1
        knx_listen: 0/0/36
        knx_send: 0/0/36
        knx_init: 0/0/37
        knx_reply: 0/0/37
```
#### device_name

Raumfeld Zone/Hörzonen name

#### stream_url

Stream URL to play
