# Volkszaehler Plugin

The Plugin can be used to send data to a running Volkszaehler server.

## Requirements

Installed and running Volkszaehler server.

## Configuration

### plugin.yaml

Typical configuration

```yaml
volkszaehler:
    class_name: Volkszaehler
    class_path: plugins.volkszaehler
    host: volkszaehler.server.com
```

### items.yaml

#### vz_uuid

UUID from Volkszaehler channel

#### Example

```yaml
general:

    S0Counter:
        name: Counter
        type: num
        knx_dpt: 12
        knx_listen: 5/0/0
        vz_uuid: b5706f60-e26c-11e1-8992-cff551322819

    Temperature:
        type: num
        knx_dpt: 9
        knx_listen: 3/1/3
        vz_uuid: 2c67c500-8cbc-11e3-8a46-0d477fb1562c
```
