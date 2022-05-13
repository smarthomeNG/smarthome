# influxdata
Plugin to store data from smarthome.py in InfluxData TSDB i.e. for graphing with Grafana or Chronograf.
This plugin uses InfluxData UDP line protocol for non-blocking execution.

Thanks to SgtSeppel for the initial plugin which can be found here: https://github.com/SgtSeppel/influxdb
I'd choose to implement UDP over the initial implementation because I run my
InfluxData server in the cloud over VPN. This setup has some latency and the
original plugin blocked my whole smarthome.py including logics not executed.

## Installation

```bash
cd smarthome.py directory
cd plugins
git clone https://github.com/rthill/influxdata.git
```

## Configuration

### /etc/influxdb/influxdb.conf

```
###
### [[udp]]
###
### Controls the listeners for InfluxDB line protocol data via UDP.
###

[[udp]]
  enabled = true
  bind-address = ":8089"
  database = "smarthome"
  # retention-policy = ""

  # These next lines control how batching works. You should have this enabled
  # otherwise you could get dropped metrics or poor performance. Batching
  # will buffer points in memory if you have many coming in.

  # batch-size = 1000 # will flush if this many points get buffered
  # batch-pending = 5 # number of batches that may be pending in memory
  # batch-timeout = "1s" # will flush at least this often even if we haven't hit buffer limit
  # read-buffer = 0 # UDP Read buffer size, 0 means OS default. UDP listener will fail if set above OS max.
```

For more information on buffers and how to setup high performance UDP listener see: https://influxdb.com/docs/v0.9/write_protocols/udp.html

### plugin.yaml

```yaml
influxdata:
    class_name: InfluxData
    class_path: plugins.influxdata
    # influx_host = localhost
    # influx_port = 8089
    influx_keyword: influx
```

### items.yaml

The configuration flag influx_keyword has a special relevance. Here you can choose which keyword the plugin should look for.
If you do not specify anything, the default keyword "influx" will be used like in the following example of an EnOcean temperature and humidity sensor:

```yaml
sensor:

    gf:

        kitchen:
            enocean_rx_id: 1234567
            enocean_rx_eep: A5_04_01

            hum:
                type: num
                influx: 'true'
                enocean_rx_key: HUM

            temp:
                type: num
                influx: 'true'
                enocean_rx_key: TMP
```

However, you can change this. Many people use the sqlite keyword to store data in a sqlite database.

If you set in plugin.yaml

```yaml
influx_keyword: sqlite
```

you do not have to update anything in your item configuration files.
All data that is pushed to sqlite (i.e. for smartVISU) will automatically be copied to InfluxData also.

## Check data

Open influx terminal or webui and change to database 'smarthome' and run:

```
> select * from "sensor.gf.kitchen.temp"
name: sensor.gf.kitchen.temp
----------------------------
time			caller	dest	source		value
1451897887326109961	EnOcean	None	01234567	21.92

> select * from "sensor.gf.kitchen.hum"
name: sensor.gf.kitchen.hum
---------------------------
time			caller	dest	source		value
1451897887305586638	EnOcean	None	01234567	44.800000000000004
```
