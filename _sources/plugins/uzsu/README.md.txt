# UZSU

## Description
Provides universal time switches for items

## Documentation

For info on the features and detailed setup see the [User Documentation](https://www.smarthomeng.de/user/plugins/uzsu/user_doc.html "Manual")
For info on how to configure the plugin see the [Configuration Documentation](https://www.smarthomeng.de/user/plugins_doc/config/uzsu.html "Configuration")

## Changelog

### v1.5.3
* Remove useless dictionary parts from uzsu items (to make double entry check work better)
* Added SciPy as a requirements
* Added User Documentation

### v1.5.2
* Make the plugin compatible with the master 1.5.1 version
* Correctly write cache file when changing the uzsu item
* Automatically activate all days of the week if no day is set via Visu
* Variety of bug fixes and optimizations
* Corrected information on web interface concerning (in)active entries

### v1.4.1 - 1.5.1
* Added a web interface for easier debugging
* Added "back in time"/initage feature to re-trigger missed uzsu evaluations on smarthomeng startup
* Added interpolation feature: the UZSU can now be used for smooth transitions of values (e.g. for light dimming, etc.)
* Added item functions to (de)activate, change interpolation and query some settings from the uzsu item via logic
* Fixed uzsu evaluation for entries without an rrule setting (day of week)
* Automatic deactivating older entries when new entry for exactly the same time (and day) is created (only works with specific VISU widgets)
* Improved error handling (detecting wrong items to be set by UZSU, empty entries, etc.)
