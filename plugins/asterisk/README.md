# Asterisk

Requirements
============
A running asterisk daemon with a configured Asterisk Manager Interface (AMI) is necessary.
In manager.config its required to enable at least:
<code>read = system,call,user,cdr</code> and `write = system,call,orginate`

Configuration
=============

## plugin.conf

The plugin needs the username and password of the AMI and a IP and port address if asterisk does not run on localhost. 

<pre>
[ast]
    class_name = Asterisk
    class_path = plugins.asterisk
    username = admin
    password = secret
    host = 127.0.0.1 # default
    port = 5038 # default
</pre>

## items.conf

### ast_dev

Its possible to specify the `ast_dev` attribute to an bool item in items.conf. The argument could be a number or string and corrospond to thhe asterisk device configuration.
E.g. <code>2222</code> for the following device in asterisk sip.conf:
<pre>[2222]
secret=very
context=internal
</pre>

### ast_box
The mailbox number of this phone. It will be set to the number of new messages in this mailbox.

### ast_db
Specify the database entry which will be updated at an item change.

In items.conf:
<pre>
[office]
    [[fon]]
        type = bool
        ast_dev = 2222
        ast_db = active/office
        [[[box]]]
            type = num
            ast_box = 22
</pre>

Calling the '2222' from sip client or making a call from it, <code>office.fon</code> will be set to True. After finishing the call, it will be set to False.


## logic.conf

It is possible to specify the `ast_userevent` keyword to every logic in logic.conf.
<pre>
[logic1]
    ast_userevent = Call

[logic2]
    ast_userevent = Action
</pre>

In the asterisk extensions.conf `exten => _X.,n,UserEvent(Call,Source: ${CALLERID(num)},Value: ${CALLERID(name)})` would trigger 'logic1' every time, this UserEvent is sent.
A specified destination for the logic will be triggered e.g. `exten => _X.,n,UserEvent(Call,Source: ${CALLERID(num)},Destination: Office,Value: ${CALLERID(name)})`


Functions
=========

call(source, dest, context, callerid=None)
------------------------------------------
`sh.ast.call('SIP/200', '240', 'door')` would initate a call from the SIP extention '200' to the extention '240' with the 'door' context. Optional a callerid for the call is usable.

db_write(key, value)
--------------------
<code>sh.ast.db_write('dnd/office', 1)</code> would set the asterisk db entry 'dnd/office' to 1.

db_read(key)
------------
<code>dnd = sh.ast.db_read('dnd/office')</code> would set 'dnd' to the value of the asterisk db entry 'dnd/office'.

mailbox_count(mailbox, context='default')
-----------------------------------------
<code>mbc = sh.ast.mailbox_count('2222')</code> would set 'mbc' to a tuple (old_messages, new_messages).

## hangup(device)
`sh.ast.hangup('30')` would close all connections from or to the device '30'.
