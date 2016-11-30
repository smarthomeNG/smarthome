# Alexa
This alexa plugin implements an "skill adapter" for Amazon's Alexa
by providing an smarthomeNG-embedded service-endpoint
where alexa can send its recognized voice-commands/directives to.

this plugin provides two features as described here: https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/overviews/understanding-the-smart-home-skill-api
- *AWS lambda skill adapter* - the shipped `aws_lambda.js` does 1:1 forwarding of alexa requests to ...
- *device cloud* - service-endpoint provided by smarthomeNG, called by the lambda skill adapter

# Alexa Skills Setup
- https://developer.amazon.com/edw/home.html#/skills/list
- https://developer.amazon.com/public/community/post/Tx3CX1ETRZZ2NPC/Alexa-Account-Linking-5-Steps-to-Seamlessly-Link-Your-Alexa-Skill-with-Login-wit

# AWS Lambda Function Setup
- logon to https://aws.amazon.com/
- create a lambda-function in the EU-sector (choose EU-Ireland whenever possible to have Alexa both in english & german)
- copy & paste `aws_lambda.js`
- provide the environmental variables as specified in the header of aws_lambda.js
- https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1#/functions?display=list

# Shortcomings / Pitfalls
this plugin/s service does not offer any ssl or authentication!! it is strongly recommended to use a reverse-proxy like nginx with both https-termination and http basic authentication. the shipped `aws_lambda.js` will do HTTPS-calls secured by HTTP Basic Authentication. see `nginx.md` for an example configuration

# Requirements
```
sudo pip3 install cherrypy
sudo pip3 install simplejson
```

# Testing
https://echosim.io/

# Configuration

## plugin.conf
basic configuration
```
[alexa]
    class_name = Alexa
    class_path = plugins.alexa
```

you may change host/ip and port of the web-service
```
[alexa]
    class_name = Alexa
    class_path = plugins.alexa
    service_host = "0.0.0.0"
    service_port = 9000
```

## items.conf
implemented actions:
- turnOn
- turnOff
- setTargetTemperature
- incrementTargetTemperature
- decrementTargetTemperature
- setPercentage
- incrementPercentage
- decrementPercentage

specify supported actions space-separated
```
[item]
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOn turnOff
```

you may omit the `alexa_name`, it will use the item's `name`
```
[item]
  name = "Diningroom Lamp"
  alexa_actions = turnOn turnOff
```

you can use multiple items for specific actions using the same alexa-name.
```
[item_only_on]
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOn

[item_only_off]
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOff
```

the device-identifier is automatically deduced from the `alexa_name` - but you can specify it explicitly using `alexa_device`
```
[item_only_on]
  alexa_device = custom_device_identifier
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOn

[item_only_off]
  alexa_device = custom_device_identifier
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOff
```

alexa supports "friendly descriptions", you can set it using `alexa_description`
```
[item]
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOn turnOff
  alexa_description = "The pompous dining room lamp in the west-wing"
```

## logging.yaml
you can enable debug logging for the alexa-plugin specifically:
```
loggers:
  plugins.alexa:
    level: DEBUG
root:
    level: INFO
    handlers: [file, console]
```
