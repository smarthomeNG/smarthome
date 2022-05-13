# SQLite (for SmartVisu >= 2.8)

## Configuration

### plugin.yaml

```yaml
sql:
    plugin_name: sqlite_visu2_8
    # path: None
    # dumpfile: /tmp/smarthomedb.dump
```

The `path` attribute allows you to specify the of the SQLite database.

If you specify a `dumpfile`, SmartHomeNG dumps the database every night into this file.

### items.yaml

For num and bool items, you could set the attribute: `sqlite`. By this you enable logging of the item values and SmartHomeNG set the item to the last know value at start up (equal cache = yes).

```yaml
outside:
    name: Outside

    temperature:
        name: Temperatur
        type: num
        sqlite: 'yes'
```

## Functions
This plugin adds one item method to every item which has sqlite enabled.

### cleanup()
This function removes orphaned item entries which are no longer referenced in the item configuration.

### dump(filename)
Dumps the database into the specified file.
`sh.sql.dump('/tmp/smarthomedb.dump')` writes the database content into /tmp/smarthomedb.dump

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
```python
sh.outside.temperature.db('min', '1d')  # returns the minimum temperature within the last day
sh.outside.temperature.db('avg', '2w', '1w')  # returns the average temperature of the week before last week
```
