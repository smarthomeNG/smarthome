.. index:: Logiken; Datum und Zeit
.. index:: Logiken; holidays
.. index:: Logiken; Feiertage

.. index:: holidays; Logiken
.. index:: Feiertage; Logiken


.. role:: bluesup
.. role:: redsup

Feiertage, Daten und Zeiten
===========================

Das Modul **shtime** stellt eine Reihe von Funktionen zur Verfügung, die es erlauben festzustellen ob ein Datum ein
Feiertag ist (und welcher). Dazu muss die Verwendung von Feiertagen in **/etc/holidays.yaml** konfiguriert sein.

Weiterhin gibt es Funktionen, die den Umgang mit Datums- und Zeitangaben vereinfachen.

Wenn eine Funktion als Parameter ein Datum oder einen Datum/Zeit Wert erwartet, kann der Parameter in einer der
folgenden Formate angegeben werden:

- **date** Objekt  -  Wenn ein date Objekt an eine Funktion übergeben wird, welche ein datetime Objekt erwartet, wird als
  Uhrzeit 0 Uhr, 0 Minuten und 0 Sekunden angenommen
- **datetime** Objekt  -  Wenn ein datetime Objekt an eine Funktion übergeben wird, welche ein date Objekt erwartet, wird
  die Zeitangabe ignoriert
- **string** mit Datum in der Form "yyyy-mm-dd", "yy-mm-dd", "dd.mm.yyyy", "dd.mm.yy", "mm/dd/yy" oder "mm/dd/yyyy"
- **string** mit einer Datum/Zeit Angabe wie z.B. "dd.mm.yyyy hh:mm" oder "dd.mm.yyyy hh:mm:ss"


.. note::

   Diese Funktionen können außer in Logiken auch in **eval** Ausdrücken in Item Attributen verwendet werden.


.. index:: Funktionen; Feiertage
.. index:: holidays; Funktionen
.. index:: Feiertage; Funktionen

Die Funktionen für Feiertags- und Wochenend-Handling sind folgende:

+------------------------------------------------+----------------------------------------------------------------------------+
| Funktion                                       | Erläuterung                                                                |
+================================================+============================================================================+
| shtime.is_holiday(date)                        | Liefert **True**, falls das Datum ein Feiertag (gesetzlich oder            |
|                                                | benutzerdefiniert) ist                                                     |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.is_public_holiday(date)                 | Liefert **True**, falls das Datum ein gesetzlicher Feiertag ist            |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.holiday_name(date, as_list=False)       | Liefert den Namen des Feiertags, falls das Datum ein Feriertag ist.        |
|                                                | Wenn mehrere Feiertage auf das selbe Datum fallen, werden sie Komma-       |
|                                                | getrennt zurück geleifert. Falls **as_list** auf **True** gesetzt wird,    |
|                                                | ist das Ergebnis kein String, sondern eine Liste mit den Feiertagsnamen.   |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.holiday_list(year)                      | Liefert eine Liste aller Feiertage für ein Jahr                            |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.public_holiday_list(year)               | Liefert eine Liste aller gesetzlichen Feiertage für ein Jahr               |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.is_weekend(date)                        | Liefert **True**, falls das Datum auf ein Wochenende (Sa, So) fällt        |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.add_custom_holiday(cust_date)           | Trägt benutzerdefinierte Feiertage ein, die den Bedingungen des            |
|                                                | übergebenen **dict** cust_date entsprechen. Das **dict** hat die selbe     |
|                                                | Struktur, wie in der Definition in /etc/holidays.yaml                      |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.add_custom_holiday_range(from_date,     | Markiert jeden Tag, beginnend mit **fromdate** bis inklusive **to_date**   |
| to_date=None, holiday_name=' ')                | als Ferientag mit dem angegebenen Namen                                    |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.time_since(dt, resulttype)              | Liefert die Zeitdifferenz zwischen dem angegeben Zeitpunkt **dt** und      |
|                                                | jetzt. **resulttype** gibt an, ob das Ergebnis als str (**s**) , als       |
|                                                | float Minuten (**m**), Stunden (**h**), Tagen (*+d**), als int Minuten     |
|                                                | (**im**), Stunden (**ih**), Tagen (*+id**) oder als tuple (**dhms**) bzw.  |
|                                                | (**ds**) zurück gegeben werden soll. Falls nicht angegeben, wird **s**     |
|                                                | verwendet.                                                                 |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.time_until(dt, resulttype)              | Liefert die Zeitdifferenz zwischen jetzt und dem angegeben Zeitpunkt       |
|                                                | **dt**. **resulttype** ist analog zu **time_since()** zu verwenden.        |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.time_diff(dt1, dt2, resulttype)         | Liefert die Zeitdifferenz zwischen den beiden angegebenen Zeitpunkten      |
|                                                | **dt1** und **dt2**.  **resulttype** ist analog zu **time_since()** zu     |
|                                                | verwenden.                                                                 |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.beginning_of_week(week, year, offset)   | Liefert das Datum des ersten Tages der angegebenen Woche. Falls **week**   |
|                                                | oder **year** nicht angegeben werden, wird der jeweils aktuelle Wert       |
|                                                | verwendet. **offset** ermöglicht es, den Wochenstart einer früheren oder   |
|                                                | späteren Woche zu eruieren (default 0).                                    |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.beginning_of_month(month, year, offset) | Liefert das Datum des ersten Tages des angegebenen Monats. Falls **month** |
|                                                | oder **year** nicht angegeben werden, wird der jeweils aktuelle Wert       |
|                                                | verwendet. **offset** ermöglicht es, den Wochenstart eines früheren oder   |
|                                                | späteren Monats zu eruieren (default 0).                                   |
+------------------------------------------------+----------------------------------------------------------------------------+
| shtime.beginning_of_year(year, offset)         | Liefert das Datum des ersten Tages des angegebenen Jahres. Falls **year**  |
|                                                | nicht angegeben wird, wird das aktuelle Jahr verwendet.                    |
|                                                | **offset** ermöglicht es, den Jahresstart eines früheren oder              |
|                                                | späteren Jahrs zu eruieren (default 0).                                    |
+------------------------------------------------+----------------------------------------------------------------------------+


