# Neato/Vorwerk Vacuum Robot


This plugin connects your Neato (https://www.neatorobotics.com/) or Vorwerk Robot with SmarthomeNG.
- Command start, stop, pause, resume cleaning and trigger sendToBase and FindMe mode.
- Read status of your robot

## Configuration

### 1) /smarthome/etc/plugin.yaml

Enable the plugin in plugin.yaml , type in your Neato or Vorwerk credentials and define whether you are using a Neato or Vorwerk robot.


### 2) Authentication

Two different authentication techniques are supported by the plugin: 

a) Authentication via "account email" and account password (applicable for Neato and old Vorwerk API)

```yaml
Neato:
    plugin_name: neato
    account_email: 'your_neato_account_email'
    account_pass: 'your_neato_account_password!'
    robot_vendor: 'neato or vorwerk'
```

b) Oauth2 authentication via "account email" and token (applicable for Vorwerk only, supports the new MyKobold APP interface) 
```yaml
Neato:
    plugin_name: neato
    account_email: 'your_neato_account_email'
    token: 'HEX_ASCII_TOKEN'
    robot_vendor: 'vorwerk'
```

In order to obtain a token, use the plugin's webinterface on the Vorwerk OAuth2 tab.

If you cannot operate the webinterface, do the following steps manually:
 
a) Enable Neato plugin and configure Vorwerk account email address

b) Enable logging at INFO level for neato plugin in logger.yaml

c) Execute plugin function request_oauth2_code. This will request a code from neato to be sent by email to the above address.

d) After reception of the code, execute the plugin function request_oauth2_token(code) with the received code as argument

e) Read the generated ASCII hex token from the logging file

f) Insert the token to the neato plugin section of the plugin.yaml configuration file


### 2) /smarthome/items/robot.yaml

Create an item based on the template below:

```yaml
Neato:
  Name:
    type: str
    neato_attribute: 'name'
    visu_acl: ro
  State:
    type: str
    value: 'offline'
    neato_attribute: 'state'
    visu_acl: ro
  StateAction:
    type: str
    neato_attribute: 'state_action'
    visu_acl: ro
  Command:
    type: num
    neato_attribute: 'command'
    visu_acl: rw
  IsDocked:
    value: False
    type: bool
    neato_attribute: 'is_docked'
    visu_acl: ro
  IsScheduleEnabled:
    value: False
    type: bool
    neato_attribute: 'is_schedule_enabled'
    visu_acl: rw
  IsCharging:
    value: False
    type: bool
    neato_attribute: 'is_charging'
    visu_acl: ro
  ChargePercentage:
    type: num
    neato_attribute: 'charge_percentage'
    visu_acl: ro
  GoToBaseAvailable:
    type: bool
    value: False
    neato_attribute: 'command_goToBaseAvailable'
    visu_acl: ro
  Alert:
    type: str
    neato_attribute: 'alert'
    visu_acl: ro

```

## Examples

Thats it! Now you can start using the plugin within SmartVisu, for example:

#### Get status from robot:
```html
<p>Name: {{ basic.value('RobotName', 'Neato.Robot.Name') }}</p>
/** Get the robots name (str)*/

<p>Cleaning status: {{ basic.value('RobotState', 'Neato.Robot.State') }}</p>
/** Get the robots cleaning status (str) */

<p>Cleaning status action: {{ basic.value('RobotStateAction', 'Neato.Robot.StateAction') }}</p>
/** Get the robots cleaning status action (str). Only when it's busy */

<p>Docking status: {{ basic.value('RobotDockingStatus', 'Neato.Robot.IsDocked') }}</p>
/** Get the robots docking status (bool) */

<p>Battery status: {{ basic.value('RobotBatteryState', 'Neato.Robot.ChargePercentage') }}</p>
/** Get the robots battery charge status (num) */
```

The following cleaning states are currently available:

| Neato.Robot.State |
| ----------------- |
| invalid           |
| idle              |
| busy              |
| paused            |
| error             |

If Neato.Robot.State == 'busy' than you can find the current cleaning activity in Neato.Robot.StateAction.

The following action states are currently available:

| Neato.Robot.StateAction                         |
| ------------------------------------------------|
| 0	Invalid                                   |
| 1	House Cleaning                            |
| 2	Spot Cleaning                             |
| 3	Manual Cleaning                           |
| 4	Docking                                   |
| 5	User Menu Active                          |
| 6	Suspended Cleaning                        |
| 7	Updating                                  |
| 8	Copying Logs                              |
| 9	Recovering Location                       |
| 10	IEC Test                                  | 
| 11	Map cleaning                              |
| 12	Exploring map (creating a persistent map) |
| 13	Acquiring Persistent Map IDs              |
| 14	Creating & Uploading Map                  |
| 15	Suspended Exploration                     |


#### Send commands to the robot:

```html

<p> {{ basic.button('RobotButton_Start', 'Neato.Robot.Command', 'Start', '', '61', 'midi') }} </p>
<p> {{ basic.button('RobotButton_Stop', 'Neato.Robot.Command', 'Stop', '', '62', 'midi') }} </p>
<p> {{ basic.button('RobotButton_Pause', 'Neato.Robot.Command', 'Pause', '', '63', 'midi') }} </p>
<p> {{ basic.button('RobotButton_Resume', 'Neato.Robot.Command', 'Resume', '', '64', 'midi') }} </p>
<p> {{ basic.button('RobotButton_Find', 'Neato.Robot.Command', 'Find', '', '65', 'midi') }}</p>

```

Following commands are currently available:

| Command (num) | Action           |
| ------------- |------------------|
| 61            | Start cleaning   |
| 62            | Stop cleaning    |
| 63            | Pause cleaning   |
| 64            | Resume cleaning  |
| 65            | Find the robot   |
| 66            | Send to base     |
| 67            | Enable schedule  |
| 68            | Disable schedule |



