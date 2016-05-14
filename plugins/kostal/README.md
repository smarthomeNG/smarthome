# KOSTAL

# Requirements

This plugin is designed to retrieve data from a [KOSTAL](http://www.kostal-solar-electric.com/) inverter module (e.g. PICO inverters).

## Supported Hardware

Is currently working with the following KOSTA inverter modules:

  * KOSTAL PIKO 7.0

# Configuration

## plugin.conf

The plugin can be configured like this:

<pre>
[KOSTAL]
   class_name = Kostal
   class_path = plugins.kostal
   ip = 10.10.10.10
#   user = pvserver
#   passwd = pvwr
#   cycle = 300
</pre>

This plugin retrieves data from a KOSTAL inverter module of a solar energy
plant.

The data retrieval is done by establishing a network connection to the 
inverter module and retrieving the status via a HTTP request.

You need to configure the host (or IP) address of the inverter module. Also
the user and password attributes (user, passwd) can be overwritten, but
defaults to the standard credentials.

The cycle parameter defines the update interval and defaults to 300 seconds.

## items.conf

### kostal

This attribute references the information to retrieve by the plugin. The
following list of information can be specified:

  * power_current: The current power of the solar installation
  * power_total: The total amount of generated energy
  * power_day: The amount of generated energy for the current day
  * status: The textual status of the module (off, feeding, ...)
  * string1_volt ... string3_volt: The current voltage of string 1, 2, 3
  * string1_ampere ... string3_ampere: The current ampere of string 1, 2, 3
  * l1_volt ... l3_volt: The current voltage of L 1, 2, 3
  * l1_watt ... l3_watt: The current watt of L 1, 2, 3

### Example

Example configuration which shows the current status and the current, total and
daily power. Additionally it shows the volts and watts for the phases.

<pre>
# items/my.conf
[solar]
    [[status]]
        type = str
        kostal = status
    [[current]]
        type = num
        kostal = power_current
    [[total]]
        type = num
        kostal = power_total
    [[day]]
        type = num
        kostal = power_day
    [[l1v]]
        type = num
        kostal = l1_watt
    [[l1w]]
        type = num
        kostal = l1_watt
    [[l2v]]
        type = num
        kostal = l2_watt
    [[l2w]]
        type = num
        kostal = l2_watt
    [[l3v]]
        type = num
        kostal = l3_watt
    [[l3w]]
        type = num
        kostal = l3_watt
</pre>

## logic.conf

No logic related stuff implemented.

# Methods

No methods provided currently.

