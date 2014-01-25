# SQLite

Configuration
=============

Remark: 
-------
The rrd plugin and the sqlite plugin can not be used together. Some pros and cons:

RRD
+ a stable, reliable tool
+ is used in a many data logging and graphing tools
- slow moving development
- only few new features on the roadmap

SQLite
+ part of python, no additional installation necessary
+ accurate logging of changing times
+ more analysis functionality

plugin.conf
-----------
<pre>
[sql]
    class_name = SQL
    class_path = plugins.sqlite
#   path = None
</pre>

The path attribute allows you to specify the of the SQLite database.

items.conf
--------------

For num and bool items, you could set the attribute: `sqlite`. By this you enable logging of the item values.
If you set this attribute to `init`, SmartHome.py tries to set the item to the last know value (like cache = yes).

<pre>
[outside]
    name = Outside
    [[temperature]]
        name = Temperatur
        type = num
        sqlite = yes
</pre>


# Functions
This plugin adds one item method to every item which has sqlite enabled.

## sh.item.db(function, start, end='now')
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
