#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab


""" commands for example plugin

This section consists of a single dict which defines all the devices' commands.
The first example illustrates the generic syntax and the possible attributes and
the second example shows nested command definitions.

If models are defined and commands with the same name are identical on different
models, this definition syntax can be used. For specifying which commands are
present on which model, see below.
Alternatively, if commands with the same name are different on different models,
see the third example for commands definition.

In the first example, only one command is given to define possible keys and their
values' meaning.
"""

commands = {
    # name of the command as used in item attribute 'ex_command'
    # provided values are defaults; dicts default to None, but are shown to
    # illustrate valid contents
    'cmd': {
        # can this command read = request values from the device?
        'read': True,

        # can this command write = send item values to the device?
        'write': False,

        # general / fallback command sequence/string/..., HTTP URL for SDP_Connection_Net_Tcp_Request
        #
        # With the SDPCommandStr class, the following substitutions are available:
        # - ``{OPCODE}`` is replaced with the opcode,
        # - ``{PARAM:attr}`` is replaced with the value of the attr element from the plugin configuration,
        # - ``{VALUE}`` is replaced with the given value (converted by DT-class)
        # - ``{CUSTOM_ATTR1}``...``{CUSTOM_ATTR3}`` is replaced by the respective custom attribute
        #
        # With the SDPCommandParseStr class, the following additional substitutions
        # apply for string values:
        # - ``{RAW_VALUE}`` is replaced with the raw value
        # - ``{RAW_VALUE_LOWER}`` is replaced with the lowercase value
        # - ``{RAW_VALUE_UPPER}`` is replaced with the uppercase value
        # - ``{RAW_VALUE_CAP}`` is replaces with the capitalized value
        'opcode': '',

        # optional, specific command to read value from device (if not defined, use opcode)
        'read_cmd': '',

        # optional, specific command to write item value to device (if not defined, use opcode)
        'write_cmd': '',

        # expected SmartHomeNG item type of associated item == default item type into which to convert replies
        'item_type': 'bool',

        # datatype used to talk to the device (see ../datatypes.py). For DT_xyz class, use 'xyz'
        'dev_datatype': 'raw',

        # optional, regex (str) or list of regexes (str) to identify a reply belonging to this command
        # additionally, with only one (optional) capturing group to automatically
        # extract the reply value from the reply
        # Value extraction is implemented only in SDPCommandParseStr as of now
        #
        # if reply_pattern is set to '*', it will be replaces with the opcode of the command
        #
        # you can use the following tokens to have them replaced by their respective values:
        # - ``{LOOKUP}`` to replace with a regex which matches on all values from the command lookup table
        # - ``{VALID_LIST}`` to replace with all valid values according to the cmd_settings
        # - ``{VALID_LIST_CI}`` ditto, with case-insensitive flag set
        # - ``{CUSTOM_PATTERN1}``...``{CUSTOM_PATTERN3}`` to replace with the respective
        #   custom pattern as defined in the device class to identify one of the custom tokens
        'reply_pattern': [],

        # optional, this dict defines limits for value validity for sending data to the device.
        # - 'valid_min': minimum value, error if value is below
        # - 'valid_max': maximum value, error if value is above
        # - 'force_min': minimum value, set to this value if below (precedence over min)
        # - 'force_max': maximum value, set to this value is above (precedence over max)
        # - 'valid_list': list of allowed values, error if not in list
        # - 'valid_list_ci': ditto, but case insensitive
        'cmd_settings': {'valid_min': 0, 'valid_max': 255, 'force_min': 0, 'force_max': 255, 'valid_list': [1, 2, 3, 4, 5]},

        # optional, specifies lookup table to use (see below)
        # if a lookup table is defined, the value from SmartHomeNG is looked up
        # in the named table and the resulting value is processed by the device
        # instead; correspondingly, a converted value from the device is fed into
        # the lookup and the respective value is passed to SmartHomeNG as the value
        # for the item.
        # This makes it easy e.g. to convert numerical values into clear-text values
        # Note: setting this option ignores the ``settings`` parameters!
        'lookup': '<table_name>',

        # optional, for JSON-RPC data. Needs to be dict or list, can be nested,
        # but nesting does not support dicts inside lists. (Nesting does, but the
        # handling doesn't... and the spec doesn't want this)
        # setting a value to ``{VALUE}`` will have it replaced with the item's value
        # setting a key to ``playerid`` or a list value to ``{ID}`` and providing
        # `playerid` as key in kwargs has it replaced with the playerid value.
        # tuples trigger eval'ing the first item of the tuple and replacing the
        # tuple with the result of the eval.
        'params': {'dict': ['or', 'list']},

        # optional, specifies item attributes if struct file is generated by plugin
        'item_attrs': {

            # the following entries are directives for the struct.yaml generator

            # create "ex_read_initial: true" entry
            # can also be specified for sections to trigger initial read group reading
            'initial': False,

            # create "ex_read_cycle: <cycle>" entry with given cycle time
            # can also be specified for section to trigger cyclic read group reading
            'cycle': None,

            # create "enforce_updates: true" entry
            'enforce': False,

            # control autocreation of item read groups. None or key not present
            # means create all levels (default)
            # 0 means don't create read groups (not even from 'read_groups' dict!)
            # x (int > 0) means include the x lowest levels of read groups
            # e.g. if current item gets read groups
            #      ['l1', 'l1.l2', 'l1.l2.l3', 'l1.l2.l3.l4'], setting
            #      read_group_levels': 2 will yield
            #      ex_read_groups: ['l1.l2.l3', 'l1.l2.l3.l4']
            'read_group_levels': None,

            # create subitem 'lookup' containing lookup table
            # if lookup_item is True or 'list', the lookup will be type 'list'
            # otherwise specify 'lookup_item': 'fwd' / 'rev' / 'rci'
            'lookup_item': False,

            # create custom[123] item attribute
            # to override inheriting custom attributes for a single item,
            # set this to ''
            #
            # for this to work, the corresponding item attribute needs to
            # be defined in plugins/<plugin>/plugin.yaml
            'custom1': None,
            'custom2': None,
            'custom3': None,

            # attributes to add to the item definition verbatim
            # e.g. eval: or on_change: attributes. you can even 
            # create special sub-items here (provide as sub-dict)
            'attributes': {
                'attr1': 'value1',
                'attr2': 'value2'
            },

            # item attribute templates to include in item definition
            # templates are defined in ``item_templates`` dict in this file
            'item_template': ['template1', 'template2'],

            # additional read group configuration
            'read_groups': [
                {
                    # name of read group
                    'name': '<read group 1>',
                    # item path of trigger item to create
                    # item location is "in" current item (as sub-item)
                    # item path is relative, each leading dot means "up 1 level"
                    # so '.sibling' and 'child' are possible as well as
                    # '...some.other.path'
                    'trigger': 'path.to.item'
                },
                {
                    'name': '<read group 2>',
                    'trigger': '..path.to.other.item'
                }
            ],
        }
    }
}

