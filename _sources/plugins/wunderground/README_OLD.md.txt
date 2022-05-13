# Wunderground

#### Version 1.2.5

This plugins can be used retrieve weather information from wunderground.

## Support
Support is provided trough the support thread within the smarthomeNG forum: [Smarthome.py](https://knx-user-forum.de/forum/supportforen/smarthome-py)


## Change History

### Changes Since version 1.2.4

- Fixed handling for %-values

README:

- Changed **pressure_trend** to string, since quite some weather stations report the trend as '-', '0', '+'
- Added forecast definitions for precipitation in mm (all day, day, night)


### Changes Since version 1.2.2

- Changed wunderground communication from xml to json
- matchstring has to be full qualified for json implementation of plugin (in xml implementation the matchstring could be minimalistic) For details, see example item.yaml at the end of this document
- Changed attribute name from **`wug_xmlstring`** to **`wug_matchstring`**
- Supports forecast information for multiple days


### Changes Since version 1.2.1

- Added attribute **`wug_datatype`** to be able to filter out wrong data sent by wunderground.


### Requirements

An api key from wunderground is needed. It can be obtained free of charge from ```https://www.wunderground.com/weather/api/d/pricing.html```.

The api key which is available free of charge allows up to 500 calls a day. Keep this in mind if you want to change the update frequency using the **`cycle`** parameter.



## Configuration

### plugin.yaml

Use the plugin configuration to configure the wunderground plugin.

You can configure multiple instances of the wunderground plugin to collect data for multiple locations.

```yaml
# for etc/plugin.yaml configuration file:
weather_somewhere:
    class_name: Wunderground
    class_path: plugins.wunderground
    apikey: xxxxyyyyxxxxyyyy
    # language: de
    location: Germany/Hamburg
    item_subtree: mein_wetter
    instance: wetter_ham
    # cycle: 600
```

#### apikey
Enter you registered wunderground API key

#### language
Defines the language for the forcast data. (en: English, de: German, fr: French)

If you need another language, lookup a complete list of language codes on www.wunderground.com


For a complete list, consult www.wunderground.com


#### location
The location for which you want weather information.
Examples (from wunderground.com):

```
CA/San_Francisco                      US state/city
60290                                 US zipcode
Australia/Sydney                      country/city
37.8,-122.4                           latitude,longitude
KJFK                                  airport code
pws:KCASANFR70                        PWS id
autoip                                AutoIP address location
autoip.json?geo_ip=38.102.136.138     specific IP address location
```

To find a location string that works for you, you can look at your local waether on wunderground.com and use the location string you see on that page.

#### item_subtree

**```item_subtree```** defines the part of the item-tree which the wunderground plugin searches during data updates for the **```wug_matchstring```** attribute.

If **```item_subtree```** is not defined or empty, the whole item-tree is searched, which creates unnecessary overhead vor SmartHomeNG.

If you are going to configure multiple instances of the plugin to get the weather report for multiple locations, you have to specify the parameter, or you will get da data mix up.

The subtrees defined by **`item_subtree`** for the different instances must not intersect!

#### instance
Name of the plugin instance (SmartPlugin attribute). This is important if you define multiple weather locations using multiple instances of the wunderground plugin.

#### cycle

This parameter usually doesn't have to be specified. It allows to change the update frequency (cycle every 600 seconds). As a standard, the plugin updates the weather data every 10 minutes. This ensures that the maximum of 500 requests for the free-of-charge- account are not maxed out, even if you use wunderground weather for two locations and/or smartVISU.

### items configuration
There are two item-attributes in items.yaml/items.yaml that are specific to the wunderground plugin. These parameters beginn with **`wug_`**.

### wug_matchstring

**`wug_matchstring`** contains a matchstring for parsing the data sent by wunderground. The commonly uesd matchstring are defined in the examples below.

#### wug_datatype
**`wug_datatype`** is used to filter out wrong data that may be sent by a weatherstation from time to time. Those wrong values are filtered and not written to the item. This attribute can have the values **`positive`** and **`percent`**.

- **`positive`** filters out all values less than 0.
- **`percent`** filters out values less than 0 and values greater than  100.

The following attributes can be used. You can define additional attributes. To do so, you have to lookup the matching wunderground matchstring on www.wunderground.com.

### value
The items can have a default value, set by using the ```value``` attribute. This attribute is not plugin specific. The default values are used, if the weather station you selected does not send data for the selected matchstring. The following example defines default values for items, which are not supported by all weather stations.


### Example: items.yaml
Example configuration of an item-subtree for the wunderground plugin in yaml-format:

```yaml

 ...:

    mein_wetter:
        # item definitions may contain a 'value: -9999' to signal that this item never
        # received an update from wunderground

        ort:
            type: str
            wug_matchstring: current_observation/display_location/city

        ort_wetterstation:
            type: str
            wug_matchstring: current_observation/observation_location/city
            value: unbekannt

        lokale_zeit:
            type: str
            wug_matchstring: current_observation/local_time_rfc822

        beobachtungszeitpunkt:
            type: str
            wug_matchstring: current_observation/observation_time_rfc822

        beobachtungszeitpunkt_datetime:
            type: num
            wug_matchstring: current_observation/observation_epoch

        wetter:
            type: str
            wug_matchstring: current_observation/weather

        wetter_icon:
            type: str
            wug_matchstring: current_observation/icon

        temperatur:
            type: num
            value: -9999
            wug_matchstring: current_observation/temp_c

        temperatur_gefuehlt:
            type: num
            value: -9999
            wug_matchstring: current_observation/feelslike_c

        rel_luftfeuchtigkeit:
            type: num
            value: -9999
            wug_matchstring: current_observation/relative_humidity
            wug_datatype: percent

        taupunkt:
            type: num
            value: -9999
            wug_matchstring: current_observation/dewpoint_c

        luftdruck:
            type: num
            wug_matchstring: current_observation/pressure_mb
            wug_datatype: positive

        luftdruck_trend:
            type: str
            wug_matchstring: current_observation/pressure_trend

        sichtweite:
            type: num
            value: -9999
            wug_matchstring: current_observation/visibility_km
            wug_datatype: positive

        uv:
            type: num
            value: -9999
            wug_matchstring: current_observation/UV
            wug_datatype: positive

        niederschlag_1std:
            type: num
            value: -9999
            wug_matchstring: current_observation/precip_1hr_metric
            wug_datatype: positive

        niederschlag_heute:
            type: num
            value: -9999
            wug_matchstring: current_observation/precip_today_metric
            wug_datatype: positive

        windrichtung:
            type: str
            wug_matchstring: current_observation/wind_dir

        windrichtung_grad:
            type: num
            wug_matchstring: current_observation/wind_degrees

        windgeschwindigkeit:
            type: num
            value: -9999
            wug_matchstring: current_observation/wind_kph
            wug_datatype: positive

        windboeen:
            type: num
            value: -9999
            wug_matchstring: current_observation/wind_gust_kph
            wug_datatype: positive

        vorhersage:

            wochentag:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/0/date/weekday

            temperatur_min:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/0/low/celsius

            temperatur_max:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/0/high/celsius

            niederschlag:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/0/pop
                wug_datatype: percent

            niederschlag_ganzertag_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/0/qpf_allday/mm
                wug_datatype: positive

            niederschlag_tag_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/0/qpf_day/mm
                wug_datatype: positive

            niederschlag_nacht_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/0/qpf_night/mm
                wug_datatype: positive

            verhaeltnisse:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/0/conditions

            maxwindspeed:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/0/maxwind/kph
                wug_datatype: positive

            maxwinddir:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/0/maxwind/dir

            maxwinddegrees:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/0/maxwind/degrees

            avgwindspeed:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/0/avewind/kph
                wug_datatype: positive

            avgwinddir:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/0/avewind/dir

            avgwinddegrees:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/0/avewind/degrees

        vorhersage1:

            wochentag:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/1/date/weekday

            temperatur_min:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/1/low/celsius

            temperatur_max:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/1/high/celsius

            niederschlag:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/1/pop
                wug_datatype: percent

            niederschlag_ganzertag_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/1/qpf_allday/mm
                wug_datatype: positive

            niederschlag_tag_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/1/qpf_day/mm
                wug_datatype: positive

            niederschlag_nacht_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/1/qpf_night/mm
                wug_datatype: positive

            verhaeltnisse:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/1/conditions

            maxwindspeed:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/1/maxwind/kph
                wug_datatype: positive

            maxwinddir:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/1/maxwind/dir

            maxwinddegrees:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/1/maxwind/degrees

            avgwindspeed:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/1/avewind/kph
                wug_datatype: positive

            avgwinddir:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/1/avewind/dir

            avgwinddegrees:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/1/avewind/degrees

        vorhersage2:

            wochentag:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/2/date/weekday

            temperatur_min:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/low/celsius

            temperatur_max:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/high/celsius

            niederschlag:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/pop
                wug_datatype: percent

            niederschlag_ganzertag_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/qpf_allday/mm
                wug_datatype: positive

            niederschlag_tag_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/qpf_day/mm
                wug_datatype: positive

            niederschlag_nacht_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/qpf_night/mm
                wug_datatype: positive

            verhaeltnisse:
                type: str
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/conditions

            maxwindspeed:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/maxwind/kph
                wug_datatype: positive

            maxwinddir:
                type: str
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/maxwind/dir

            maxwinddegrees:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/maxwind/degrees

            avgwindspeed:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/avewind/kph
                wug_datatype: positive

            avgwinddir:
                type: str
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/avewind/dir

            avgwinddegrees:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/2/avewind/degrees

        vorhersage3:

            wochentag:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/3/date/weekday

            temperatur_min:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/3/low/celsius

            temperatur_max:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/3/high/celsius

            niederschlag:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/3/pop
                wug_datatype: percent

            niederschlag_ganzertag_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/3/qpf_allday/mm
                wug_datatype: positive

            niederschlag_tag_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/3/qpf_day/mm
                wug_datatype: positive

            niederschlag_nacht_mm:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/3/qpf_night/mm
                wug_datatype: positive

            verhaeltnisse:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/3/conditions

            maxwindspeed:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/3/maxwind/kph
                wug_datatype: positive

            maxwinddir:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/3/maxwind/dir

            maxwinddegrees:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/3/maxwind/degrees

            avgwindspeed:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/3/avewind/kph
                wug_datatype: positive

            avgwinddir:
                type: str
                wug_matchstring: forecast/simpleforecast/forecastday/3/avewind/dir

            avgwinddegrees:
                type: num
                value: -9999
                wug_matchstring: forecast/simpleforecast/forecastday/3/avewind/degrees

```

### logic.yaml

No logic configuration implemented.

## Methods / Functions

No methods or functions are implemented.
