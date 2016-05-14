# Whatsapp - Yowsup 2

# Requirements/Description

This Plugin uses Yowsup 2 as basis: https://github.com/tgalal/yowsup
You have to install Yowsup 2 from May 6, 2015 or newer on your system before using this plugin. Yowsup 2 is not delivered with this plugin!
Please ensure that the latest Yowsup 2 version is in your pythonpath and used by this plugin.

To use this Plugin you need:
* Free PhoneNumber
* PhoneNumber registered on Whatsapp. see: http://www.forum-raspberrypi.de/Thread-tutorial-mit-dem-pi-ueber-whatsapp-nachrichten-etc-senden

# Known Bugs
Reconnect is on connection loss is buggy.

# Configuration

## plugin.conf

<pre>
[whatsapp]
	class_name = Whatsapp
	class_path = plugins.whatsapp
	account = '4917912345678'
	password = 'abcdefghi='
	trusted = 4917912345678 4917912345679
	logic = 'Logi_Whatsapp'

</pre>

Description of the attributes:

* account: Registered Whatsapp PhoneNumber including country code, without '+' or '00' eg. 417912345678 (Switzerland/Swisscom) (Yowsup:phone)
* password: Password to use for login. Base64 encoded. (Yowsup:password)
* trusted: Space separated List with PhoneNumbers you Trust
* logic: Logic that is called when msg from trusted number is received

## logic.conf
To receive messages you have to add the logic defined in plugin.conf. It will be called from the Plugin.
<pre>
[Logi_Whatsapp]
   filename = whatsapp.py 
</pre>

In the context of the KNX plugin the trigger dictionary consists of the following elements:
trigger['value']    The Message received
trigger['source']   The Sender 

# Functions
* sending a Message

<pre>
* sh.whatsapp("Message to send", "497912345678") #Will send to a explicite PhoneNumber.
</pre>
If no phoneNumeber is set, it will take the first number from the trusted numbers


## Examples for whatsapp.py

msg = trigger['value']
absender = trigger['source']

if msg == "athome?":
    answer = "yes" if sh.myitem.athome() else "no"
    sh.whatsapp(answer)

