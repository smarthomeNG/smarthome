# mvg_live - MVG Live

## Requirements
This plugin requires lib PyMVGLive. You can install this lib with:

```
sudo pip3 install mvg --upgrade
```

This plugin provides functionality to query the data of www.mvv-muenchen.de via the python package "mvg" (pip install mvg).

Take care to not run it too often. My example below is manually triggered by a select action in the
smartVISU 2.9 select widget including a refresh button.

Forum thread to the plugin: https://knx-user-forum.de/forum/supportforen/smarthome-py/1108867-neues-plugin-mvg_live

## Configuration

### plugin.yaml

```yaml
mvg_live:
    plugin_name: mvg_live
```

### items.yaml

Currently, no pre defined items exist, the example below needs these items:

```yaml
travel_info:

    mvg_station:

        search:
            type: str
            cache: 'yes'
            visu_acl: rw

            result:
                type: str
                cache: 'yes'
                visu_acl: ro

            refresh:
                type: bool
                visu_acl: rw
                enforce_updates: 'true'
```

## Functions

### get_station_departures(self, station, timeoffset=0, entries=10, ubahn=True, tram=True, bus=True, sbahn=True):
Returns information about the departures in a specific station. See www.mvg-live.de for the allowed names.

## Logics

### logics.yaml

```yaml
MVGWatch:
    filename: mvg.py
    watch_item:
      - travel_info.mvg_station.search
      - travel_info.mvg_station.search.refresh
```

### mvg.py

For the images I am using https://commons.wikimedia.org/wiki/M%C3%BCnchen_U-Bahn?uselang=de and https://commons.wikimedia.org/wiki/Category:Line_numbers_of_Munich_S-Bahn
and put them in the dropins folder of smartVISU (/dropins/icons/myglive/Muenchen_%s.svg.png). %s is e.g. S8 or U3 and inputted from the departure array.
```html
import logging
from datetime import datetime
from lib.shtime import Shtime
logger = logging.getLogger('mvg_info logics')
now = Shtime.get_instance().now()

results = sh.mvg_live.get_station_departures(sh.general.travel_info.mvg_station.search())
html_string = '<table>'
i = 1

for result in results:
    if result['type'] in ["U-Bahn","S-Bahn"]:
        result['linesymbolurl'] = 'https://<sv_dyndns_url>/smartVISU/dropins/icons/mvglive/Muenchen_%s.svg.png'%result['line']
        dir_info = ''
        line_string = '<tr><td style="width: 10px;"></td>'
        line_string += '<td><img src="%s" alt="%s"/></td>' % (result['linesymbolurl'],result['linesymbolurl']) #<td><td style="margin-left: 5px;"><img src="%s" alt="%s"/>
        line_string += '<td style="text-align: left; padding-left: 15px; width:60%;">'
        line_string += '%s </td>' % result['destination']
        line_string += '<td style="color: #000; font-weight: bold; font-size: 25px;">'
        calculated_delay = ""
        if int(datetime.fromtimestamp(result['time']-result['planned']).strftime("%M")) > 0:
            calculated_delay = "(+%i)"%int(datetime.fromtimestamp(result['time']-result['planned']).strftime("%M"))
        line_string += '<div style="background-color: #fff; width: 120px; ">%s %s</div></td></tr>' % (datetime.fromtimestamp(result['time']).strftime("%H:%M"),calculated_delay) #calculated_delay)
        html_string += line_string
        i = i + 1
    if i == 7:
        break

html_string += '</table>'
sh.general.travel_info.mvg_station.search.result(html_string)
```

### smartVISU integration (Requires smartVISU 2.9, as select widget is used)

![smartVISU 2.9 integration](https://github.com/smarthomeNG/plugins/blob/develop/mvg_live/mvg.PNG?raw=true "smartVISU 2.9 integration")

```html
<div class="block">
    <div class="set-2" data-role="collapsible-set" data-theme="c" data-content-theme="a" data-mini="true">
        <div data-role="collapsible" data-collapsed="false">
            <h3>MVG Info</h3>
            <table><tr>
                <td style="width: 100%;">
                {{ basic.select('travel_info.mvg_station.search', 'travel_info.mvg_station.search', '', ['Frankfurter Ring', 'Hauptbahnhof', 'Karlsplatz (Stachus)', 'Marienplatz'], '', ['Frankfurter Ring', 'Hauptbahnhof', 'Karlsplatz (Stachus)', 'Marienplatz']) }}
                </td><td>
                {{ basic.button('travel_info.mvg_station.search.refresh', 'travel_info.mvg_station.search.refresh', '', 'refresh', '1', 'mini') }}
                </td>
            </tr></table>
            {{ basic.print('travel_info.mvg_station.search.result', 'travel_info.mvg_station.search.result', 'html') }}
        </div>
    </div>
</div>
```
