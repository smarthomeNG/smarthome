# Simulation

## Description

The simulation plugin allows simulating presence in case none is at home.
To achieve this, the plugin constantly records all configured items and
writes changes to those (events) into a file. It is a text file where each event has one
line. The file can be modified using a text editor, but be careful.
Upon request the plugin can playback the contents of this file.

## Requirements

This plugins has no requirements.

## Configuration

### plugin.yaml

```yaml
simulation:
    class_name: Simulation
    class_path: plugins.simulation
    data_file: /usr/smarthome/var/db/simulation.txt
    # callers:
    #   - KNX
    #   - Visu
```

`data_file`: This is the file where all recorded events are stored.

`callers`: Is an optional list of event sources for recording of events. When an item is changed, the change is done
by someone, e.g. knx for changes from the bus. The caller name is set by the plugin programmer and has to be
found out manually.
Only item changes with a caller in the list are recorded to the simulation file. In the example above e.g. uzsu is
ignored.
Be aware that the caller in the list has to be case sensitive. Otherwise it won't trigger.

### items.yaml


```yaml
sim: track
```

 Add ``sim: track`` to each item that you want to include in the simulation. All items with with the sim
 Attribute are tracked in the data_file. Each change of the item is stored as one line. Only bool
 and number items are supportet.

#### Example

```yaml
eg:

    flur:

        licht:
            type: bool
            visu_acl: rw
            knx_dpt: 1
            knx_cache: 1/1/1
            knx_send: 1/1/0
            enforce_updates: 'yes'
            sim: track
```

Add to your item tree some adminstrative items:

```yaml
sim:

    status:
        type: num
        sim: state
        visu_acl: ro

    control:
        type: num
        sim: control
        visu_acl: rw

    message:
        type: str
        sim: message
        visu_acl: ro

    tank:
        type: num
        sim: tank
        visu_acl: ro
```

These items are needed to control the simulation plugin. If they do not exist,
the plugin will fail to initialize.

**state**: is set by the plugin and can be read in order to see which state the plugin
       is in.

       00: Stop
           The plugin is inactive. It does not record or play anything
       01: Standby
           The plugin does not yet record, but will start at a scheduled time
       02: Record
           The plugin records all configured events
       04: Play
           The plugin plays the event file

**control**: The control item is set by the user to

       01: Stop
           Setting control to 01 will stop recording or playback
       02: Play
           Setting control to 02 will start playback. If record is running, it will
           be stopped automatically
       03: Record
           Setting control to 03 will start recording. If playback is running, it will
           be stopped automatically

**message**:
The message item is set by the plugin depending in the events. In case of recording
it contains the last recorded event. In case of playback it contains the next event.
In case of errors, it will contain an error message. Use this in a visualization
in order to see what the plugin is doing.

**tank**:
Thank contains the actual value of day that are stored in the events file. The value
will grow up to 14 and then stay constant. Put his in the visu in case you want to
see if there are already enough events to start a playback.

## Usage

### Record

The plugin starts automatically together with smarthome.py. After initialization
it automatically starts to record all changes to items that have the ``sim: track``
in the item.yaml file. Item datatypes bool and num have been tested. When an
item is changed it is called an event. All events are stored in a text file.
It does not matter where the change is initiated from with one exception:
The plugin does not record events that are triggered by the plugin itself when
it is in playback mode.
When the plugin initializes for the first time, the event file is created. On
all subsequent starts events are appended to the existing file. The plugin records
a maximum of 14 days. When the 15th day is over, the first day is deleted. So the
file always contains the recent 14 days plus the rest of today.
When recording starts, either after startup or after setting control to 03,
it does not start immediately. In case the event file is empty, recording will start
at next midnight. Until midnight the plugin will be in stand-by. By that there will
always be a full day in the file.
In case the plugin finds events in the file, it compares the last recorded event
with the actual time. In case the actual time is max. 15 minutes advance the last
recorded event, recording will start immediately. In case the actual time is
more advance, recording will start one minute after the last event on the next day.
Ba this behavior empty gaps in the event file are avoided when recording was stopped
for some time because .eg. playback was active.
If control is set to 01, recording stops immediately.

### Playback

Setting control to 02 will start playback. Recording will stop automatically.
Item changes triggered by the simulation are not recorded.
In playback mode, the plugin reads the file line by line and executes the events
by changing the item as it was recorded. When the file ends, the simulation stops.
The day of the event is ignored. The plugin just plays the time stamps one after
the other. In case the next time stamp is before the actual time the plugin
shifts the event to the next day.


### Control

The plugin needs certain control items to exist. They can be integrated in
smartVISU. I created a block the looks like in the following picture:

![screenshot](assets/widget.png)

The code is here. Replace the item names with yours from the item.yaml file.
The png files for the lamps are in the package.

#### SmartVisu 2.9:

