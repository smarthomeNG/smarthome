# DbLog

Use this plugin to store the log of item values into a database. It supports
different databases which provides a [Python DB API 2](http://www.python.org/dev/peps/pep-0249/)
implementation (e.g. [SQLite](http://docs.python.org/3.2/library/sqlite3.html)
which is already bundled with Python or MySQL by using a
[implementation module](https://wiki.python.org/moin/MySQL)).

Before you can use any of the database implementation please make sure to
register them in the common configuration file `smarthome.conf`. Details
see [configuration page](http://mknx.github.io/smarthome/config.html).

It will create the following tables:

  * Table `item` - the item table contains all items and thier last known value
  * Table `log` - the history log of the item values

The `item` table contains the following columns:

  * Column `id` - a unique ID which is incremented by one for each new item
  * Column `name` - the item's ID / name
  * Column `time` - the unix timestamp in microseconds of last change
  * Column `val_str` - the string value if type is `str`
  * Column `val_num` - the number value if type is `num`
  * Column `val_bool` - the boolean value if type is `bool`

The `log` table contains the following columns:

  * Column `time` - the unix timestamp in microseconds of value
  * Column `item_id` - the reference to the unique ID in `item` table
  * Column `val_str` - the string value if type is `str`
  * Column `val_num` - the number value if type is `num`
  * Column `val_bool` - the boolean value if type is `bool`

# Requirements

If you want to log to a given database system you need to install the right
Python DB API 2 implementation of the database and register them by adding it
to the `smarthome.conf` configuration file.

After this you can use them by referencing the alias name of the database
registration.

# Configuration

## plugin.conf

<pre>
[dblog]
    class_name = DbLog
    class_path = plugins.dblog
    db = sqlite
    connect = database:/path/to/log.db | check_same_thread:0
</pre>

The following attributes can be used in the plugin configuration:

   * `db` - specifies the type of database to use by using an alias (register
     them in `smarthome.conf`)
   * `connect` - specifies the connection parameters which is directly
     used to invoke the `connect()` function of the DB API 2 implementation
     (for SQLite lookup [here](http://docs.python.org/3.2/library/sqlite3.html#sqlite3.connect),
     other databases depends on implementation)

## items.conf

The plugin supports the types `str`, `num` and `bool` which can be logged
into the database.

### dblog
This attribute enables the database logging when set to a value (e.g. `yes`).

<pre>
[some]
    [[item]]
        type = num
        dblog = yes
</pre>


# Functions
This plugin does not provide additional functions.

