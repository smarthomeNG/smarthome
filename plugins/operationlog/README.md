# OperationLog

This plugins can be used to create logs which are cached, written to file and stored in memory to be used by items or other
plugins. Furthermore the logs can be visualised by smartVISU using the standard widget "status.log".

# Requirements

No special requirements.

# Configuration

## plugin.conf

Use the plugin configuration to configure the logs.

<pre>
[mylogname1]
   class_name = OperationLog
   class_path = plugins.operationlog
   name = mylogname1
#   maxlen = 50
#   cache = yes
#   logtofile = yes
#   filepattern = {year:04}-{month:02}-{day:02}-{name}.log



[mylogname2]
   class_name = OperationLog
   class_path = plugins.operationlog
   name = mylogname2
   maxlen = 0
   cache = no
   logtofile = yes
   filepattern = yearly_log-{name}-{year:04}.log

   ...
</pre>

This will register two logs named mylogname1 and mylogname2. The first one named mylogname1 is configured with the default configuration as shown, caching the log to file (smarthome/var/cache/mylogname1) and logging to file (smarthome/var/log/operationlog/yyyy-mm-dd-mylogname1.log). Every day a new logfile will be created. The last 50 entries will be kept in memory.

The entries of the second log will not be kept in memory, only logged to a yearly file with the pattern yearly_log-mylogname2-yyyy.  

## items
Configure an item to be logged as follows:

<pre>
[foo]
    [[bar]]
        type = num
        olog = mylogname1
        olog_level = ERROR
</pre> 

When the item gets updated a new log entry using loglevel 'ERROR' will be generated in the log mylogname1. The format of the entry will be "foo.bar = value". Item types num, bool and str can be used.

## Functions

<pre>
sh.mylogname1('level_keyword', msg)
</pre>

Logs the message in `msg` parameter with the given log level specified in the `level_keyword` parameter. 

Using the loglevel keywords 'INFO', 'WARNING' and 'ERROR' (upper or lower case) will cause the smartVISU plugin "status.log" to mark the entries with the colors green, yellow and red respectively. Alternative formulation causing a red color are 'EXCEPTION' and 'CRITICAL'. Using other loglevel keyword will result in log entry without a color mark.

<pre>
sh.mylogname1(msg)
</pre>

Logs the message in the `msg` parameter with the default loglevel 'INFO'.

 <pre>
data = sh.mylogname1()
</pre>

will return a deque object containing the log with the last `maxlen` entries.





This plugin is inspired from the plugins MemLog and AutoBlind, reusing some of their sourcecode.