```html
/** # Simulations Plugin Bedienung ---------------------------------------------------------*/
<div class="block">
	<div class="set-2" data-role="collapsible-set" data-theme="c" data-content-theme="a" data-mini="true">
		<div data-role="collapsible" data-collapsed="false">
		<h3>Anwesenheitssimulation</h3>
		<table width=100%>
			<tr>
				<td>{{ basic.symbol('','sim.status','','lamp_sim.svg',['4','0','1','2','3'],'',['#0b0','#A4A4A4','#A4A4A4','#A4A4A4','#A4A4A4']) }}</td>
				<td>Aufgenommene Tage<br>{{ basic.print('', 'sim.tank') }}</td>
				<td>{{ basic.symbol('','sim.status','','lamp_sim.svg',['0','4','1','2','3'],'',['#A4A4A4','#A4A4A4','#fa3','#f00','#BF00FF']) }}</td>
				<td rowspan=3 width="20%">{{ basic.tank('P_tank1', 'sim.tank',0,15,1,'cylinder','#0C0') }}</td>
			</tr><tr>
				<td>{{ basic.stateswitch('', 'sim.control', 'mini', '2', 'audio_play.svg', '', '') }}</td>
				<td>{{ basic.stateswitch('', 'sim.control', 'mini', '1', 'audio_stop.svg', '', '') }}</td>
				<td>{{ basic.stateswitch('', 'sim.control', 'mini', '3', 'audio_rec.svg', '', '') }}</td>
				<td></td>
			</tr><tr>
				<td colspan=3 width="80%">{{basic.print('','sim.message', 'html') }}</td>
				<td></td>
			</tr>
		</table>
	</div>
  </div>
</div>
```

#### SmartVisu <= 2.8:

```html
<h1><img class="icon" src='{{ icon0 }}time_clock.png' />Simulation</h1>
<div class="block">
  <div class="set-2" data-role="collapsible-set" data-theme="c" data-content-theme="a" data-mini="true">
    <div data-role="collapsible" data-collapsed="false">
      <h3>Anwesenheitssimulation</h3>
      <table width=100%>
	<tr>
	  <td>
            {{basic.symbol('P_SIM01','ZF.sim.status','',icon0~'lamp_green.png',4)}}
            {{basic.symbol('P_SIM02','ZF.sim.status','',icon0~'lamp_off.png',0)}}
            {{basic.symbol('P_SIM03','ZF.sim.status','',icon0~'lamp_off.png',1)}}
            {{basic.symbol('P_SIM04','ZF.sim.status','',icon0~'lamp_off.png',2)}}
            {{basic.symbol('P_SIM05','ZF.sim.status','',icon0~'lamp_off.png',3)}}
	  </td>
	  <td>
              Days recorded<br>{{ basic.value('P_SIM_T', 'ZF.sim.tank') }}
	  </td>
	  <td>
            {{basic.symbol('P_SIM06','ZF.sim.status','',icon0~'lamp_off.png',0)}}
            {{basic.symbol('P_SIM07','ZF.sim.status','',icon0~'lamp_off.png',4)}}
            {{basic.symbol('P_SIM08','ZF.sim.status','',icon0~'lamp_orange.png',1)}}
            {{basic.symbol('P_SIM09','ZF.sim.status','',icon0~'lamp_red.png',2)}}
            {{basic.symbol('P_SIM10','ZF.sim.status','',icon0~'lamp_purple.png',3)}}
	  </td>
	  <td rowspan=3 width="20%">
            {{ basic.tank('P_tank1', 'ZF.sim.tank',0,15,1,'cylinder','#0C0') }}
	  </td>
	</tr>
	<tr>
	  <td>
            {{basic.button('P_SIMBTN04','ZF.sim.control','Play','',2) }}
	  </td>
	  <td>
            {{basic.button('P_SIMBTN05','ZF.sim.control','Stop','',1) }}
	  </td>
	  <td>
            {{basic.button('P_SIMBTN06','ZF.sim.control','Rec','',3) }}
	  </td>
	  <td>
	  </td>
	</tr>
	<tr>
          <td colspan=3 width="80%">
            {{basic.value('P_SIMSTAT','ZF.sim.message') }}
	  </td>
	  <td>
	  </td>
	</tr>
      </table>
    </div>
  </div>
</div>

```

## Internals

### Event file format

Each event is stored in one line in the following format:
```
Day;Time;Item;Value;Trigger e.g:

Tue;06:05:27;OG.Tobias.Deckenlicht;True;KNX
```
At 00:00 the string "NextDay" is put into one line. The value of Trigger
is the source from where the item was changed during record.
Day and Trigger are ignored for the time being and might be used later.

### State Diagram

The following state diagram shows the state changes depenging on the control item.
The state is stored in the state item.

![Statediagram](assets/state_diagram.png)
