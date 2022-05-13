# Nuki

Plugin for integrating [Nuki Smartlock](https://nuki.io/de/smart-lock/) into smarthome.py facilitating triggering lock actions and getting status information from it.

## Requirements

You need a [Nuki Bridge](https://nuki.io/de/bridge/) which is already paired with your Nuki Smartlock(s).

## Support

You can find the official support thread for this plugin in the [KNX-User-Forum](https://knx-user-forum.de/forum/supportforen/smarthome-py/1052437-nuki-smartlock-plugin-support-thread).

## Configuration

### plugin.yaml

```yaml
nuki:
    class_name: Nuki
    class_path: plugins.nuki
    bridge_ip: 192.168.1.10
    bridge_port: 8080
    bridge_api_token: q1W2e3
```

#### Attributes

* `bridge_ip` : IP address of the Nuki Bridge
* `bridge_port` : Port number of the Nuki Bridge
* `bridge_api_token` : Token for authentification of the API connection

This information can be set via the Nuki App. 

IMPORTANT: This plugin release (and following) uses the http module (services) extension for
the callback from the Nuki Bridge. Therefore this module must be configured to use the plugin.
Configuring IP and Port for the Callback is not possible within the plugin anymore.
Also note, that the service_user and service_password of the http module cannot be used with
the Nuki bridge (limitation of the bridge, basic auth not supported). Even when configuring them, 
the Nuki callback service won't use it.

### item.yaml

To get the Nuki functionality working, an item has to be type of `num` and  must implement two attributes,
`nuki_id` and `nuki_trigger`.

#### nuki_id
This attribute connects the related item with the corresponding Nuki Smart Lock.
The `nuki_id` can be figured out via the REST API of the Nuki Bridge (see API documentation) or by just (re)starting
SmarthomeNG with the configured Nuki plugin in the log level INFO / DEBUG. The `name` and the `nuki_id` of all paired Nuki Locks will be written to
the log file of SmarthomeNG.

Additionally, the IDs of all paired Nuki Locks are now also shown in the web interface of the plugin!

#### nuki_trigger

There are four types of nuki triggers, `action`, `state`, `doorstate` (only Nuki 2.0!) and `battery`. An item can only have one trigger
attribute at once.

##### action
If you declare an item with the attribute `nuki_trigger: action` you can send actions to your Nuki lock. Below you
can find a list of possible lock actions:

* 1     (unlock)
* 2     (lock)
* 3     (unlatch)
* 4     (lock 'n' go)
* 5     (lock 'n' go with unlatch)

If you set the the items value to one of this numbers, the corresponding lock action will be triggered.


##### state
If you declare an item with the attribute `nuki_trigger: state`, this item will be set to the actual lock state,
whenever these lock state was changed. Find the list with the possible values below:

* 0     (uncalibrated)
* 1     (locked)
* 2     (unlocking)
* 3     (unlocked)
* 4     (locking)
* 5     (unlatched)
* 6     (unlatched (lock 'n' go))
* 7     (unlatching)
* 254   (motor blocked)
* 255   (undefined)


##### doorstate
If you declare an item with the attribute `nuki_trigger: doorstate`, this item will be set to the actual door state,
whenever these door state was changed (only Nuki 2.0!). Find the list with the possible values below:

* 1     (deactivated)
* 2     (door closed)
* 3     (door opened)
* 4     (door state unknown)
* 5     (calibrating)


##### battery
If you declare an item with the attribute `nuki_trigger: state`, this item holds the actual battery state of your
Nuki lock.

* 0     (Batteries are good. No need to replace it.)
* 1     (Batteries are low. Please replace as soon as possible.)


### Example:

```yaml
MyNukiLock:

    MyLockState:
        type: num
        nuki_id: 123456789
        nuki_trigger: state

    MyLockBattery:
        type: num
        nuki_id: 123456789
        nuki_trigger: battery

    MyLockAction:
        type: num
        nuki_id: 123456789
        nuki_trigger: action
        enforce_updates: 'true'
```
