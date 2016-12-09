# Mail

Requirements
============
This plugin has no requirements or dependencies.

Configuration
=============

plugin.conf
-----------
<pre>
[mail]
    class_name = SMTP
    class_path = plugins.mail
    host = mail.example.com
    mail_from = mail@example.com
    # ssl = False
    # username = False
    # password = False

[imap]
    class_name = IMAP
    class_path = plugins.mail
    host = mail.example.com
    username = smarthome
    password = secret
    # ssl = False
    # port = default
    # cycle = 300
</pre>

### Attributes
  * `host`: specifies the hostname of your mail server.
  * `port`: if you want to use a nonstandard port.
  * `username`/`password`: login information
  * `ssl`: specifies if you want to use SSL/TLS.
  * `mail_from`: for SMTP you have to specify an origin mail address.
  * `cycle`: for IMAP you could specify the intervall how often the inbox is checked

## items.conf

There is no item specific configuration.

## logic.conf

You could assign the following keywords to a logic. The matching order is as listed.

### mail_subject
If the incoming mail subject matches the value of this key the logic will be triggerd.

### mail_to
If the mail is sent to specified address the logic will be triggerd.

### mail
A genric flag to trigger the logic on receiving a mail.

Attention:
   * You could only call one logic per mail!
   * If a mail is processed by a logic it will be delteted (moved to Deleted folder).
   * There is no email security. You have to use an infrastructure which provides security (e.g. own mail server which only accepts authenticated messages for the inbox).

<pre>
[sauna]
    filename = sauna.py
    mail_to = sauna@example.com

[mailbox]
    filename = mailbox.py
    mail = yes
</pre>

A mail to `sauna@example.com` will only trigger the logic 'sauna'. Every other mail is process by the 'mailbox' logic.

# Usage
If a logic is triggered by this plugin it will set the trigger `source` to the from address and the `value` contains an [email object](http://docs.python.org/2.6/library/email.message.html).

See the [phonebook logic](https://github.com/smarthomeNG/smarthome/wiki/Phonebook) for a logic which is triggerd by IMAP.

# Functions
The SMTP object provides one function (sending) and you access without specifing a method name.
`sh.mail(to, subject, message)` e.g. `sh.mail('admin@smart.home', 'Rain: Help me', 'You could send UTF-8 encoded subjects and messages')`
