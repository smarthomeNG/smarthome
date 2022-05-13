# XMPP

## Requirements/Description

This Plugin uses slixmpp as basis to connect to XMPP etc services: https://pypi.org/project/slixmpp/

At this stage the XMPP plugin module only supports sending messages.
Recevied messages are ignored.

In case you want some OTR you have to install https://pypi.org/project/slixmpp-omemo/
and use this XEP-384 from there (currently only possible via manual installation).

This Plugin can also be used to setup a standard logger category which
can be used to log messages using XMPP to some chat or groupchat contact.
The logging configuration looks like this:

```yaml
handlers:
    xmpp:
        class: plugins.xmpp.XMPPLogHandler
        formatter: shng_simple
        xmpp_plugin: xmpp
        xmpp_receiver: room@conference.example.com
        xmpp_receiver_type: groupchat
loggers:
    xmpp:
        handlers: [xmpp]
        level: WARN
```

This requires a XMPP plugin configured in a section named `xmpp` (e.g.
see below for example) which is referenced in the `xmpp_plugin` setting.
The receiver and chat type needs to be specified to configure the target
contact receiving the messages.

It is also possible to log all messages to a given operation log instance
via XMPP. E.g. when having multiple operation logs configured, one for events
one for alarms, the alarms operation log can be send via XMPP when it
receives log messages:

```yaml
loggers:
    plugins.operationlog.alarms:
        handlers: [xmpp]
        level: INFO
```


## Configuration

### plugin.yaml

```yaml
xmpp:
    class_name: XMPP
    class_path: plugins.xmpp
    jid: 'user account eg skender@somexmppserver.com'
    password: your xmpp server password
    #server: 127.0.0.1:5222
    #use_ipv6: 1
    #plugins:
    #  - xep_0199  # MUC
    #  - xep_0045  # PING
```

Description of the attributes:

* jid: jabber/xmpp user account
* password: jabber/xmpp user password
* server: IP and (optionally) port of server to connect
* use_ipv6: enable IPv6 support, which is the default
* plugins: list of plugins (XEP to support)

#### XEP supported

- XEP-0004: Data Forms
- XEP-0009: Jabber-RPC
- XEP-0012: Last Activity
- XEP-0013: Flexible Offline Message Retrieval
- XEP-0016: Privacy Lists
- XEP-0020: Feature Negotiation
- XEP-0027: Current Jabber OpenPGP Usage
- XEP-0030: Service Discovery
- XEP-0033: Extended Stanza Addressing
- XEP-0045: Multi-User Chat
- XEP-0047: In-band Bytestreams
- XEP-0048: Bookmarks
- XEP-0049: Private XML Storage
- XEP-0050: Ad-Hoc Commands
- XEP-0054: vcard-temp
- XEP-0059: Result Set Management
- XEP-0060: Publish-Subscribe
- XEP-0065: SOCKS5 Bytestreams"
- XEP-0066: Out of Band Data
- XEP-0070: Verifying HTTP Requests via XMPP
- XEP-0071: XHTML-IM
- XEP-0077: In-Band Registration
- XEP-0078: Non-SASL Authentication
- XEP-0079: Advanced Message Processing
- XEP-0080: User Location
- XEP-0082: XMPP Date and Time Profiles
- XEP-0084: User Avatar
- XEP-0085: Chat State Notifications
- XEP-0086: Error Condition Mappings
- XEP-0091: Legacy Delayed Delivery
- XEP-0092: Software Version
- XEP-0095: Stream Initiation
- XEP-0096: SI File Transfer
- XEP-0106: JID Escaping
- XEP-0107: User Mood
- XEP-0108: User Activity
- XEP-0115: Entity Capabilities
- XEP-0118: User Tune
- XEP-0122: Data Forms Validation
- XEP-0128: Service Discovery Extensions
- XEP-0131: Stanza Headers and Internet Metadata
- XEP-0133: Service Administration
- XEP-0138: Compression"
- XEP-0152: Reachability Addresses
- XEP-0153: vCard-Based Avatars
- XEP-0163: Personal Eventing Protocol (PEP)
- XEP-0172: User Nickname
- XEP-0184: Message Delivery Receipts
- XEP-0186: Invisible Command
- XEP-0191: Blocking Command
- XEP-0196: User Gaming
- XEP-0198: Stream Management
- XEP-0199: XMPP Ping
- XEP-0202: Entity Time
- XEP-0203: Delayed Delivery
- XEP-0221: Data Forms Media Element
- XEP-0222: Persistent Storage of Public Data via PubSub
- XEP-0223: Persistent Storage of Private Data via PubSub
- XEP-0224: Attention
- XEP-0231: Bits of Binary
- XEP-0235: OAuth Over XMPP
- XEP-0242: XMPP Client Compliance 2009
- XEP-0249: Direct MUC Invitations
- XEP-0256: Last Activity in Presence
- XEP-0257: Client Certificate Management for SASL EXTERNAL
- XEP-0258: Security Labels in XMPP
- XEP-0270: XMPP Compliance Suites 2010
- XEP-0279: Server IP Check
- XEP-0280: Message Carbons
- XEP-0297: Stanza Forwarding
- XEP-0300: Use of Cryptographic Hash Functions in XMPP
- XEP-0302: XMPP Compliance Suites 2012
- XEP-0308: Last Message Correction
- XEP-0313: Message Archive Management
- XEP-0319: Last User Interaction in Presence
- XEP-0323 Internet of Things - Sensor Data
- XEP-0325 Internet of Things - Control
- XEP-0332: HTTP over XMPP transport
- XEP-0333: Chat Markers
- XEP-0334: Message Processing Hints
- XEP-0335: JSON Containers
- XEP-0352: Client State Indication
- XEP-0363: HTTP File Upload
- XEP-0380: Explicit Message Encryption
- XEP-0394: Message Markup


### logic.yaml
At this stage there are no specific logic files. But in order to use this module you can create a logic file for another attribute and execute
or send messages to your xmpp account via sh.xmpp.send

## Functions
* sending a Message

```python
sh.xmpp.send("skender@somexmppserver.me", "ALARM: Triggered, Danger.", 'chat')
```

Send a message via xmpp
Requires:
        * mto = To whom eg 'skender@haxhimolla.im'
        * msgsend = body of the message eg 'Hello world'
        * mtype = message type, could be 'chat' or 'groupchat'


### Example for an action/logic file

```python
msg = trigger['value']

if sensor == "athome?":
    answer = "Someone has entered the house" if sh.myitem.athome() else "All secure"
    sh.xmpp.send("skender@haxhimolla.me", answer, 'chat')
```
