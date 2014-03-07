This is the subproject 'plugin.sonos' for the Smarthome.py framework (https://github.com/mknx/smarthome).
The plugin is designed to control the sonos speakers in connection with the sonos server.


0. Release
-----------------------------
  v0.3.1  2014-02-18
    -- bugfix in parse_input method: '\r' was not stripped correctly

  v0.3    2014-02-12
    -- bug in thread routine 'subscribe' caused plugin not to resubscribed to sonos broker

  v0.2    2014-02-10
    -- command 'next' and 'previous' added

  v0.1    2014-01-28
    -- Initial release
    -- new commands: seek, track_position, track_duration
    -- requires sonos_broker server v0.1.2


1. Requirements:
-----------------------------

  sonos_broker server v0.1.2
  (https://github.com/pfischi/shSonos)

  smarthome.py


2. Integration in Smarthome.py
------------------------------

  Go to /usr/smarthome/etc and edit plugins.conf and add ths entry:

    [sonos]
  
      class_name = Sonos
      class_path = plugins.sonos
      broker_url = 192.168.178.31:12900               #this is the sonos server ip and port


  Go to /usr/smarthome/items
    
  Create a file named sonos.conf
  
  Edit file with this sample of mine:
  
  
    [sonos]
        sonos_uid = RINCON_000E5123456789             #replace uid with your sonos speaker uid

        [[mute]]
            type = bool
            enforce_updates = True
            sonos_recv = speaker/<sonos_uid>/mute
            sonos_send = speaker/<sonos_uid>/mute/set/{}
            sonos_init = speaker/<sonos_uid>/mute

        [[led]]
            type = bool
            enforce_updates = True
            sonos_recv = speaker/<sonos_uid>/led
            sonos_send = speaker/<sonos_uid>/led/set/{}
            sonos_init = speaker/<sonos_uid>/led

        [[volume]]
            type = num
            enforce_updates = True
            sonos_recv = speaker/<sonos_uid>/volume
            sonos_send = speaker/<sonos_uid>/volume/set/{}
            sonos_init = speaker/<sonos_uid>/volume

        [[stop]]
            type = bool
            enforce_updates = True
            sonos_recv = speaker/<sonos_uid>/stop
            sonos_send = speaker/<sonos_uid>/stop/set/{}
            sonos_init = speaker/<sonos_uid>/stop

        [[play]]
            type = bool
            enforce_updates = True
            sonos_recv = speaker/<sonos_uid>/play
            sonos_send = speaker/<sonos_uid>/play/set/{}
            sonos_init = speaker/<sonos_uid>/play

        [[seek]]
            type = str
            enforce_updates = True
            sonos_send = speaker/<sonos_uid>/seek/set/{}    #use HH:mm:ss

        [[pause]]
            type = bool
            enforce_updates = True
            sonos_recv = speaker/<sonos_uid>/pause
            sonos_send = speaker/<sonos_uid>/pause/set/{}
            sonos_init = speaker/<sonos_uid>/pause

        [[next]]
            type = bool
            enforce_updates = True
            sonos_send = speaker/<sonos_uid>/next/set/{}

        [[previous]]
            type = bool
            enforce_updates = True
            sonos_send = speaker/<sonos_uid>/previous/set/{}

        [[track]]
            type = str
            enforce_updates = True
            sonos_recv = speaker/<sonos_uid>/track
            sonos_init = speaker/<sonos_uid>/track

        [[track_position]]
            type = str
            enforce_updates = True
            sonos_recv = speaker/<sonos_uid>/track_position         #there is no udp event, so poll (e.g 1sec) if needed
            sonos_init = speaker/<sonos_uid>/track_position

        [[track_duration]]
            type = str
            enforce_updates = True
            sonos_recv = speaker/<sonos_uid>/track_duration
            sonos_init = speaker/<sonos_uid>/track_duration

        [[artist]]
            type = str
            enforce_updates = True
            sonos_recv = speaker/<sonos_uid>/artist
            sonos_init = speaker/<sonos_uid>/artist

        [[streamtype]]
            type = str
            enforce_updates = True
            sonos_recv = speaker/<sonos_uid>/streamtype
            sonos_init = speaker/<sonos_uid>/streamtype

        [[play_uri]]
            enforce_update = True
            type = str
            sonos_send = speaker/<sonos_uid>/play_uri/set/{}
            #x-file-cifs://192.168.0.10/music/Depeche Mode - Heaven.mp3

  
  To get your sonos speaker id, type this command in your browser (while sonos server running):
  
    http://<sonos_server_ip:port>/client/list
      

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
    
