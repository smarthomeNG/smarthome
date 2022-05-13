# RRDTool

## Requirements

Rrdtool itself needs to be installed as well as the Python3 bindings:

```bash
sudo apt-get install librrd-dev libpython3-dev
```

## Configuration

Comparison between database Plugin and rrdtool:

The rrd plugin and the database plugin can not be used together on a single item.

RRD
+ a stable, reliable tool
+ is used in a many data logging and graphing tools
- development did not happen the last few years

Database Plugin
+ Support for many different databases such as SQLite, MySQL/MariaDB, etc.
+ accurate logging of changing times
+ more analysis functionality

### plugin.yaml

```yaml
rrd:
    class_name: RRD
    class_path: plugins.rrd
    # step = 300
    # rrd_dir = /usr/local/smarthome/var/rrd/
```

`step` sets the cycle time how often entries will be updated.
`rrd_dir` specify the rrd storage location.

### items.yaml

#### rrd
To active rrd logging (for an item) simply set this attribute to yes.
If you set this attribute to `init`, SmartHomeNG tries to set the item to the last known value (like cache = yes).

If this same item has the attribute 'sqlite' or 'database' it is likely that one of the plugins will not work. 
To prevent this problem there is the attribute `rrd_no_series`

#### rrd_no_series
Set this item attribut to True to prevent the plugin from setting an items series function.

#### rrd_ds_name
Alternative data source name. If set then the item's name will not be used for data source but this name instead.
This way existing data sources can be used for data aggregation.

#### rrd_min
Set this item attribute to `True` to log the minimum as well. Default is False.

#### rrd_max
Set this item attribute to `True` to log the maximum as well. Default is False.

#### rrd_mode
Set the type of data source. Default ist `gauge`.
  * `gauge` - should be used for things like temperatures.
  * `counter` - should be used for continuous incrementing counters like the Powermeter (kWh), watercounter (m^3), pellets (kg).

```yaml
rrd_examples:
    outside:
        name: Outside
        temperature:
            name: Temperatur
            type: num
            rrd: init
            rrd_min: 'yes'
            rrd_max: 'yes'

    office:
        name: Büro
        temperature:
            name: Temperatur
            type: num
            rrd: 'yes'

        water:
            name: Wasser
            type: num
            rrd_type: counter
```

## Methods

This plugin adds one item method to every item which has rrd enabled.

### sh.item.db(function, start, end='now')
This method returns you a value for the specified function and timeframe.

Supported functions are:

   * `avg`: for the average value
   * `max`: for the maximum value
   * `min`: for the minimum value
   * `last`: for the last value

For the timeframe you have to specify a start point and a optional end point. By default it ends 'now'.
The time point could be specified with `<number><interval>`, where interval could be:

   * `i`: minute
   * `h`: hour
   * `d`: day
   * `w`: week
   + `m`: month
   * `y`: year

## Examples
```python
sh.outside.temperature.db('min', '1d')  # returns the minimum temperature within the last day
sh.outside.temperature.db('avg', '2w', '1w')  # returns the average temperature of the week before last week
```
## Web Interfaces

For building a web interface for a plugin, SmartHomeNG delivers a set of 3rd party components with the HTTP module. 
For addons, etc. that are delivered with the components, see /modules/http/webif/gstatic folder!

The plugin needs further components, they have to be located in the static folder of the plugin's web interface 
folder (webif).
 