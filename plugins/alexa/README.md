# Alexa
This alexa plugin implements an "skill adapter" for Amazon's Alexa
by providing an smarthomeNG-embedded service-endpoint
where alexa can send its recognized voice-commands/directives to.

please this for a basic understanding: https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/overviews/understanding-the-smart-home-skill-api
this plugin provides two features:
- *AWS lambda skill adapter*  - the shipped `aws_lambda.js` does 1:1 forwarding of alexa requests to ...
- *device cloud* - service-endpoint provided by smarthomeNG

# Alexa Skills Setup
- https://developer.amazon.com/edw/home.html#/skills/list
- https://developer.amazon.com/public/community/post/Tx3CX1ETRZZ2NPC/Alexa-Account-Linking-5-Steps-to-Seamlessly-Link-Your-Alexa-Skill-with-Login-wit

# AWS Lambda Function Setup
- logon to https://aws.amazon.com/
- create a lambda-function in the EU-sector (choose EU-Ireland whenever possible to have Alexa both in english & german)
- use aws_lambda.js to copy & paste
- provide the environmental variables as specified in the header of aws_lambda.js
- https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1#/functions?display=list

# Shortcomings / Pitfalls
- the python service does not offer ssl or authentication, a reverse-proxy like nginx with both https-termination and http basic authentication is strongly advised and actually required, since the shipped aws_lambda.js will only do https-requests and does http basic auth.

# Requirements
<pre>
sudo pip3 install cherrypy
sudo pip3 install simplejson
</pre>

# Testing
https://echosim.io/

# Configuration

## plugin.conf
<pre>
[alexa]
    class_name = Alexa
    class_path = plugins.alexa
</pre>

<pre>
[alexa]
    class_name = Alexa
    class_path = plugins.alexa
    service_host = "0.0.0.0"
    service_port = 9000
</pre>

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

<pre>
[item]
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOn turnOff
</pre>

<pre>
[item_only_on]
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOn

[item_only_off]
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOff
</pre>

<pre>
[item_only_on]
  alexa_device = custom_device_identifier
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOn

[item_only_off]
  alexa_device = custom_device_identifier
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOff
</pre>

<pre>
[item]
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOn turnOff
  alexa_description = "The pompous dining room lamp in the west-wing"
</pre>

## logging.yaml
<pre>
loggers:
  plugins.alexa:
    level: DEBUG
root:
    level: INFO
    handlers: [file, console]
</pre>
