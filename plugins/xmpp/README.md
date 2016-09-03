# XMPP 

# Requirements/Description

This Plugin uses sleekxmpp as basis to connect to XMPP etc services: https://pypi.python.org/pypi/sleekxmpp

At this stage the XMPP plugin module only supports in sending messages. Recevied messages are ignored. OTR not supported
as the sleekxmpp libraries do not support this as yet.

# Known Bugs
Non known at this stage.

# Configuration

## plugin.conf

<pre>
[xmpp]
    class_name = XMPP
    class_path = plugins.xmpp
    jid = 'user account eg skender@somexmppserver.com'
    password = your xmpp server password
</pre>

Description of the attributes:

* jid: jabber/xmpp user account
* password: jabber/xmpp user password

## logic.conf
At this stage there are no specific logic files. But in order to use this module you can create a logic file for another attribute and execute
or send messages to your xmpp account via sh.xmpp.send

<pre>
None
</pre>

# Functions
* sending a Message

<pre>
* sh.xmpp.send("skender@somexmppserver.me", "ALARM: Triggered, Danger.", 'chat')
</pre>

Send a message via xmpp
Requires:
        * mto = To whom eg 'skender@haxhimolla.im'
        * msgsend = body of the message eg 'Hello world'
        * mtype = message type, could be 'chat' or 'groupchat'


## Examples for an action/logic file

msg = trigger['value']

if sensor == "athome?":
    answer = "Someone has entered the house" if sh.myitem.athome() else "All secure"
    sh.xmpp.send("skender@haxhimolla.me", answer, 'chat')

