# CLI

Configuration
=============

plugin.conf
-----------
<pre>
[cli]
   class_name = CLI
   class_path = plugins.cli
#   ip = 127.0.0.1
#   port = 2323
#   update = false
</pre>

This plugin listens for a telnet connection. 
<code>ip = </code> used network interface, e.g. 127.0.0.1 (localhost, default) or listen on all network interfaces: 0.0.0.0
<code>port =</code> used network port, default 2323
<code>update =</code> restrict the access of the items to read only (false, default) or allows read/write access (true)

Usage
=====

Telnet to the configured IP adress and port. 
<code>help</code>list an set of available commands:
<pre>
cl: clean (memory) log
ls: list the first level items
ls item: list item and every child item (with values)
la: list all items (with values)
lo: list all logics and next execution time
lt: list current thread names
update item = value: update the specified item with the specified value
up: alias for update
tr logic: trigger logic
rl logic: reload logic
rr logic: reload and run logic
quit: quit the session
q: alias for quit
</pre>

Example:
<code>up office.light = On</code> to update an item.
