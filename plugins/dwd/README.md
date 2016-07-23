# DWD

Thread for the Plugin: https://knx-user-forum.de/forum/supportforen/smarthome-py/34390-dwd-plugin

Requirements
============
This plugin needs an FTP account from the Deutscher Wetterdienst.
You could get it, free of charge, [here](http://kunden.dwd.de/gdsRegistration/gdsRegistrationStart.do).

# Configuration

## plugin.conf
<pre>
[dwd]
   class_name = DWD
   class_path = plugins.dwd
   username = ****
   password = ****
</pre>

You only need to specify your username and password.

## items.conf

There are no dwd specific item options.

# Functions

I'm sorry but this plugin return a _lot_ of information. See the Wiki for a item configuration and two logics using this plugin.
[DWD Logic](https://github.com/smarthomeNG/smarthome/wiki/DWD)

## current(Location)
Have a look at one file in the `gds/specials/observations/tables/germany` directory for the available locations.
This function returns a dictonary with the values for the availabe information.

## forecast(Area, Location)
See the `gds/specials/forecasts/tables/germany/` for the available areas (e.g. Deutschland, Mitte, Nordost ...) and locations.

## pollen(Area)
See `gds/specials/alerts/health/s_b31fg.xml` for available areas.

## uvi(Location)
See `gds/specials/alerts/health/s_b31fg.xml` for available locations.

## warnings(Issuer, LocationCode)
See `gds/help/legend_warnings.pdf` for possible issuers and Locations.

## ftp_quit()
This function should be called after all dwd request are finished.
