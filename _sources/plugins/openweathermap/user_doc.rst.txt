
.. index:: Plugins; openweathermap (openweathermap.org Wetterdaten)
.. index:: openweathermap
.. index:: Wetter; openweathermap
.. index:: struct; openweathermap

==============
openweathermap
==============

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Dieses Plugin stellt die Wetterinformationen via OpenWeatherMap (https://openweathermap.org/) zur Verfügung.
Die folgenden APIs von OpenWeatherMap werden unterstützt:

- weather
- forecast
- uvi (deprecated)
- onecall
- onecall-0...onecall-4 (verwendet die "time-machine" Funktion der one-call API, um historische Daten einschließlich heute (onecall-0) zu beziehen.
- layer
- airpollution


Requirements
============

Zur Verwendung des Plugins wird ein API Key von OpenWeatherMap benötigt, der kostenfrei bei https://openweathermap.org zu erstellen ist.

.. note:: Die kostenfreie Version ermöglicht 60 Datenabrufe pro Minute bzw. 1000 pro Tag. Das Plugin nutzt mehrfache (bis zu 10) Abrufe pro Updatezyklus. Achtung also beim Einstellen des Update-Cycle bzw. bei Verwendung des gleichen API Keys inder smartVISU.


Migration von vorheriger Version 1.5.1
======================================

Plugin-parameter
----------------

* Ein neuer Parameter 'altitude' wurde hinzugefügt um die Höhenangabe über Meeresniveau zu haben. Dies wird für die ETO-Berechnung benötigt. Wird diese Konfiguration weggelassen, so wird das Plugin ALLE Geo-Koordinaten aus der SHNG-Konfiguration nutzen.
* Man kann die Interpretation der aktuellen Koordinaten im Webinterface prüfen, in dem man auf die Geo-Koordinaten in der Tabelle oben rechts klickt. Eine zoom-bare Karte mit einem präzisen Zeiger wird dargestellt.
* 'softfail_precipitation' und 'softfail_wind_gust' können verwendet werden um fehlende Werte für Niederschlag ('rain' / 'snow') und Windböen ('wind_gust') zu ersetzen. Das Standardverhalten ist 0 für den Niederschlag und 'wind_speed' für den Wert von 'wind_gust'.


Item-attribute
--------------

* 'x', 'y', 'z'-Attribute für die Kartenelemente wurden umbenannt in 'owm_coord_x', 'owm_coord_y' and 'owm_coord_z' - diese Parameter können gänzlich weggelassen werden. In diesem Fall werden die Werte aus den Plugin-Koordinaten abgeleitet.


Hints
-----

* In früheren Versionen der OpenWeatherMap-API konnten die match_strings 'main/grnd_level' und 'main/sea_level' verwendet werden um verschiedene Luftdruck-Werte zu erhalten. Jetzt gibt es nur noch einen Wert 'current/pressure'.
* Die uvi-API ist seitens OpenWeatherMap abgekündigt. Anstelle von 'uvi_value' sollte nun 'current/uvi' verwendet werden.


Funktionaliät
=============

Allgemeine Information
----------------------

Die von OpenWeatherMap bereitgestellten Daten werden mit Hilfe eines "Matchstrings" zu den Items verknüpft. Der "Matchstring" definiert den Pfad zur Datenquelle innerhalb des Datenfeldes.
Die Liste der unterstützten APIs stellt die Namen der "data-source-keys" dar, die im Plugin verwendet werden. Das Ergebnis des letzten Datenabrufes wird im WebIF des Plugins dargestellt.
Das Plugin lädt, abhängig von dem in der Itemkonfiguration definierten "Matchstrings", die notwendigen Daten. Ist kein entsprechender "Matchstring" definiert, wird die jeweilige API nicht abgerufen.
Der bevorzugte Weg ist die Verwendung der "one-call" API.

Alle Wetterdaten werden in metrischen Einheiten (m, mm, hPa, °C) dargestellt.


Rohe JSON Daten in ein Item speichern
-------------------------------------

Nutze die "data-source-keys" um die entsprechende Datenquelle zu identifizieren.

.. code:: yaml

    kompletter_onecall_json:
        type: str
        owm_raw_file: onecall


Verfügbare Matchstrings
-----------------------

Der Beginn des "Matchstring" definiert die zu verwendende Daten-Quelle (API):

- beginnt mit ``virtual/`` siehe `Virtual Matchstrings`; Beispiel: virtual/past24h/sum/rain/1h um die Gesamtmenge an Regen der letzten 24h zu bekommen
- beginnt mit ``forecast/daily/``, siehe `Daily forecast (calculated)`; Beispiel: forecast/daily/0/main/temp_min um die niedrigste Tagestemperatur für morgen zu bekommen
- endet mit ``/eto`` beginnt mit ``current/`` oder ``daily/``, siehe `Evapotranspiration`; Beispiel: daily/1/eto für den morgigen ETO-Wert.
- beginnt mit ``forecast/`` (Datenquelle ist die forecast-API); Beispiel: forecast/1/main/humidity um die vorhergesagte Luftfeuchtigkeit on 3h von jetzt zu bekommen (Bemerkung: ``forecast/`` wird durch ``list/`` ersetzt, wenn entsprechende Items in der Datenquelle vorhanden sind)
- beginnt mit ``uvi`` (Datenquelle ist die uvi-API); Beispiel: uvi_value um den UV-Index Wert zu bekommen; Diese API is veraltet und durch current/uvi ersetzt
- beginnt mit ``current/``  Beispiel: current/weather/description um die textuelle Beschreibung des aktuellen Wetters in der definierten Sprache zu bekommen
- beginnt mit ``hour/I/`` wobei I [0..47] die Anzahl der Stunden von jetzt in die Zukunft angibt. Beispiel: hour/2/feels_like um die gefühlte Temperatur in 2 Stunden von jetzt zu bekommen; (Bemerkung: Der prefix "hour/" wird durch "hourly/" ersetzt, wenn entsprechende Items in der Datenquelle vorhanden sind) Die folgende Liste enthält alle verfügbaren Datenpunkte:

  - ``dt`` Zeitpunkt der folgenden Daten
  - ``temp`` Temperatur, °C
  - ``feels_like`` gefühlte Temperatur, °C
  - ``pressure`` Luftdruck auf Meereshöhe, hPa
  - ``humidity`` Relative Luftfeuchtigkeit, %RH
  - ``dew_point`` Taupunkt, °C
  - ``uvi`` UV-Index
  - ``clouds`` Bewölkung, %
  - ``rain/1h`` Regenmenge, mm
  - ``snow/1h`` Schneemenge, mm
  - ``pop`` Niederschlagswahrscheinlichkeit (Propability of precipitation), %
  - ``visibility`` Durchschnittliche Sichtweite, m
  - ``wind_speed`` Windgeschwindigkeit, m/s (dies kann erweitert werden um ``wind_speed/beaufort`` und ``wind_speed/description``, um die Windstärke nach Beaufort als Wert bzw. Beschreibung zu bekommen)
  - ``wind_deg`` Windrichtung, °
  - ``wind_gust`` Windböen, m/s
  - ``weather/0/id`` Wetterbedingungs-ID
  - ``weather/0/main`` Gruppenname der Wetter-Parameter (Rain, Snow, Extreme etc.)
  - ``weather/0/description`` Wetterbeschreibung innerhalb der Gruppe
  - ``weather/0/icon`` Wetter-Icon-ID


- beginnt mit ``day/N/`` wobei N [0..6] die Anzahl der Tage von heute in die Zukunft ist bzw. [-4..-0] die Anzahl der Tage von heute in die Vergangenheit ist. Achtung: -0 and 0 ergeben verschiedene Werte! Datenquelle ist onecall-API; Beispiel: day/1/feels_like/night um die morgige gefühlte Nachttemperatur zu bekommen; (Bemerkung: Der prefix "day/" wird durch "daily/" ersetzt, wenn entsprechende Items in der Datenquelle vorhanden sind) Die folgende Liste enthält alle verfügbaren Datenpunkte:

  - ``dt`` Zeitpunkt der folgenden Daten
  - ``sunrise`` Sonnenaufgang dieses Tages, UTC
  - ``sunset`` Sonnenuntergang dieses Tages, UTC
  - ``moonrise`` Mondaufgang dieses Tages, UTC
  - ``moonset`` Monduntergang dieses Tages, UTC
  - ``temp/morn`` Morgentemperatur, °C
  - ``temp/day`` Tagestemperatur, °C
  - ``temp/eve`` Abendtemperatur, °C
  - ``temp/night`` Nachttemperatur, °C
  - ``temp/min`` minimale Tagestemperatur, °C
  - ``temp/max`` maximale Tagestemperatur, °C
  - ``feels_like/morn`` Gefühlte Morgentemperatur, °C
  - ``feels_like/day`` Gefühlte Tagestemperatur, °C
  - ``feels_like/eve`` Gefühlte Abendtemperatur, °C
  - ``feels_like/night`` Gefühlte Nachttemperatur, °C
  - ``pressure`` Luftdruck auf Meereshöhe, hPa
  - ``humidity`` realtive Luftfeuchtigkeit, %RH
  - ``dew_point`` Taupunkt, °C
  - ``uvi`` Maximum UV-Index des Tages
  - ``clouds`` Bewölkung, %
  - ``rain`` Regenmenge, mm
  - ``snow`` Schneemenge, mm
  - ``pop`` Niederschlagswahrscheinlichkeit (Propability of precipitation), %
  - ``visibility`` Durchschnittliche Sichtweite, m
  - ``wind_speed`` Windgeschwindigkeit, m/s (dies kann erweitert werden um wind_speed/beaufort und wind_speed/description, um die Windstärke nach Beaufort als Wert bzw. Beschreibung zu bekommen)
  - ``wind_deg`` Windrichtung, °
  - ``wind_gust`` Windböen, m/s
  - ``weather/0/id`` Wetterbedingungs-ID
  - ``weather/0/main`` Gruppenname der Wetter-Parameter (Rain, Snow, Extreme etc.)
  - ``weather/0/description`` Wetterbeschreibung innerhalb der Gruppe
  - ``weather/0/icon`` Wetter-Icon-ID


  Hängt man ``hour/I/`` an den Matchstring an, wird die gewählte Stunde "I" des entsprechenden Tages ausgewählt. Warnung: Zugriff auf "day/-0/hour/18/..." früher als 18.00 Uhr (UTC!!) führt zu einem ERROR, da die API historische Daten und Vorhersagedaten nicht kombinieren kann.

  Beispiele:

  - ``day/-1/hour/13/temp`` um die gestrige Temperatur um 13.00 Uhr UTC zu bekommen
  - ``day/-2/pressure`` um den durchnittliche (?) Luftdruck von Vorgestern (heute -2 Tage) zu bekommen

- beginnt mit ``airpollution`` Retrieves Air-Quality-Index and air-pollution component values. Original data-source is the airpollution API. In general you can retrieve the following values:

  - ``airpollution/main/aqi`` AirQualityIndex
  - ``airpollution/components/co`` CO Wert
  - ``airpollution/components/no`` NO Wert
  - ``airpollution/components/no2`` NO2 Wert
  - ``airpollution/components/o3`` Ozonwert
  - ``airpollution/components/so2`` SO2 Wert
  - ``airpollution/components/pm2_5`` Partikel 2-5µm
  - ``airpollution/components/pm10`` Partikel 10µm
  - ``airpollution/components/nh3`` NH3 Wert

  Ergänzt man ``/day/-1/hour/11/`` zwischen airpollution und main oder component, mit day [-1 .. -4] und hour [0 .. 23] erhält man die Daten für eine definierte Stunde am definierten Tag in der Vergangenheit.

  Ergänzt man ``/hour/11`` (ohne Tag) mit hour [0 .. 72] erhält man die Vorhersage-Daten für die definierte Stunde von jetzt ab.

  Beispiele:

  - ``airpollution/day/-1/hour/11/main/aqi`` um den AirQualityIndex von gestern 12:00 UTC zu bekommen
  - ``airpollution/day/-4/hour/9/main/aqi`` um den AirQualityIndex vor 4 Tagen um 9:00 UTC zu bekommen
  - ``airpollution/hour/24/main/aqi`` um den AirQualityIndex von morgen zur gleichen Zeit zu bekommen

- endet mit ``_new`` bereitet eine map-layer URL entweder mit den gegebenen Parametern owm_coord_x, owm_coord_y, owm_coord_z oder von einer Verwendung der aktuellen Geo-Koordinaten. Liste der map-layers:

  - ``clouds_new``
  - ``precipitation_new``
  - ``pressure_new``
  - ``wind_new``
  - ``temp_new``

- bei allen anderen Werten wird versucht, diese gegen die weather-API zu prüfen.

  - ``base`` / ``cod`` / ``sys/id`` / ``sys/type`` um einige interne Parameter zu bekommen.
  - ``coord/lon`` / ``coord/lat`` / ``id`` / ``name`` / ``sys/country`` / ``timezone`` für OWMs Interpretation deiner Ortsdaten.
  - ``clouds/all`` / ``visibility`` um die aktuelle Bewölkung und Sichtweite zu bekommen.
  - ``dt`` / ``sys/sunrise`` / ``sys/sunset`` um den Abfragezeitpunkt, Sonnenaufgang und Sonnenuntergang in UTC zu bekommen.
  - ``main/temp`` / ``main/feels_like`` / ``main/temp_max`` / ``main/temp_min`` um die aktuellen / heutigen Temperaturwerte zu bekommen.
  - ``rain/1h`` / ``rain/3h`` / ``snow/1h`` / ``snow/3h`` um die aktuelle Vorhersagedaten in mm zu bekommen.1
  - ``main/humidity`` / ``main/pressure`` um die aktuelle relative Luftfeuchtigkeit in % und den Luftdruck in mbar zu bekommen.
  - ``weather/0/id`` um die Wetterbedingungs-ID zu bekommen.
  - ``weather/0/main`` um den Gruppenname der Wetter-Parameter (Rain, Snow, Extreme etc.) zu bekommen
  - ``weather/0/description`` um die Wetterbeschreibung innerhalb der Gruppe zu bekommen
  - ``weather/0/icon`` um die Wetter-Icon-ID zu bekommen.
  - ``wind/deg`` / ``wind/speed`` / ``wind/gust`` um die Werte für Windrichtung, Windgeschwindigkeit und Windböen zu bekommen. Beaufort-suffixes funktionieren hier nicht)

.. note:: Matchstrings werden durch das Plugin verändert, um eine klare Unterscheidung der Datenquellen für Wartung und Code-Lesbarkeit des Plugin zu gewährleisten.


Zugriff auf Listen
------------------
Die Wetterkonditionen sind als Liste gespeichert und können mit ``current/weather/0/description`` adressiert werden. Da der Datentyp "list" nicht offensichtlich ist, setzt das Plugin automatisch "/0/" ein, um auf das erste Element der Liste zuzugreifen.
Deshalb führt ``current/weather/description`` zum entsprechenden Wert und einer WARNING im Log bei jedem Update. Diese Umsetzung soll dazu dienen, Probleme leicht zu identifizieren und durch ein Update des Matchstrings in der Konfiguration zu beheben.
Dynamischen Listen wie bspw. bei ``alerts`` beinhalten eine unbekannte Anzahl von Elementen in der Liste. Mit ``@count`` kann die Anzahl der Listenelemente ermittelt werden.
Beispiele: ``current/weather/@count`` (immer 1) oder ``alerts/@count``


Virtuelle Matchstrings
----------------------

Nicht alle Daten können direkt von den APIs abgerufen werden. Eine Daten müssen aus mehreren Datenquellen aggregiert werden. Bspw. müssen, um die Regenmenge der letzten 24 Stunden zu bekommen, die entsprechenden Daten von heute und gestern abgerufen und dann addiert werden.
Diese Funktion ist im Plugin integriert und wird mit dem Prefix ``virtual`` aktiviert.

Ein virtueller Matchstring besteht aus den folgenden Elementen:

- prefix ``virtual``
- Zeitraum zusammengesetzt aus der Richtung (past or next) und einer Zahl mit Einheit für Stunden "h" bzw. Tage "d"; Beispiele inkl. der maximal möglichen Zeitspanne

  - ``next6d`` Vorschau auf die nächten 6 Tage
  - ``next48h`` Vorschau auf die nächten 48 Stunden
  - ``past4d`` Rückschau auf die nächten 4 Tage
  - ``past96h`` Rückschau auf die nächten 96 Stunden

- Funktion

  - ``sum`` Summe
  - ``max`` Maximalwert
  - ``min`` Minimalrwe
  - ``avg`` Mittelwert
  - ``all`` erzeugt eine Liste mit allen Einträgen

- Matchstring, der ein Element der stündlichen one-call API abfragt

Beispiele:

- ``virtual/past24h/sum/rain/1h`` um die Regenmenge der letzten 24h zu bekommen
- ``virtual/next24h/sum/rain/1h`` um die voraussichtliche Regenmenge der nächsten 24h zu bekommen
- ``virtual/next24h/avg/wind_speed`` um die voraussichtliche mittlere Windgeschwindigkeit der nächsten 24h zu bekommen
- ``virtual/next12h/max/wind_gust`` um die voraussichtliche max. Windböen der nächsten 12h zu bekommen

.. note:: Für den Werte bei ``next#d`` werden die Tageseinträge der gleich API verwendet!


Hier ein Beispiel für die Verwendung der virtuellen Matchstrings mit dem smartVISU ``rain_overview-widget`` dieses Plugins:

.. code:: yaml

    weather:
        as_of:
            type: num
            remark: This has to be a time-stamp to work properly, so no eval here
            owm_matchstring: current/dt
        rain_past_12h:
            type: list
            owm_matchstring@home: virtual/past12h/all/rain/1h
        rain_next_12h:
            type: list
            owm_matchstring@home: virtual/next12h/all/rain/1h

.. code:: html

    {% import "widgets_openweathermap.html" as owm %}
    {{ owm.rain_overview('visual_id', 'weather.rain_past_12h', 'weather.rain_next_12h', 'weather.as_of') }}


Tagesvorhersage (berechnet)
---------------------------

Ein anderer Typ von virtuellen Matchstrings wird verwendet, um einen Tagesvorhersage zu berechnen.

- prefix ``forecast``
- attribut ``daily``
- Tagesangabe N im Bereich [0 .. 4] mit 0 für morgen und 1 für übermorgen usw.
- Nummer des Listenelement ``0``
- Matchstring, der ein Element der forecast API abfragt
- optional: Suffix ``/min`` oder ``/max`` an den Matchstring, um eine Aggregierungsfunktion zu wählen. ``avg`` wird als Standard verwendet.


Beispiele:
- ``forecast/daily/0/main/temp`` um die morgige Tagestemperatur zu bekommen
- ``forecast/daily/0/main/temp_min/min`` um die morgige minimale Tagestemperatur zu bekommen
- ``forecast/daily/0/main/temp_max/max``  um die maximale Tagestemperatur zu bekommen


Verdunstung / Evapotranspiration
--------------------------------

Die Verdunstung trägt Effekten wie Wind, Sonneneinstrahlung, Luftdruck und relative Luftfeuchtigkeit Rechnung und berechnet den Verlust von Wasser im Boden durch Verdunstung.
Die Datenquelle für die zur Berechnung notwendigen Daten ist die one-call API. Das Ergebnis der Berechnung ist der Bedarf an Bewässerung in mm. Dies kann in Relation mit der Regenmenge genutzt werden, um die wirklichen Bewässerungsbedarf zu ermitteln.

Beispiele:

- ``current/eto`` um die aktuelle Verdunstung zu bekommen
- ``daily/0/eto`` um die heutige Verdunstung zu bekommen
- ``daily/1/eto`` um die morgige Verdunstung zu bekommen


Weitere Informationen gibt es bei der originalen Implementierung: (https://github.com/MTry/homebridge-smart-irrigation)

Die Implementierung der Berechnung basiert auf: (https://edis.ifas.ufl.edu/pdffiles/ae/ae45900.pdf) und ist beschrieben (http://www.fao.org/3/X0490E/x0490e00.htm#Contents)

.. note:: Die Formel zur Berechnung der Verdunstung benötigt die Sonnenstrahlung, welches nicht bei der freien OWM API zur Verfügung steht. Anstelle dessen wird er UV-Index verwendet, der als equivalent anzusehen ist.
	Nichtsdestotrotz ist die Verwendung des UV-Index anstelle der realen Sonnenstrahlung aus wissenschaftlicher Sicht falsch.


Wetteralarme
------------

Wetteralarme werden von der entsprechenden Behörde wie bspw. der Deutscher Wetterdienst bereitgestellt und entsprechend weitergeleitet. Im Falle eines Alarmes, werden 2 Einträge (einer in Landessprache und einer in Englisch) in der Liste zugefügt.
Liegt kein realer Alarm vor, ist der Alarm-Knoten der API-Antwort nicht vorhanden und führt zu einem Fehler bzw ERROR im Log. Um dies zu verhindern, stellt das Plugin sicher, dass immer mindestens ein Alarm, der "Placebo-Alarm" mit der Beschreibung "No Alert" ein. vorliegt.
So wird sichergestellt, dass der Matchstring ``alerts/0/event`` immer einen Wert zugewiesen bekommt.
Durch die Verwendung von ``alerts/@count`` kann die Anzahl der vorliegenden Alarme ermittelt werden. Liegt nur der "Placebo-Alarm" vor, ist die Antwort der numerische Wert "0".

Eine Möglichkeit die Alarme in der smartVISU darzustellen, ist die Verwendung des Widgets ``status.activelist``:

.. code:: html

    {{ status.activelist('', 'weather.alerts', 'event', 'start', 'description', '') }}


Matchstring Fehlerbehandlung
----------------------------
Das typische Prüfen der Matchstrings wird bei die Wurzel der JSON-Antwort des API-Abrufes beginnen und dann dem im Matchstring definierten "Pfades" folgend die entsprechenden Daten aus dem JSON dem Item zuweisen.
Wenn der nächste Knoten entlang dieses "Pfades" nicht erreicht werden kan, wird ein ERROR geloggt. Typischerweise entsteht das durch Schreibfehler oder fehlender/falsche Indizes bei Listen.
Nicht alle Antworten der OWM APIs enthalten alle Daten/Werte. Bspw. sind Daten für ``rain``und ``snow`` nur beinhaltet, wenn es regnet oder schneit oder regen oder schneien wird.
Für Matchstrings die auf ``snow/3h``, ``snow/1h``, ``rain/3h`` oder ``rain/1h`` enden, wird das "nicht passende" Item den Wert 0 statt None erhalten. Dies wird (wenn aktiviert) als DEBUG Nachricht im Log eingetragen. Dieses Verhalten ist konfigurierbar über den Plugin-Parameter ``softfail_precipitation``.



Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/openweathermap` beschrieben bzw. in der **plugin.yaml** nachzulesen.


Nachfolgend noch einige Zusatzinformationen.


Items
-----

Für die Nutzung des Plugins muss in den entsprechenden Items das Attribute ``owm_matchstring`` konfiguriert werden. Optional kann dass Attribut ``owm_match_prefix`` verwendet werden.
Dieser String wird dem ``owm_matchstring`` vorangestellt und erlaubt eine bessere Struktur bzw. eine einfachere Definition von structs.

.. note:: Die korrekte Definition und Verwendung der Instanz des Plugins ist für die einwandfreie Funktion des Plugins notwendig. In den Beispielen lautet der Name der Instanz **home**, ein Betrieb komplett ohne Instanznamen, also nur mit der Default-Instanz ist aber möglich.

Beispiel:

.. code:: yaml

    forecast_daily1_no_prefix:
        type: str
        remark: This is a valid way of adressing the description of tomorrows weather
        owm_matchstring@home: day/1/weather/0/description

    forecast_daily1_with_prefix:
        type: str
        remark: here the match-string is compiled as day/1/weather/0/description
        owm_match_prefix@home: day/1
        owm_matchstring@home: /weather/0/description

        temp_night:
            type: num
            remark: here the match-string is compiled as day/1/temp/night, inheriting the prefix from the parent-element.
            owm_match_prefix@home: ../.
            owm_matchstring@home: /temp/night

Hier nachfolgend eine komplette item.yaml für die Anwendung des Plugins. Die Instanz (hier **home**) als auch der Plugin-Name (hier **openweathermap**) ist gemäß Eurer Definition anzupassen.

.. code:: yaml

    wetter:
        owm:
            locals:
                instance: home
                struct: openweathermap.locals

            current:
                instance: home
                struct: openweathermap.current

            forecast:
                hourly:
                    currently_plus_1h:
                        instance: home
                        owm_match_prefix@home: hour/1
                        struct: openweathermap.forecast_hourly

                    currently_plus_2h:
                        instance: home
                        owm_match_prefix@home: hour/2
                        struct: openweathermap.forecast_hourly

                    currently_plus_3h:
                        instance: home
                        owm_match_prefix@home: hour/3
                        struct: openweathermap.forecast_hourly

                    currently_plus_4h:
                        instance: home
                        owm_match_prefix@home: hour/4
                        struct: openweathermap.forecast_hourly

                    currently_plus_5h:
                        instance: home
                        owm_match_prefix@home: hour/5
                        struct: openweathermap.forecast_hourly

                    currently_plus_6h:
                        instance: home
                        owm_match_prefix@home: hour/6
                        struct: openweathermap.forecast_hourly

                    currently_plus_7h:
                        instance: home
                        owm_match_prefix@home: hour/7
                        struct: openweathermap.forecast_hourly

                    currently_plus_8h:
                        instance: home
                        owm_match_prefix@home: hour/8
                        struct: openweathermap.forecast_hourly

                    currently_plus_9h:
                        instance: home
                        owm_match_prefix@home: hour/9
                        struct: openweathermap.forecast_hourly

                    currently_plus_10h:
                        instance: home
                        owm_match_prefix@home: hour/10
                        struct: openweathermap.forecast_hourly

                    currently_plus_11h:
                        instance: home
                        owm_match_prefix@home: hour/11
                        struct: openweathermap.forecast_hourly

                    currently_plus_12h:
                        instance: home
                        owm_match_prefix@home: hour/12
                        struct: openweathermap.forecast_hourly

                    currently_plus_13h:
                        instance: home
                        owm_match_prefix@home: hour/13
                        struct: openweathermap.forecast_hourly

                    currently_plus_14h:
                        instance: home
                        owm_match_prefix@home: hour/14
                        struct: openweathermap.forecast_hourly

                    currently_plus_15h:
                        instance: home
                        owm_match_prefix@home: hour/15
                        struct: openweathermap.forecast_hourly

                    currently_plus_16h:
                        instance: home
                        owm_match_prefix@home: hour/16
                        struct: openweathermap.forecast_hourly

                    currently_plus_17h:
                        instance: home
                        owm_match_prefix@home: hour/17
                        struct: openweathermap.forecast_hourly

                    currently_plus_18h:
                        instance: home
                        owm_match_prefix@home: hour/18
                        struct: openweathermap.forecast_hourly

                    currently_plus_19h:
                        instance: home
                        owm_match_prefix@home: hour/19
                        struct: openweathermap.forecast_hourly

                    currently_plus_20h:
                        instance: home
                        owm_match_prefix@home: hour/20
                        struct: openweathermap.forecast_hourly

                    currently_plus_21h:
                        instance: home
                        owm_match_prefix@home: hour/21
                        struct: openweathermap.forecast_hourly

                    currently_plus_22h:
                        instance: home
                        owm_match_prefix@home: hour/22
                        struct: openweathermap.forecast_hourly

                    currently_plus_23h:
                        instance: home
                        owm_match_prefix@home: hour/23
                        struct: openweathermap.forecast_hourly

                    currently_plus_24h:
                        instance: home
                        owm_match_prefix@home: hour/24
                        struct: openweathermap.forecast_hourly

                    currently_plus_25h:
                        instance: home
                        owm_match_prefix@home: hour/25
                        struct: openweathermap.forecast_hourly

                    currently_plus_26h:
                        instance: home
                        owm_match_prefix@home: hour/26
                        struct: openweathermap.forecast_hourly

                    currently_plus_27h:
                        instance: home
                        owm_match_prefix@home: hour/27
                        struct: openweathermap.forecast_hourly

                    currently_plus_28h:
                        instance: home
                        owm_match_prefix@home: hour/28
                        struct: _openweathermap.forecast_hourly

                    currently_plus_29h:
                        instance: home
                        owm_match_prefix@home: hour/29
                        struct: openweathermap.forecast_hourly

                    currently_plus_30h:
                        instance: home
                        owm_match_prefix@home: hour/30
                        struct: openweathermap.forecast_hourly

                    currently_plus_31h:
                        instance: home
                        owm_match_prefix@home: hour/31
                        struct: openweathermap.forecast_hourly

                    currently_plus_32h:
                        instance: home
                        owm_match_prefix@home: hour/32
                        struct: openweathermap.forecast_hourly

                daily:
                    today:
                        instance: home
                        owm_match_prefix@home: day/0
                        struct: openweathermap.forecast_daily

                    today_plus_1d:
                        instance: home
                        owm_match_prefix@home: day/1
                        struct: openweathermap.forecast_daily

                    today_plus_2d:
                        instance: home
                        owm_match_prefix@home: day/2
                        struct: openweathermap.forecast_daily

                    today_plus_3d:
                        instance: home
                        owm_match_prefix@home: day/3
                        struct: openweathermap.forecast_daily

                    today_plus_4d:
                        instance: home
                        owm_match_prefix@home: day/4
                        struct: openweathermap.forecast_daily

                    today_plus_5d:
                        instance: home
                        owm_match_prefix@home: day/5
                        struct: openweathermap.forecast_daily

                    today_plus_6d:
                        instance: home
                        owm_match_prefix@home: day/6
                        struct: openweathermap.forecast_daily

                    today_plus_7d:
                        instance: home
                        owm_match_prefix@home: day/7
                        struct: openweathermap.forecast_daily

            # historics:
                # daily:
                    # today:
                        # instance: home
                        # owm_match_prefix@home: day/-0
                        # struct: openweathermap.historical_daily

                    # today_minus_1d:
                        # instance: home
                        # owm_match_prefix@home: day/-1
                        # struct: openweathermap.historical_daily

                    # today_minus_2d:
                        # instance: home
                        # owm_match_prefix@home: day/-2
                        # struct: openweathermap.historical_daily

                    # today_minus_3d:
                        # instance: home
                        # owm_match_prefix@home: day/-3
                        # struct: openweathermap.historical_daily

                    # today_minus_4d:
                        # instance: home
                        # owm_match_prefix@home: day/-4
                        # struct: openweathermap.historical_daily

                    # today_minus_5d:
                        # instance: home
                        # owm_match_prefix@home: day/-5
                        # struct: openweathermap.historical_daily

                # hourly:
                    # currently_minus_1h:
                        # dt:
                            # remark: Time of the forecasted data, Unix, UTC
                            # type: str
                            # eval: datetime.datetime.fromtimestamp(value, datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')
                            # owm_matchstring@home: hour/-1/dt
                        # temp:
                            # remark: Temperature. Units default kelvin, metric Celsius, imperial Fahrenheit. How to change units used
                            # type: num
                            # owm_matchstring@home: hour/-1/temp
                        # feels_like:
                            # remark: Temperature. This accounts for the human perception of weather. Units default kelvin, metric Celsius, imperial Fahrenheit.
                            # type: num
                            # owm_matchstring@home: hour/-1/feels_like
                        # pressure:
                            # remark: Atmospheric pressure on the sea level, hPa
                            # type: num
                            # owm_matchstring@home: hour/-1/pressure
                        # humidity:
                            # remark: Humidity, %
                            # type: num
                            # owm_matchstring@home: hour/-1/humidity
                        # dew_point:
                            # remark: Atmospheric temperature (varying according to pressure and humidity) below which water droplets begin to condense and dew can form. Unitsdefault kelvin, metric Celsius, imperial Fahrenheit.
                            # type: num
                            # owm_matchstring@home: hour/-1/dew_point
                        # clouds:
                            # remark: Cloudiness, %
                            # type: num
                            # owm_matchstring@home: hour/-1/clouds
                        # visibility:
                            # remark: Average visibility, metres
                            # type: num
                            # owm_matchstring@home: hour/-1/visibility
                        # wind_speed:
                            # remark: Wind speed. Unitsdefault metre/sec, metric metre/sec, imperial miles/hour.How to change units used
                            # type: num
                            # owm_matchstring@home: hour/-1/wind_speed
                        # wind_gust:
                            # remark: (where available) Wind gust. Unitsdefault metre/sec, metric metre/sec, imperial miles/hour. How to change units used
                            # type: num
                            # owm_matchstring@home: hour/-1/wind_gust
                        # wind_deg:
                            # remark: Wind direction, degrees (meteorological)
                            # type: num
                            # owm_matchstring@home: hour/-1/wind_deg
                        # rain:
                            # remark: (where available) Rain volume for last hour, mm
                            # type: num
                            # owm_matchstring@home: hour/-1/rain/1h
                        # snow:
                            # remark: (where available) Snow volume for last hour, mm
                            # type: num
                            # owm_matchstring@home: hour/-1/snow/1h
                        # weather_id:
                            # remark: Weather condition id
                            # type: num
                            # owm_matchstring@home: hour/-1/weather/0/id
                        # weather_main:
                            # remark: Group of weather parameters (Rain, Snow, Extreme etc.)
                            # type: str
                            # owm_matchstring@home: hour/-1/weather/0/main
                        # weather_description:
                            # remark: Weather condition within the group (full list of weather conditions). Get the output in your language
                            # type: str
                            # owm_matchstring@home: hour/-1/weather/0/description
                        # weather_icon:
                            # remark: Weather icon id. How to get icons
                            # type: str
                            # owm_matchstring@home: hour/-1/weather/0/icon

            alerts:
                instance: home
                struct: openweathermap.alerts

            airpollution:
                instance: home
                struct: openweathermap.airpollution



Anwendungen
===========

Steuerung einer täglichen Bewässerung bspw. für Pflanzen
--------------------------------------------------------
Mit der Verwendung dieser Methode können die Pflanzen bedarfsgerecht bewässert werden. Dazu wird das Irrigation struct
verwendet, um -basierend auf dem Wasserbedarf-  ein Bewässerungsventil automatisch nach Abgabe der Tageswassermenge abzuschalten.
Im Kombination mit der UZSU kann man die Bewässerung auch automatisch starten. Hier sollte dann logischerweise nur eine Zeit am Tag definiert werden.

item.yaml

.. code:: yaml

    garden:
        gut_feeling_for_irrigation:
            type: num
            cache: yes
            remark: Value ranging from 0 to 2 where 1 would be normal, and 2 would double the amount
        irrigation_valve1:
            knx_dpt: 1
            knx_send: ...
            knx_cache: ...
            struct:
                - owm.irrigation
                - uzsu.child  # in case you want to start automatically
            evaporation:
                exposure_factor:
                    initial_value: 0.9  # Lightly shady area (greenhouses could be 0.7)
            rain:
                exposure_factor:
                    initial_value: 0.5  # half covered by a roof (greenhouses would be 0)
            factors:
                flowrate_l_per_min:
                    initial_value: 3.8  # liters per minute by irrigation system
                area_in_sqm:
                    initial_value: 6  # area covered by irrigation system
                crop_coefficient:
                    initial_value: 0.9  # depends on the type of crop, typically 0.3 to 0.9
                plant_density:
                    initial_value: 1  # are your plants planted close (1.5) or wide apart (0.3), typically 0.3 to 1.5
                gut_feeling:
                    eval: sum
                    eval_trigger:
                        - garden.gut_feeling_for_irrigation

Das komplette struct zeigt die Funktionsweise:

.. code:: yaml

    irrigation:
        type: bool
        autotimer: sh..schedule_seconds() = False
        visu_acl: rw
        enforce_updates: 'true'

        schedule_seconds:
            type: num
            initial_value: 0
            visu_acl: ro
            eval: round((sh...todays_water_demand_in_l() / sh...factors.flowrate_l_per_min()) * 60)
            eval_trigger:
                - ..factors.flowrate_l_per_min
                - ..todays_water_demand_in_l

            remaining_time:
                type: num
                visu_acl: ro
                enforce_updates: 'true'
                eval: sh...() - sh....age() if sh....() else 0
                eval_trigger: ...
                cycle: 1

        todays_water_demand_in_l:
            type: num
            eval: max(0, (sh...evaporation() * sh...evaporation.exposure_factor()) - (sh...rain() * sh...rain.exposure_factor())) * sh...factors()
            eval_trigger:
                - ..evaporation
                - ..evaporation.exposure_factor
                - ..rain
                - ..rain.exposure_factor
                - ..factors

        evaporation:
            type: num
            initial_value: 0
            owm_matchstring@instance: day/0/eto

            exposure_factor:
                remark: 'How exposed is your area to evaporation? Lower the factor for less exposure (e.g. shading, or wind-shields) or higher the factor if there is more sun (reflection) or wind (droughty areas).'
                type: num
                cache: yes
                initial_value: 1

        rain:
            type: num
            eval: sum
            eval_trigger:
                - .past_12h
                - .next_12h

            past_12h:
                type: num
                owm_matchstring@instance: virtual/past12h/sum/rain/1h
            next_12h:
                type: num
                owm_matchstring@instance: virtual/next12h/sum/rain/1h

            exposure_factor:
                remark: 'How exposed is your area to rain? Lower the factor for less exposure (e.g. roofs or bushes) or higher the factor if additional water is put there (e.g. from roof-drains).'
                initial_value: 1
                type: num
                cache: yes

        factors:
            type: num
            eval: sh..area_in_sqm() * sh..crop_coefficient() * sh..plant_density() * sh..gut_feeling()
            eval_trigger:
                - .area_in_sqm
                - .crop_coefficient
                - .plant_density
                - .gut_feeling

            flowrate_l_per_min:
                remark: 'How much water is transported by your irrigation-system? liters per minute'
                initial_value: 4
                type: num
                cache: yes

            area_in_sqm:
                remark: 'This is the irrigated area. This is important for the effectivity of rain vs. evaporation.'
                initial_value: 1
                type: num
                cache: yes

            crop_coefficient:
                remark: 'This is the coefficient that can be set based on the plants. Typically 0.3 to 0.9'
                initial_value: 0.9
                type: num
                cache: yes

            plant_density:
                remark: 'How dense are the plants planted? Typically 0.3 to 1.5'
                initial_value: 1
                type: num
                cache: yes

            gut_feeling:
                remark: 'This is a factor that should be used to tweak irrigation based on gut-feelings, typically this should be assigned centrally for the whole yard (use eval).'
                initial_value: 1
                type: num
                cache: yes

In der smartVISU kann das beinhaltete Widget verwendet werden.
Das Beispiel, passend zur YAML von oben:

.. code:: html

    {% import "widgets_openweathermap.html" as owm %}
    {{ owm.irrigation('valve_1', 'The greenhouse', 'garden.irrigation_valve1') }}


Steuerung einer wöchtenlichen Bewässerung bspw. für Rasen
---------------------------------------------------------

Mit der Verwendung dieser Methode kann Rasen bedarfsgerecht bewässert werden. Dazu wird das irrigation_weekly struct
verwendet, um -basierend auf dem wöchentlichen Wasserbedarf-  ein Bewässungsventil automtisch zu schalten.
Im Kombination mit der UZSU kann man die Bewässerung auch automatisch starten.
In diesem Falle werden die vergangenen 4 und die Vorhersage der kommenden 3 Tage für die Berechnung herangezogen.

item.yaml

.. code:: yaml

    garden:
        gut_feeling_for_irrigation:
            type: num
            cache: yes
            remark: Value ranging from 0 to 2 where 1 would be normal, and 2 would double the amount
        irrigation_valve2:
            knx_dpt: 1
            knx_send: ...
            knx_cache: ...
            struct:
                - owm.irrigation_weekly
                - uzsu.child  # in case you want to start automatically
            evaporation:
                exposure_factor:
                    initial_value: 0.9  # Lightly shady area (greenhouses could be 0.7)
            rain:
                exposure_factor:
                    initial_value: 0.5  # half covered by a roof (greenhouses would be 0)
            factors:
                flowrate_l_per_min:
                    initial_value: 20   # liters per minute by irrigation system
                area_in_sqm:
                    initial_value: 350  # area covered by irrigation system
                gut_feeling:
                    eval: sum
                    eval_trigger:
                        - garden.gut_feeling_for_irrigation

Das komplette struct zeigt die Funktionsweise:

.. code:: yaml

    irrigation_weekly:
        type: bool
        autotimer: sh..schedule_seconds() = False
        visu_acl: rw
        enforce_updates: 'true'

        schedule_seconds:
            type: num
            initial_value: 0
            visu_acl: ro
            eval: round((sh...weeks_water_demand_in_l() / sh...factors.flowrate_l_per_min()) * 60)
            eval_trigger:
                - ..factors.flowrate_l_per_min
                - ..weeks_water_demand_in_l

            remaining_time:
                type: num
                visu_acl: ro
                enforce_updates: 'true'
                eval: sh...() - sh....age() if sh....() else 0
                eval_trigger: ...
                cycle: 5

        weeks_water_demand_in_l:
            type: num
            eval: max(0, (sh...evaporation() * sh...evaporation.exposure_factor()) - (sh...rain() * sh...rain.exposure_factor())) * sh...factors()
            eval_trigger:
                - ..evaporation
                - ..evaporation.exposure_factor
                - ..rain
                - ..rain.exposure_factor
                - ..factors

        evaporation:
            type: num
            initial_value: 0
            eval: sum
            eval_trigger:
                - .day_past3
                - .day_past2
                - .day_past1
                - .day_past0
                - .day_next1
                - .day_next2
            day_past3:
                type: num
                owm_matchstring@instance: day/-3/eto
            day_past2:
                type: num
                owm_matchstring@instance: day/-2/eto
            day_past1:
                type: num
                owm_matchstring@instance: day/-1/eto
            day_past0:
                type: num
                owm_matchstring@instance: day/-0/eto
            day_next0:
                type: num
                owm_matchstring@instance: day/0/eto
            day_next1:
                type: num
                owm_matchstring@instance: day/1/eto
            day_next2:
                type: num
                owm_matchstring@instance: day/2/eto

            exposure_factor:
                remark: 'How exposed is your area to evaporation? Lower the factor for less exposure (e.g. shading, or wind-shields) or higher the factor if there is more sun (reflection) or wind (droughty areas).'
                type: num
                cache: yes
                initial_value: 1

        rain:
            type: num
            eval: sum
            eval_trigger:
                - .past_4d
                - .next_3d

            past_4d:
                type: num
                owm_matchstring@instance: virtual/past4d/sum/rain/1h
            next_3d:
                type: num
                owm_matchstring@instance: virtual/next3d/sum/rain

            exposure_factor:
                remark: 'How exposed is your area to rain? Lower the factor for less exposure (e.g. roofs or bushes) or higher the factor if additional water is put there (e.g. from roof-drains).'
                initial_value: 1
                type: num
                cache: yes

        factors:
            type: num
            eval: sh..area_in_sqm() * sh..gut_feeling()
            eval_trigger:
                - .area_in_sqm
                - .gut_feeling

            flowrate_l_per_min:
                remark: 'How much water is transported by your irrigation-system? liters per minute'
                initial_value: 4
                type: num
                cache: yes

            area_in_sqm:
                remark: 'This is the irrigated area. This is important for the effectivity of rain vs. evaporation.'
                initial_value: 1
                type: num
                cache: yes

            gut_feeling:
                remark: 'This is a factor that should be used to tweak irrigation based on gut-feelings, typically this should be assigned centrally for the whole yard (use eval).'
                initial_value: 1
                type: num
                cache: yes

In der smartVISU kann das beinhaltete Widget verwendet werden.
Das Beispiel, passend zur YAML von oben:

.. code:: html

    {% import "widgets_openweathermap.html" as owm %}
    {{ owm.irrigation_weekly('valve_2', 'Lawn in the backyard', 'garden.irrigation_valve2') }}


Funktionen des Plugins
======================


get_beaufort_number(value_in_meter_per_second)
----------------------------------------------
Berechnet aus der Windgeschwindigkeit die Windstärke nach Beaufort



get_beaufort_description(bft_number)
------------------------------------
Berechnet aus der Windgeschwindigkeit die Beschreibung der Windstärke nach Beaufort



Web Interface
=============


OWM Items
---------

The WebIF Reiter "items" zeigt alle Items, für die ein OWM Attribut konfiguriert ist.

Gelistet und periodisch aktualisiert sind:
  - item path
  - item type
  - owm_matchstring
  - item value
  - date and trigger of last update
  - date of last change


JSON
----

The Reiter "JSON" beinhaltet a Menu mit den verschieden OWM APIs und den jeweiligen Roh-Daten in JSON format.


Tipps and Tricks
================
Um die Werte der datetime (dt) lesbar dazustellen, kann ``eval`` verwendet werden.

.. code:: yaml

    conditions_as_of:
          type: str
          owm_matchstring: day/1/dt
          eval: datetime.datetime.fromtimestamp(value, datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')



Hinweise
========

- Alle angegebenen Zeiten sind un UTC. Bedingt dadurch ergibt sich ein Zeitversatz von 1h (MEZ) oder 2h (MESZ) für Abfragewerte für Deutschland.
- Die Formel zur Berechnung der Verdunstung benötigt die Sonnenstrahlung, welches nicht bei der freien OWM API zur Verfügung steht. Anstelle dessen wird er UV-Index verwendet, der als equivalent anzusehen ist. Nichtsdestotrotz ist die Verwendung des UV-Index anstelle der realen Sonnenstrahlung aus wissenschaftlicher Sicht falsch.
- Die Abfrage ``weather`` liefert eine Liste zurück. Es muss als Matchstring also ``weather/0/id`` verwendet werden, um den Wert für die ID zu bekommen.
