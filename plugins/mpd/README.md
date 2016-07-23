# MPD

Requirements
============
You only need one or more Music Player Daemons (MPD).

Configuration
=============

## plugin.conf

<pre>
[mpd]
    class_name = MPD
    class_path = plugins.mpd
</pre>

## items.conf

You could see a full featured item configuration at the end of this file.

<pre>
[living]
    type = bool
    [[mpd]]
        type = str
        mpd_host = 127.0.0.1
        mpd_port = 6600
        [[[state]]]
            type = str
            mpd_listen = state
            mpd_send = value  # sends the item value. e.g. sh.dev.mpd.state('play') will send 'play'
        [[[volume]]]
            type = num
            mpd_listen = volume
            mpd_send = volume
        [[[jungle]]]
            type = bool
            mpd_file = http://jungletrain.net/64kbps.m3u
            enforce_updates = yes
</pre>


### mpd_host
This attribute is mandatory. You have to provide the IP address or host name of a MPD system.

### mpd_port
You could specify a port to connect to. By default port 6060 is used.

### mpd_listen
You could assign the following values to `mpd_listen`:

   * `state`: ("play", "stop", or "pause")
   * `volume`: (0-100)
   * `repeat`: (0 or 1)
   * `random`: (0 or 1)
   * `single`: (0 or 1)
   * `time`: <int elapsed> (of current playing/paused song)
   * `total`: <time total> (of current playing/paused song)
   * `percent`: (0-100)
   * `play`: (0 or 1)
   * `pause`: (0 or 1)
   * `stop`: (0 or 1)
   * `song`: (current song stopped on or playing, playlist song number)
   * `playlistlength`: (integer, the length of the playlist)
   * `nextsongid`: (next song, playlist song number)

   * `title`: current song title
   * `name`: current song name
   * `album`: current song album
   * `artist`: current song artist
   * `file`: current song file
   * `albumartist`: album artist
   * `track`: album track
   * `disc`: album disc


### mpd_send
The following `mpd_send` attributes could be defined to send changes to the system:

   * `volume`: a numeric value (0 -100)
   * `repeat`: enable/disable repeat
   * `random`: enable/disable random
   * `single`: enable/disable repeat current song 
   * `<command>`: send the specified command at an item change. See below for a list of commands.

### mpd_file
You could specify a file, directory or URL which will be played if the value of this item change.



# Functions

## command(cmd)
Send any of the commands: `play`, `pause`, `stop`, `next`, `previous`...<br />
For a complete list see: [http://www.musicpd.org/doc/protocol/command_reference.html](http://www.musicpd.org/doc/protocol/command_reference.html)

## play(file)
Plays the specified file, directory or URL.

## add(file)
Adding the specified file, directory or URL to the playlist.


# Example item.conf
<pre>
[living]
    [[mpd]]
        type = str
        mpd_host = 127.0.0.1
        mpd_port = 6600
        [[[state]]]
            type = str
            mpd_listen = state
            mpd_send = value  # sends the item value. e.g. sh.dev.mpd.state('play') will send 'play'
        [[[volume]]]
            type = num
            mpd_listen = volume
            mpd_send = volume
        [[[play]]]  # any call of dev.mpd.play will send 'play'
            type = bool
            # knx_listen ....
            mpd_send = play
            enforce_updates = yes
#       [[[time]]]
#          type = num
#          mpd_listen = time
        [[[total]]]
            type = num
            mpd_listen = total
        [[[percent]]]
            type = num
            mpd_listen = percent
        [[[repeat]]]
            type = bool
            mpd_listen = repeat
            mpd_send = repeat
        [[[title]]]
            type = str
            mpd_listen = title
        [[[album]]]
            type = str
            mpd_listen = album
        [[[artist]]]
            type = str
            mpd_listen = artist
        [[[name]]]
            type = str
            mpd_listen = name
        [[[track]]]
            type = str
            mpd_listen = track
        [[[rick]]]
            type = bool
            mpd_file = http://rick.net/roll.m3u
            enforce_updates = yes
        [[[url]]]
            type = str
            mpd_file = value  # plays the item value
            enforce_updates = yes
[office]
    [[mp2]]
        type = str
        mpd_host = 127.0.0.1
        mpd_port = 6601
        [[[state]]]
            type = str
            mpd_listen = state
            mpd_send = value
        [[[volume]]]
            type = num
            mpd_listen = volume
            mpd_send = volume
        [[[name]]]
            type = str
            mpd_listen = name
        [[[track]]]
            type = str
            mpd_listen = track
</pre>