""" commands: nested definitions

If many commands are present, it might be beneficial to create a hierarchical
structure via nested dicts. This is simple as nesting can - more or less - be
used as you like.
In the item definition, the combined command names from the following example
are:

* level1a.level2a.cmd1
* level1a.level2b.cmd1
* level1a.level2b.cmd2

Note that the two commands 'cmd1' are completely independent, as the internal
name includes the full path.
"""

commands = {
    'level1a': {
        'level2a': {
            'cmd1': {'contents': 'like first example'}
        },
        'level2b': {
            'cmd1': {'as': 'above'},
            'cmd2': {'still': 'unchanged'}
        }
    }
}

""" commands: model-specific definitions

The following commands example is for a scenario where different models are
configured and have overlapping command definitions with different contents.

The key on the first level specify the model or 'ALL' for commands common to
all models. 'ALL' needs to be present, even if it is an empty dict, as this
indicates the second definition syntax. Models not present on the first level
will load only the commands from the 'ALL' section.
Below the first level, commands are defined as in the first or second example,
nesting commands is supported.
There exist no dependencies between the different models.

In this case, the ``models`` dict (see next paragraph) is not necessary and
will be ignored.
"""

commands = {
    'ALL': {
        'cmd1': {'read': True, 'write': True, 'opcode': '1a', 'attrib': '...'},
        'cmd2': {'read': False, 'write': True, 'opcode': '2b', 'attrib': '...'},
    },
    'model1': {
        'cmd3': {'read': True, 'write': False, 'opcode': '3c', 'attrib': '...'},
        'cmd4': {'read': False, 'write': False, 'opcode': '4d', 'attrib': '...'},
    },
    'model3': {
        # note different opcode for cmd1, which overwrites cmd1 from ALL section
        'cmd1': {'read': True, 'write': True, 'opcode': '3a', 'attrib': '...'},
        'cmd3': {'read': True, 'write': False, 'opcode': '3z', 'attrib': '...'},
    },
    'model4': {
        'section1': {
            'cmd1': {'read': True, 'write': True, 'opcode': 'VI', 'attrib': '...'},
            'cmd2': {'read': False, 'write': True, 'opcode': 'VII', 'attrib': '...'},
        },
        'section2': {
            'cmd1': {'read': True, 'write': True, 'opcode': 'XX', 'attrib': '...'},
            'cmd2': {'read': False, 'write': True, 'opcode': 'YY', 'attrib': '...'},
        }
    }
}

