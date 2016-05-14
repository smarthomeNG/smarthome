# Notify My Android

# Requirements

NMA API-KEY

get it from http://www.notifymyandroid.com/ for free

# Configuration

## plugin.conf

<pre>
[nma]
    class_name = NMA
    class_path = plugins.nma
#    apikey = <your-api-key>
</pre>

Description of the attributes:

* __apikey__: set api-key globally so you do not have to set it in the function calls

# Functions

Because there is only one function you could access it directly by the object. 

<pre>
sh.nma('Intrusion', 'Living room window broken!')
</pre>

This function takes several arguments:

* __event__: Event (up to 1000 chars)
* __description__: Text describing the event in detail (up to 1000 chars)
* __priority__: Ranging from -2 (Very low) to 2 (Emergency) - not used by now! 
* __url__: URL to be send with the notification (up to 2000 chars)
* __apikey__: API-KEY used for this request - not necessary if global 'apikey' is set
* __application__: Name of the application (default: 'SmartHome')
 
# Examples
<pre>
sh.nma('Intrusion', 'Living room window broken', 2, 'http://yourvisu.com/')
sh.nma('Tumbler', 'finished', apikey='<your-api-key>')
</pre>
