# Alexa
This plugin implements a "skill adapter" for Amazon's Alexa by providing a JSON-webservice (embedded into smarthomeNG)
where Alexa can send her recognized voice-commands/directives to. The plugin processes these directives and may turnOn/Off devices, change temperature, dim the lights, etc.

This plugin provides two features as described here: [Understanding the Smart Home Skill API](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/overviews/understanding-the-smart-home-skill-api)
- *AWS lambda skill adapter* - the shipped `aws_lambda.js` does 1:1 forwarding of alexa requests to ...
- *device cloud* - JSON webservice, embedded into smarthomeNG, which is called by the above lambda skill adapter and does the actual processing

Please use [this thread for support, questions, feedback etc.](https://knx-user-forum.de/forum/supportforen/smarthome-py/1021150-amazon-alexa-plugin)

## Alexa Setup
- [Five Steps Before Developing a Smart Home Skill](https://developer.amazon.com/public/community/post/Tx4WG410EHXIYQ/Five-Steps-Before-Developing-a-Smart-Home-Skill)
- [5 Steps to Seamlessly Link Your Alexa Skill with Login with Amazon](https://developer.amazon.com/public/community/post/Tx3CX1ETRZZ2NPC/Alexa-Account-Linking-5-Steps-to-Seamlessly-Link-Your-Alexa-Skill-with-Login-wit)

### AWS Lambda
- create the lambda-function in EU-Ireland (which supports Alexa in both english and german)
- copy & paste `aws_lambda.js` as a `Node.js` Lambda
- provide the environmental variables as specified in the header of `aws_lambda.js`

## Shortcomings / Pitfalls
This plugin/s service *does not offer any ssl or authentication*! It is strongly recommended to use a reverse-proxy in your smarthome to enforce HTTPS and authentication. As of now, the shipped `aws_lambda.js` only supports HTTPS-calls with HTTP Basic Authentication. See the shipped `nginx.md` for an example configuration of the lightweight and very good reverse-proxy Nginx.

## Configuration

### plugin.yaml
basic configuration
```
alexa:
    plugin_name: alexa
```

you may change host/ip and port of the web-service
```
alexa:
    plugin_name: alexa
    service_host: '0.0.0.0'
    service_port: 9000
```

### items.conf
implemented actions (case-sensitive, [exactly as specified](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference)):
- `turnOn`
- `turnOff`
- `setTargetTemperature`
- `incrementTargetTemperature`
- `decrementTargetTemperature`
- `setPercentage`
- `incrementPercentage`
- `decrementPercentage`

Specify *supported actions* space-separated
```
[item]
type = bool
name = diningroomlamp
alexa_name = "Diningroom Lamp"
alexa_actions = "turnOn turnOff"
```

You may omit the `alexa_name` (which is used as the '*friendly name*' in alexa) and reuse the normal `name` property
```
[item]
type = bool
name = "Diningroom Lamp"
alexa_actions = "turnOn turnOff"
```

You can use *different items for specific actions* using the same alexa-name.
however, it is recommended to use the device-identifier for this purpose instead (see next example)
```
[item_only_on]
type = bool
alexa_name = "Diningroom Lamp"
alexa_actions = turnOn

[item_only_off]
type = bool
alexa_name = "Diningroom Lamp"
alexa_actions = turnOff
```

The *device-identifier* is automatically deduced from the `alexa_name` - but you can specify it explicitly using `alexa_device`
(please note the [format of the `applianceId`](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#discovery-messages))
```
[[item_only_on]]
type = bool
alexa_name = "Diningroom Lamp"
alexa_device = diningroom-lamp
alexa_actions = turnOn

[[item_only_off]]
type = bool
alexa_device = diningroom-lamp
alexa_actions = turnOff
```

Alexa demands "*friendly descriptions*", you should set it using `alexa_description`. If not set, the `alexa_name` is used as a fallback.
```
[item]
type = bool
alexa_name = "Diningroom Lamp"
alexa_actions = "turnOn turnOff"
alexa_description = "The pompous dining room lamp in the west-wing"
```

You may provide an *type* as described in the [Appliance and Scene Categories](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference#appliance-categories). Alexa allows you to specify multiple types, space-separated. Types are only /required/ if you want to use scenes (see next paragraph)
```
[item]
type = bool
alexa_name = "Diningroom Lamp"
alexa_actions = "turnOn turnOff"
alexa_types = "LIGHT"
alexa_description = "The pompous dining room lamp in the west-wing"
```

To support *Scenes* you have to either provide `SCENE_TRIGGER` or `ACTIVITY_TRIGGER` as `alexa_types`. Furthermore, the word `scene` should/must(?) appear in the description. Please read the [Requirements to Describe a Scene](https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/providing-scenes-in-a-smart-home-skill#discoverappliancesresponse-requirements-to-describe-a-scene) for the full spec, basics as follows:

> The friendlyDescription must be present and include the word “scene” as well as how the scene is connected.
> For example: “scene connected via vendor name”. The >friendly description should not exceed 128 characters.

and
> A friendlyName is the name that customers use to interact with your scene and must be present.
> The goal is to enable customers to interact with a scene in a way that is natural and easy.
> A friendlyName should follow these guidelines:
> Preferred option includes only the scene name.
> This provides the simplest and most natural way for a customer to interact with a scene
> Optionally includes the room name, if a similar scene is offered in different rooms
> Optionally includes “scene”
> Optionally includes the preposition “in” between the scene name and a room name
> Should not include special characters or punctuation
> Should not exceed 128 characters

```
[scene]
type = bool
alexa_name = "Cozy in Diningroom"
alexa_actions = "turnOn"
alexa_types = "SCENE_TRIGGER"
alexa_description = "scene via smarthomeNG"
```

To provide *multiple names for the same device*, you can specific alias-names via 'alexa_alias'. For each alias another device will be created and is also visible in your alexa app (and thus will clutter up your list of devices ...). Separate multiple alias names by comma. If you define groups in your alexa app, you shouldn't assign the aliases to the groups as well. This could trigger the underlying items multiple times, for each group-assigned device once.
```
[item]
type = bool
alexa_name = "Diningroom Lamp"
alexa_alias = "Dining Lamp, Chandelier"
alexa_actions = "turnOn turnOff"
alexa_description = "The pompous dining room lamp in the west-wing"
```

By default, `turnOn` will trigger `True` and `turnOff` will trigger `False` on the item. You can change this by defining `alexa_item_turn_on` and/or `alexa_item_turn_off`. You can combine this with limiting the list of supported actions (by specifying `alexa_actions`).
```
[item]
type = num
alexa_name = "TV Scene"
alexa_actions = "turnOn"
alexa_item_turn_on = 3
```

You may define the *item's value-range* which controls the percentage-directives (default: 0-100) and limits the temperature-directives (default: 16-26), use `alexa_item_range` to specify an explicit range (e.g. you should use this when dimming lights via KNX or generally dealing with ranges like DPT=5 which is 1 byte: 0-255):
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

You can define `alexa_name` & `alexa_description` centrally in one item and *reference the device in other items* just by using the `alexa_device` (you must always define a `type` though!). this is the recommended fully-specified, no-fallbacks configuration.
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
    [[[scenes]]]
      [[[[gemuetlich]]]]
      type = num
      enforce_updates = on
      knx_dpt = 17
      knx_send = 0/1/100
      alexa_device = ew_scene_gemuetlich
      alexa_name = "Gemütlich"
      alexa_description = "Szene Gemütlich aufrufen"
      alexa_actions = "turnOn"
      alexa_item_turn_on = 1

      [[[[essen]]]]
      type = num
      enforce_updates = on
      knx_dpt = 17
      knx_send = 0/1/100
      alexa_device = ew_scene_essen
      alexa_name = "Essen"
      alexa_description = "Szene Essen aufrufen"
      alexa_actions = "turnOn"
      alexa_item_turn_on = 2

      [[[[tv]]]]
      type = num
      enforce_updates = on
      knx_dpt = 17
      knx_send = 0/1/100
      alexa_device = ew_scene_tv
      alexa_name = "Fernsehen"
      alexa_description = "Szene Fernsehen aufrufen"
      alexa_actions = "turnOn"
      alexa_item_turn_on = 3

    [[[couch]]]
    type = bool
    alexa_device = ew_light_couch
    alexa_name = "Couch"
    alexa_alias = "Sofa, Wohnzimmer"
    alexa_description = "Deckenlampe über der Couch im Wohnzimmer"
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

    [[[couch_fenster]]]
    type = bool
    alexa_device = ew_light_couch_fenster
    alexa_name = "Couch-Fenster"
    alexa_alias = "Sofa-Fenster, Wohnzimmer-Fenster"
    alexa_description = "Lampe in der Nord-Fensterlaibung bei der Couch im Wohnzimmer"
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
    knx_listen = 2/2/21
    knx_init = 2/2/21
    knx_send = 2/2/20

    [[[couch_stehlampe]]]
    type = bool
    alexa_device = ew_light_couch_stehlampe
    alexa_name = "Couch-Stehlampe"
    alexa_alias = "Sofa-Stehlampe, Wohnzimmer-Stehlampe, Couch-Stehleuchte, Sofa-Stehleuchte, Wohnzimmer-Stehleuchte"
    alexa_description = "Stehlampe bei der Couch im Wohnzimmer"
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
    knx_listen = 2/2/31
    knx_init = 2/2/31
    knx_send = 2/2/30

    [[[couch_regal]]]
    type = bool
    alexa_device = ew_light_couch_regal
    alexa_name = "Couch-Regal"
    alexa_alias = "Sofa-Regal, Wohnzimmer-Regal"
    alexa_description = "Kleine Lampe im Regal bei der Couch im Wohnzimmer"
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
    knx_listen = 2/2/11
    knx_init = 2/2/11
    knx_send = 2/2/10

    [[[mitte]]]
    type = bool
    alexa_device = ew_light_mitte
    alexa_name = "Mittlere Lampe"
    alexa_alias = "Mitte"
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
    alexa_alias = "Esszimmer"
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

    [[[esstisch_fenster]]]
    type = bool
    alexa_device = ew_light_esstisch_fenster
    alexa_name = "Esstisch-Fenster"
    alexa_alias = "Esszimmer-Fenster"
    alexa_description = "Lampe in der Süd-Fensterlaibung beim Esstisch im Wohnzimmer"
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
    knx_listen = 2/2/71
    knx_init = 2/2/71
    knx_send = 2/2/70

    [[[esstisch_stehlampe]]]
    type = bool
    alexa_device = ew_light_esstisch_stehlampe
    alexa_name = "Esstisch-Stehlampe"
    alexa_alias = "Esszimmer-Stehlampe"
    alexa_description = "Stehlampe beim Esstisch im Wohnzimmer"
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
    knx_listen = 2/2/51
    knx_init = 2/2/51
    knx_send = 2/2/50

    [[[kueche]]]
    type = bool
    alexa_device = ew_light_kueche
    alexa_name = "Küche"
    alexa_description = "Deckenlicht in der Küche"
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
    knx_listen = 1/2/31
    knx_init = 1/2/31
    knx_send = 1/0/30
      [[[[dimmen]]]]
      type = num
      alexa_device = ew_light_kueche
      alexa_actions = "setPercentage incrementPercentage decrementPercentage"
      alexa_item_range = 0-255
      knx_dpt = 5
      knx_listen = 1/2/35
      knx_init = 1/2/35
      knx_send = 1/2/34

    [[[arbeitsplatte]]]
    type = bool
    alexa_device = ew_light_kueche_arbeitsplatte
    alexa_name = "Arbeitsplatte"
    alexa_alias = "Tresen, Counter"
    alexa_description = "Arbeitsplatten-Licht in der Küche"
    alexa_actions = "turnOn turnOff"
    knx_dpt = 1
    knx_listen = 1/2/61
    knx_init = 1/2/61
    knx_send = 1/0/90

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

### logging.yaml
you can enable debug logging for the alexa-plugin specifically:
```
loggers:
  plugins.alexa:
    level: DEBUG
root:
    level: INFO
    handlers: [file, console]
```
