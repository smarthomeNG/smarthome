
Berechnung von Zeitdaten
========================

Ziel
----

Im folgenden Beispiel werden mehrere zeitbezogene Informationen
berechnet. Die Item-Werte können z.B. in Kombination mit dem
Datenbank-Plugin und eval-Ausdrücken (“Minuten / Sekunden seit
Mitternacht / Beginn des Jahres” usw. genutzt werden.

Daher enthält jedes zeitbezogene Item ein dbstr-Unteritem, welches
direkt ein datenbankfähiges Format bereitstellt.

Beispiel
--------

Im folgenden Beispiel zählt eine Abfrage alle “1” -Werte für das Item
**knx.cellar.utility_room.water_meter** im Zeitfenster seit Mitternacht
bis jetzt. Eine 1 entspricht hier 1 Liter Wasser. Auf diese Weise kann
der Verbrauch seit Mitternacht berechnet werden:

.. code-block:: yaml

   #Example: use time data for database queries
   consumption_since_midnight:
       type: num
       eval: sh.knx.cellar.utility_room.water_meter.db('count>0', sh.minute.since.midnight.dbstr(), 'now')
       eval_trigger: knx.cellar.utility_room.water_meter
       database@mysqldb: init


Logik
-----

Die Logik setzt eine Item Struktur voraus, die weiter unten beschrieben
ist.

/usr/local/smarthome/logics/zeit.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   #!/usr/bin/env python3
   # zeit.py

   sh_now = sh.now()
   debug = False

   # Funktionen

   #def leap_year(year):
   #    if (year % 400 == 0) or ((year % 4 == 0) and not (year % 100 == 0)):
   #        return True
   #    else:
   #        return False

   def days_of_month(month, year):
       if month in [1, 3, 5, 7, 8, 10, 12]:
           days = 31
       elif month in [4, 6, 9, 11]:
           days = 30
       elif (year % 400 == 0) or ((year % 4 == 0) and not (year % 100 == 0)):  #Schaltjahr
           days = 29
       else:
           days = 28
       return days

   def days_of_year(year):
       period_end = datetime.datetime(year,12,31)
       days_of_year = (period_end - datetime.datetime(period_end.year, 1, 1)).days + 1
       return(days_of_year)

   def day_of_year(year,month,day):
       period_end = datetime.datetime(year,month,day)
       day_of_year = (period_end - datetime.datetime(period_end.year, 1, 1)).days + 1
       return(day_of_year)

   if debug == True:
       print("RUNNING LOGIC OF TIME - REMOVE AFTER DEBUG")
       print(sh_now.hour) #Stunde
       print(sh_now.minute) #Minute
       print(sh_now.second) #Sekunde
       print(sh_now.day)  #Tag
       print(sh_now.month) #Monat
       print(sh_now.isoweekday()) #Wochentag
       print(sh.now().isocalendar()[1]) #Kalenderwoche

   # Sekunde/Minute
   sh.second.since.minute(sh_now.second)
   sh.second.until.minute(60 - sh_now.second - 1)

   # Minute/Stunde
   sh.minute.since.hour(sh_now.minute)
   sh.minute.until.hour(60 - sh_now.minute - 1)

   # Stunde/Tag
   sh.hour.since.midnight(sh_now.hour)
   sh.hour.until.midnight(24 - sh_now.hour - 1)

   # Tag/Woche
   sh.day.since.week(sh_now.isoweekday())
   sh.day.until.week(7 - sh_now.isoweekday())

   # Stunde/Woche
   sh.hour.since.week(sh.hour.since.midnight() + (24 * (sh.day.since.week() - 1)))
   sh.hour.until.week(sh.hour.until.midnight() + (24 * sh.day.until.week()))

   # Kalenderwoche/Jahr
   sh.week.since.year(sh.now().isocalendar()[1])
   sh.week.until.year(52-sh.now().isocalendar()[1])

   # Monat/Jahr
   sh.month.since.year(sh_now.month)
   sh.month.until.year(12-sh_now.month)

   # Sekunde/Stunde
   sh.second.since.hour(sh.second.since.minute() + (60 * sh.minute.since.hour()))
   sh.second.until.hour(sh.second.until.minute() + (60 * sh.minute.until.hour()))

   # Sekunde/Tag
   sh.second.since.midnight(sh.second.since.minute() + (3600 * sh.hour.since.midnight()))
   sh.second.until.midnight(sh.second.until.minute() + (3600 * sh.hour.until.midnight()))

   # Minute/Tag
   sh.minute.since.midnight(sh.minute.since.hour() + (60 * sh.hour.since.midnight()))
   sh.minute.until.midnight(sh.minute.until.hour() + (60 * sh.hour.until.midnight()))

   # Minute/Woche
   sh.minute.since.week(sh.minute.since.hour() + (60 * sh.hour.since.week()))
   sh.minute.until.week(sh.minute.until.hour() + (60 * sh.hour.until.week()))

   # Sekunde/Woche
   sh.second.since.week(sh.second.since.minute() + (60 * sh.minute.since.week()))
   sh.second.until.week(sh.second.until.minute() + (60 * sh.minute.until.week()))

   # Tage/Monat
   sh.day.since.month(sh_now.day - 1)
   sh.day.until.month(days_of_month(sh_now.month,sh_now.year) - sh.day.since.month() - 1)

   # Wochen/Monat
   sh.week.since.month((sh.day.since.month()-1)//7+1)
   sh.week.until.month((sh.day.until.month())//7)

   # Tage/Jahr
   sh.day.since.year(day_of_year(sh_now.year,sh_now.month,sh_now.day) - 1)
   sh.day.until.year(days_of_year(sh_now.year) - sh.day.since.year() - 1)

   # Stunde/Monat
   sh.hour.since.month((24 * sh.day.since.month()) + sh.hour.since.midnight())
   sh.hour.until.month((24 * days_of_month(sh_now.month,sh_now.year)) - sh.hour.since.month() - 1)

   # Stunde/Jahr
   sh.hour.since.year((24 * sh.day.since.year()) + sh.hour.since.midnight())
   sh.hour.until.year((24 * days_of_year(sh_now.year)) - sh.hour.since.year() - 1)

   # Minute/Monat
   sh.minute.since.month((60 * sh.hour.since.month()) + sh.minute.since.hour())
   sh.minute.until.month(sh.minute.since.month() - (60 * sh.hour.until.month()) - 1)

   # Minute/Jahr
   sh.minute.since.year((60 * sh.hour.since.year()) + sh.minute.since.hour())
   sh.minute.until.year((60 * sh.hour.until.year()) + sh.minute.until.hour())

   # Sekunde/Monat
   sh.second.since.month((60 * sh.minute.since.month()) + sh.second.since.minute())
   sh.second.until.month((60 * sh.minute.until.month()) + sh.second.until.minute())

   # Sekunde/Jahr
   sh.second.since.year((60 * sh.minute.since.year()) + sh.second.since.minute())
   sh.second.until.year((60 * sh.minute.until.year()) + sh.second.until.minute())


/usr/local/smarthome/etc/logic.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   zeitberechnung:
       filename: zeit.py
       crontab:
         - init
         - '* * * *'


Items
-----

/usr/local/smarthome/items/zeit.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   %YAML 1.1
   ---
   month:
       since:
           year:
               type: num
               dbstr:
                   type: str
                   eval_trigger: month.since.year
                   eval: str(sh.month.since.year()) + 'm'

       until:
           year:
               type: num
               dbstr:
                   type: str
                   eval_trigger: month.until.year
                   eval: str(sh.month.until.year()) + 'm'

   week:
       since:
           month:
               type: num
           year:
               type: num
       until:
           month:
               type: num
           year:
               type: num

   day:
       since:
           week:
               type: num
               dbstr:
                   type: str
                   eval_trigger: day.since.week
                   eval: str(sh.day.since.week()) + 'd'

           month:
               type: num
               dbstr:
                   type: str
                   eval_trigger: day.since.month
                   eval: str(sh.day.since.month()) + 'd'
           year:
               type: num
               dbstr:
                   type: str
                   eval_trigger: day.since.year
                   eval: str(sh.day.since.year()) + 'd'

       until:
           week:
               type: num
               dbstr:
                   type: str
                   eval_trigger: day.since.week
                   eval: str(sh.day.since.week()) + 'd'

           month:
               type: num
               dbstr:
                   type: str
                   eval_trigger: day.until.month
                   eval: str(sh.day.until.month()) + 'd'

           year:
               type: num
               dbstr:
                   type: str
                   eval_trigger: day.until.year
                   eval: str(sh.day.until.year()) + 'd'

   hour:
       since:
           midnight:
               type: num
               dbstr:
                   type: str
                   eval_trigger: hour.since.midnight
                   eval: str(sh.hour.since.midnight()) + 'h'

           week:
               type: num
               dbstr:
                   type: str
                   eval_trigger: hour.since.week
                   eval: str(sh.hour.since.week()) + 'h'

           month:
               type: num
               dbstr:
                   type: str
                   eval_trigger: hour.since.month
                   eval: str(sh.hour.since.month()) + 'h'

           year:
               type: num
               dbstr:
                   type: str
                   eval_trigger: hour.since.year
                   eval: str(sh.hour.since.year()) + 'h'

       until:
           midnight:
               type: num
               dbstr:
                   type: str
                   eval_trigger: hour.until.midnight
                   eval: str(sh.hour.until.midnight()) + 'h'

           week:
               type: num
               dbstr:
                   type: str
                   eval_trigger: hour.until.week
                   eval: str(sh.hour.until.week()) + 'h'

           month:
               type: num
               dbstr:
                   type: str
                   eval_trigger: hour.until.month
                   eval: str(sh.hour.until.month()) + 'h'

           year:
               type: num
               dbstr:
                   type: str
                   eval_trigger: hour.until.year
                   eval: str(sh.hour.until.year()) + 'h'

   minute:
       since:
           hour:
               type: num
               dbstr:
                   type: str
                   eval_trigger: minute.since.hour
                   eval: str(sh.minute.since.hour()) + 'i'

           midnight:
               type: num
               dbstr:
                   type: str
                   eval_trigger: minute.since.midnight
                   eval: str(sh.minute.since.midnight()) + 'i'

           week:
               type: num
               dbstr:
                   type: str
                   eval_trigger: minute.since.week
                   eval: str(sh.minute.since.week()) + 'i'

           month:
               type: num
               dbstr:
                   type: str
                   eval_trigger: minute.since.month
                   eval: str(sh.minute.since.month()) + 'i'

           year:
               type: num
               dbstr:
                   type: str
                   eval_trigger: minute.since.year
                   eval: str(sh.minute.since.year()) + 'i'

       until:
           hour:
               type: num
               dbstr:
                   type: str
                   eval_trigger: minute.until.hour
                   eval: str(sh.minute.until.hour()) + 'i'

           midnight:
               type: num
               dbstr:
                   type: str
                   eval_trigger: minute.until.midnight
                   eval: str(sh.minute.until.midnight()) + 'i'

           week:
               type: num
               dbstr:
                   type: str
                   eval_trigger: minute.until.week
                   eval: str(sh.minute.until.week()) + 'i'

           month:
               type: num
               dbstr:
                   type: str
                   eval_trigger: minute.until.month
                   eval: str(sh.minute.until.month()) + 'i'

           year:
               type: num
               dbstr:
                   type: str
                   eval_trigger: minute.until.year
                   eval: str(sh.minute.until.year()) + 'i'

   second:
       since:
           minute:
               type: num

           hour:
               type: num

           midnight:
               type: num

           week:
               type: num

           month:
               type: num

           year:
               type: num

       until:

           minute:
               type: num

           hour:
               type: num

           midnight:
               type: num

           week:
               type: num

           month:
               type: num

           year:
               type: num

