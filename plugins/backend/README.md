# Backend GUI

This plugin delivers information about the current SmartHomeNG installation. Right now it serves as a support tool for helping other users with an installation that does not run properly. Some highlights:

* a list of installed python modules is shown versus the available versions from PyPI
* a list of items and their attributes is shown
* a list of logics and their next execution time
* a list of current schedulers and their next execution time
* direct download of sqlite database (if plugin is used) and smarthome.log
* some information about frequently used daemons like knxd/eibd is included
* supports basic authentication
* multi-language support

There is however only basic protection against unauthorized access or use of the plugin so be careful when enabling it with your network.

Call the backend-webserver: **```http://<ip of your SmartHomeNG server>:8383```**

Support is provided trough the support thread within the smarthomeNG forum: 

[knx-user-forum.de/forum/supportforen/smarthome-py/959964-support-thread-f%C3%BCr-das-backend-plugin](https://knx-user-forum.de/forum/supportforen/smarthome-py/959964-support-thread-für-das-backend-plugin)


# Requirements
This plugin is running under Python >= 3.4 as well as the libs cherrypy and jinja2. You can install them with:
<pre>
(sudo apt-get install python-cherrypy)
sudo pip3 install cherrypy
(sudo apt-get install python-jinja2)
sudo pip3 install jinja2
</pre>
And please pay attention that the libs are installed for Python3 and not an older Python 2.7 that is probably installed on your system.

The log level filter in the log file view will only work with "%(asctime)s %(levelname)-8s" in the beginning of the configured format! Dateformat needs to be datefmt: '%Y-%m-%d %H:%M:%S'

## Running this plugin under Python 3.2
If you really need to run this plugin under Python 3.2 you may not use the newest version of all packages. The packages **Jinja2** and **MarkupSafe** have dropped support for Python 3.2. Make sure to install the following older versions into your Phython3.2 environment, as newer versions are not compatible with Python 3.2 any more:

<pre>
- Jinja2	v2.6
- MarkupSafe	v0.15
</pre>

.

To support visualization, the visu_websocket plugin has to be used. It has to be PLUGIN_VERSION >= "1.1.2".


# Configuration

## plugin.conf
<pre>
[BackendServer]
	class_name = BackendServer
	class_path = plugins.backend
	#ip = xxx.xxx.xxx.xxx
	#port = 8383
	#updates_allowed = True
	#threads = 8
	#user = admin
	#password = very_secure_password
	#hashed_password = 1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d
	#language = en
	#developer_mode = on
	#pypi_timeout = 5
</pre>

### ip
IP address to start the backend server. Usually it doesnot need to be configured.

If not configured the standard ip address of the system is used. If you like to restrict the usage of the BackendServer to the system itself (the browser ist running on the smarthomeNG system itself), you can configure the ip to 127.0.0.1. In this case, the BackendServer is only available through the localhost address.

### port
The port on which the backend server listens. By default port **`8383`** is used.

### updates_allowed

By default, the backend server allows updates to the running smarthomeNG instance. For instance, it is possible to trigger or to reload a logic. Setting **`updates_allowed`** to **`False`**, you can disable these features.

###  threads

Number of worker threads to start by cherrypy (default 8, which may be too much for slow CPUs)

### user (optional)
The user for basic authentication. If left out, the user name is set as "admin"

### password (optional)
The plaintext password for basic authentication. If you want to store your password as md5 hash, use 'md5password' instead. If both "password" and "md5password" are left out, basic authentication is disabled.

### hashed_password (optional)
The password for basic authentication as hash value. Can be used instead of "password" if you do not want a plaintext password in your config file. If both "password" and "hashed_password" are left out, basic authentication is disabled. Currently hashed_password is the SHA-512 hash value of the password. To create the hash for your password, you can use function "Create password hash" on page "Services" in the backend.

### language (optional)
You can specify a language to use for the plugin. Besides the standard language (german) which is used, if this parameter isn't set, you can specify english (for the time being). The language is specified by  **`en`**

### developer_mode (optional)
You may specify develper_mode = on, if you are developiing within the backend plugin. At the moment, the only thing that changes is an additional button **``relaod translation``** on the services page

### pypi_timeout (optional)
Timeout for PyPI accessibility check (seconds). PyPI is queried on page "Systeminfo" to compare installed python module versions with current versions if accessible. If you receive the message "PyPI inaccessible" on systems with internet access you may increase the value. On systems where PyPI can not be reached (no/restricted internet access) you may set the timeout to 0 which disables the PyPI queries.
