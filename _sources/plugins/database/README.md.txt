# Database
https://knx-user-forum.de/forum/supportforen/smarthome-py/1021844-neues-database-plugin

Use this plugin to store the log of item values into a database. It supports
different databases which provides a [Python DB API 2](http://www.python.org/dev/peps/pep-0249/)
implementation (e.g. [SQLite](http://docs.python.org/3.2/library/sqlite3.html)
which is already bundled with Python or MySQL by using a
[implementation module](https://wiki.python.org/moin/MySQL)).

The plugin will create the following database structure:

  * Table `item` - the item table contains all items and thier last known value
  * Table `log` - the history log of the item values

The `item` table contains the following columns:

  * Column `id` - a unique ID which is incremented by one for each new item
  * Column `name` - the item's ID / name
  * Column `time` - the unix timestamp in microseconds of last change
  * Column `val_str` - the string value if type is `str`
  * Column `val_num` - the number value if type is `num`
  * Column `val_bool` - the boolean value if type is `bool` or `num`
  * Column `changed` - the unix timestamp in microseconds of record change

The `log` table contains the following columns:

  * Column `time` - the unix timestamp in microseconds of value
  * Column `item_id` - the reference to the unique ID in `item` table
  * Column `duration` - the duration in microseconds
  * Column `val_str` - the string value if type is `str`
  * Column `val_num` - the number value if type is `num`
  * Column `val_bool` - the boolean value if type is `bool` or `num`
  * Column `changed` - the unix timestamp in microseconds of record change

## Requirements

If you want to log to a given database system you need to install the right
Python DB API 2 implementation of the database and configure it in the
plugin configuration (driver and connection parameters, see below).

**Important**: This plugin supports drivers using one of the following
format (or parameter) styles: qmark, format, numeric and pyformat.
Make sure the installed module supports one of this!

Tested drivers (other may work too):

   * SQLite (`driver = sqlite3`)
      * Standard [driver](https://docs.python.org/3/library/sqlite3.html#module-sqlite3) from Python
   * MySQL (`driver = pymysql`)
      * [PyMySQL](http://pymysql.readthedocs.io/)

## Configuration

### plugin.yaml

```yaml
database:
    plugin_name: database
    driver: sqlite3
    connect:
      - "database:/path/to/log.db"
      - "check_same_thread:0"
    # prefix: log
    # precision: 2
```

The following attributes can be used in the plugin configuration:

   * `driver` - specifies the DB-API2 driver module (e.g. Python includes
     the SQLite driver by importing the module `sqlite3`, to use it here
     just set the driver parameter to the module name `sqlite3`)
   * `connect` - specifies the connection parameters which is directly
     used to invoke the `connect()` function of the DB API 2 implementation
     (for SQLite lookup [here](http://docs.python.org/3.2/library/sqlite3.html#sqlite3.connect),
     other databases depends on implementation). An example connect string for pymysql could be
     `connect = host:127.0.0.1 | port:3306 | user:db_user | passwd:db_password | db:smarthome`
   * `prefix` - if you want to log into an existing database with other tables
     you can specify a prefix for the plugins' tables
   * `precision` - specifies the amount of digits after comma for values
     queried from the database (defaults to 2, other values are -1 to return
     raw float values, 0 to return integer numbers, >0 for the given amount
     of digits after comma)

### items.yaml

The plugin supports the types `str`, `num` and `bool` which can be logged
into the database.

#### database
This attribute enables the database logging when set (just use value `yes`).

If value `init` is used, the item will
be initialized from the database after SmartHomeNG is restarted. Also, in this
case the item's inital_value is prevented from being written to the database.

```yaml
some:
    item:
        type: num
        database: 'yes' # or 'init'
```

#### database_acl
Specifies if the Database plugin should be used for read only or read and write values (which is
the default). Sometimes you only want to use the database to read values from and just ignore
changes on the items and do not populate them to the database. Useful if you generate the
database data by external modules, but want still able to change the items to reflect the
current state.

Use "rw" to specify that changes will also populate to the database, use "ro" to simple ignore
changes on the items and do not populate them to the database. Only read items from the database
when using the methods described below for retrieving data.

## Functions
This plugin adds functions to retrieve data for items.

### sh.item.db(function, start, end='now')
Function like the SQLite plugin is registering: this method returns you a value
for the specified function and timeframe.

Supported functions are:

   * `avg`: for the average value
   * `count`: for the amount of values not "0" (more examples: `count>10`, `count<10`, `count=10`)
   * `countall`: for the amount of values (without checking any condition)
   * `max`: for the maximum value
   * `min`: for the minimum value
   * `on`: percentage (as float from 0.00 to 1.00) where the value has been greater than 0.
   * `sum`: for the summarized value
   * `raw`: for the raw values
   * `integrate`: Discrete time integration of values within given time span. Is equivalent to: sum (value*duration)

For the timeframe you have to specify a start point and a optional end point. By default it ends 'now'.
The time point could be specified with `<number><interval>`, where interval could be:

   * `i`: minute
   * `h`: hour
   * `d`: day
   * `w`: week
   + `m`: month
   * `y`: year

```python
sh.outside.temperature.db('min', '1d')  # returns the minimum temperature within the last day
sh.outside.temperature.db('avg', '2w', '1w')  # returns the average temperature of the week before last week
```

### sh.item.series(function, start, end='now', count=100)
This method returns historical values for the specified function and timeframe.

Supported functions and timeframes are same as supported in the `db` function.

```python
sh.outside.temperature.series('min', '1d', count=10)  # returns 10 minimum values within the last day
sh.outside.temperature.series('avg', '2w', '1w')  # returns the average values of the week before last week
```

Additionally to the aggregation function a finalizer function can be specified when
fetching series to apply to the results before returning them. Specify the function
as prefix to the actual aggregation function (e.g. "diff:avg").

Supported finalizer functions are:

   * `diff`: return the differences between values

```python
sh.outside.temperature.series('diff:avg', '2w', '1w')  # returns the differences between average values
```


### sh.item.dbplugin
This property returns the associated `database` plugin instance. See the list of method below
to know what you can do with this instance.

```python
dbplugin = sh.outside.temperature.dbplugin   # get associated database plugin instance
```

## dbplugin.id(item)
This method returns the ID in the database for the given item.

```python
dbplugin = sh.outside.temperature.dbplugin   # get associated database plugin instance
dbplugin.id(sh.outside.temperature)          # returns the ID for the given item
```

### dbplugin.db()

This method will return the associated database connection object. This can
be used to execute native query, but you should use the plugin methods below.
The database connection object can be used for locking.

```python
dbplugin = sh.outside.temperature.dbplugin   # get associated database plugin instance
dbplugin.db().lock()                         # lock the connection for processing
#... do something
dbplugin.db().release()                      # release lock again after processing
```

### dbplugin.dump(dumpfile, id = None, time = None, time_start = None, time_end = None, changed = None, changed_start = None, changed_end = None, cur = None)

This method will dump the complete log table if not restricted by some argument.
The restriction can be specified by specifying some of the criteria arguments
(e.g. id, time_start, time_end, ...). These arguments only allow one value to
be specified (if you want to dump more items you need to invoke the method
multiple times).

The parameters have the same meaning as described in `readLogs()` method.

```python
dbplugin = sh.outside.temperature.dbplugin   # get associated database plugin instance
dbplugin.dump("/path/dump.csv")              # dump all items
dbplugin.dump("/path/dump.csv", id=1)        # only dump item with id 1
dbplugin.dump("/path/dump.csv", id="test")   # only dump item with name "test"
```

#### dbplugin.insertLog(id, time, duration=0, val=None, it=None, changed=None, cur=None)

This method will insert a new log entry for the given item with the following
data (in the `log` database table):
* `id` - the item ID to insert an item for
* `time` - the timestamp (in microseconds) to record the log for
* `duration` - the amount of time to record the given value for
* `val` - the value to record
* `it` - the item type / type of value as string (e.g. 'str', 'num', 'bool')
* `changed` - the timestamp (in microseconds) when the change was created
* `cur` - specifies an existing cursor

#### dbplugin.updateLog(id, time, duration=0, val=None, it=None, changed=None, cur=None)

This method will update an existing log entry (in the `log` database table)
identified by item id and time. See `insertLog()` method for the details of the
parameters.

#### dbplugin.readLog(id, time, cur = None)

This method will read existing log data for given item and time.

#### dbplugin.readLogs(id, time = None, time_start = None, time_end = None, changed = None, changed_start = None, changed_end = None, cur = None)

This method will read existing log data for given item and parameters. If
you omit the parameters it will completely ignored.

* `id` - the item ID to delete items for
* `time` - the timestamp (in microseconds) to delete the log for
* `time_start` / `time_end` - can be used instead of `time` parameter to specify a time range
* `changed` - the timestamp (in microseconds) of changed value to delete
* `changed_start` / `changed_end` - can be used instead of `changed` parameter to specify a time range
* `cur` - specifies an existing cursor

```python
dbplugin.readLogs(1)             # read ALL log entries for item 1
dbplugin.readLogs(1, 12345)      # read log entry for item 1 and timestamp 12345
```

#### dbplugin.deleteLog(id, time = None, time_start = None, time_end = None, changed = None, changed_start = None, changed_end = None, cur = None)
This method will delete the given items identified by the given parameters. The
parameters have the same meaning as described in `readLogs()` method.

```python
dbplugin.deleteLog(1)            # delete ALL log entries for item 1
dbplugin.deleteLog(1, 12345)     # delete log entry for item 1 and timestamp 12345
```

#### dbplugin.insertItem(name, cur=None)

This method will insert a new item entry with the given name/id and return the ID
of the newly inserted item.

```python
id = dbplugin.insertItem("some.test.item")   # insert new item
```

#### dbplugin.updateItem(id, time, duration=0, val=None, it=None, changed=None, cur=None)

This method will register the given value as the last/current value of the
item (in the `item` database table).

```python
dbplugin.updateItem(id, 12345, 0, 100)       # update item value in database for timestamp 12345, duration 0, value 100
```


%--------------------------------------------
# Vollständig übernommen in plugin.yaml
%--------------------------------------------

#### dbplugin.readItem(id, cur=None)

This method will read the item data including all fields. When the id
parameter is a string it is assumed that the item should be selected by
the items name and not by the items ID.

```python
data = dbplugin.readItem(1)                  # read all fields of item with ID 1 which contains the last item status
data = dbplugin.readItem("test.item")        # read all fields of item with name test.item which contains the last item status
```

#### dbplugin.readItems(cur=None)

This method will read all items data including all fields.

```python
items = dbplugin.readItems()                 # read all fields of all item which contains the last item status
```

#### dbplugin.deleteItem(id, cur=None)

This method will delete the item and its log data.

```python
dbplugin.deleteItem(id)                      # delete the item and log data from database
```

#### dbplugin.cleanup()

This method will remove all items and logs from database of items which
are currenlty not configured to be logged to database. Beware of this using
in a multi-instance setup, since one instance does not know the item of
the other instance!

```python
dbplugin.cleanup()                           # cleanup database, remove non-database item from database
```
