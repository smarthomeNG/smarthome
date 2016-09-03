#Database
##General
This plugin is meant to be a drop-in replacement for the old sqlite plugin. The advantage of this new plugin is it's database abstraction.
It supports multiple database engines under the hood. Currently it has been tested with sqlite3, mysql and postgresql.
##Migration
To facilitate migration to a new dtabase engine you can find a converter script inside the `converter` subdirectory.
##Configuration
###plugin.conf examples
#### sqlite3
<pre>
[database]
    class_name = Database
    class_path = plugins.database
    engine = sqlite
    database = var/db/smarthome.db
</pre>
#### mysql
<pre>
[database]
    class_name = Database
    class_path = plugins.database
    engine = mysql
    database = smarthome
    host = localhost
    username = smarthome
    password = smarthome
</pre>
#### postgresql
<pre>
[database]
    class_name = Database
    class_path = plugins.database
    engine = postgres
    database = smarthome
    host = localhost
    username = smarthome
    password = smarthome
</pre>

###items.conf
For num and bool items, you could set the attribute: `database`. By this you enable logging of the item values and SmartHome.py set the item to the last know value at start up (equal cache = yes).

<pre>
[outside]
    name = Outside
    [[temperature]]
        name = Temperatur
        type = num
        database = yes
</pre>


## Functions
This plugin adds one item method to every item which has database enabled.

### cleanup()
This function removes orphaned item entries which are no longer referenced in the item configuration.

### move(old, new)
This function renames item entries.
`sh.sql.move('my.old.item', 'my.new.item')`

### sh.item.db(function, start, end='now')
This method returns you an value for the specified function and timeframe.

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
