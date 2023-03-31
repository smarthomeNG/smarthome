# jvcproj - JVC D-ILA Control

With this plugin you can control JVC D-ILA projectors over TCP by using the "JVC External Control Command Communication Specification" and transfer gammatables generated with jvcprojectortools.

## Notes
I use the plugin to control my JVC DLA- X5000 and transfer raw gammatables generated with jvcprojectortools by arvehj. Many thanks to arvehjs groundwork so i could have a look in the communication procedure!
You can use all operation commands given in the "JVC External Control Command Communication Specification". Wrong or unknown commands will be ignored by the plugin and the projector. Most of the commands will not be acknowledged when the projector has no input signal. Request commands are not yet supported.
The gamma table configuration files can be raw gamma table files (loaded from the projector with jvcprojectortools) or the configuration files that are generated with jvcprojectortools when you save your parameters. When using these files only the deposited raw gamma data ("table"- data) is needed and will be transfered.

The plugin should work from the projector generation X3/X7/X9 up to X5900/X7900/X9900 and surely for upcoming generations, too.

Please use [this thread for support, questions, feedback etc.](https://knx-user-forum.de/forum/supportforen/smarthome-py/1188479-plugin-steuerung-von-jvc-d-ila-projektoren)

## Configuration

### plugin.yaml

```yaml
jvcproj:
    plugin_name: jvcproj
    host: 1.1.1.1 # host address of the projector
    gammaconf_dir: ... # optional, location gamma table configuration files
```

#### Attributes
  * `host`: the host address of the projector
  * `gammaconf_dir`: location where the gammatable configuration files are saved. Default is '/usr/local/smarthome/etc/jvcproj/'

### items.yaml

#### operation commands
The plugin uses the raw hex operation commands. A list of all commands (depending on the projectors series) can be found by looking at the JVC support homepage or by searching for JVC projector RS-232 command lists.
Here is a small example for an operation command "Power On" (21 89 01 50 57 31 0A):

  * `21`: Header - an operation command always start with 21 (ASCII: "!")
  * `89 01`: Unit ID - is fixed at 89 01 for all models
  * `50 57`: Command - varies depending on the command. In this example 50 57 (ASCII: "PW")
  * `30`: Data - This is the value to apply to the command. Using the Power example above, the data value for On is 31 (ASCII: "1"). Length varies depending on command (not always 1 byte)!
  * `0A`: End - This signifies the end of the command and is fixed at 0A for all models.

### Example:

```yaml
jvcproj:

    testcmd:
    # command NULL
        type: bool
        visu_acl: rw
        jvcproj_cmd: 21 89 01 00 00 0A
        enforce_updates: True

    pwon:
    # command Power ON
        type: bool
        visu_acl: rw
        jvcproj_cmd: 21 89 01 50 57 31 0A
        enforce_updates: True

    pwoff:
    # command Power OFF
        type: bool
        visu_acl: rw
        jvcproj_cmd: 21 89 01 50 57 30 0A
        enforce_updates: True

    picmode:

        cmdoff:
        # command ClearMotionDrive OFF
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 50 4D 43 4D 30 0A
            enforce_updates: True

        cmdlow:
        # command ClearMotionDrive LOW
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 50 4D 43 4D 33 0A
            enforce_updates: True

        sdrlow:
        # commands to set -picture user 1- and -gamma custom 1- and -gamma correction import-
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 50 4D 50 4D 30 43 0A | 21 89 01 50 4D 47 54 34 0A | 21 89 01 50 4D 47 43 30 34 0A
            enforce_updates: True

        sdrhigh:
        # commands to set -picture user 2- and -gamma custom 2- and -gamma correction import-
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 50 4D 50 4D 30 44 0A | 21 89 01 50 4D 47 54 35 0A | 21 89 01 50 4D 47 43 30 34 0A
            enforce_updates: True

        hdrlow:
        # commands to set -picture user 4- and -gamma custom 3- and -gamma correction import-
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 50 4D 50 4D 30 46 0A | 21 89 01 50 4D 47 54 36 0A | 21 89 01 50 4D 47 43 30 34 0A
            enforce_updates: True

        hdrhigh:
        # commands to set -picture user 3- and -gamma custom 3- and -gamma correction import-
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 50 4D 50 4D 30 45 0A | 21 89 01 50 4D 47 54 36 0A | 21 89 01 50 4D 47 43 30 34 0A
            enforce_updates: True

    gamma:

        hdrlow:
        # command to set gammatable from file to -gamma custom 3-
            type: bool
            visu_acl: rw
            jvcproj_gamma: jvc_gamma_HDR_lowdynamic.conf | custom3
            enforce_updates: True

        hdrmid:
        # command to set gammatable from file to -gamma custom 3-
            type: bool
            visu_acl: rw
            jvcproj_gamma: jvc_gamma_HDR_middynamic.conf | custom3
            enforce_updates: True

        hdrhigh:
        # command to set gammatable from file to -gamma custom 3-
            type: bool
            visu_acl: rw
            jvcproj_gamma: jvc_gamma_HDR_highdynamic.conf | 21 89 01 50 4D 47 54 36 0A
            enforce_updates: True

    lens:

        mem219:
        # command to set -lens memory 1- and -lens mask 1-
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 49 4E 4D 4C 30 0A | 21 89 01 49 53 4D 41 30 0A
            enforce_updates: True

        mem169:
        # command to set -lens memory 2- and -lens mask 2-
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 49 4E 4D 4C 31 0A | 21 89 01 49 53 4D 41 31 0A
            enforce_updates: True

    rc:
    # remote control commands

        menu:
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 52 43 37 33 32 45 0A
            enforce_updates: True

        ok:
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 52 43 37 33 32 46 0A
            enforce_updates: True

        up:
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 52 43 37 33 30 31 0A
            enforce_updates: True

        down:
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 52 43 37 33 30 32 0A
            enforce_updates: True

        left:
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 52 43 37 33 33 36 0A
            enforce_updates: True

        right:
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 52 43 37 33 33 34 0A
            enforce_updates: True

        info:
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 52 43 37 33 37 34 0A
            enforce_updates: True

        back:
            type: bool
            visu_acl: rw
            jvcproj_cmd: 21 89 01 52 43 37 33 30 33 0A
            enforce_updates: True
```

#### jvcproj_cmd:
Item to send one (or more) commands to the projector. The commands must be seperated with a `|`.
When more than one command is given in an item the commands will be sent one after the other until the list is finished or an error occures.
The commands can be listed with or without spaces (21 89 01 50 57 31 0A or 2189015057310A).

Example to set lens memory 1 (with spaces) and set lens mask to user 1 (without spaces). Commands are seperated with "|"...

```yaml
    mem219:
    # command to set -lens memory 1- and -lens mask 1-
        type: bool
        visu_acl: rw
        jvcproj_cmd: 21 89 01 49 4E 4D 4C 30 0A | 21890149534D41300A
        enforce_updates: True
```

#### jvcproj_gamma:
Item to send a gamma table from a declared file. This item needs exactly two arguments!
The first argument is the name of the gamma table configuration file to be loaded. The file must exist in the declared path in the plugin.yaml (default /usr/local/smarthome/etc/jvcproj/ ).
The second argument is the gamma slot where to load the gamma data. This MUST be a custom gamma table and can be declared with custom1/custom2/custom3 or the compatible hex commands.

Two examples, both will load the gamma data from file to gamma slot custom 3
```yaml
    hdrmid:
    # command to set gammatable from file to -gamma custom 3-
        type: bool
        visu_acl: rw
        jvcproj_gamma: jvc_gamma_HDR_middynamic.conf | custom3
        enforce_updates: True

    hdrhigh:
    # command to set gammatable from file to -gamma custom 3-
        type: bool
        visu_acl: rw
        jvcproj_gamma: jvc_gamma_HDR_highdynamic.conf | 21 89 01 50 4D 47 54 36 0A
        enforce_updates: True
```

### logging
Debug logging informationen for this plugin can be activated in the logging.yaml
```yaml
loggers:
...
    plugins.jvcproj:
        level: DEBUG
...
```
