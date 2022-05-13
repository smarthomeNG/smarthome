# Indego Plugin

#### Version 1.x.y

This Plugin can connect to the Indego Server and communicate trough the server with Bosch Indego 
lawn mowers with Connect feature over GSM (some older models don't have the connect-feature!).

It is working with the new models like 350 / 400 but also with the older 800/1000/1200 with Connect feature.

With this plugin you can send following commands to your Indego Connect Mower:
- Mow (start mowing)
- Pause (pause mowing / moving)
- go home (go home to charge station)
- enable / disable the smart mowing function (the server will decide at which time your mower will start and stop mowing, considering the temperature and weather)
- set /get the smart mowing frequency (-100 for the lowest mowing frequency +100 for the highest frequency, in my case "0" worked the best)

And get information:
1. Download the actual Map of your garden with a visualisation of the part that had been mowed in the actual session and that needs to be mowed. You also see the position of the mower (yellow point). As the Map is only updated from time to time the position is not very accurate.
2. See the percentage of what had been mowed 
3. See the status of the mower (like docked, mowing, learning garden, going back to the station)
4. See history data of your Mower (like overall mowing time, charge time, next planned smart mowing time and date
5. See user data, like Username, Mode, Firmware version, serial number
6. Get alert messages and the date they occurred and delete them from the server afterwards
7. Get very accurate weather forecast for your address for the next four days, (incl. exp. sunshine hours, possibility of rain, amount of rain for diffrent daytimes)

The plugin does not offer the possibility to set the times of mowing, this can be handled in the app, or for example here: http://grauonline.de/alexwww/indego/indego.html
Please note that you cannot connect with multiple devices at a time with the server. If you connect with the app, the plugin will loose the connection (and try to authenticate again, which will make the authentication of the app invalid). You should avoid to be connecting with the app and the plugin at a time, because it will start the authentication procedure again and again.

Feel free to implement the missing functions in the plugin, as I don't change them, I have no need to be able to change the mowing dates with the calender or the location of the mower.
If you have a problem please start logging the plugins output in debug mode and check the server responses and Plugin outputs. 
From time to time Bosch is adding something, so you might also find new features if you have a look at the server response in debug mode.
For developing you can use a REST client (for example https://github.com/chao/RESTClient)

For support use this thread: https://knx-user-forum.de/forum/supportforen/smarthome-py/966612-indego-connect


### Further Information
Documentation of the server communication: 

* https://github.com/zazaz-de/iot-device-bosch-indego-controller/blob/master/PROTOCOL.md (might be out-dated!)
* https://github.com/zazaz-de/iot-device-bosch-indego-controller/blob/master/README.md

## Requirements

Before you can use the plugin you need to install the indego app on a mobile device and register you Indego mower. 
You will need the Username and Password you set in the app to connect this plugin to the Bosch IOT Server..
For smart mowing it is needed to enter the location in the app or at: http://grauonline.de/alexwww/indego/indego.html

### Supported Hardware

* Indego Connect 350
* Indego Connect 400
* Indego 800/1000/1200 with Connect feature.

## Configuration

### plugin.yaml

Please refer to the documentation generated from plugin.yaml metadata.

```yaml
MyIndego:
    class_name: Indego
    class_path: plugins.indego
    user: 'NUTZERNAME' # -> you need to use the name that you used on your Indego App
    password: 'PASSWORT' # -> you need to use the password that you used on your Indego App
    cycle: 30 # frequency of when how often the status is updated, is working without a problem with 30seconds, not sure when the server will start to be annoyed by your requests 
    img_pfad: '/tmp/garden.svg'  # path where to save the mapfile, take care you smarthome user has write access
    url: 'https://api.indego.iot.bosch-si.com/api/v1/'
    parent_item: 'indego' # the parent item for all relating indego items
```

### items.yaml

**Todo here** Put a sample documentation here 
Please refer to the documentation generated from plugin.yaml metadata.

**Todo here**
Any logics supported?
### logic.yaml
Please refer to the documentation generated from plugin.yaml metadata.

### Integration into SmartVisu

#### for SmartVISU Version 2.9 (aka develop)
**Todo here** 
You can use the dropins folder for SmartVISU for all additional stuff without affecting the ``git pull`` mechanism 

see here 
https://knx-user-forum.de/forum/supportforen/smartvisu/1144945-k%C3%BCrzlich-hinzugef%C3%BCgte-features
and here
https://github.com/Martin-Gleiss/smartvisu/blob/develop/dropins/README.md


#### for SmartVISU Version < = 2.8 (aka master)

In smartVISU_dropins you will find resources for usage with SmartVISU.

copy all png files in ``smartVISU_dropins\lib\weather\pics`` to the folder ``[your smartVISU home]\lib\weather\pics``

copy all svg files in ``smartVISU_dropins\icons`` to the folder ``[your smartVISU home]\icons\ws"

copy ``smartVISU_dropins\pages\your pages folder\widget_basic_input.html`` and 
``smartVISU_dropins\pages\your pages folder\widget_basic_large_symbol.html`` to your pages folder at ``[your smartVISU home]\pages\{your folder}``

copy ``smartVISU_dropins\pages\your pages folder\indego.html`` to ``[your smartVISU home]\pages\{your folder}\indego.html``

Edit ``[your smartVISU home]\pages\{your folder}\indego.html`` and adjust the path of the map in line 22 
``{{ multimedia.image('image3', {path where your map is saved, defined in plugin conf img_pfad}, 'corner','20s') }} </br>``

Please be aware that SmartHomeNG user as well as the Webserver needs to have access to the image file! 

## Methods
Please refer to the documentation generated from plugin.yaml metadata.


## Examples


You need the following item structure for the plugin to work (which is provided as example.yaml)
The base item ``indego`` may be changed to something else but it is mandatory.

```yaml
%YAML 1.1
---

indego:

    online:
        type: bool

    stateCode:
        type: num

    state_str:
        type: str

    stateError:
        type: num

    config_change:
        type: bool
        indego_add_key: config_change

    mow_trig:
        type: bool
        indego_add_key: mow_trig

    stateLevel:
        type: num

    docked:
        type: bool
        sqlite: 'yes'

    moving:
        type: bool
        sqlite: 'yes'

    pause:
        type: bool
        sqlite: 'yes'

    help:
        type: bool
        sqlite: 'yes'

    mowedPercent:
        type: num

    mapSvgCacheDate:
        type: foo
        cache: 'on'

    mapUpdateAvailable:
        type: bool

    mowedDate:
        type: foo
        cache: 'on'

    xPos:
        type: num

    yPos:
        type: num

    svg_xPos:
        type: num

    svg_yPos:
        type: foo

    mowmode:
        type: num

    next_time:
        type: foo
        cache: 'on'

    runtimeTotalOperationMins:
        type: num
        sqlite: 'yes'

        hours:
            type: num
            sqlite: 'yes'
            eval: round(sh.indego.runtimeTotalOperationMins()/60,0)
            eval_trigger: indego.runtimeTotalOperationMins

    runtimeTotalChargeMins:
        type: num
        sqlite: 'yes'

        hours:
            type: num
            sqlite: 'yes'
            eval: round(sh.indego.runtimeTotalChargeMins()/60,0)
            eval_trigger: indego.runtimeTotalChargeMins

    runtimeSessionOperationMins:
        type: num
        sqlite: 'yes'

    runtimeSessionChargeMins:
        type: num
        sqlite: 'yes'

    SMART:
        type: bool
        visu_acl: rw
        indego_smart: 'yes'
        cache: 'on'

        frequenz:
            type: num
            indego_frequency: 'yes'
            cache: 'on'

    MOW:
        type: bool
        visu_acl: rw
        indego_command: '{"state":"mow"}'
        autotimer: 5 = False

    PAUSE:
        type: bool
        visu_acl: rw
        indego_command: '{"state":"pause"}'
        autotimer: 5 = False

    RETURN:
        type: bool
        visu_acl: rw
        indego_command: '{"state":"returnToDock"}'
        autotimer: 5 = False

    alm_sn:
        type: num

    alm_name:
        type: str

    service_counter:
        type: num

    needs_service:
        type: bool

    alm_mode:
        type: str

    bareToolnumber:
        type: str

    alm_firmware_version:
        type: str
        cache: 'on'

        before:
            type: str
            cache: 'on'

        changed:
            type: foo
            cache: 'on'

    alert_message:
        type: str
        cache: 'on'

    alert_id:
        type: str
        cache: 'on'

    alert_id_send:
        type: str
        cache: 'on'

    alert_flag:
        type: str
        cache: 'on'

    alert_headline:
        type: str
        cache: 'on'

    alert_date:
        type: foo
        cache: 'on'

    weather:

        int_0:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_1:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_2:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_3:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_4:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_5:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_6:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_7:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_8:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_9:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_10:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_11:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_12:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_13:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_14:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_15:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_16:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_17:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_18:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        int_19:

            wwsymbol_mg2008:
                type: num
                cache: 'on'

            td:
                type: num
                cache: 'on'

            dateTime:
                type: foo
                cache: 'on'

            tt:
                type: num
                cache: 'on'

            wwtext:
                type: str

            rrr:
                type: num
                cache: 'on'

            prrr:
                type: num
                cache: 'on'

            intervalLength:
                type: num
                cache: 'on'

            spells:
                type: bool
                cache: 'on'

            Sonne:
                type: bool
                cache: 'on'

            Wolken:
                type: bool
                cache: 'on'

            Regen:
                type: bool
                cache: 'on'

            Gewitter:
                type: bool
                cache: 'on'

        day_0:

            tx:
                type: num
                cache: 'on'

            date:
                type: foo
                cache: 'on'

            wochentag:
                type: str
                cache: 'on'

            sun:
                type: num
                cache: 'on'

            tn:
                type: num
                cache: 'on'

        day_1:

            tx:
                type: num
                cache: 'on'

            date:
                type: foo
                cache: 'on'

            wochentag:
                type: str
                cache: 'on'

            sun:
                type: num
                cache: 'on'

            tn:
                type: num
                cache: 'on'

        day_2:

            tx:
                type: num
                cache: 'on'

            date:
                type: foo
                cache: 'on'

            wochentag:
                type: str
                cache: 'on'

            sun:
                type: num
                cache: 'on'

            tn:
                type: num
                cache: 'on'

        day_3:

            tx:
                type: num
                cache: 'on'

            date:
                type: foo
                cache: 'on'

            wochentag:
                type: str
                cache: 'on'

            sun:
                type: num
                cache: 'on'

            tn:
                type: num
                cache: 'on'

        day_4:

            tx:
                type: num
                cache: 'on'

            date:
                type: foo
                cache: 'on'

            wochentag:
                type: str
                cache: 'on'

            sun:
                type: num
                cache: 'on'

            tn:
                type: num
                cache: 'on'
```

