# Elro

## Description

You can use this Plugin to control elro (or elro-based) remote-control-switches (rc-switches).
If the backend-server uses the same command-syntax as the rc_switch_server project,
you can even control non-elro rc-switches too! (Or everything other that can be switched on and off)

For rc_switch_server command-syntax look at https://github.com/Brootux/rc_switch_server.py (Server-Clients)

## Requirements

  * Installed and running rc_switch_server (https://github.com/Brootux/rc_switch_server.py)

## Configuration

### plugin.yaml

You have to just simply copy the following into your plugin.yaml file. The ip-address/hostname of the rc_switch_server has to be setup later in the items.yaml!

```yaml
elro:
    class_name: Elro
    class_path: plugins.elro
```

### items.yaml

The most item-fields of this plugin are mandatory. So you should always use all of the fields showed in the following example.

#### Example

```yaml
RCS:
    type: str
    elro_host: localhost
    elro_port: 6700

    A:
        type: bool
        elro_system_code: 0.0.0.0.1
        elro_unit_code: 1
        elro_send: value
        enforce_updates: 'yes'
        visu_acl: rw

    B:
        type: bool
        elro_system_code: 0.0.0.0.1
        elro_unit_code: 2
        elro_send: value
        enforce_updates: 'yes'
        visu_acl: rw

    C:
        type: bool
        elro_system_code: 0.0.0.0.1
        elro_unit_code: 4
        elro_send: value
        enforce_updates: 'yes'
        visu_acl: rw

    D:
        type: bool
        elro_system_code: 0.0.0.0.1
        elro_unit_code: 8
        elro_send: value
        enforce_updates: 'yes'
        visu_acl: rw
```

Description of the attributes:

* __elro_host__: the ip-address/hostname of the rc_switch_server (mandatory)
* __elro_port__: the port of the rc_switch_server
* __elro_system_code__: the code of your home (mandatory)
* __elro_unit_code__: the code of the unit, you want to switch (mandatory)
* __elro_send__: use always "value" here (mandatory)

Hints:
* __You have to setup the items as showed in a tree structure with the `elro_host` as its root!__ (The tree can be a subtree of a greater tree but always has to be `elro_host` as a attribute of the root item)
* For __elro_system_code__ you have to set the correct bits of you code (no conversion)
* For __elro_unit_code__ you have to convert your settings to binary (A = 1, B = 2, C = 4, D = 8, ...)
* For __elro_send__ always use the transmitting of a value per button (because sometimes the signals dont get transported correctly from remote-transmitter, so you should have the chance to send "on" or "off" more than once)

### Example for multiple rc_switch_server´s

```yaml
RCS1:
  type: str
  elro_host: localhost
  elro_port: 6700
  A:
    type: bool
    elro_system_code: '0.0.0.0.1'
    elro_unit_code: 1
    elro_send: value
    enforce_updates: yes
    visu_acl: rw

RCS2:
  type: str
  elro_host: 192.168.0.100
  elro_port: 6666
  A:
    type: bool
    elro_system_code: '0.0.0.0.2'
    elro_unit_code: 1
    elro_send: value
    enforce_updates: yes
    visu_acl: rw
```

### SmartVisu

I suggest you to use the following setup per rc-switch:

```html
<span data-role="controlgroup" data-type="horizontal">
	<h3>TV-Center</h3>
	{{ basic.button('rcs_tv_on', 'RCS.A', 'On', '', '1', 'midi') }}
	{{ basic.button('rcs_tv_off', 'RCS.A', 'Off', '', '0', 'midi') }}
</span>
```
