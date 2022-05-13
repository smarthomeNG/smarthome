# mailsend

## Requirements

This plugin has no requirements or dependencies.

## Configuration

### plugin.yaml

```yaml
mail:
    plugin_name: mailsend
    host: mail.example.com
    mail_from: mail@example.com
    # tls: True
    # username: False
    # password: False

```

#### Attributes
  * `host`: specifies the hostname of your mail server.
  * `port`: if you want to use a nonstandard port.
  * `username`/`password`: login information
  * `tls`: specifies if you want to use SSL/TLS.
  * `mail_from`: for SMTP you have to specify an origin mail address.

### items.yaml

There is no item specific configuration.


## Functions

The SMTP object provides one function (sending) and you access without specifing a method name.
`sh.mail(to, subject, message)` e.g. `sh.mail('admin@smart.home', 'Rain: Help me', 'You could send UTF-8 encoded subjects and messages')`
