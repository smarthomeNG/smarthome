# OperationLog

This plugins can be used to create logs which are cached, written to file and stored in memory to be used by items or other
plugins. Furthermore the logs can be visualized by SmartVISU using the standard widget **status.log**.

## Requirements

No special requirements.

## Configuration

### plugin.yaml

Use the plugin configuration to configure the logs.

```yaml
mylogname1:
    class_name: OperationLog
    class_path: plugins.operationlog
    name: mylogname1
    # maxlen = 50
    # cache = yes
    # logtofile = yes
    # filepattern = {year:04}-{month:02}-{day:02}-{name}.log
    # logger =

mylogname2:
    class_name: OperationLog
    class_path: plugins.operationlog
    name: mylogname2
    maxlen: 0
    cache: 'no'
    logtofile: 'yes'
    filepattern: yearly_log-{name}-{year:04}.log
```

This will register two logs named **mylogname1** and **mylogname2**.
The first one named **mylogname1** is configured with the default configuration as shown,
caching the log to file ``var/cache/mylogname1`` and logging to file ``var/log/operationlog/yyyy-mm-dd-mylogname1.log``.

Every day a new logfile will be created. The last 50 entries will be kept in memory.


The entries of the second log will not be kept in memory, only logged to a yearly file with the pattern ``var/log/yearly_log-mylogname2-yyyy.log``.

The logging file can be named as desired. The keys `{name}`, `{year}`, `{month}` and `{day}` are replaced by the log name and current time respectively.
Every time a log entry is written, the file name is checked and a new file is created upon change.

If you also want to log to a configured logger of the environment
you can specify the logger name in the `logger` setting.


### items.yaml

Configure an item to be logged as follows:

```yaml
foo:
    name: Foo

    bar:
        type: num
        olog: mylogname1
        # olog_rules: *:value
        # olog_txt: {id} = {value}
        # olog_level: INFO
```

foo.bar uses the minimum configuration and default values.
When the item gets updated a new log entry using loglevel 'INFO' will be generated in the log mylogname1.
The format of the entry will be "foo.bar = value".
The default value `olog_rules = *:value` defines all values to trigger a log entry.
Item types `num`, `bool` and `str` can be used.

Define a list of parameters in `olog_rules` to map item values to string properties using the format `key:value` where the item value is used as key.
Limit the values to be logged by defining `lowlimit:<lowest value>` and `highlimit:<highest value>`, see examples below. A log entry is generated for `lowlim` <= item value < `highlim`.

The logtext can be defined using the `olog_txt` attribute. The following predefined keys can be used in the text:

Key         | Description
----------- | -----------
`{value}`   | item value
`{mvalue}`  | mapped value defined in `olog_rules` from key `value`
`{name}`    | name attribute of item
`{age}`     | time since the previous change of the item value
`{pname}`   | name attribute of the parent item
`{id}`      | item id
`{pid}`     | id of the parent item
`{lowlim}`  | lower limit of the item value generating a log entry
`{highlim}` | upper limit of the item value generating a log entry

Furthermore user defined python expressions can be used in the logtext. Define as follows:

`{eval=<python code>}`

The code is replaced by the return value of the \<python code> for the logtext. Multiple `{eval=<python code>}` statements can be used.   

### item log examples:

```yaml
foo:
    name: Foo

    bar1:
        type: num
        name: Bar1
        olog: mylogname1
        olog_rules:
          - 2:two
          - 0:zero
          - 1:one
          - '*:value'
        olog_txt: This is a log text for item with name {name} and value {value} mapped to {mvalue}, parent item name is {pname}
        olog_level: ERROR

    bar2:
        type: bool
        name: Bar2
        olog: mylogname1
        olog_rules:
          - True:the value is true
          - False:the value is false
        olog_txt: This is a log text for {value} mapped to '{mvalue}', {name} changed after {age} seconds
        olog_level: warning

    bar3:
        type: str
        name: Bar3
        olog: mylogname1
        olog_rules:
          - t1:text string number one
          - t2:text string number two
          - '*:value'
        olog_txt: "text {value} is mapped to logtext '{mvalue}', expression with syntax errors: {eval=sh.this.item.doesnotexist()*/+-42}"
        olog_level: critical

    bar4:
        type: num
        name: Bar4
        olog: mylogname1
        olog_rules:
          - lowlim:-1.0
          - highlim:10.0
        olog_txt: Item with name {name} has lowlim={lowlim} <= value={value} < highlim={highlim}, the value {eval='increased' if sh.foo.bar4() > sh.foo.bar4.prev_value() else 'decreased'} by {eval=round(abs(sh.foo.bar4() - sh.foo.bar4.prev_value()), 3)}
        olog_level: info
```

### Logics.yaml

Configure a logic to be logged as follows:

```yaml
some_logic:
    filename: script.py
    olog: mylogname1
    # olog_txt: The logic {logic.name} was triggered!
    # olog_level: INFO
```

To enable logging for a given logic when it is triggered just
add the `olog` attribute to the logic configuration. As default a simple
log text is logged: Logic {logic.name} triggered.

Optionally you can overwrite the default log text using the `olog_txt`
attribute. In contrast to the item setting this supports different predefined
keys as listed below:

Key         | Description
----------- | -----------
`{plugin.*}`| the plugin instance (e.g. plugin.name for the name of the plugin)
`{logic.*}` | the logic object (e.g. logic.name for the name)
`{by}`      | name of the source of the logic trigger
`{source}`  | identifies the source of change
`{dest}`    | identifies the destination of change

Furthermore user defined python expressions can be used in the log text. Define as follows:

`{eval=<python code>}`

The code is replaced by the return value of the <python code> for the log text. Multiple `{eval=<python code>}` statements can be used.


### Functions

```python
sh.mylogname1('<level_keyword>', msg)
```


Logs the message in `msg` parameter with the given log level specified in the `<level_keyword>` parameter.

Using the log level keywords `INFO`, `WARNING` and `ERROR` (upper or lower case) will cause 
the **SmartVISU** widget **status.log** to mark the entries with the colors green, yellow and red respectively.
Alternative formulation causing a red color are `EXCEPTION` and `CRITICAL`. 
Using other log level keywords will result in a log entry without a color mark.

```python
sh.mylogname1(msg)
```

Logs the message in the `msg` parameter with the default log level `INFO`.

```python
data = sh.mylogname1()
```

will return a deque object containing the log with the last `maxlen` entries.

This plugin is inspired from the plugins MemLog and AutoBlind, reusing some of their source code.
