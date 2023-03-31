# Apple TV plugin

#### Version 1.7.1

With this plugin you can control one or more Apple TV's. Each Apple TV needs an own plugin instance. It uses the fantastic [pyatv library](https://github.com/postlund/pyatv/tree/v0.3.9) from [Pierre Ståhl](https://github.com/postlund). It also provides a web interface to be used with the `http` module.


## Requirements
This plugin is designed to work with SHNG v1.5. It runs on current develop version, but using Python >= 3.5 is mandatory.

### Needed software

* Python >= 3.6
* [pyatv package](https://github.com/postlund/pyatv "pyatv page on GitHub")

### Supported Hardware

* [Apple TV](https://www.apple.com/tv/), all generations should work

## Configuration

### plugin.yaml

```yaml
appletv:
    plugin_name: appletv
    #instance: wohnzimmer
    #ip: 192.168.2.103
    #login_id: 00000000-0580-3568-6c73-86bd9b834320
```
The `instance` name is only needed if you have more than one Apple TV. If not specified it uses the default instance.

The parameters `ip` and `login_id` are needed if you have more than one Apple TV. If you omit them the plugin tries to autodetect the Apple TV and uses the first one it finds. You can find the needed parameters for all detected devices in the plugin's web interface.

### items.yaml

Here comes a list of all possible items.
#### name (string)
Contains the name of the device, will be filled by autodetection on plugin startup

#### artwork_url (string)
Contains a URL to the artwork of the currently played media file (if available). 

#### play_state (integer)
The current state of playing as integer. Currently supported play states:

* 0: Device is in idle state
* 1: No media is currently select/playing
* 2: Media is loading/buffering
* 3: Media is paused
* 4: Media is playing
* 5: Media is being fast forwarded
* 6: Media is being rewinded

#### play\_state\_string (string)
The current state of playing as text.

#### playing (bool)
`True` if play\_state is 4 (Media is playing), `False` for all other play\_states.

#### media_type (integer)
The current state of playing as integer. Currently supported play states:

* 1: Media type is unknown
* 2: Media type is video
* 3: Media type is music
* 4: Media type is TV

#### media\_type\_string (string)
The current media type as text.

#### album (string)
The album name. Only relevant if content is music.

#### artist (string)
The artist name. Only relevant if content is music.

#### genre (string)
The genre of the music. Only relevant if content is music.

#### title (string)
The title of the current media.

#### position (integer)
The actual position inside the playing media in seconds.

#### total_time (integer)
The actual playint time of the media in seconds.

#### position_percent (integer)
The actual position inside the playing media in %.

#### repeat (integer)
The current state of selected repeat mode. Currently supported repeat modes:

* 0: No repeat
* 1: Repeat current track
* 2: Repeat all tracks

#### repeat_string (string)
The actual choosen type of repeat mode as string.

#### shuffle (bool)
`True` if shuffle is enabled, `False` if not.

#### rc_top_menu (bool)
Set this item to `True` to return to home menu.
The plugin resets this item to `False` after command execution.

#### rc_menu (bool)
Set this item to `True` to return to menu.
The plugin resets this item to `False` after command execution.

#### rc_select
Set this item to `True` to press the 'select' key.
The plugin resets this item to `False` after command execution.

#### rc_left, rc_up, rc_right, rc_down (bools)
Set one of these items to `True` to move the cursor to the respective direction.
The plugin resets these items to `False` after command execution.

#### rc_previous
Set this item to `True` to press the 'previous' key.
The plugin resets this item to `False` after command execution.

#### rc_play
Set this item to `True` to press the 'play' key.
The plugin resets this item to `False` after command execution.

#### rc_pause
Set this item to `True` to press the 'pause' key.
The plugin resets this item to `False` after command execution.

#### rc_stop
Set this item to `True` to press the 'stop' key.
The plugin resets this item to `False` after command execution.

#### rc_next
Set this item to `True` to press the 'next' key.
The plugin resets this item to `False` after command execution.

#### Example

```yaml
atv:
    wohnzimmer:
        name:
            type: str
            atv@wohnzimmer: name
        artwork_url:
            type: str
            atv@wohnzimmer: artwork_url
        play_state:
            type: num
            atv@wohnzimmer: play_state
        play_state_string:
            type: str
            atv@wohnzimmer: play_state_string
        playing:
            type: bool
            atv@wohnzimmer: playing
        media_type:
            type: num
            atv@wohnzimmer: media_type
        media_type_string:
            type: str
            atv@wohnzimmer: media_type_string
        album:
            type: str
            atv@wohnzimmer: album
        artist:
            type: str
            atv@wohnzimmer: artist
        genre:
            type: str
            atv@wohnzimmer: genre
        title:
            type: str
            atv@wohnzimmer: title
        position:
            type: num
            visu_acl: rw
            atv@wohnzimmer: position
        total_time:
            type: num
            atv@wohnzimmer: total_time
        position_percent:
            type: num
            atv@wohnzimmer: position_percent
        repeat:
            type: num
            visu_acl: rw
            atv@wohnzimmer: repeat
        repeat_string:
            type: str
            atv@wohnzimmer: repeat_string
        shuffle:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: shuffle
        rc_top_menu:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_top_menu
        rc_menu:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_menu
        rc_select:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_select
        rc_left:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_left
        rc_up:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_up
        rc_down:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_down
        rc_right:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_right
        rc_previous:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_previous
        rc_play:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_play
        rc_pause:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_pause
        rc_stop:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_stop
        rc_next:
            type: bool
            visu_acl: rw
            atv@wohnzimmer: rc_next
```

## Methods

### is_playing()
Returns `true` or `false` indicating if the Apple TV is currently playing media.  
Example: `playing = sh.appletv.is_playing()`

### play()
Sends a pause command to the device.  
Example: `sh.appletv.play()`

### pause()
Sends a pause command to the device.  
Example: `sh.appletv.pause()`

### play_url(url)
Plays a media using the given URL. Thed media must of course be compatible with the Apple TV device. For this to work SHNG must be authenticated with the device first. This is done by using the "Authenticate" button in the web interface. A PIN code displayed on the TV screen must then be entered in the web interface. This should only be needed once and be valid forever.  
Example: `sh.appletv.play_url('http://distribution.bbb3d.renderfarming.net/video/mp4/bbb_sunflower_1080p_60fps_normal.mp4')`

## Visualisation with SmartVISU
If you use SmartVISU as your visualisation you can use the following html code inside one of your pages to get you started:

```
<div class="block">
    <div class="set-2" data-role="collapsible-set" data-theme="c" data-content-theme="a" data-mini="true">
        <div data-role="collapsible" data-collapsed="false">
            <h3>Apple TV {{ basic.print('', 'atv.wohnzimmer.name') }} ({{ basic.print('', 'atv.wohnzimmer.media_type_string') }} {{ basic.print('', 'atv.wohnzimmer.play_state_string') }})</h3>
            <table width="100%">
                <tr>
                    <td>
                        {{ basic.stateswitch('', 'atv.wohnzimmer.rc_top_menu', '', '1', 'jquery_home.svg', '') }}
                        {{ basic.stateswitch('', 'atv.wohnzimmer.rc_menu', '', '1', 'control_return.svg', '') }}
                    </td>
                    <td>
                        {{ basic.stateswitch('', 'atv.wohnzimmer.rc_up', '', '1', 'control_arrow_up.svg', '') }}
                    </td>
                </tr>
                <tr>
                    <td>
                        {{ basic.stateswitch('', 'atv.wohnzimmer.shuffle', '', '', 'audio_shuffle.svg', '') }}
                        {{ basic.stateswitch('', 'atv.wohnzimmer.repeat', '', [0,1,2], ['audio_repeat.svg','audio_repeat_song.svg','audio_repeat.svg'], '', ['icon0','icon1','icon1']) }}
                    </td>
                    <td>
                        {{ basic.stateswitch('', 'atv.wohnzimmer.rc_left', '', '1', 'control_arrow_left.svg', '') }}
                        {{ basic.stateswitch('', 'atv.wohnzimmer.rc_select', '', '1', 'control_ok.svg', '') }}
                        {{ basic.stateswitch('', 'atv.wohnzimmer.rc_right', '', '1', 'control_arrow_right.svg', '') }}
                    </td>
                </tr>
                <tr>
                    <td>&nbsp;</td>
                    <td>
                        {{ basic.stateswitch('', 'atv.wohnzimmer.rc_down', '', '1', 'control_arrow_down.svg', '') }}
                    </td>
                </tr>
                <tr>
                    <td colspan="2">&nbsp;</td>
                </tr>
                <tr>
                    <td colspan="2">
                        {{ basic.print('', 'atv.wohnzimmer.artist') }} - {{ basic.print('', 'atv.wohnzimmer.album') }}
                    </td>
                </tr>
                <tr>
                    <td colspan="2">
                        {{ basic.print('', 'atv.wohnzimmer.title') }} ({{ basic.print('', 'atv.wohnzimmer.genre') }})
                    </td>
                </tr>
                <tr>
                    <td colspan="2">{{ basic.slider('', 'atv.wohnzimmer.position_percent', 0, 100, 1, 'horizontal', 'none') }}</td>
                </tr>
                <tr>
                    <td colspan="2">
                        <div data-role="controlgroup" data-type="horizontal">
                            {{ basic.stateswitch('', 'atv.wohnzimmer.rc_previous', '', '1', 'audio_rew.svg', '') }}
                            {{ basic.stateswitch('', 'atv.wohnzimmer.rc_play', '', '1', 'audio_play.svg', '') }}
                            {{ basic.stateswitch('', 'atv.wohnzimmer.rc_pause', '', '1', 'audio_pause.svg', '') }}
                            {{ basic.stateswitch('', 'atv.wohnzimmer.rc_next', '', '1', 'audio_ff.svg', '') }}
                        </div>
                    </td>
                </tr>
                <tr>
                    <td colspan="2">
                        {{ basic.print ('', 'atv.wohnzimmer.artwork_url', 'html', '\'<img src="\' + VAR1 + \'" height="150" />\'') }}
                    </td>
                </tr>
            </table>
        </div>
    </div>
</div>
```

