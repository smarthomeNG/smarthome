# CLI

Configuration
=============

plugin.conf
-----------
<pre>
[cli]
    class_name = CLI
    class_path = plugins.cli
    #ip = 127.0.0.1
    #port = 2323
    #update = false
    #hashed_password = 1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d
</pre>

This plugin listens for a telnet connection. 
<code>ip = </code> used network interface, e.g. 127.0.0.1 (localhost, default) or listen on all network interfaces: 0.0.0.0
<code>port =</code> used network port, default 2323
<code>update =</code> restrict the access of the items to read only (false, default) or allows read/write access (true)
<code>hashed_password = </code> password that needs to be entered on login. SHA-512 hashed. Value shown above is "very_secure_password"
Usage
=====

Telnet to the configured IP adress and port. 

Enter <code>help</code> for a list of available commands.

command | function
--- | ---
<code>cl [log]</code> | clean (memory) log
<code>dump [item]</code> | dump details about given item
<code>la</code> | list all items (with values)
<code>ld [log]</code> | log dump of (memory) log
<code>lo</code> | list all logics and next execution time
<code>ls</code> | list the first level items
<code>ls [item]</code> | list item and every child item (with values)
<code>lt</code> | list current thread names
<code>rl [logic]</code> | reload logic
<code>rr [logic]</code> | reload and run logic
<code>rt</code> | return runtime
<code>si [task]</code> | show details for given task
<code>sl</code> | list all scheduler tasks by name
<code>st</code> | list all scheduler tasks by execution time
<code>tr [logic]</code> | trigger logic
<code>up</code> | alias for update
<code>update [item] = [value]</code> | update the specified item with the specified value
<code>quit</code> | quit the session
<code>q</code> | alias for quit

Plugins may append additional commands. They will be listed with the "help" command, too.

Example:
<code>up office.light = On</code> to update an item.
