# wetter.com

## Requirements

wetter.com account with project, recommended: 3 days, all data transmitted


## Configuration

### plugin.yaml

```yaml
wettercom:
    class_name: wettercom
    class_path: plugins.wettercom
    # apikey: <enter your api code here>
    # project: <enter your project name here>
```

add your project on wetter.com and paste API-key and project name
in plugin.yaml

### items.yaml

Create a yaml file in the items folder with the following content or copy the file from additional_files

#### Example

```yaml
wetter:
    vorhersage:
        heute:
            frueh:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
            mittag:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
            spaet:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
            nacht:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
        morgen:
            frueh:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
            mittag:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
            spaet:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
            nacht:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
        uebermorgen:
            frueh:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
            mittag:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
            spaet:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
            nacht:
                temperatur:
                    max:
                        type: num
                    min:
                        type: num
                text:
                    type: str
                code:
                    type: num
                wind:
                    geschwindigkeit:
                        type: num
                    richtung:
                        type: num
                        text:
                            type: str
                niederschlag:
                    type: num
```

This structure will be filled by the example logic file (see below)

### logic.yaml
Use etc/logic.yaml for cyclic call (900s or so, requests are limited
at 10000 / month)

```yaml
wettercom:
    filename: wettercom.py
    visu_acl: rw
    crontab: init
    cycle: 900
```

#### Example wettercom.py

Create a wettercom.py File in the logics folder or copy the file from additional_files.
Change the city code appropriately!

```python
#!/usr/bin/env python
# parse weather data

forecast = sh.wettercom.forecast('CITYCODE')

d0 = sh.now().date()
d1 = (sh.now() + dateutil.relativedelta.relativedelta(days=1)).date()
d2 = (sh.now() + dateutil.relativedelta.relativedelta(days=2)).date()

items = { d0: sh.wetter.vorhersage.heute, d1: sh.wetter.vorhersage.morgen, d2: sh.wetter.vorhersage.uebermorgen}
try:
  for date in forecast:
      if date.date() in items:
          base = items[date.date()]
          if date.hour == 6:
              frame = base.frueh
          elif date.hour == 11:
              frame = base.mittag
          elif date.hour == 23:
              frame = base.nacht
          else:  # hour == 18
              frame = base.spaet
          frame.temperatur.min(forecast[date][0])
          frame.temperatur.max(forecast[date][1])
          frame.text(forecast[date][2])
          frame.niederschlag(forecast[date][3])
          frame.wind.geschwindigkeit(forecast[date][4])
          frame.wind.richtung(forecast[date][5])
          frame.wind.richtung.text(forecast[date][6])
          frame.code(forecast[date][7])
except TypeError as e:
  logger.debug("Problems fetching wetter.com forecast.  TypeError: {}".format(e))

except AttributeError as e:
  logger.debug("Problems fetching wetter.com forecast.  AttributeError: {}".format(e))

except:
  e = sys.exc_info()[0]
  logger.debug("Problems fetching wetter.com forecast:  {}".format(e))

logger.debug(forecast)
```

This logic will parse the weather data and put it in the example items.yaml
above.

## Methods

### search(location)
Uses wetter.com to search for your city_code. method will return an
empty dictionary if no match is found. If more than one match is found,
the dictionary will contain at most 20 matches, best match first

### forecast(city_code)
Returns forecast data for your city_code (use search or wetter.com
website to find it). Forecast data is returned as dictionary for each
date/time (usually three days at four times). Values are min. temperature,
max. temperature, weather condition text, condensation probability,
wind speed, wind direction in degree, wind direction text,
weather condition code (can be used to select appropriate icon)
