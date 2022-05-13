# smarthome-slack
Plugin to send push notifications to Slack 

## Configuration
### etc/plugin.yaml single instance example
```yaml
SlackInstance:
    plugin_name: slack
    token: abc/def/ghi # Token for posting to workspace '<your_team>'
```

### etc/plugin.yaml multi instance example
If you want to post to more than one Slack workspace or if you want to use more than one incoming webhook / authentication token, configure this plugin with multiple instances.
```yaml
SlackInstance_1:
    plugin_name: slack
    instance: WorkspaceYourTeam
    token: abc/def/ghi # Token for posting to workspace '<your_team>'

SlackInstance_2:
    plugin_name: slack
    instance: WorkspaceAnotherTeam
    token: jkl/mno/pqr # Token for posting to another workspace '<another_team>'
```

## Usage
To enable posting to Slack you need to create an "incoming webhook" there, which gives you an authorization token.
Open the following URL for your team workspace.
https://<your_team>.slack.com/apps/new/A0F7XDUAZ-incoming-webhooks
Create a new webhook at which you need to select one channel of your workspace.
The created URL contains an API token which authorizes posting to every channel in this workspace.
Afterwards you need to setup your etc/plugin.yaml as described above and insert the webhook token.

To send a notification use the following syntax in your logics with the first parameter being the desired channel:
```python
# Default informational notification to channel #general
sh.SlackInstance.notify('#general', 'Ding Dong: Front door')
# Or use the following to set the default notification type to normal
sh.SlackInstance.notify('#otherChannel', 'Ding Dong: Front door', 'normal')
# Other notification types use warning, danger or good.
sh.SlackInstance.notify('#differentChannel', 'Alarm: Garage door open', 'danger')
```

To learn more on message formatting (e.g. bold, underline, URLs, Emojis, multiline) visit the following link:
https://api.slack.com/docs/message-formatting


For most users a single instance would be sufficient.
If you want to go beyond that and want to send notifications to more than one Slack workspace or if you want to use more than one incoming webhook / authentication token, you need to generate a webhook / token in every Slack workspace.
For each of them you'll need to configure a instace of this plugn in etc/plugin.yaml with different instance names as shown in multi instance example configuration above.
Sending notifications in multi instance example:
```python
# Sending a notification to two workspaces
sh.SlackInstance_1.notify('#general', 'Hello first workspace!')
sh.SlackInstance_2.notify('#general', 'Hello second workspace!')
```