.. index:: Funktionen; Datum und Zeit

Die Funktionen für das Datums-Handling sind folgende:

+-----------------------------------------------+----------------------------------------------------------------------------------+
| Funktion                                      | Erläuterung                                                                      |
+===============================================+==================================================================================+
| shtime.today(offset=0)                        | Liefert das aktuelle Datum als **date**                                          |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.tomorrow()                             | Liefert das Datum des folgenden Tages als **date**                               |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.yesterday()                            | Liefert das Datum des zurück liegenden Tages als **date**                        |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.beginning_of_week(week=None,           | Liefert das Datum des Montags der Woche als **date**                             |
| year=None, offset=0)                          |                                                                                  |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.beginning_of_month(month=None,         | Liefert das Datum des 1. des angegebenen Monats als **date**                     |
| year=None, offset=0)                          |                                                                                  |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.beginning_of_year(year=None, offset=0) | Liefert das Datum des 1. Januar des angegebenen Jahres als **date**              |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.current_year(offset=0)                 | Liefert das aktuelle Jahr                                                        |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.current_month(offset=0)                | Liefert den aktuellen Monat                                                      |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.current_day(offset=0)                  | Liefert den aktuellen Tag                                                        |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.day_of_year(date=None, offset=0)       | Liefert als Ergebnis, der wievielte Tag im Jahr das angegebene Datum ist         |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.length_of_year(year=None, offset=0)    | Liefert die Anzahl Tage, die das angegebene Jahr hat                             |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.length_of_month(month=None, year=None, | Liefert die Anzahl Tage, die der angegebene Monat im angegebenen Jahr hat        |
| offset=0)                                     |                                                                                  |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.calendar_week(date=None, offset=0)     | Liefert die Kalenderwoche (nach ISO), in der das angegebene Datum liegt          |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.weekday(date=None, offset=0)           | Liefert den Wochentag nach ISO (1=Montag - 7=Sonntag) für das angegebene Datum   |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.weekday_name(date=None, offset=0)      | Liefert den Namen des Wochentags für das angegebene Datum                        |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.date_transform(date)                   | Wandelt ein Datum welches als **date**, **datetime** oder **string** angegeben   |
|                                               | wurde, in ein Datum vom Typ **date**                                             |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.datetime_transform(date)               | Wandelt eine Datums/Zeitangabe welche als **date**, **datetime** oder **string** |
|                                               | angegeben wurde, in ein eine Datums/Zeitangabe vom Typ **datetime**              |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.time_since(dt, resulttype='s')         | Liefert die vergangene Zeit von der angegeben Datums/Zeitangabe bis jetzt.       |
|                                               | Über den Parameter **resulttype** kann festgelegt warden, in welcher Form        |
|                                               | das Ergebnis zurück geliefert werden soll:                                       |
|                                               |                                                                                  |
|                                               | - s           -> Anzahl Sekunden                                                 |
|                                               | - m           -> Minuten (mit Nachkommastellen)                                  |
|                                               | - h           -> Stunden (mit Nachkommastellen)                                  |
|                                               | - d           -> Tage (mit Nachkommastellen)                                     |
|                                               | - im          -> Anzahl Minuten (Ganzzahl)                                       |
|                                               | - ih          -> Anzahl Stunden (Ganzzahl)                                       |
|                                               | - id          -> Anzahl Tage (Ganzzahl)                                          |
|                                               | - dhms        -> Tuple (<Tage>, <Stunden>, <Minuten>, <Sekunden>)                |
|                                               | - ds          -> Tuple (<Tage>, <Sekunden>)                                      |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.time_until(dt, resulttype='s')         | Liefert die vergehende Zeit von jetzt bis zur angegeben Datums/Zeitangabe.       |
|                                               | Der Parameter **resulttype** ist bei der Funktion **shtime.time_since()**        |
|                                               | beschrieben.                                                                     |
+-----------------------------------------------+----------------------------------------------------------------------------------+
| shtime.time_diff(dt1, dt2,                    | Liefert die vergehende Zeit von jetzt bis zur angegeben Datums/Zeitangabe.       |
| resulttype='s')                               | Der Parameter **resulttype** ist bei der Funktion **shtime.time_since()**        |
|                                               | beschrieben.                                                                     |
+-----------------------------------------------+----------------------------------------------------------------------------------+


