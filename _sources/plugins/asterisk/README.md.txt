# Asterisk

## Requirements

A running asterisk daemon with a configured Asterisk Manager Interface (AMI) is necessary.
In manager.config its required to enable at least:
``read = system,call,user,cdr`` and ``write = system,call,orginate``

## Configuration

### plugin.yaml

The plugin needs the username and password of the AMI and a IP and port address if asterisk does not run on localhost.

```yaml
ast:
    plugin_name: asterisk
    username: admin
    password: secret
    host: 127.0.0.1    # default
    port: 5038    # default

```

### items.yaml

#### ast_dev

It is possible to specify the ``ast_dev`` attribute to an bool item in items.yaml.
The argument could be a number or string and correspond to the asterisk device configuration.
E.g. ``2222`` for the following device in asterisk ``sip.conf``:

```
[2222]
secret=very
context=internal
```

#### ast_box
The mailbox number of this phone. It will be set to the number of new messages in this mailbox.

#### ast_db
Specify the database entry which will be updated at an item change.

In items.yaml:

```yaml
office:

    fon:
        type: bool
        ast_dev: 2222
        ast_db: active/office

        box:
            type: num
            ast_box: 22
```

Calling the '2222' from sip client or making a call from it, item ``office.fon`` will be set to True.
After finishing the call, it will be set to False.


### logic.yaml

It is possible to specify the `ast_userevent` keyword to every logic in logic.yaml.

```
logic1:
    ast_userevent: Call

logic2:
    ast_userevent: Action
```

In the asterisk extensions.conf ``exten => _X.,n,UserEvent(Call,Source: ${CALLERID(num)},Value: ${CALLERID(name)})`` would trigger 'logic1' every time, this UserEvent is sent.

A specified destination for the logic will be triggered e.g. ``exten => _X.,n,UserEvent(Call,Source: ${CALLERID(num)},Destination: Office,Value: ${CALLERID(name)})``


### Functions


#### call(source, dest, context, callerid=None)

`sh.ast.call('SIP/200', '240', 'door')` would initate a call from the SIP extention '200' to the extention '240' with the 'door' context. Optional a callerid for the call is usable.

#### db_write(key, value)

``sh.ast.db_write('dnd/office', 1)`` would set the asterisk db entry ``dnd/office`` to ``1``.

#### db_read(key)

``dnd = sh.ast.db_read('dnd/office')`` would set ``dnd`` to the value of the asterisk db entry ``dnd/office``.

#### mailbox_count(mailbox, context='default')

``mbc = sh.ast.mailbox_count('2222')`` would set ``mbc`` to a tuple ``(old_messages, new_messages)``.

#### hangup(device)

``sh.ast.hangup('30')`` would close all connections from or to the device ``30``.
