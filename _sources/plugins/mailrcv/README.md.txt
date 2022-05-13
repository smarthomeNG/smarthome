# mailrcv

## Requirements

This plugin has no requirements or dependencies.

## Configuration

### plugin.yaml

```yaml
imap:
    plugin_name: mailrcv
    host: mail.example.com
    username: smarthome
    password: secret
    # tls: False
    # port: default
    # cycle: 300
```

#### Attributes
  * `host`: specifies the hostname of your mail server.
  * `port`: if you want to use a nonstandard port.
  * `username`/`password`: login information
  * `tls`: specifies if you want to use SSL/TLS.
  * `cycle`: for IMAP you could specify the intervall how often the inbox is checked

### items.yaml

There is no item specific configuration.

### logic.yaml

You could assign the following keywords to a logic. The matching order is as listed.

#### mail_subject

If the incoming mail subject matches the value of this key the logic will be triggerd.

#### mail_to

If the mail is sent to specified address the logic will be triggerd.

If gmail is used, you can trigger multiple logics with one account - just extend email address
with ['+' sign](https://gmail.googleblog.com/2008/03/2-hidden-ways-to-get-more-from-your.html)
(eg use `myaccount+logicname@gmail.com` to trigger `logicname`)

For safety reasons, use only dedicated gmail account with this plugin and filter out messages
from unkown senders (eg create filter `from:(-my_trusted_mail@example.com)` with action archive
or delete)


#### mail

A generic flag to trigger the logic on receiving a mail.

Attention:
   * You could only call one logic per mail!
   * If a mail is processed by a logic it will be delteted (moved to Deleted folder).
   * There is no email security. You have to use an infrastructure which provides security (e.g. own mail server which only accepts authenticated messages for the inbox).

```yaml
sauna:
    filename: sauna.py
    mail_to: sauna@example.com

mailbox:
    filename: mailbox.py
    mail: 'yes'
```

A mail to `sauna@example.com` will only trigger the logic 'sauna'. Every other mail is process by the 'mailbox' logic.

## Usage

If a logic is triggered by this plugin it will set the trigger `source` to the from address and the `value` contains an [email object](http://docs.python.org/2.6/library/email.message.html).

See the [phonebook logic](https://github.com/smarthomeNG/smarthome/wiki/Phonebook) for a logic which is triggerd by IMAP.

