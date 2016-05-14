# MemLog

This plugins can be used to create in-memory logs which can be used by items or other
plugins.

# Requirements

No special requirements.

# Configuration

## plugin.conf

Use the plugin configuration to configure the in-memory logs.

<pre>
[memlog]
   class_name = MemLog
   class_path = plugins.memlog
   name = alert
#   mappings = time | thread | level | message
#   maxlen = 50
#   items = first.item.now | second.item.thread.info | third.item.level | fourth.item.msg
</pre>

This will register a in-memory log with the name "alert". This can be used to attach 
to items.

### name attribute

This will give the in-memory log a name which can be used when accessing them.

### mappings attribute

This configures the list of values which are logged for each log message. The following
internal mappings can be used and will be automatically set - if not given explicitely
when logging data:
* `time` - the timestamp of log
* `thread` - the thread logging data
* `level` - the log level (defaults to INFO)

### maxlen attribute

Defines the maximum amount of log entries in the in-memory log.

### items attribute

Each time an item is updated using the `memlog` configuration setting, a log entry will
be written using the list of items configured in this attribute as log values.

When this is not configured, the default mapping values will be used the the associated
item`s value will be logged.

## items.conf

The following attributes can be used.

### memlog

Defines the name of in-memory log which should be used to log the item's content to
the log. Everything is logged with 'INFO' level.

### Example

Simple item logging:

<pre>
# items/my.conf

[some]
    [[item]]
        type = str
        memlog = alert
</pre>

## logic.conf

No logic configuration implemented.

# Methodes

The `memlog()` method name is the plugin name which is used in the plugin configuration.
If you use another name, you need to use this name as method name too.

## memlog(entry)
This log the given list of elements of `entry` parameter. The lsit should have the same amount
of items you used in the mapping parameter (see also the default for this value).

`sh.memlog((self._sh.now(), threading.current_thread().name, 'INFO', 'Some information'))`

## memlog(msg)

This log the given message in `msg` parameter with the default log level.

## memlog(lvl, msg)

This logs the message in `msg` parameter with the given log level specified in `lvl`
parameter.

