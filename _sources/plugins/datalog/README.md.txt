# DataLog

## Requirements

Plugin to dump the item data into files on the file system. It can be used
to configure different logs and log patterns and assign them to the
items. These items will be logged to the files.

## Supported Hardware

No special hardware required.

## Configuration

### plugin.yaml

The plugin can be configured using the following settings:

```
datalog:
    plugin_name: datalog
#    path: var/log/data
#    filepatterns:
#      - default:{log}-{year}-{month}-{day}.csv
#      - yearly:{log}-{year}.csv
#    logpatterns:
#      - csv:{time};{item};{value}\n
#    cycle: 300
```

This will setup the logs `default` and `yearly`, which are using the configured
pattern to build the target file name (key-value pairs). The `default` log is
configured automatically if you do not specify any file patterns.

Additionally the patterns to use to log the data into the files is also
configured there. The key-value pairs are specifying the file extension
and the log pattern to use. In this example all log files having the extension
`.csv` will be logged using the configured pattern. This is also the default
if you do not specify any log patterns in the configuration.

Both settings can make use of some placeholders (see below).

The path parameter can be used to log into a different path instead of the
default path and the cycle parameter defines the interval to use to dump the
data into the log files, which defaults to 300 seconds.

Placeholders which can be used in the `logpatterns` option:

   * `time` - the string representation of the time
   * `stamp` - the unix timestamp of the time
   * `item` - the id of the item
   * `value` - the value of items

Example:

```yaml
datalog:
   plugin_name = datalog
   filepatterns = default:{log}-{year}-{month}-{day}.csv | custom:{log}-{year}-{month}-{day}.txt
   logpatterns = csv:{time};{item};{value}\n
```

In this example the `default` log file will use the configured log pattern. The
`custom` log file is completely ignored, since no pattern is configured.

#### path attribute

Specifies the path to log into. The default value is `var/log/data` which can
be changed by using this option. All log files will be logged into this directory.
It's not possible to configure different log paths for different log files.

#### filepatterns attribute

This specifies a list of file patterns, which is used to build the target files
to log data into. It's using a key-value pair syntax, which means you can
configure multiple file patterns or log files.

Placeholders which can be used in the `filepatterns` option:

   * `log` - specifies the type of log (e.g. "default" in the example above)
   * `year` - the current year
   * `month` - the current month
   * `day` - the current day

#### logpatterns attribute

The log pattners setting configured the format in which the data will be
logged into the log files. It's using a key-value pair syntax, which means
you can configure multiple log patterns.

A log pattern is used for logging when a file pattern is configured, where
the extension (part behind the last `.`) matches the key.


### items.yaml

Example configuration using the plugin configuration on top of the page.

```yaml
some:
    item1:
        type: str
        datalog: default
    item2:
        type: num
        datalog:
          - default
          - custom
    item3:
        type: num
        datalog: custom
```

This will log the items

   * `some.item1` to the `default` log
   * `some.item2` to the `default` and `custom` log
   * `some.item3` to the `custom` log

### logic.yaml

No logic related stuff implemented.

## Methods

No methods provided currently.
