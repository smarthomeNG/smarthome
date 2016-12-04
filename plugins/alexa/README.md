# Alexa
This plugin implements a "skill adapter" for Amazon's Alexa by providing a JSON-webservice (embedded into smarthomeNG)
where Alexa can send her recognized voice-commands/directives to. The plugin processes these directives and may turnOn/Off devices, change temperature, dim the lights, etc.

This plugin provides two features as described here: [Understanding the Smart Home Skill API](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/overviews/understanding-the-smart-home-skill-api)
- *AWS lambda skill adapter* - the shipped `aws_lambda.js` does 1:1 forwarding of alexa requests to ...
- *device cloud* - JSON webservice, embedded into smarthomeNG, which is called by the above lambda skill adapter and does the actual processing

Please use [this thread for support, questions, feedback etc.](https://knx-user-forum.de/forum/supportforen/smarthome-py/1021150-amazon-alexa-plugin)

# Alexa Setup
- [Five Steps Before Developing a Smart Home Skill](https://developer.amazon.com/public/community/post/Tx4WG410EHXIYQ/Five-Steps-Before-Developing-a-Smart-Home-Skill)
- [5 Steps to Seamlessly Link Your Alexa Skill with Login with Amazon](https://developer.amazon.com/public/community/post/Tx3CX1ETRZZ2NPC/Alexa-Account-Linking-5-Steps-to-Seamlessly-Link-Your-Alexa-Skill-with-Login-wit)

## AWS Lambda
- create the lambda-function in EU-Ireland (which supports Alexa in both english and german)
- copy & paste `aws_lambda.js` as a `Node.js` Lambda
- provide the environmental variables as specified in the header of `aws_lambda.js`

# Shortcomings / Pitfalls
This plugin/s service *does not offer any ssl or authentication*! It is strongly recommended to use a reverse-proxy in your smarthome to enforce HTTPS and authentication. As of now, the shipped `aws_lambda.js` only supports HTTPS-calls with HTTP Basic Authentication. See the shipped `nginx.md` for an example configuration of the lightweight and very good reverse-proxy Nginx.

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
implemented actions (case-sensitive, [exactly as specified](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference)):
- `turnOn`
- `turnOff`
- `setTargetTemperature`
- `incrementTargetTemperature`
- `decrementTargetTemperature`
- `setPercentage`
- `incrementPercentage`
- `decrementPercentage`

specify supported actions space-separated
```
[item]
type = foo
alexa_name = "Diningroom Lamp"
alexa_actions = "turnOn turnOff"
```

you may omit the `alexa_name`
```
[item]
type = foo
name = "Diningroom Lamp"
alexa_actions = "turnOn turnOff"
```

you can use multiple items for specific actions using the same alexa-name.
```
[item_only_on]
type = foo
alexa_name = "Diningroom Lamp"
alexa_actions = turnOn

[item_only_off]
type = foo
alexa_name = "Diningroom Lamp"
alexa_actions = turnOff
```

the device-identifier is automatically deduced from the `alexa_name` - but you can specify it explicitly using `alexa_device` (please note the [format of the `applianceId`](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#discovery-messages))
```
[[item_only_on]]
type = foo
alexa_name = "Diningroom Lamp"
alexa_device = diningroom-lamp
alexa_actions = turnOn

[[item_only_off]]
type = foo
alexa_device = diningroom-lamp
alexa_actions = turnOff
```

alexa demands "friendly descriptions", you should set it using `alexa_description`. If not set, the `alexa_name` is used as a fallback.
```
[item]
type = foo
alexa_name = "Diningroom Lamp"
alexa_actions = "turnOn turnOff"
alexa_description = "The pompous dining room lamp in the west-wing"
```

you may define the item's value-range which controls the percentage-directives (default: 0-100) and limits the temperature-directives (default: 16-26), use `alexa_item_range` to specify an explicit range (e.g. you should use this when dimming lights via KNX or generally dealing with ranges like DPT=5 which is 1 byte: 0-255):
```
[[[[dim]]]]
type = num
alexa_device = the_light
alexa_actions = "setPercentage incrementPercentage decrementPercentage"
alexa_item_range = 0-255
knx_dpt = 5
knx_listen = 1/1/1
knx_init = 1/1/1
knx_send = 1/1/0
````

you can define `alexa_name` & `alexa_description` centrally in one item and reference the device in other items just by using the `alexa_device` (you must always define a `type` though!)
```
[root]
  [[livingroom_lamps]]
  type = foo
  alexa_device = livingroom_lamps
  alexa_name = "Livingroom"
  alexa_description = "Couch and Main Livingroom-Lamps"

    [[[couch]]]
    type = bool
    alexa_device = livingroom_lamps
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
    knx_listen = 1/2/1
    knx_init = 1/2/1
    knx_send = 1/2/0

    [[[main]]]
    type = bool
    alexa_device = livingroom_lamps
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
		knx_listen = 1/2/11
    knx_init = 1/2/11
    knx_send = 1/2/10
```

real-life example:
```
[smarthome]
  [[ew]]
    [[[couch]]]
    type = bool
    alexa_device = ew_light_couch
    alexa_name = "Couch"
    alexa_description = "Couch-Deckenlampe im Wohnzimmer"
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
    knx_listen = 1/2/1
    knx_init = 1/2/1
    knx_send = 1/2/0
      [[[[dimmen]]]]
      type = num
      alexa_device = ew_light_couch
      alexa_actions = "setPercentage incrementPercentage decrementPercentage"
      alexa_item_range = 0-255
      knx_dpt = 5
      knx_listen = 1/2/5
      knx_init = 1/2/5
      knx_send = 1/2/4

    [[[mitte]]]
    type = bool
    alexa_device = ew_light_mitte
    alexa_name = "Mittlere Lampe"
    alexa_description = "Mittlere Deckenlampe im Wohnzimmer"
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
    knx_listen = 1/2/11
    knx_init = 1/2/11
    knx_send = 1/2/10
      [[[[dimmen]]]]
      type = num
      alexa_device = ew_light_mitte
      alexa_actions = "setPercentage incrementPercentage decrementPercentage"
      alexa_item_range = 0-255
      knx_dpt = 5
      knx_listen = 1/2/15
      knx_init = 1/2/15
      knx_send = 1/2/14

    [[[esstisch]]]
    type = bool
    alexa_device = ew_light_esstisch
    alexa_name = "Esstisch"
    alexa_description = "Esstischlampe im Wohnzimmer"
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
    knx_listen = 1/2/21
    knx_init = 1/2/21
    knx_send = 1/2/20
      [[[[dimmen]]]]
      type = num
      alexa_device = ew_light_esstisch
      alexa_actions = "setPercentage incrementPercentage decrementPercentage"
      alexa_item_range = 0-255
      knx_dpt = 5
  		knx_listen = 1/2/25
      knx_init = 1/2/25
      knx_send = 1/2/24

    [[[heizung]]]
    type = num
    alexa_device = ew_temp
    alexa_name = "Heizung"
    alexa_description = "Fussbodenheizung im Wohnzimmer"
    alexa_actions = "setTargetTemperature incrementTargetTemperature decrementTargetTemperature"
    knx_dpt = 9
    knx_listen = 3/2/3
    knx_init = 3/2/3
    knx_send = 3/2/2
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
