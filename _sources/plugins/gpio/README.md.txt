# GPIO

## Configuration

Information can be found at the [Configuration Documentation](https://www.smarthomeng.de/user/plugins_doc/config/gpio.html)

## Changelog
1.0
- initial release

1.0.1
- Changed event detection from constant polling to GPIO.add_event_detect

1.4.2
- added parameter support for GPIO pull-up/pull-down configuration (global / per
  item)
- changed startup code to prevent unwanted output changes
- cleaned up code, removed unnecessary parts

