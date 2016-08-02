# iCal

# Requirements
This plugin has no requirements or dependencies.

# Configuration

## plugin.conf
<pre>[ical]
    class_name = iCal
    class_path = plugins.ical
</pre>

# Functions
Because there is only one function you could access it directly by the object. With the above plugin.conf it would look like this: `events = sh.ical('http://cal.server/my.ical')`.

This function has one mandatory and two optional arguments. `sh.ical(file, delta=1, offset=0)`

   * file: specify a local file or a url starting with 'http://'
   * delta: how many additional days should the analysed. By default it will for events for today and the next day (delta=1).
   * offset: when should the analysed timeframe start. By default today (offset = 0).

It returns a dictonary with a datetime.date object as key and an array including
the event start time
the event end time
the event's class type (e.g. private calendar entry)
the event's summary, i.e. content


<pre>
today = sh.now().date()
tomorrow = today + datetime.timedelta(days=1)

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
