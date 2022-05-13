# MVG Live

## Requirements
This plugin requires lib PyMVGLive. You can install this lib with:

```
sudo pip3 install PyMVGLive --upgrade
```

This plugin provides functionality to query the data of www.mvg-live.de via the python package PyMVGLive.
Take care to not run it too often. My example below is manually triggered by a select action in the
smartVISU 2.9 select widget or a refresh button.

Forum thread to the plugin: https://knx-user-forum.de/forum/supportforen/smarthome-py/1108867-neues-plugin-mvg_live

## Configuration

### plugin.yaml

```yaml
mvg_live:
    class_name: MVG_Live
    class_path: plugins.mvg_live
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

```html
results = sh.mvg_live.get_station_departures(sh.travel_info.mvg_station.search(), entries=15, bus=False, tram=False)
html_string = '<table>'
i = 1
for result in results:

    dir_info = ''
    line_string = '<tr><td style="width: 10px;"></td>'
    line_string += '<td><img src="%s" alt="%s"/><td><td style="margin-left: 5px;"><img src="%s" alt="%s"/></td>' % (
    result['productsymbolurl'], result['product'], result['linesymbolurl'], result['linename'])
    line_string += '<td style="text-align: left; padding-left: 15px; width: 100%;">'
    line_string += '%s </td>' % result['destination']
    line_string += '<td style="color: #000; font-weight: bold; font-size: 25px;">'
    line_string += '<div style="background-color: #fff; width: 30px; ">%i</div></td></tr>' % result['time']
    html_string += line_string
    i = i + 1
    if i == 7:
        break

html_string += '</table>'
sh.travel_info.mvg_station.search.result(html_string)
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
