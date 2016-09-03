# SQLite

Configuration
=============

plugin.conf
-----------
<pre>
[sql]
    class_name = SQL
    class_path = plugins.sqlite
</pre>

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
   * `sum`: for the value sum

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
