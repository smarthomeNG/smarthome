This sub-project is a client implementation fpr the Sonos Broker. It is a plugin for the 
Smarthome.py framework (https://github.com/smarthomeNG/smarthome).

##Release

v0.9  (2016-11-20)
    
    -- added missing 'track_album' property
    -- add new property 'playlist_total_tracks'
    -- change expected Sonos Broker version to 0.9

v0.8.2  (2016-11-14)

    -- change expected Sonos Broker version to 0.8.2
 
v0.8.1  (2016-11-14)

    -- switching versioning to the current Sonos Broker version
    -- change expected Sonos Broker version to 0.8.1
    
v1.8    (2016-11-11)
    
    -- ATTENTION: commands 'get_playlist' and 'set_playlist' removed  and replaced by 'sonos_playlists' and
       'load_sonos_playlist'
    --command "load_sonos_playlist" with parameter added. The commands loads a Sonos playlist by its name.
        -- optional parameters: play_after_insert, clear_queue
    -- command "play_tunein" added
        -- 'play_tunein' expects a radio station name. The name will be searched within TuneIn and the 
            first match is played. To make sure the correct radio station is played provide the full radio 
            station showing in the Sonos app.
    -- 'clear_queue' command added. The command clears the current queue.
    -- version check against Sonos Broker to identify an out-dated plugin or Broker
    

## Requirements:

  sonos_broker server v0.8.3
  (https://github.com/pfischi/shSonos)

  SmarthomeNG 
  (https://github.com/smarthomeNG/smarthome)


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
        
        [[track_album]]
            type = str
            sonos_recv = track_album
    
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

        [[playlist_total_tracks]]
            type = num
            sonos_recv = playlist_total_tracks
    
        [[streamtype]]
            type = str
            sonos_recv = streamtype
            visu_acl = rw
    
        [[play_uri]]
            type = str
            enforce_updates = True
            sonos_send = play_uri
    
        [[play_tunein]]
            # 'play_tunein' expects a radio station name
            # The name will be searched within TuneIn and the first match is played.
            # To make sure the correct radio station is played provide the full radio station 
            # showing in the Sonos app.
            type = str
            enforce_updates = True
            sonos_send = play_tunein
            
        [[play_snippet]]
            type = str
            enforce_updates = True
            sonos_send = play_snippet
    
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

        [[model_number]]
            type = str
            sonos_recv = model_number
            visu_acl = rw
    
        [[display_version]]
            type = str
            sonos_recv = display_version
            visu_acl = rw
    
        [[household_id]]
            type = str
            sonos_recv = household_id
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
        
        [[sonos_playlists]]
            type = str  
            sonos_send = sonos_playlists
            enforce_updates = True

        [[load_sonos_playlist]]
            type = str
            sonos_send = load_sonos_playlist
            enforce_updates = True

            [[[play_after_insert]]]
                type = bool
                value = 1
            
            [[[clear_queue]]]
                type = bool
                value = 1
        
        [[balance]]
            type = num
            visu_acl = rw
            sonos_recv = balance
            sonos_send = balance
            
            [[[group_command]]]
                type = bool
                value = 0
        
        [[wifi_state]]
            type = bool
            visu_acl = rw
            sonos_recv = wifi_state
            sonos_send = wifi_state

            [[[persistent]]]
                type = bool
                value = 0
            
        [[clear_queue]]    
            type = bool
            enforce_updates = True
            sonos_send = clear_queue
        
        
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
    play_tunein
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
    balance

## Methods

get_favorite_radiostations(<start_item>, <max_items>)

    Get all favorite radio stations from sonos library

    start_item [optional]: item to start, starting with 0 (default: 0)
    max_items [optional]: maximum items to fetch. (default: 50)

    Parameter max_items can only be used, if start_item is set (positional argument)

    It's a good idea to check to see if the total number of favorites is greater than the amount of
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

    call this function with:
    sh.sonos.get_favorite_radiostations()
    
version()

    current plugin version
    
    call this function with:
    sh.sonos.version()

refresh_media_library(<display_option>)
    
    Refreshs the media library
    For parameter 'display_option' see 
    <a href="http://www.sonos.com/support/help/3.4/en/sonos_user_guide/Chap07_new/Compilation_albums.htm">Sonos Help Page</<a>
    
    call this function with:
    
    sh.sonos.refresh_media_library()

discover()

    Performs a manual scan for Sonos speaker in the network.
    
    call this function with:
    sh.sonos.discover()


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