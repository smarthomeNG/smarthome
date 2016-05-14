This sub-project is a client implementation fpr the Sonos Broker. It is a plugin for the 
Smarthome.py framework (https://github.com/mknx/smarthome).

##Release
  
  v1.3  2015-01-18

    --  added "get_playlist" and "set_playlist" commmands
        It is now possible to store the playlist for later use.
    --  added "is_coordinator" property
    --  added "tts_local_mode" property
    --  added a fallback method to retrieve the local ip address
    --  only working with Sonos Broker version v0.5

  v1.2  2014-11-09
  
    --  added force_stream_mode option to play_tts command (see broker documentation)
    --  added 'fade_in' parameter to play_snippet and play_tts command
        -- the volume for the resumed track fades in

  v1.1  2014-09-23

    --  changed commands to JSON requests to implement the new command interface introduced in Broker v0.3 
    --  added group_command parameter to following items (update your sonos.conf !!!):
        -   mute, led, volume, volume_up, volume_down, play_tts, play_snippet, max_volume, bass, 
            treble, loudness
        -   play_tts, play_snippet: the group parameter only affects the 'volume'-sub-parameter
    --  broker_url parameter was not checked properly for invalid values 
    
    
  v1.0  2014-07-08
    
    --  parameter 'broker_url' in plugin configuration now optional
        -   if value is not set, the current system ip and the default broker port (12900) will be assumed
        -   manually add  this parameter, if the sonos broker is not running on the same system
    --  added optional parameter 'refresh' to plugin configuration (edit /usr/smarthome/etc/plugin.conf)
        -   this parameter specifies, how often the broker is requested for sonos status updates 
            (default: 120s)
        -   Normally, all changes to the speakers will be triggered automatically to the plugin.
    --  bug: if a sonos speaker was reported by the broker but was not declared in sonos.conf, an error 
        occured
    
  
  v0.9    2014-06-15
    
    --  changed values play, pause, stop, led back to normal values (no toggle values). 
        It makes logics easier to write.
    --  new commands:
        -   bass [read/write]: sets the bass for a speaker (value between -10 and 10)
        -   treble [read/write]: sets the treble value for a speaker (value between -10 and 10)
        -   loudness [read/write]: sets the loudness compensation for a speaker (value 0|1)
        -   playmode [read/write] sets the playmode for a sonos speaker 
            values: 'normal', 'shuffle_norepeat', 'shuffle', 'repeat_all'
    
    
  v0.8.1  2014-06-07
    
    --  bugfixes in some command processing
    

## Requirements:

  sonos_broker server v0.3
  (https://github.com/pfischi/shSonos)

  smarthome.py
  (https://github.com/mknx/smarthome)


## Integration in Smarthome.py

Go to /usr/smarthome/etc and edit plugins.conf and add ths entry:

    [sonos]
      class_name = Sonos
      class_path = plugins.sonos
      #broker_url = 192.168.178.31:12900        #optional
      #refresh = 120                            #optional
      
You dont't have to set the ***broker_url*** variable. If value is not set, the current system ip and the default 
broker port (12900) will be assumed. Add this this parameter manually, if the sonos broker is not running on 
the same system.
The ***refresh*** parameter specifies, how often the broker is requested for sonos status updates (default: 120s).
Normally, all changes to the speakers will be triggered automatically to the plugin.

Go to /usr/smarthome/items
    
Create a file named sonos.conf.
  
Edit file with this sample of mine:
  
    [Kinderzimmer]
        sonos_uid = rincon_100e88c3772e01500

        [[mute]]
            type = bool
            enforce_updates = True
            visu_acl = rw
            sonos_recv = mute
            sonos_send = mute
    
            [[[group_command]]]
                type = bool
                value = 0
    
        [[led]]
            type = bool
            enforce_updates = True
            visu_acl = rw
            sonos_recv = led
            sonos_send = led
    
            [[[group_command]]]
                type = bool
                value = 0
    
        [[volume]]
            type = num
            enforce_updates = True
            visu_acl = rw
            sonos_recv = volume
            sonos_send = volume
    
            [[[group_command]]]
                type = bool
                value = 0
    
        [[max_volume]]
            type = num
            enforce_updates = True
            visu_acl = rw
            sonos_recv = max_volume
            sonos_send = max_volume
    
            [[[group_command]]]
                type = bool
                value = 0
    
        [[stop]]
            type = bool
            enforce_updates = True
            visu_acl = rw
            sonos_recv = stop
            sonos_send = stop
    
        [[play]]
            type = bool
            enforce_updates = True
            visu_acl = rw
            sonos_recv = play
            sonos_send = play
    
        [[seek]]
            type = str
            enforce_updates = True
            visu_acl = rw
            sonos_send = seek    #use HH:mm:ss
    
        [[pause]]
            type = bool
            enforce_updates = True
            visu_acl = rw
            sonos_recv = pause
            sonos_send = pause
    
        [[next]]
            type = foo
            enforce_updates = True
            sonos_send = next
            visu_acl = rw
    
        [[previous]]
            type = foo
            enforce_updates = True
            sonos_send = previous
            visu_acl = rw
    
        [[track_title]]
            type = str
            sonos_recv = track_title
    
        [[track_duration]]
            type = str
            sonos_recv = track_duration
            visu_acl = rw
    
        [[track_position]]
            type = str
            sonos_recv = track_position
            visu_acl = rw
    
        [[track_artist]]
            type = str
            sonos_recv = track_artist
    
        [[track_uri]]
            type = str
            sonos_recv = track_uri
            visu_acl = rw
    
        [[track_album_art]]
            type = str
            sonos_recv = track_album_art
    
        [[playlist_position]]
            type = num
            sonos_recv = playlist_position
            visu_acl = rw
    
        [[streamtype]]
            type = str
            sonos_recv = streamtype
            visu_acl = rw
    
        [[play_uri]]
            type = str
            enforce_updates = True
            sonos_send = play_uri
            visu_acl = rw
    
        [[play_snippet]]
            type = str
            enforce_updates = True
            sonos_send = play_snippet
            visu_acl = rw
    
            [[[volume]]]
                type = num
                value = -1
    
            [[[group_command]]]
                type = bool
                value = 0
    
        [[play_tts]]
            type = str
            enforce_updates = True
            sonos_send = play_tts
            visu_acl = rw
    
            [[[volume]]]
                type = num
                value = -1
    
            [[[language]]]
                type = str
                value = 'de'
    
            [[[group_command]]]
                type = bool
                value = 0
    
        [[radio_show]]
            type = str
            sonos_recv = radio_show
            visu_acl = rw
    
        [[radio_station]]
            type = str
            sonos_recv = radio_station
            visu_acl = rw
    
        [[uid]]
            type = str
            sonos_recv = uid
            visu_acl = rw
    
        [[ip]]
            type = str
            sonos_recv = ip
            visu_acl = rw
    
        [[model]]
            type = str
            sonos_recv = model
            visu_acl = rw
    
        [[zone_name]]
            type = str
            sonos_recv = zone_name
            visu_acl = rw
    
        [[zone_icon]]
            type = str
            sonos_recv = zone_icon
            visu_acl = rw
    
        [[serial_number]]
            type = str
            sonos_recv = serial_number
            visu_acl = rw
    
        [[software_version]]
            type = str
            sonos_recv = software_version
            visu_acl = rw
    
        [[hardware_version]]
            type = str
            sonos_recv = hardware_version
            visu_acl = rw
    
        [[mac_address]]
            type = str
            sonos_recv = mac_address
            visu_acl = rw
    
        [[status]]
            type = bool
            sonos_recv = status
            visu_acl = rw
    
        [[join]]
            type = str
            enforce_updates = True
            sonos_send = join
            visu_acl = rw
    
        [[unjoin]]
            type = foo
            enforce_updates = True
            sonos_send = unjoin
            visu_acl = rw
    
        [[partymode]]
            type = foo
            enforce_updates = True
            sonos_send = partymode
            visu_acl = rw
    
        [[volume_up]]
            type = foo
            enforce_updates = True
            visu_acl = rw
            sonos_send = volume_up
    
            [[[group_command]]]
                type = bool
                value = 0
    
        [[volume_down]]
            type = foo
            enforce_updates = True
            visu_acl = rw
            sonos_send = volume_down
    
            [[[group_command]]]
                type = bool
                value = 0
    
        [[additional_zone_members]]
            type = str
            visu_acl = rw
            sonos_recv = additional_zone_members
    
        [[bass]]
            type = num
            visu_acl = rw
            sonos_recv = bass
            sonos_send = bass
    
            [[[group_command]]]
                type = bool
                value = 0
    
        [[treble]]
            type = num
            visu_acl = rw
            sonos_recv = treble
            sonos_send = treble
    
            [[[group_command]]]
                type = bool
                value = 0
    
        [[loudness]]
            type = bool
            visu_acl = rw
            sonos_recv = loudness
            sonos_send = loudness
    
            [[[group_command]]]
                type = bool
                value = 0
    
        [[playmode]]
            type = str
            enforce_updates = True
            visu_acl = rw
            sonos_recv = playmode
            sonos_send = playmode
    
        [[alarms]]
            type = dict
            enforce_updates = True
            visu_acl = rw
            sonos_recv = alarms
            sonos_send = alarms
        
        [[is_coordinator]]
            type = bool
            sonos_recv = is_coordinator

        [[tts_local_mode]]
            type = bool
            sonos_recv = tts_local_mode
        
        [[get_playlist]]
           type = str  # the give item value represents the local file path
                    # where to save the playlist
            sonos_send = get_playlist
            enforce_updates = True

        [[set_playlist]]
            type = str  # the give item value represents the file path where
                        # the playlist is stored (previously saved with
                        # 'get_playlist')
            sonos_send = set_playlist
            enforce_updates = True

            [[[play_after_insert]]]
                type = bool
                value = 0

        
 This sonos.conf file implements most of the commands to interact with the Sonos Broker. Please follow the detailed
 description under the [command section in the Broker manual](../README.md#available-commands).

 You can find an example config in the plugin sub-directory "examples". 


 To get your sonos speaker id, type this command in your browser (while sonos server is running):
  
    http://<sonos_server_ip:port>/client/list

## Group behaviour

 If two or more speakers are in the same zone, most of the commands are automatically executed for all zone
 members. Normally the Sonos API requires to send the command to the zone master. This is done by the Broker
 automatically. You don't have to worry about which speaker is the zone master. Just send your command to one 
 of the zone member speaker. 

##### These commands will always act as group commands:

    stop
    play
    seek
    pause
    next
    previous
    play_uri
    play_snippet ('group_command' parameter only affects the snippet volume)
    play_tts ('group_command' parameter only affects the snippet volume)
    partymode
    playmode
    set_playlist

###### These commands only act as group commands if the parameter 'group_command' is set to 1:

    mute
    led
    volume
    max_volume
    volume_up
    volume_down
    join
    unjoin
    bass
    treble
    loudness

## Methods

get_favorite_radiostations(<start_item>, <max_items>)

    Get all favorite radio stations from sonos library

    start_item [optional]: item to start, starting with 0 (default: 0)
    max_items [optional]: maximum items to fetch. (default: 50)

    Parameter max_items can only be used, if start_item is set (positional argument)

    It's a good idea to check to see if the total number of favorites is greater than the amount you
    requested ('max_items'), if it is, use `start` to page through and  get the entire list of favorites.

    Response:

    JSON object, utf-8 encoded

    Example:

    {
        "favorites":
        [
            { "title": "Radio TEDDY", "uri": "x-sonosapi-stream:s80044?sid=254&flags=32" },
            { "title": "radioeins vom rbb 95.8 (Pop)", "uri": "x-sonosapi-stream:s25111?sid=254&flags=32" }
        ],
            "returned": 2,
            "total": "10"
    }

version()

    current plugin version


## smartVISU Integration

more information here: https://github.com/pfischi/shSonos/tree/develop/widget.smartvisu


## Logic examples

To run this plugin with a logic, here is my example:
    
Go to /usr/smarthome/logics and create a self-named file (e.g. sonos.py)
Edit this file and place your logic here:
    
    
    #!/usr/bin/env python
    #

    if sh.ow.ibutton():
        sh.sonos.mute(1)
    else:
        sh.sonos.mute(0)

    
  Last step: go to /usr/smarthome/etc and edit logics.conf
  Add a section for your logic:
    
    # logic
    [sonos_logic]
        filename = sonos.py
        watch_item = ow.ibutton
    
    
In this small example, the sonos speaker with uid RINCON_000E58D5892E11230 is muted when the iButton is connected
to an iButton Probe.