""" model: (optional) specifications for dev example

Different models of a type (eg. different heating models of the same manufacturer
or different AV receivers of the same series) might require different command
sets.

This - optional - dict allows to specify sets of commands which are supported
by different models. The keys are the model names and the values are lists of
all commands supported by the respective model. Commands listed under the
special - optional - key `ALL` are added to all models.

If the device is configured without a model name, all commands will be available.
If the device is configured with a model name not listed here (but the ``models``
dict is present), the device will not load.
If the device is configured with a model name, but the ``models`` dict is not
present, the device will have all commands available.

If the second variant (see example 3 above) of defining commands is chosen,
this dict will be ignored.

Hint: as this example only defines one command, the following example is purely
      fictional...
"""

models = {
    'ALL': ['cmd10', 'cmd11'],
    'model1': ['cmd1', 'cmd2', 'cmd3', 'cmd4'],
    'model2': ['cmd1', 'cmd2', 'cmd3', 'cmd5'],
    'model3': ['cmd1', 'cmd2', 'cmd4', 'cmd5', 'cmd6']
}


""" lookup: (optional) definition of lookup tables (see commands table)

Each table is a plain dict containing device values as keys and corresponding
SmartHomeNG item values as values. Lookup tables are used both for forward
(device -> shng) and reverse (shng -> device) lookups. By default, reverse
lookups are case insensitive to allow for typos.

The lookups dict can have two forms:

a) without the ability to contain model specific data
b) with the ability to contain model specific data

Case a) is the easier one: each key is a lookup table name and each value is
a plain dict with ``<device value>: <shng item value>`` dict entries.

Example:
"""

lookups = {
    'table1': {
        1: 'foo',
        2: 'bar',
        3: 'baz'
    },
    'table2': {
        'a': 'lorem',
        'b': 'ipsum',
        'c': 'dolor'
    }
}

""" lookup: (optional) model-specific lookup tables
Case b) is basically the same, but with an additional first level inserted.
The first level MUST contain a key named 'ALL' (duh), which specifies
"generic" lookup tables valid for all models. The value to this key is a dict
like the one in case a).
The first level CAN (and should, why would you do it otherwise?) have
additional entries named for the supported models. Its value again is a dict
like the one in case a). These entries are ADDED to the generic entries,
while tables existent in both are taken from the model-specific dict.

In the following example, all models will use ``table1`` and ``table2``;
both model1 and model2 will have the additional ``table3``, while only
model1 has a modified ``table1``.

Example:
"""

lookups = {
    'ALL': {
        'table1': {
            1: 'foo',
            2: 'bar',
            3: 'baz'
        },
        'table2': {
            'a': 'lorem',
            'b': 'ipsum',
            'c': 'dolor'
        }
    },
    'model1': {
        'table1': {
            1: 'boo',
            2: 'far',
            3: 'faz'
        },
        'table3': {
            1.0: 'one',
            2.0: 'two',
            3.0: 'three',
            3.14: 'pi'
        }
    },
    'model2': {
        'table3': {
            1.0: 'one',
            2.0: 'two',
            3.0: 'three',
            3.14: 'pi'
        }
    }
}

""" item templates: (optional) definition of templates for struct generation

With this dict, you can define templates - sets of item attributes or even
item structures - to be referenced by a command and inserted into the struct
generator output where appropriate.

While the example below only visualizes the syntax of the templates dict, a
possible implementaion might include on_change, autotimer, eval constructs as
well as ancillary subitems.

Feel free to completely ignore this.

Example:
"""

item_templates = {
    'template1': {
        'foo': 'bar',
        'foof': 'barf'
    },
    'template2': {
        'foop': 'barp',
        'floop': 'blarp'
    }
}
