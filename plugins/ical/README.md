# iCal

# Requirements
This plugin has no requirements or dependencies.

# Configuration

## plugin.conf
<pre>[ical]
    class_name = iCal
    class_path = plugins.ical
    # calendars = private:http://example.com/private.ics | http://example.com/public.ics | holiday:http://example.com/holidays.ics
    # cycle = 3600
</pre>

### Attributes

The following attributes can be specified:
  * `calendars`: list of calendars to automatically keep up to day and provided via `sh.ical()` function. Configures an alias (optional) and the URI of calendar, which can be a local file or a remote file when starting with `http://`.
  * `cycle`: specifies the interval in seconds to update the calendars. By default it 3600 seconds.

## items.conf
<pre>[calendar]
  [[holiday]]
    type = bool
    ical_calendar = holiday
  [[private]]
    type = bool
    ical_calendar = private
  [[public]]
    type = bool
    ical_calendar = http://example.com/public.ics
</pre>

### ical_calendar

This configures a connection between the item and the given calendar. You can specify the calendar URI or the calendar alias (as used in this example).
The configured calendar will automatically be added to the internal calendar cache and will automatically be updated.

When configured, each time an event is taken place at the moment, the item will be set to true or if not, to false.

The update interval for the item updates is currently at one minutes. Which means each minutes it will be checked if an event is take place and
the items will be updated.

# Functions
Because there is only one function, you could access it directly by the object. With the above `plugin.conf` it would look like this: `events = sh.ical('http://cal.server/my.ical')`.

This function has one mandatory and two optional arguments. `sh.ical(file, delta=1, offset=0)`

   * file: specify a local file, a url starting with 'http://' or a calendar alias configured in the plugin configuration.
   * delta: how many additional days should the analysed. By default it will for events for today and the next day (delta=1).
   * offset: when should the analysed timeframe start. By default today (offset = 0).

It returns a dictonary with a datetime.date object as key and an array including
the event start time
the event end time
the event's class type (e.g. private calendar entry)
the event's summary, i.e. content


If you want to use a calendar more regularly it could be helpful to configure this calendar in the plugin configuration to make it
automatically available via an alias and keep them up to date.

<pre>
today = sh.now().date()

holidays = sh.ical('http://cal.server/holidays.ical')
if today in holidays:
    print 'yeah'
else:
    print 'naah'

events = sh.ical('http://cal.server/events.ical')
for day in events:
    print("Date: {0}".format(day))
    for event in events[day]:
        start = event['Start']
        summary = event['Summary']
        cal_class = event['Class']
        print("Time: {0} {1}".format(start, summary))
        if 'testword' in str(summary).lower():
            print 'calendar entry with testword found'
            if start.date() == tomorrow:
                print 'Textword calendar entry starts tommorrow')
        if 'private' in str(cal_class).lower():
            print 'Private calendar entry found.'

</pre>

You can also use the plugin configuration to configure the calendars and using an alias instead. This will ease the access
to the calendar and you don't need to know the exact calendar URL each time you want to access it.

<pre>[ical]
    class_name = iCal
    class_path = plugins.ical
    calendars = holidays:http://cal.server/holidays.ical | events:http://cal.server/events.ical
    # cycle = 3600
</pre>

<pre>
holidays = sh.ical('holidays')   # access the holidays.ical
...

events = sh.ical('events')       # access the events.ical
...
</pre>

