# CLI

## Configuration

### plugin.yaml

```
cli:
    plugin_name: cli
    # ip = 127.0.0.1
    # port = 2323
    # update = false
    # hashed_password = 1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d
```

This plugin listens for a telnet connection.

``ip = `` used network interface, e.g. 127.0.0.1 (localhost, default) or listen on all network interfaces: 0.0.0.0
``port =`` used network port, default 2323
``update =`` restrict the access of the items to read only (false, default) or allows read/write access (true)
``hashed_password = `` password that needs to be entered on login. SHA-512 hashed. Value shown above is "very_secure_password"

The hashed_password can be obtained by using the backend's service page and the hash generator.

## Usage

Telnet to the configured IP adress and port.

Enter ``help`` for a list of available commands.

You can enter ``help [commandgroup]`` to see only commands belonging to that group (and global commands). Commandgroups are ``item``, ``logic``, ``log`` and ``scheduler``.

command | function
--- | ---
``if`` | list the first level items
``if [item]`` | list item and every child item (with values)
``ii [item]`` | dump detail-information about a given item - command alias: dump
``il`` | list all items (with values) - command alias: la
``iup`` | alias for iupdate
``iupdate [item] = [value]`` | update the item with value - command alias: update
``ld [logic]`` | disables logic - command alias: dl
``le [logic]`` | enables logic - command alias: el
``li [logic]`` | dump details about a given logic (new in v1.4)
``ll`` | list all logics and next execution time - command alias: lo
``lr [logic]`` | reload a logic - command alias: rl
``lrr [logic]`` | reload and run a logic - command alias: rr
``lt [logic]`` | trigger a logic - command alias: tr
``logc [log]`` | clean (memory) log
``logd [log]`` | log dump of (memory) log
``rt`` | return runtime
``si [task]`` | show details for given task
``sl`` | list all scheduler tasks by name
``st`` | list all scheduler tasks by execution time
``tl`` | list current thread names
``quit`` | quit the session
``q`` | alias for quit

Plugins may append additional commands. They will be listed with the "help" command, too.

### Example:
``up office.light = On`` to update an item named _office.light_ to value _On_
