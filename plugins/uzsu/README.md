# UZSU
Provides universial time switches for items.

# Requirements
Calculating of sunset/sunrise in triggers, requires installation of ephem.

# Configuration

## plugin.conf

<pre>
[uzsu]
   class_name = UZSU
   class_path = plugins.uzsu
</pre>

## items.conf

### uzsu
You have to specify a item with `type = dict` and with the `uzsu_item` attribute set to the path of the item which will be set by this item. The dict has to have two keys. `active` which says if the whole list of entries should be active or not and `list` which contains a list of all entries (see the Item Data Format section for more details).

<pre>
# items/my.conf

[someroom]
    [[someitem]]
        type = int
        [[[anotheritem]]]
            type = dict
            uzsu_item = someroom.someitem
            cache = True
</pre>

If you specify the `cache = True` as well, then you're switching entries will be there even if you restart smarthome.py.

# Item Data Format

Each UZSU item is of type list. Each list entry has to be a dict with specific key and value pairs. Here are the possible keys and what their for:

* __dtstart__: a datetime object. Exact datetime as start value for the rrule algorithm. Important e.g. for FREQ=MINUTELY rrules (optional).

* __value__: the value which will be set to the item.

* __active__: `True` if the entry is activated, `False` if not. A deactivated entry is stored to the database but doesn't trigger the setting of the value. It can be enabled later with the `update` method.

* __time__: time as string to use sunrise/sunset arithmetics like in the crontab eg. `17:00<sunset`, `sunrise>8:00`, `17:00<sunset`. You also can set the time with `17:00`.

* __rrule__: You can use the recurrence rules documented in the [iCalendar RFC](http://www.ietf.org/rfc/rfc2445.txt) for recurrence use of a switching entry.

## Example

Activates the light every other day at 16:30 and deactivates it at 17:30 for five times:

<pre>
sh.eg.wohnen.kugellampe.uzsu({'active':True, 'list':[
{'value':1, 'active':True, 'rrule':'FREQ=DAILY;INTERVAL=2;COUNT=5', 'time': '16:30'},
{'value':0, 'active':True, 'rrule':'FREQ=DAILY;INTERVAL=2;COUNT=5', 'time': '17:30'}
]})
</pre>
