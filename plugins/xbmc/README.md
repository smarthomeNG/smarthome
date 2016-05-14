# XBMC

Requirements
============
You only need one or more XBMC (12 a.k.a. Frodo or above) with
System-Settings-Service "Allow programs on other systems to control XBMC" enabled.

Configuration
=============

## plugin.conf

<pre>
[xbmc]
    class_name = XBMC
    class_path = plugins.xbmc
</pre>

## items.conf
<pre>
[living]
    [[xbmc]]
        type = str
        xbmc_host = xbmc.home
        # xbmc_port = 9090
        xbmc_listen = state
        [[[title]]]
            type = str
            xbmc_listen = title
        [[[media]]]
            type = str
            xbmc_listen = media
        [[[volume]]]
            type = num
            xbmc_listen = volume
            xbmc_send = volume
        [[[mute]]]
            type = bool
            xbmc_listen = mute
            xbmc_send = mute
</pre>

### xbmc_host
This attribute is mandatory. You have to provide the IP address or host name of the XBMC system.

### xbmc_port
You could specify a port to connect to. By default port 9090 is used.

### xbmc_listen
You could assign the following values to `xbmc_listen`:

   * `volume` a numeric value (0 -100)
   * `mute` a bool flag
   * `title` a string with the name of the movie, song or picture
   * `media` a string with the current media type (Video, Audio, Picture)
   * `state` current state as string (Menu, Playing, Pause)

### xbmc_send
The following `xbmc_send` attributes could be defined to send changes to the system:

   * `volume` a numeric value (0 -100)
   * `mute` a bool flag


## logic.conf

Functions
=========
This plugin provides the function to send notification messages to xbmc. 
`notify_all(title, message, picture)` to send the notification to all xbmc systems and extends the item with the notify method.
The picture attribute is optional.

<pre>
sh.xbmc.notify_all('Phone', 'Sister in law calling', 'http://smarthome.local/img/phone.png') 
# or for a dedicated xbmc
sh.living.xbmc.notify('Door', 'Ding Dong')
</pre>