.. note::

   Funktionen, die als Parameter ein **date** erwarten, können ohne diesen Parameter aufgerufen werden. Dann wird das
   aktuelle Datum verwendet.

   Funktionen, die als Parameter ein **year** und/oder **month** erwarten, können ohne diesen Parameter aufgerufen
   werden. Dann wird eine Liste über alle vorberechneten Feiertage zurück geliefert.

   Funktionen, die als Parameter ein **offset** erwarten, können ohne diesen Parameter aufgerufen werden. Der Standardwert ist 0.
   Offset ist ein positiver (für zukünftige Werte) oder negativer (für vergangene Werte) Integerwert.
   Beispiel: shtime.beginning_of_week(None, -2) würde das Startdatum der vorletzten Woche liefern.
   shtime.day_of_year(shtime.today(), 2) oder shtime.day_of_year(shtime.today(2)) 
   den Tag innerhalb des aktuellen Jahres von übermorgen.

.. tip::

   Die Funktionen wie **shtime.today()** sind im Zusammenhang mit den Feiertags-Funktionen nützlich. Um z.B. festzustellen,
   ob der folgende Tag ein Feiertag ist, kann einfach **shtime.is_holiday(shtime.tomorrow())** aufgerufen werden.


Die Funktionen für das Zeit-Handling sind folgende:

+---------------------------------+----------------------------------------------------------------------------------------+
| Funktion                        | Erläuterung                                                                            |
+=================================+========================================================================================+
| shtime.now()                    | Liefert die aktuelle Zeit, unter Berücksichtigung der Zeitzone                         |
+---------------------------------+----------------------------------------------------------------------------------------+
| shtime.tz()                     | Liefert die aktuelle lokale Zeitzone                                                   |
+---------------------------------+----------------------------------------------------------------------------------------+
| shtime.tzname()                 | Liefert den Namen der aktuellen lokalen Zeitzone (z.B. CET)                            |
+---------------------------------+----------------------------------------------------------------------------------------+
| shtime.utcnow()                 | Liefert die aktuelle Zeit in GMT, also ohne Berücksichtigung der Zeitzone              |
+---------------------------------+----------------------------------------------------------------------------------------+
| shtime.runtime()                | Liefert die Laufzeit von SmartHomeNG, seit SmartHomeNG das letzte mal gestartet wurde. |
+---------------------------------+----------------------------------------------------------------------------------------+


