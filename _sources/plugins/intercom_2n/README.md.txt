
# Intercom-2N Plugin

## Requirements

This plugin is designed to work with the [2N Intercom systems](http://www.2n.cz/en/), the official distributor in
Germany is [Keil Telecom](http://www.keil-telecom.de).

The plugin is tested to work with [2N Helios IP Verso](http://www.2n.cz/en/products/intercom-systems/ip-intercoms/helios-ip-verso/) but should be working with all device,
which integrates the [2N Helio HTTP API](https://wiki.2n.cz/hip/hapi/latest/en).

Please use the support thread in the [KNX-User-Forum](https://knx-user-forum.de/forum/supportforen/smarthome-py/1030539-plugin-2n-intercom-t%C3%BCrsprechanlagen) for any questions and bug reports.

Most of the commands need the 'Enhanced Integration' licence key. ([Shop Keil Telecom](http://www.keil-onlineshop.de/2N-EntryCom-IP/2N-EntryCom-IP-Lizenzen/)).
The event listening feature should be working without any extra license.

You must also add the required privileges to your user. This can be done in the web-interface of your 2N Intercom.   


Command       | Service      | Privileges  | License     
-------------:|-------------:| -----------:|------------:
system_info|System|System Control|No
system_status|System|System Control|Yes
system_restart|System|System Control|Yes
firmware_upload|System|System Control|Yes
firmware_apply|System|System Control|Yes
config_get|System|System Control|Yes
config_upload|System|System Control|Yes
factory_reset|System|System Control|Yes
switch_caps|Switch|Switch Monitoring|Yes
switch_status|Switch|Switch Monitoring|Yes
switch_control|Switch|Switch Control|Yes
io_caps|I/O|I/O Monitoring|Yes
io_status|I/O|I/O Monitoring|Yes
io_control|I/O|I/O Control|Yes
phone_status|Phone/Call|Call Monitoring|Yes
call_status|Phone/Call|Call Monitoring|Yes
call_dial|Phone/Call|Call Control|Yes
call_answer|Phone/Call|Call Control|Yes
call_hangup|Phone/Call|Call Control|Yes
camera_caps|Camera|Camera Monitoring|No
camera_snapshot|Camera|Camera Monitoring|No
display_caps|Display|Display Control|Yes
display_upload_image|Display|Display Control|Yes
log_caps|Logging| |No
log_subscribe|Logging| |No
log_unsubscribe|Logging| |No
log_pull|Logging| |No
audio_test|Audio|Audio Control|Yes
email_send|E-mail|E-mail Control|Yes
pcap|System|System Control|Yes
pcap_restart|System|System Control|Yes
pcap_stop|System|System Control|Yes


## Plugin setup

Edit your ```plugin.yaml``` and add following lines:


```yaml
intercom_2n:
    plugin_name: intercom_2n
    intercom_ip: 192.168.0.10
    ssl: 'True'
    auth_type: 2
    username: my_user
    password: my_pass
```

Change <b>intercom_ip</b>, <b>ssl</b>, <b>auth_type</b>, <b>username</b> and <b>password</b> to your needs.

The ```auth_type``` parameter must be set to one of the following values:

    0: no authentication
    1: Basic Authentication
    2: Digest Authentication

This value must be the same as the value in web-interface of your 2N Intercom.
Despite the fact that you can adjust different security settings for different APIs in your 2N Intercom,
this plugin only supports a consistent setting for all APIs. So just set all security parameter in the web-interface to
the same setting (under Services --> HTTP-API).

If you set the authentication methode to Digest (maybe the securest setting) you might wondering about some '401' logs of the
underlying python requests class. This is a feature and can be ignored (they have to call the function twice, the first
call is always an 401 unauthorized error).

Copy the ```2n_intercom.yaml``` from the example directory of this plugin (usually under ```plugins/intercom_2n/example```
(or paste the example below) to the items directory. You can delete unwanted events or commands, but always the complete subtree.
<b>Don't change the structure of an event or command</b>, the internal processing depends on it.


## Plugin usage

### Events

The integrated event handling is working out of the box. You don't have to care about event subscription and renewing of
this subscription. If an 2N Intercom event occurs, the child items of an event will be set with the incoming value.

Example:

```yaml
Intercom_2n:

    Events:

        DeviceState:
            # Signals the device state changes.
            event_2n: DeviceState

            device_state:
                # Signalled device state:
                # startup – generated one-time after device start (always the first event ever)
                type: str
                event_data_2n: state
```

If the 2N device state was changed (for example an reboot), the item ```Intercom_2n.Events.DeviceState.device_state``` will be
set to 'startup'.
An event can have more than one sub-item, all of them will be set to the appropriate event value.

**Implemented events:**

Event type |Description |Note
---------:|------------:|----:
AudioLoopTest|Signals performance and result of an automatic audio loop test.|with a valid Enhanced Audio licence key only
CallStateChanged|Signals a setup/end/change of the active call state. 	 
CardEntered|Signals tapping of an RFID card on the card reader.|for RFID card reader equipped models only
CodeEntered|Signals entering of a user code via the numeric keypad.|for numeric keypad equipped models only
DeviceState|Signals a system event generated at device state changes. 	 
DoorOpenTooLong|Signals excessively long door opening, or door closing failure within the timeout.|for digital input equipped models only
InputChanged|Signals a change of the logic input state. 	 
KeyPressed|Signals pressing of a speed dial/numeric keypad button. 	 
KeyReleased|Signals releasing of a speed dial/numeric keypad button. 	 
LoginBlocked|Signals temporary blocking of login to the web interface. 	 
MotionDetected|Signals motion detection via a camera.|for camera-equipped models only
NoiseDetected|Signals an increased noise level detection.|for microphone/microphone input equipped models only
OutputChanged|Signals a change of the logic output state. 	 
RegistrationStateChanged|Signals a change of the SIP server registration state. 	 
SwitchStateChanged|Signals a switch 1–4 state change. 	 
TamperSwitchActivated|Signals tamper switch activation.|for tamper switch equipped models only
UnauthorizedDoorOpen|Signals unauthorised door opening.|for digital input equipped models only
UserAuthenticated|Signals user authentication and subsequent door opening. 	 


### Commands

All commands consists of one or more sub-items. There is always an ```execute``` item. If you set this item to ```True```,
the command defined in the parent item (attribute ```command_2n```) will be executed. The result value will be stored as
the value of the parent item.

Example:
```yaml
Intercom_2n:

    Commands:

        switch_caps:
            type: str
            command_2n: switch_caps
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'
```

If you set the item ```Intercom_2n.Commands.system_info.execute = 1```, the item value of ```Intercom_2n.Commands.system_info```
should be something like this:

```
    {
        'success" : true,
         "result" : {
         "variant" : "2N Helios IP Vario",
         "serialNumber" : "08-1240-1138",
         "hwVersion" : "535v1",
         "swVersion" : "2.10.0.19.2",
         "buildType" : "beta",
         "deviceName" : "2N Helios IP Vario"
         }
    }
```

Most of the command have multiple options to set. All options are sub-items of a command. Some of them are mandatory,
others are optional. All commands and command options are documented in the example below (and in the example item file)
and should be self-explanatory.


## Example item config

```
Intercom_2n:

    Events:

        DeviceState:
            # Signals the device state changes.
            event_2n: DeviceState

            device_state:
                # Signalled device state:
                # startup – generated one-time after device start (always the first event ever)
                type: str
                event_data_2n: state

        AudioLoopTest:
            # Signals performance and result of an automatic audio loop test. The AudioLoopTest event is only available in
            # selected models with a valid Enhanced Audio licence. The event is signalled whenever the automatic test has
            # been performed (either scheduled or manually started).
            event_2n: AudioLoopTest

            audio_test_result:
                # Result of an accomplished text:
                # passed – the test was carried out successfully, no problem has been detected.
                # failed – the test was carried out, a loudspeaker/microphone problem has been detected.
                type: str
                event_data_2n: result
                enforce_updates: 'true'

        MotionDetected:
            # Signals motion detection via a camera. The event is available in camera-equipped models only. The event is
            # generated only if the function is enabled in the intercom camera configuration.
            event_2n: MotionDetected

            state:
                # Motion detector state:
                # in – signals the beginning of the interval in which motion was detected.
                # out – signals the end of the interval in which motion was detected.
                type: str
                event_data_2n: state
                enforce_updates: 'true'

        NoiseDetected:
            # Signals an increased noise level detected via an integrated or external microphone. The event is generated only
            # if this function is enabled in the intercom configuration.
            event_2n: NoiseDetected

            state:
                # Noise detector state:
                # in – signals the beginning of the interval in which noise was detected.
                # out – signals the end of the interval in which noise was detected.
                type: str
                event_data_2n: state
                enforce_updates: 'true'

        KeyPressed:
            # Signals pressing (KeyPressed) of speed dial or numeric keypad buttons.
            event_2n: KeyPressed

            key_code:
                # Pressed button code:
                # 0 to 9 – numeric keypad buttons
                # %1–%150 – speed dialling buttons
                # * – button with a * or phone symbol
                # – button with a # or key symbol
                type: str
                event_data_2n: key
                enforce_updates: 'True'

        KeyReleased:
            # Signals releasing (KeyReleased) of speed dial or numeric keypad buttons.
            event_2n: KeyReleased

            key_code:
                # Released button code:
                # 0 to 9 – numeric keypad buttons
                # %1–%150 – speed dialling buttons
                # * – button with a * or phone symbol
                # – button with a # or key symbol
                type: str
                event_data_2n: key
                enforce_updates: 'True'

        CodeEntered:
            # Signals entering of a user code via the numeric keypad. The event is generated in numeric keypad equipped
            # devices only.
            event_2n: CodeEntered

            code:
                # User code, 1234, e.g.. The code includes 2 digits at least and 00 cannot be used.
                type: str
                event_data_2n: code
                enforce_updates: 'True'

            valid:
                # Code validity (i.e. if the code is defined as a valid user code or universal switch code in the intercom
                # configuration):
                # false – invalid code
                # true – valid code
                type: bool
                event_data_2n: valid
                enforce_updates: 'True'

        CardEntered:
            # Signals tapping an RFID card on the card reader. The event is generated in RFID card reader equipped devices
            # only.
            event_2n: CardEntered

            direction:
                # RFID direction:
                # in – arrival
                # out – departure
                # any – passage
                # Note: Set the card reader direction using the intercom configuration interface.
                type: str
                event_data_2n: direction
                enforce_updates: 'true'

            reader:
                # RFID card reader/Wiegand module name, or one of the following non-modular intercom model values:
                # internal – internal card reader (2N® Helios models)
                # external – external card reader connected via the Wiegand interface
                # Note: Set the card reader name using the intercom configuration interface.
                type: str
                event_data_2n: reader
                enforce_updates: 'true'

            uid:
                # Unique identifier of the applied card (hexadecimal format, 6 - 16 characters depending on the card type)
                type: str
                event_data_2n: uid
                enforce_updates: 'true'

            valid:
                # Validity of the applied RFID card (if the card uid is assigned to one of the intercom users listed in the phonebook)
                # false – invalid card
                # true – valid card
                type: bool
                event_data_2n: valid
                enforce_updates: 'true'

        InputChanged:
            # Signals a state change of the logic input. Use the /api/io/caps function to get the list of available inputs.
            event_2n: InputChanged

            port:
                # I/O port name
                type: str
                event_data_2n: port
                enforce_updates: 'true'

            state:
                # Current I/O port logic state:
                # false – inactive, log. 0
                # true – active, log. 1
                type: bool
                event_data_2n: port
                enforce_updates: 'true'

        OutputChanged:
            # Signals a state change of the logic output. Use the /api/io/caps function to get the list of available
            # outputs.
            event_2n: OutputChanged

            port:
                # I/O port name
                type: str
                event_data_2n: port
                enforce_updates: 'true'

            state:
                # Current I/O port logic state:
                # false – inactive, log. 0
                # true – active, log. 1
                type: bool
                event_data_2n: port
                enforce_updates: 'true'

        SwitchState:
            # Signals a switch state change (refer to the intercom configuration in Hardware | Switches).
            event_2n: SwitchStateChanged

            switch:
                # Switch number 1..4
                type: num
                event_data_2n: switch
                enforce_updates: 'true'

            state:
                # Current logic state of the switch:
                # false – inactive, log.0
                # true – active, log.1
                type: bool
                event_data_2n: state
                enforce_updates: 'true'

        CallState:
            # Signals a setup/end/change of the active call state.
            event_2n: CallStateChanged

            state:
                # Current call state:
                # connecting – call setup in progress (outgoing calls only)
                # ringing – ringing
                # connected – call connected
                # terminated – call terminated
                type: str
                event_data_2n: state
                enforce_updates: 'true'

            direction:
                # Call direction:
                # incoming – incoming call
                # outgoing – outgoing call
                type: str
                event_data_2n: direction
                enforce_updates: 'true'

            reason:
                # Call end reason. The parameter is available only if the call end state is signalled.
                # normal – normal call end
                # busy – called station busy
                # rejected – call rejected
                # noanswer – no answer from called user
                # noresponse – no response from called station (to SIP messages)
                # completed_elsewhere – call answered by another station (group calls) failure – call setup failure
                type: str
                event_data_2n: reason
                enforce_updates: 'true'

            peer:
                # SIP URI of the calling (incoming calls) or called (outgoing calls) subscriber
                type: str
                event_data_2n: peer
                enforce_updates: 'true'

            session:
                # Unique call identifier. Can also be used in the /api/call/answer, /api/call, /hangup and /api/call/status
                # functions.
                type: num
                event_data_2n: session
                enforce_updates: 'true'

            call:
                # TBD ??? (yes, this is the value described in the official documentation, don't know what this is)
                type: num
                event_data_2n: call
                enforce_updates: 'true'

        RegistrationStateChanged:
            # Signals a change of the SIP account registration state.
            event_2n: RegistrationStateChanged

            sipAccount:
                # SIP account number showing a state change:
                # 1 – SIP account 1
                # 2 – SIP account 2
                type: num
                event_data_2n: sipAccount
                enforce_updates: 'true'

            state:
                # New SIP account registration state:
                # registered – account successfully registered
                # unregistered – account unregistered
                # registering – registration in progress
                # unregistering – unregistration in progress
                type: str
                event_data_2n: state
                enforce_updates: 'true'

        TamperSwitchActivated:
            # Signals tamper switch activation - device cover opening. Make sure that the tamper switch function is
            # configured in the Digital Inputs | Tamper Switch menu.
            event_2n: TamperSwitchActivated

            state:
                # Tamper switch state:
                # in – signals tamper switch activation (i.e. device cover open).
                # out – signals tamper switch deactivation (device cover closed).
                type: str
                event_data_2n: state
                enforce_updates: 'true'

        UnauthorizedDoorOpen:
            # Signals unauthorised door opening. Make sure that a door-open switch is connected to one of the digital
            # inputs and the function is configured in the Digital Inputs | Door State menu.
            event_2n: UnauthorizedDoorOpen

            state:
                # Unauthorised door opening state:
                # in – signals the beginning of the unauthorised opening state.
                # out – signals the end of the unauthorised door opening state.
                type: str
                event_data_2n: state
                enforce_updates: 'true'

        DoorOpenTooLong:
            # Signals an excessively long door opening or failure to close the door within a timeout. Make sure that a
            # door-open switch is connected to one of the digital inputs and the function is configured in the
            # Digital Inputs | Door State menu.
            event_2n: DoorOpenTooLong

            state:
                # DoorOpenToo Long state:
                # in – signals the beginning of the DoorOpenTooLong state.
                # out – signals the end of the DoorOpenTooLong state.
                type: str
                event_data_2n: state
                enforce_updates: 'true'

        LoginBlocked:
            # Signals a temporary blocking of the web interface access due to repeated entering of an invalid login name
            # or password.
            event_2n: LoginBlocked

            address:
                # IP address from which invalid data were entered repeatedly.
                type: str
                event_data_2n: address
                enforce_updates: 'true'

    Commands:

        system_info:
            # The /api/system/info function provides basic information on the device: type, serial
            # number, firmware version, etc. The function is available in all device types regardless
            # of the set access rights.
            type: str
            command_2n: system_info
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example:
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"variant\" : \"2N Helios IP Vario\",
        # \"serialNumber\" : \"08-1860-0035\",
        # \"hwVersion\" : \"535v1\",
        # \"swVersion\" : \"2.10.0.19.2\",
        # \"buildType\" : \"beta\",
        # \"deviceName\" : \"2N Helios IP Vario\"
        # }
        # }
        system_status:
            # The /api/system/status function returns the current intercom status.
            # The function is part of the System service and the user must be assigned the System
            # Control privilege for authentication if required. The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: system_status
            enforce_updates: 'true'

            execute:
                type: bool
                enforce_updates: 'true'
                command_2n: execute

        # item value example:
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"systemTime\" : 1418225091,
        # \"upTime\" : 190524
        # }
        # }
        system_restart:
            # The /api/system/restart restarts the intercom.
            # The function is part of the System service and the user must be assigned the System
            # Control privilege for authentication if required. The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: system_restart
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        firmware_upload:
            # The /api/firmware function helps you upload a new firmware version to the device.
            # When the upload is complete, use /api/firmware/apply to confirm restart and FW change.
            # The function is part of the System service and the user must be assigned the System
            # Control privilege for authentication if required . The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: firmware_upload
            enforce_updates: 'true'

            firmware_file:
                # file path to firmware file
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example:
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"version\" : \"2.10.0.19.2\",
        # \"downgrade\" : false
        # }
        # }
        firmware_apply:
            # The /api/firmware/apply function is used for earlier firmware upload ( PUT
            # /api/firmware ) confirmation and subsequent device restart.
            # The function is part of the System service and the user must be assigned the System
            # Control privilege for authentication if required. The function is available with the
            # Enhanced Integration licence key only.
            type: str
            commmand_2n: firmware_apply
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        config_get:
            # The /api/config function helps you to download the device configuration.
            # The function is part of the System service and the user must be assigned the System
            # Control privilege for authentication if required . The function is available with the
            # Enhanced Integration licence key only.
            type: str
            enforce_updates: 'true'
            command_2n: config_get

            config_file:
                # save path  of config file
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # value item example
        # {
        # \"success\" : true
        # }
        config_upload:
            # The /api/config function helps you to upload the device configuration.
            # The function is part of the System service and the user must be assigned the System
            # Control privilege for authentication if required . The function is available with the
            # Enhanced Integration licence key only.
            type: str
            enforce_updates: 'true'
            command_2n: config_upload

            config_file:
                # path to file which should be uploaded
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        factory_reset:
            # The /api/config/factoryreset function resets the factory default values for all the
            # intercom parameters. This function is equivalent to the function of the same name in
            # the System / Maintenance / Default setting section of the configuration web interface .
            # The function is part of the System service and the user must be assigned the System
            # Control privilege for authentication if required. The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: factory_reset
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        switch_caps:
            # The /api/switch/caps function returns the current switch settings and control
            # options. Define the switch in the optional switch parameter. If the switch parameter
            # is not included, settings of all the switches are returned.
            # The function is part of the Switch service and the user must be assigned the Switch
            # Monitoring privilege for authentication if required . The function is available with the Enhanced
            # Integration licence key only.
            type: str
            command_2n: switch_caps
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"switches\" : [
        # {
        # \"switch\" : 1,
        # \"enabled\" : true,
        # \"mode\" : \"monostable\",
        # \"switchOnDuration\" : 5,
        # \"type\" : \"normal\"
        # },
        # {
        # \"switch\" : 2,
        # \"enabled\" : true,
        # \"mode\" : \"monostable\",
        # \"switchOnDuration\" : 5,
        # \"type\" : \"normal\"
        # },
        # {
        # \"switch\" : 3,
        # \"enabled\" : false
        # },
        # {
        # \"switch\" : 4,
        # \"enabled\" : false
        # }]
        # }
        # }
        switch_status:
            # The /api/switch/status function returns the current switch statuses.
            # The function is part of the Switch service and the user must be assigned the Switch
            # Monitoring privilege for authentication if required. The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: switch_status
            enforce_updates: 'true'

            switch:
                # (optional) number of switch
                # 0 for all switches
                type: num

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"switches\" : [
        # {
        # \"switch\" : 1,
        # \"active\" : false
        # },
        # {
        # \"switch\" : 2,
        # \"active\" : false
        # },
        # {
        # \"switch\" : 3,
        # \"active\" : false
        # },
        # {
        # \"switch\" : 4,
        # \"active\" : false
        # }]
        # }
        # }
        switch_control:
            # The /api/switch/ctrl function controls the switch statuses. The function has two
            # mandatory parameters: switch , which determines the switch to be controlled, and
            # action , defining the action to be executed over the switch (activation, deactivation, state change).
            # The function is part of the Switch service and the user must be assigned the Switch
            # Control privilege for authentication if required . The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: switch_control
            enforce_updates: 'true'

            switch:
                # Mandatory switch identifier (typically, 1 to 4). Use also /api/switch/caps
                # to know the exact count of switches
                type: num

            action:
                # Mandatory action defining parameter ( on – activate switch, off – deactivate switch,
                # trigger – change switch state).
                type: str

            response:
                # Optional parameter modifying the intercom response to include the text
                # defined here instead of the JSON message.
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example (differs if response parameter was used)
        # {
        # \"success\" : true
        # }
        io_caps:
            # The /api/io/caps function returns a list of available hardware inputs and outputs
            # (ports) of the device. Define the input/output in the optional port parameter. If the
            # port parameter is not included, settings of all the inputs and outputs are returned .
            # The function is part of the I/O service and the user must be assigned the I/O
            # Monitoring privilege for authentication if required . The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: io_caps
            enforce_updates: 'true'

            port:
                # optional input/output identifier; if empty all ports will be listed
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"ports\" : [
        # {
        # \"port\" : \"relay1\",
        # \"type\" : \"output\"
        # },
        # {
        # \"port\" : \"relay2\",
        # \"type\" : \"output\"
        # }]
        # }
        # }
        io_status:
            # The /api/io/status function returns the current statuses of logic inputs and outputs
            # (ports) of the device. Define the input/output in the optional port parameter. If the
            # port parameter is not included, statuses of all the inputs and outputs are returned.
            # The function is part of the I/O service and the user must be assigned the I/O
            # Monitoring privilege for authentication if required . The function is available with the
            type: str
            command_2n: io_status
            enforce_updates: 'true'

            port:
                # Optional input/output identifier. Use also /api/io/caps to get
                # identifiers of the available inputs and outputs.
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"ports\" : [
        # {
        # \"port\" : \"relay1\",
        # \"state\" : 0
        # },
        # {
        # \"port\" : \"relay2\",
        # \"state\" : 0
        # }]
        # }
        # }
        io_control:
            # The /api/io/ctrl function controls the statuses of the device logic outputs. The
            # function has two mandatory parameters: port, which determines the output to be
            # controlled, and action, defining the action to be executed over the output (activation,
            # deactivation).
            # The function is part of the I/O service and the user must be assigned the I/O
            # Control privilege for authentication if required . The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: io_control
            enforce_updates: 'true'

            port:
                # Mandatory I/O identifier. Use also /api/io/caps to get the identifiers of
                # the available inputs and outputs.
                type: str

            action:
                # Mandatory action defining parameter (on – activate output, log. 1, off –
                # deactivate output, log. 0)
                type: str

            response:
                # Optional parameter modifying the intercom response to include the text
                # defined here instead of the JSON message.
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example (differs if response parameter was used)
        # {
        # \"success\" : true
        # }
        phone_status:
            # The /api/phone/status functions helps you get the current statuses of the device
            # SIP accounts.
            # The function is part of the Phone/Call service and the user must be assigned the
            # Phone/Call Monitoring privilege for authentication if required . The function is
            # available with the Enhanced Integration licence key only.
            type: str
            command_2n: phone_status
            enforce_updates: 'true'

            account:
                # Optional SIP account identifier (1 or 2). If the parameter is not included,
                # the function returns statuses of all the SIP accounts.
                type: num

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"accounts\" : [
        # {
        # \"account\" : 1,
        # \"sipNumber\" : \"5046\",
        # \"registered\" : true,
        # \"registerTime\" : 1418034578
        # },
        # {
        # \"account\" : 2,
        # \"sipNumber\" : \"\",
        # \"registered\" : false
        # }]
        # }
        # }
        call_status:
            # The /api/call/status function helps you get the current states of active telephone
            # calls. The function returns a list of active calls including parameters.
            # The function is part of the Phone/Call service and the user must be assigned the
            # Phone/Call Monitoring privilege for authentication if required . The function is
            # available with the Enhanced Integration licence key only.
            type: str
            command_2n: call_status
            enforce_updates: 'true'

            session:
                # Optional call identifier. If the parameter is not included, the function
                # returns statuses of all the active calls.
                type: num

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"sessions\" : [
        # {
        # \"session\" : 1,
        # \"direction\" : \"outgoing\",
        # \"state\" : \"ringing\"
        # }]
        # }
        call_dial:
            # The /api/call/dial function initiates a new outgoing call to a selected phone number
            # or sip uri. After some test with a Fritzbox, it seems you have to call '**your_number/1'
            # to call internal phones. '/2' seems to be necessary if you want to call number over sip account 2.
            # The function is part of the Phone/Call service and the user must be assigned the
            # Phone/Call Control privilege for authentication if required . The function is available
            # with the Enhanced Integration licence key only.
            type: str
            command_2n: call_dial
            enforce_updates: 'true'

            number:
                # Mandatory parameter specifying the destination phone number or sip uri
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"session\" : 2
        # }
        # }
        call_answer:
            # The /api/call/answer function helps you answer an active incoming call (in the
            # ringing state).
            # The function is part of the Phone/Call service and the user must be assigned the
            # Phone/Call Control privilege for authentication if required . The function is available
            # with the Enhanced Integration licence key only.
            type: str
            command_2n: call_answer
            enforce_updates: 'true'

            session:
                # Active incoming call identifier
                type: num

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        call_hangup:
            # The /api/call/hangup helps you hang up an active incoming or outgoing call.
            # The function is part of the Phone/Call service and the user must be assigned the
            # Phone/Call Control privilege for authentication if required . The function is available
            # with the Enhanced Integration licence key only.
            type: str
            command_2n: call_hangup
            enforce_updates: 'true'

            session:
                # Active call identifier
                type: num

            reason:
                # End call reason:
                # normal - normal call end (default value) reason
                # rejected - call rejection signalling
                # busy - station busy signalling
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        camera_caps:
            # The /api/camera/caps function returns a list of available video sources and
            # resolution options for JPEG snapshots to be downloaded via the
            # /api/camera/snapshot function.
            # The function is part of the Camera service and the user must be assigned the Camera
            # Monitoring privilege for authentication if required.
            type: str
            command_2n: camera_caps
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"jpegResolution\" : [
        # {
        # \"width\" : 160,
        # \"height\" : 120
        # },
        # {
        # \"width\" : 176,
        # \"height\" : 144
        # },
        # {
        # \"width\" : 320,
        # \"height\" : 240
        # },
        # {
        # \"width\" : 352,
        # \"height\" : 272
        # },
        # {
        # \"width\" : 352,
        # \"height\" : 288
        # },
        # {
        # \"width\" : 640,
        # \"height\" : 480
        # }],
        # \"sources\" : [
        # {
        # \"source\" : \"internal\"
        # },
        # {
        # \"source\" : \"external\"
        # }]
        # }
        # }
        camera_snapshot:
            # The /api/camera/snapshot function helps you download images from an internal or
            # external IP camera connected to the intercom. Specify the video source, resolution and
            # other parameters.
            # The function is part of the Camera service and the user must be assigned the Camera
            # Monitoring privilege for authentication if required.
            type: str
            command_2n: camera_snapshot
            enforce_updates: 'true'

            width:
                # Mandatory parameter specifying the horizontal resolution of the JPEG image in pixels
                type: num

            height:
                # Mandatory parameter specifying the vertical resolution of the JPEG image in pixels.
                type: num

            snapshot_file:
                # File path where the snapshot is stored to.
                type: str

            source:
                # Optional parameter defining the video source ( internal – internal camera,
                # external – external IP camera). If the parameter is not included, the default video source included in
                # the Hardware / Camera / Common settings section of the configuration web interface is selected.
                type: str

            time:

            # Optional parameter defining the snapshot time in the intercom memory where time <= 0 … count of
            # seconds to the past, time > 0 … count of seconds from 1.1.1970 (Unix Time). The time values must be
            # within the intercom memory range: <-30, 0> seconds.
            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        display_caps:
            # The /api/display/caps function returns a list of device displays including their
            # properties. Use the function for display detection and resolution.
            # The function is part of the Display service and the user must be assigned the Display
            # Control privilege for authentication if required . The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: display_caps
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"displays\" : [
        # {
        # \"display\" : \"internal\",
        # \"resolution\" : {
        # \"width\" : 320,
        # \"height\" : 240
        # }
        # }]
        # }
        # }
        display_upload_image:
            # The /api/display/image function helps you upload content to be displayed.
            # Note: The function is available only if the standard display function is disabled in the Hardware / Display
            # section of the configuration web interface.
            # The function is part of the Display service and the user must be assigned the Display
            # Control privilege for authentication if required . The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: display_upload_image
            enforce_updates: 'true'

            gif_file:
                # Mandatory parameter file path to a GIF image with display resolution
                type: str

            display:
                # Mandatory display identifier ( internal )
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        display_delete_image:
            # The /api/display/image function helps you delete content from the display.
            # Note: The function is available only if the standard display function is disabled in the Hardware / Display
            # section of the configuration web interface.
            # The function is part of the Display service and the user must be assigned the Display
            # Control privilege for authentication if required . The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: display_delete_image
            enforce_updates: 'true'

            display:
                # Mandatory display identifier ( internal )
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        log_caps:
            # The /api/log/caps function returns a list of supported event types that are recorded
            # in the device. This list is a subset of the full event type list below:
            # The function is part of the Logging service and requires no special user privileges.
            type: str
            command_2n: log_caps
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true,
        # \"result\" : {
        # \"events\" : [
        # \"KeyPressed\",
        # \"KeyReleased\",
        # \"InputChanged\",
        # \"OutputChanged\",
        # \"CardEntered\",
        # \"CallStateChanged\",
        # \"AudioLoopTest\",
        # \"CodeEntered\",
        # \"DeviceState\",
        # \"RegistrationStateChanged\",
        # ...
        # ]
        # }
        # }
        audio_test:
            # The /api/audio/test function launches an automatic test of the intecom built-in
            # microphone and speaker. The test result is logged as an AudioLoopTest event.
            # The function is part of the Audio service and the user must be assigned the
            # Audio Control privilege for authetication if required. The function is only available with
            # the Enhanced Integration and Enhanced Audio licence key.
            type: str
            command_2n: audio_test
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        email_send:
            # The /api/email/send function sends an e-mail to the required address. Make sure
            # that the SMTP service is configured correctly for the device (i.e. correct SMTP server
            # address, login data etc.).
            # The function is part of the Email service and the user must be assigned the Email
            # Control privilege for authentication if required. The function is available with the
            # Enhanced Integration licence key only.
            type: str
            command_2n: email_send
            enforce_updates: 'true'

            to:
                # Mandatory parameter specifying the delivery address.
                type: str

            subject:
                # Mandatory parameter specifying the subject of the message.
                type: str

            body:
                # Optional parameter specifying the contents of the message (including html marks if necessary).
                # If not completed, the message will be delivered without any contents.
                type: str

            picture_count:
                # Optional parameter specifying the count of camera images to be enclosed.
                # If not completed, no images are enclosed. Parameter values: 0-5.
                type: num

            width:
                # Image width in pixel. Optional if picture_count = 0.
                type: num

            height:
                # Image height in pixel. Optional if picture_count = 0.
                type: num

            timespan:
                # Optional parameter specifying the timespan in seconds of the snapshots enclosed to the email.
                # Default value: 0.
                type: num

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        pcap:
            # The /api/pcap function helps download the network interface traffic records (pcap
            # file). You can also use the /api/pcap/restart a /api/pcap/stop functions for
            # network traffic control.
            # The function is part of the System service and the user must be assigned the System
            # Control privilege for authentication if required. The function is available with the
            # Enhanced Integration licence key only
            type: str
            command_2n: pcap
            enforce_updates: 'true'

            pcap_file:
                # Mandatory parameter file path where the pcap is saved to
                type: str

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        pcap_restart:
            # The /api/pcap/restart function deletes all records and restarts the network interface
            # traffic recording.
            # The function is part of the System service and the user must be assigned the System
            # Control privilege for authentication if required. The function is available with the
            # Enhanced Integration licence key only
            type: str
            command_2n: pcap_restart
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'

        # item value example
        # {
        # \"success\" : true
        # }
        pcap_stop:
            # The /api/pcap/stop function stops the network interface traffic recording.
            # The function is part of the System service and the user must be assigned the System
            # Control privilege for authentication if required. The function is available with the
            # Enhanced Integration licence key only
            type: str
            command_2n: pcap_stop
            enforce_updates: 'true'

            execute:
                type: bool
                command_2n: execute
                enforce_updates: 'true'
                # item value example
                # {
                # \"success\" : true
                # }
```
