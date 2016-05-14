# Boxcar Notification Service

# Requirements

You need to register at http://boxcar.io and get a free Boxcar Account.
In addition you need the free Boxcar App from Apple Appstore on your iOS Device.

## Supported Hardware

* Hardware supported by Boxcar.io Service (ATM only iOS, Android comming soon - perhaps)

# Configuration

## plugin.conf

Please provide a plugin.conf snippet for your plugin with ever option your plugin supports. Optional attributes should be commented out.

<pre>
[bc]
	class_name = Boxcar
	class_path = plugins.boxcar
	apikey     = abcdefghij123456 # Get it from your Boxcar Account
	email      = your@mail.org    # Registered with Boxcar
</pre>


## items.conf

Not needed yet.

## logic.conf
To push a message to your iOS Device just call
<pre>
sh.bc('House at Tulpenstrasse',' Waschmaschine fertig!')
</pre>

sh is the main smarthome instance.
bc is the name of the plugin instance (defined in plugins.conf in the squre brackets).
Two parameters with text to be send are supported.
If you only want to send one string, set the second string to an empty string.

