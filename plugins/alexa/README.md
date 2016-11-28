# Alexa

# Intro
This alexa plugin implements an "skill adapter" for Amazon's Alexa by providing an smarthomeNG-embedded service-endpoint where alexa can send its recognized voice-commands/directives to.

# Alexa Skills Setup
https://developer.amazon.com/edw/home.html#/skills/list

# AWS Lambda Function Setup
https://eu-west-1.console.aws.amazon.com/lambda/home?region=eu-west-1#/functions?display=list

# Requirements
sudo pip3 install cherrypy
sudo pip3 install simplejson

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

[item]
  alexa_name = "Diningroom Lamp"
  alexa_actions = turnOn turnOff
  alexa_description = "The pompous dining room lamp in the west-wing"
</pre>
