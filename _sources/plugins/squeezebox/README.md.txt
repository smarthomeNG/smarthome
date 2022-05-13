# Squeezebox

## New in version 1.4

* Switch from lib.connection to lib.network
* Added autoreconnect option

## New in version 1.3.2

* Remove the automatic '?' addition to init commands
* Update struct templates
* Allow commands without playerid (for server queries, etc.)

## New in version 1.3.1

* Parse the plugin parameters in Smart Plugin style
* Update the plugin.yaml (move documentation there)
* Include item struct templates for players
* fix umlaut problems
* add album art url automatically
* small tweaks

## New in version 1.3.0

* The plugin is now a Smart Plugin. You can change the logging level in logging.yaml
* When the end of a playlist is reached the plugin now changes the mode correctly to "stop"
* When playing a radio station the play mode is now correctly set to "play"
* When starting playing by adding and playing a playlist the play mode is now correctly set to "play"
* The player_id in your conf file is now searched not only in the parent item but also 2 levels further up
