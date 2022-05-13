# plex

Plugin to send push notifications to Plex clients like RasPlex.
I only have tested the plugin with RasPlex, the notification module should also be compatible with OpenElec, XBMC / Kodi Frodo and higher.

## Installation

```
cd smarthome.py directory
cd plugins
git clone https://github.com/rthill/plex.git
```

## Configuration

### plugin.yaml

```yaml
plex:
    class_name: Plex
    class_path: plugins.plex
    displaytime: 6500 # Default is 6000 (6 sec)
```

### items.yaml
```
mm:

    gf:

        living:

            plex:
                type: foo
                plex_host: rasplex.plugin.lu
                plex_port: 3005    # Optional: default is 3005
```

## Usage

To send notifications use the following syntax in your logics:

```python
# Default informational notification
sh.plex.notify('Door', 'Ding Dong\nFront door')
sh.plex.notify('Door', 'Ding Dong\nFront door', 'info')

# Warning notification
sh.plex.notify('Door', 'Garage door is open for 1 hour', 'warning')

# Error notification
sh.plex.notify('Logic XYZ', 'Execution failed ....', 'error')
```
