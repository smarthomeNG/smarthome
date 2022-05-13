# snom

## Requirements
This plugin has no requirements or dependencies.

## Configuration

### plugin.yaml

```yaml
snom:
    class_name: Snom
    class_path: plugins.snom
    # phonebook: None
    # username: None
    # password: None
```

#### Attributes
  * `host`: specifies the hostname of your mail server.
  * `port`: if you want to use a nonstandard port.
  * `username`/`password`: login information for _all_ snom phones
  * `phonebook`: path to a xml phonebook file e.g. '/var/www/voip/phonebook.xml'

### items.yaml

#### snom_host
With 'snom_host' you specify the host name or IP address of a snom phone.

#### snom_key
This is the key name of an item in the snom configuration. You have to specify the 'snom_host' in the same or the item above to make the link to the phone.

```yaml
phone:
    snom_host: 10.0.0.4

    display:
        type: str
        snom_key: user_realname1

    mailbox:
        type: num
        ast_box: 33

    hook:
        type: bool
        nw: 'yes'
```

### logic.yaml

Currently there is no logic configuration for this plugin.

## Functions

### phonebook_add(name, number)

If you have specified a phonebook, you could add or change existing entries by calling this function.
You to provide the (unique) name and a number. It will replace the number of an existing entry with exactly the same name.

See the [phonebook logic](https://github.com/smarthomeNG/smarthome/wiki/Phonebook) for a logic which is using this function.
