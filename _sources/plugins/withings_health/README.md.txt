# Withings Health

## Description

This plugin allows to retrieve data from the Withings (former Nokia) Health API (https://developer.withings.com/api). Currently it 
only has support for "Withings WS-50 Smart Body Analyzer", a wifi capabale scale.

Support Thread: https://knx-user-forum.de/forum/supportforen/smarthome-py/1141179-nokia-health-plugin

## Requirements

This plugin requires lib withings-api. You can install this lib with: 

```bash
sudo pip3 install withings-api --upgrade
```

You have to register at https://account.withings.com/partner/add_oauth2.
The callback URL to enter when registering is shown via the plugin's web interface and can be added as soon as client_id and consumer_secret have been set in etc/plugin.yaml

The OAuth2 process can then be triggered via the Web Interface of the plugin. Therefore, at least the first four items of the example below need to exist (access_token, token_expiry, token_type, refresh_token).

In case your SmartHomeNG instance is offline for too long, the tokens expire. You then have to start the OAuth2 process via the Web Interface again. Errors will be logged in this case!

## Configuration

### plugin.yaml
```yaml
withings_health: 
    plugin_name: withings_health
    user_id: <your user id>
    client_id: <your client id>
    consumer_secret: <your consumer secret>
    cycle: 300
    instance: withings_health
    
```

### items.yaml

Please be aware that there are dependencies for the values. E.g. the body measurement index will only be calculated if a
height exists. From what i saw so far is, that the height is transmitted only one time, the first time the scale 
communicates with the Withings (former Nokia) servers. In case you miss it, set the item value manually!

The first four items are mandatory, as they are needed for OAuth2 data!

```yaml
body:

    access_token:
        type: str
        visu_acl: ro
        cache: yes
        withings_type@withings_health: access_token

    token_expiry:
        type: num
        visu_acl: ro
        cache: yes
        withings_type@withings_health: token_expiry

    token_type:
        type: str
        visu_acl: ro
        cache: yes
        withings_type@withings_health: token_type

    refresh_token:
        type: str
        visu_acl: ro
        cache: yes
        withings_type@withings_health: refresh_token

    weight:
        type: num
        visu_acl: ro
        withings_type@withings_health: weight

    height:
        type: num
        visu_acl: ro
        withings_type@withings_health: height

    bmi:
        type: num
        visu_acl: ro
        withings_type@withings_health: bmi

    bmi_text:
        type: str
        visu_acl: ro
        withings_type@withings_health: bmi_text

    fat_ratio:
        type: num
        visu_acl: ro
        withings_type@withings_health: fat_ratio

    fat_free_mass:
        type: num
        visu_acl: ro
        withings_type@withings_health: fat_free_mass

    fat_mass_weight:
        type: num
        visu_acl: ro
        withings_type@withings_health: fat_mass_weight

    heart_rate:
        type: num
        visu_acl: ro
        withings_type@withings_health: heart_rate
```

