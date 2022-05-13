.. index:: Plugins; ical
.. index:: ical

ical
####

Einführung
==========

Das iCal Plugin dient dazu, Kalender (online oder offline) einzulesen und nach Einträgen zu durchsuchen.


Konfiguration
=============

.. important::

      Detaillierte Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/ical` zu finden.

Kalenderdateien können in der etc/plugin.yaml als "Alias" hinterlegt werden. Auf diese Kurznamen kann in weiterer Folge, z.B. in einer Logik referenziert werden.

.. code-block:: yaml

    # etc/plugin.yaml
    ical:
        plugin_name: ical
        #calendars:
		    #	- example:http://server.com/test.ics
		    #cycle: 3600

Außerdem können Kalender Items zugewiesen werden, indem das entsprechende Attribut im gewünschten Item angegeben wird. Das Item wird auf wahr gesetzt, sobald aktuell ein Event stattfindet.

.. code-block:: yaml

    # items/item.yaml
    calendaritem:
        type: bool
            ical_calendar: test_downloaded.ics


Funktionen
==========

.. important::

      Detaillierte Informationen zu den Funktionen des Plugins sind unter :doc:`/plugins_doc/config/ical` zu finden.


Beispiel
========

.. code-block:: python

    today = sh.now().date()

    # To check a calendar file use one of the following three options:
	# a) Local file
	dir = sh.get_basedir()
    calendarfile = '{}/var/ical/holidays.ics'.format(dir)
    holidays = sh.ical(calendarfile)

    # b) Reference a calendar defined in the etc/plugin.yaml. Query tomorrow
	# The second found entry for an event should be considered.
	holidays = sh.ical('holidays', delta=0, offset=1, prio=2)

    # c) http(s) file, disabled https verification.
	holidays = sh.ical('https://cal.server/holidays.ics', verify=false)

    # Test if there is an entry for today or not.
	if today in holidays:
        logger.info('There is a calendar entry for today.')
    else:
        logger.info('No entry for today.')

    # list all events of online calendar using given or default delta and offset
	for day in holidays:
        logger.info("Date: {0}".format(day))
        for event in holidays[day]:
            #The folloging code extracts the start time in python datetime format, already converted into the local time zone configured for smarthomeNG.
            start = event['Start']
            summary = event['Summary']
            cal_class = event['Class']
            logger.info("Time: {0} {1}".format(start, summary))
            if 'testword' in str(summary).lower():
                logger.info('calendar entry with testword found')
                if start.date() == tomorrow:
                    logger.info('Testword calendar entry starts tommorrow')
            if 'private' in str(cal_class).lower():
                logger.info('Private calendar entry found.')
