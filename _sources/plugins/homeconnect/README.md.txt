# HomeConnect

## Description

This plugin allows to retreive and utilize appliances of BSH/Siemens HomeConnect (https://www.home-connect.com/). 
You need to register as a developer at https://developer.home-connect.com/ to obtain a client id and a client secret, but 
also have a regular HomeConnect account.
## Requirements

This plugin directly includes an older working state of code of the following library: https://github.com/DavidMStraub/homeconnect/.
Thanks to the author DavidMStraub for pointing me to that older version. The library is not needed.

The OAuth2 process can then be triggered via the Web Interface of the plugin. Currently the acquired token is stored in the plugin folder
as JSON file. Later I plan to store the information into an item!

In case your SmartHomeNG instance is offline for too long, the tokens expire. You then have to start the OAuth2 process via the Web Interface again. Errors will be logged in this case!

## Configuration

### plugin.yaml
```yaml
home_connect:
    plugin_name: homeconnect
    client_id: "..."
    client_secret: "..."
```

### items.yaml

Currently no items are defined for the plugin. The current state is only for testing the oauth and appliance retrieval.

