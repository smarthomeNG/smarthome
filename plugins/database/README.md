# Database

Use this plugin to store the log of item values into a database. It supports
different databases which provides a [Python DB API 2](http://www.python.org/dev/peps/pep-0249/)
implementation (e.g. [SQLite](http://docs.python.org/3.2/library/sqlite3.html)
which is already bundled with Python or MySQL by using a
[implementation module](https://wiki.python.org/moin/MySQL)).

Before you can use any of the database implementation please make sure to
register them in the common configuration file `smarthome.conf`. Details
see [configuration page](https://github.com/smarthomeNG/smarthome/wiki/Configuration). Further
details see also the requirements section below.

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
  * Column `val_str` - the string value if type is `str`
  * Column `val_num` - the number value if type is `num`
  * Column `val_bool` - the boolean value if type is `bool` or `num`
  * Column `changed` - the unix timestamp in microseconds of record change

# Requirements

If you want to log to a given database system you need to install the right
Python DB API 2 implementation of the database and register them by adding it
to the `smarthome.conf` configuration file. For example using SQLite and a
MySQL driver you may add the following (requires PyMySQL module installed):

<pre>
db = sqlite:sqlite3 | mysql:pymysql
</pre>

After this you can use them by referencing the alias name of the database
registration. In the example above the alias is "sqlite" or "mysql".

**Important**: This plugin supports drivers using one of the following
format (or parameter) styles: qmark, format, numeric and pyformat.
Make sure the installed module supports one of this!

Tested drivers (other may work too):
   * SQLite
      * Standard [driver](https://docs.python.org/3/library/sqlite3.html#module-sqlite3) from Python
   * MySQL
      * [PyMySQL](http://pymysql.readthedocs.io/)

# Configuration

## plugin.conf

<pre>
[database]
    class_name = Database
    class_path = plugins.database
    db = sqlite
    connect = database:/path/to/log.db | check_same_thread:0
    #prefix = log
</pre>

The following attributes can be used in the plugin configuration:

   * `db` - specifies the type of database to use by using an alias (register
     them in `smarthome.conf`)
   * `connect` - specifies the connection parameters which is directly
     used to invoke the `connect()` function of the DB API 2 implementation
     (for SQLite lookup [here](http://docs.python.org/3.2/library/sqlite3.html#sqlite3.connect),
     other databases depends on implementation)
   * `prefix` - if you want to log into an existing database with other tables
     you can specify a prefix for the plugins' tables

## items.conf

The plugin supports the types `str`, `num` and `bool` which can be logged
into the database.

### database
This attribute enables the database logging when set (just use value `yes`).

<pre>
[some]
    [[item]]
        type = num
        database = yes
        #database_acl = rw
</pre>

### database_acl
Specifies if the Database plugin should be used for read only or read and write values (which is
the default). Sometimes you only want to use the database to read values from and just ignore
changes on the items and do not populate them to the database. Useful if you generate the
database data by external modules, but want still able to change the items to reflect the
current state.

Use "rw" to specify that changes will also populate to the database, use "ro" to simple ignore
changes on the items and do not populate them to the database. Only read items from the database
when using the methods described below for retrieving data.

# Functions
This plugin adds functions to retrieve data for items.

## sh.item.db(function, start, end='now')
Function like the SQLite plugin is registering: this method returns you a value
for the specified function and timeframe.

Supported functions are:

   * `avg`: for the average value
   * `max`: for the maximum value
   * `min`: for the minimum value
   * `on`: percentage (as float from 0.00 to 1.00) where the value has been greater than 0.

For the timeframe you have to specify a start point and a optional end point. By default it ends 'now'.
The time point could be specified with `<number><interval>`, where interval could be:

   * `i`: minute
   * `h`: hour
   * `d`: day
   * `w`: week
   + `m`: month
   * `y`: year

e.g.
<pre>
sh.outside.temperature.db('min', '1d')  # returns the minimum temperature within the last day
sh.outside.temperature.db('avg', '2w', '1w')  # returns the average temperature of the week before last week
</pre>

## sh.item.series(function, start, end='now', count=100)
This method returns historical values for the specified function and timeframe.

Supported functions and timeframes are same as supported in the `db` function.

e.g.
<pre>
sh.outside.temperature.series('min', '1d', count=10)  # returns 10 minimum values within the last day
sh.outside.temperature.series('avg', '2w', '1w')  # returns the average values of the week before last week
</pre>

## sh.item.dbplugin
This property returns the associated `database` plugin instance. See the list of method below
to know what you can do with this instance.

e.g.
<pre>
dbplugin = sh.outside.temperature.dbplugin   # get associated database plugin instance
</pre>

## dbplugin.id(item)
This method returns the ID in the database for the given item.

e.g.
<pre>
dbplugin = sh.outside.temperature.dbplugin   # get associated database plugin instance
dbplugin.id(sh.outside.temperature)          # returns the ID for the given item
</pre>

## dbplugin.db()
This method will return the associated database connection object. This can
be used to execute native query, but you should use the plugin methods below.
The database connection object can be used for locking.

<pre>
dbplugin = sh.outside.temperature.dbplugin   # get associated database plugin instance
dbplugin.db().lock()                         # lock the connection for processing
... do something
dbplugin.db().release()                      # release lock again after processing
</pre>

### dbplugin.insertLog(id, time, duration=0, val=None, it=None, changed=None, cur=None)
This method will insert a new log entry for the given item with the following
data (in the `log` database table):
* `id` - the item ID to insert an item for
* `time` - the timestamp (in microseconds) to record the log for
* `duration` - the amount of time to record the given value for
* `val` - the value to record
* `it` - the item type / type of value as string (e.g. 'str', 'num', 'bool')
* `changed` - the timestamp (in microseconds) when the change was created
* `cur` - specifies an existing cursor

### dbplugin.updateLog(id, time, duration=0, val=None, it=None, changed=None, cur=None)
This method will update an existing log entry (in the `log` database table)
identified by item id and time. See `insertLog()` method for the details of the
parameters.

### dbplugin.readLog(id, time, cur = None)
This method will read existing log data for given item and time.

### dbplugin.readLogs(id, time = None, time_start = None, time_end = None, changed = None, changed_start = None, changed_end = None, cur = None)
This method will read existing log data for given item and parameters. If
you omit the parameters it will completely ignored.

* `id` - the item ID to delete items for
* `time` - the timestamp (in microseconds) to delete the log for
* `time_start` / `time_end` - can be used instead of `time` parameter to specify a time range
* `changed` - the timestamp (in microseconds) of changed value to delete
* `changed_start` / `changed_end` - can be used instead of `changed` parameter to specify a time range
* `cur` - specifies an existing cursor

e.g.
<pre>
dbplugin.readLogs(1)             # read ALL log entries for item 1
dbplugin.readLogs(1, 12345)      # read log entry for item 1 and timestamp 12345
</pre>

### dbplugin.deleteLog(id, time = None, time_start = None, time_end = None, changed = None, changed_start = None, changed_end = None, cur = None)
This method will delete the given items identified by the given parameters. The
parameters have the same meaning as described in `readLogs()` method.

e.g.
<pre>
dbplugin.deleteLog(1)            # delete ALL log entries for item 1
dbplugin.deleteLog(1, 12345)     # delete log entry for item 1 and timestamp 12345
</pre>

### dbplugin.insertItem(name, cur=None)
This method will insert a new item entry with the given name/id and return the ID
of the newly inserted item.

e.g.
<pre>
id = dbplugin.insertItem("some.test.item")   # insert new item
</pre>

### dbplugin.updateItem(id, time, duration=0, val=None, it=None, changed=None, cur=None)
This method will register the given value as the last/current value of the
item (in the `item` database table).

e.g.
<pre>
dbplugin.updateItem(id, 12345, 0, 100)       # update item value in database for timestamp 12345, duration 0, value 100
</pre>


### dbplugin.readItem(id, cur=None)
This method will read the item data including all fields.

e.g.
<pre>
data = dbplugin.readItem(id)                 # read all fields of item which contains the last item status
</pre>



