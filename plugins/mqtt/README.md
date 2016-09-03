# MQTT

Requirements
============
This plugin needs the following MQTT python modules:

   * [paho-mqtt](https://pypi.python.org/pypi/paho-mqtt)

<pre>In Linux systems can use: pip install paho-mqtt </pre>

Configuration
=============

plugin.conf
-----------
<pre>
[mqtt]
    class_name = Mqtt
    class_path = plugins.mqtt
    host = 'hostexample.lan'
    port = 1883
    
</pre>


items.conf
--------------

With this attribute you could specify channels to send and receive info.

# Example
<pre>
[alarm_in]
	# messages coming from the alarm panel
        mqtt_topic_in = "/alarm/out"
        type = foo
        name = alarm_test_mqtt_in

[alarm_out]
	# messages to send to the alarm panel
        mqtt_topic_out = "/alarm/in"
        type = foo
        name = alarm_test_mqtt_out
</pre>

Now you could simply use:
<pre>sh.alarm_out(arm)</pre> to send a mqtt message via the topic /alarm/out.
<pre>sh.alarm_in()</pre> to see messages coming from mqtt bus via topic /alarm/in

logic.conf 
-------------

[Alarm]
    watch_item = alarm_in # monitor for changes
