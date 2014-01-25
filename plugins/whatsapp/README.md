# Whatsapp

# Requirements/Description

This Plugin use this Source as basis: https://github.com/tgalal/yowsup

To use this Plugin you need:
* Free PhoneNumber
* PhoneNumber registered on Whatsapp. see: http://www.forum-raspberrypi.de/Thread-tutorial-mit-dem-pi-ueber-whatsapp-nachrichten-etc-senden

# Configuration

## plugin.conf

<pre>
[whatsapp]
	class_name = Whatsapp
	class_path = plugins.whatsapp
	account = '417912345678'
	password = 'abcdefghi...'
	trusted = 417912345678 | 417912345678 
	logic = 'Logi_Whatsapp'
</pre>

Description of the attributes:

* account: Registered Whatsapp PhoneNumber including country code, without '+' or '00' eg. 417912345678 (Switzerland/Swisscom) (Yowsup:phone)
* password: Password to use for login. (Yowsup:password)
* trusted: Pipe(|)-separated List with PhoneNumbers you Trust
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
* sending a Picture

<pre>
* sh.whatsapp("Message to send", "417912345678") #Will send to a explicite PhoneNumber.
* sh.whatsapp("Message to send")  #Will send to the sender.
* sh.whatsapp.sendPicture(url, username, password, phoneNumber)
** variables: username, password, phoneNumber are optional
</pre>
If no phoneNumeber is set, it will take the first number from the trusted numbers


## Examples for whatsapp.py

msg = trigger['value']
absender = trigger['source']

if msg == "Zuhause?":
    antwort = "Ja" if sh.presenz.anwesend() else "Nein"
    sh.whatsapp(antwort)

