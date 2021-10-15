==========================
Release 1.x - tt. mmm 2021
==========================

Es gibt eine Menge neuer Features im Core von SmartHomeNG und den Plugins.

.. note::

    Diese Release Notes sind ein Arbeitsstand.

     - Berücksichtigt sind Commits im smarthome Repository bis incl. 8. Oktober 2021
       (...)
     - Berücksichtigt sind Commits im plugins Repository bis incl. 6. Oktober 2021
       (...)


Überblick
=========

Dieses ist neues Release für SmartHomeNG. Die Änderungen gegenüber dem Release v1.8.x sind im
folgenden in diesen Release Notes beschrieben.


Unterstützte Python Versionen
-----------------------------

Die älteste offiziell unterstützte Python Version für SmartHomeNG Release 1.8 ist Python 3.6.
(Siehe auch *Hard- u. Software Anforderungen* im Abschnitt *Installation* zu unterstützten Python Versionen)

..
    Das bedeutet nicht unbedingt, dass SmartHomeNG ab Release 1.8 nicht mehr unter älteren Python Versionen läuft,
    sondern das SmartHomeNG nicht mehr mit älteren Python Versionen getestet wird und das gemeldete Fehler mit älteren
    Python Versionen nicht mehr zu Buxfixen führen.

    Es werden jedoch zunehmend Features eingesetzt, die erst ab Python 3.6 zur Verfügung stehen.
    So ist Python 3.6 die minimale Vorraussetzung zur Nutzung des neuen Websocket Moduls.


Minimum Python Version
----------------------

Die absolute Minimum Python Version in der SmartHomeNG startet wurde auf v3.6 angehoben, da Python 3.5 im
September 2020 End-of-Life (End of security fixes) gegangen ist. Bei einer Neuinstallation wird jedoch empfohlen
auf einer der neueren Python Versionen (3.7 oder 3.8) aufzusetzen.

.. important::

   Mit dem kommenden Release 1.9 werden die unterstützten Python Versionen
   :doc:`(wie hier beschrieben) </installation/anforderungen>` auf **Python 3.7, 3.8, 3.9** angehoben. Python 3.6
   hatte bereits eine Reihe sehr interessanter Features und Verbesserungen gebracht, die dann in SmartHomeNG genutzt
   werden können.

   Sollten solche neuen Features in den Core Einzug halten, wird die **Absolute Minimum Python Version** auf 3.6
   angehoben werden. Sollten die Features nur in Plugins genutzt werden, so können nur solche Plugins nicht genutzt
   werden, wenn eine ältere Python Version als 3.6 eingesetzt wird.


Änderungen am Core
==================

Bugfixes in the CORE
--------------------

* Fixes in lib.network
* Fixes in lib.utils

* Fixes in modules.mqtt
* Fixes in modules.websocket

* modules.websocket: Bugfix for smartVISU payload protocol (command 'log')
* create var/log directory prior recording output from pip


Updates in the CORE
-------------------

* Removed references to lib.connection
* etc.logging.yaml.default: Changes to new logging handlers
* move crontab in lib.triggertimes, extend syntax for crontabs

* Items:

  * ...

* Logics:

  * ...

* lib.backup:

  * Added new struct files of ../etc directory to configuration backup
  * Added *.pem to backup of certificate files

lib.env.location:

  * Added lat, lon and elev settings from smarthome.yaml to items

* lib.item:

  * Added loading of structs from multiple files (etc/struct_xyz.yaml) in addition to loading from etc/struct.yaml
  * Extended functionallity for item logging (incl. shngadmin and documentation)

* lib.network:

  * first udp server implementation
  * Removed setting of loglevel for logger lib.network (should be defined in etc/logging.yaml)

* lib.smarthome:

  * Added loglevel NOTICE

* lib.userfunctions

  * New library, that implements userfuncations for eval-statements and logics

* Modules:

  * admin:

    * Display of structs in shngadmin is now sorted and grouped by plugin
    * Randomized calls to find blog articles on smarthomeng.de

  * http:

    * update chartjs to 2.9.4
    * added Datatables Javascript v1.11.0 to allow table sorting in WebIFs, updated documentation
    * updated bootstrap to 4.6.0
    * updated bootstrap datepicker to 1.9.0
    * updated Font Awesome to 5.15.4
    * updated jquery to 3.6.0
    * updated popper.js to 2.10.1

  * websocket:

    * Changes to memory logging in core

* Plugins:

  * ...

* tests:

  * mock.core: Read core version from bin.shngversion.py
  * migrated tests to Travis-CI.com, updated Readme


Änderungen bei Plugins
======================

New Plugins
-----------

For details of the changes of the individual plugins, please refer to the documentation of the respective plugin.

* avm_smarthome: AVM smarthome plugin for DECT sockes, smart radiator control DECT301 and Comet DECT and DECT
  smarthome sensors based on HTTP GET Request
* homeconnect: usage of the BSH/Siemens HomeConnect interface with oauth2
* husky: plugin to control Husqvarna automower
* sma_mb: this plug-in reads the current values of an SMA inverter via SMA Speedwire fieldbus/Modbus



Plugin Updates
--------------

* asterix:

  * adjusted plugin to lib.network

* avm:

  * handle callmonitor reconnect
  * avoid error message on requested shutdown
  * moved webif to seperate file
  * fixed rare error in function _update_home_automation
  * catching exceptions when Ethernet is temporary unavailable

* bsblan:

  * revised README
  * compatibility check for BSB-LAN Version 2.x
  * adjusted link to icon in readme.md

* casambi:

  * Catch socket errors leading to unintentional termination of EventHandlerThread
  * deleted readme and improved user_doc
  * added automatic sessionID request, e.g. after Casambi API key validity has been extended
  * improved webinterface
  * added english translation for webinterface
  * added python websocket to plugin requirements
  * fixed requirement websocket-client
  * added tunable white (CCT) support
  * added extended debugging for CCT commands
  * debugging setups with more than one Casambi network
  * removed unjustified error/warning messages
  * fixed status decode error
  * added backend online status parsing to item
  * fixed unknown variable error in debug message

* cli:

  * adjustments to new network classes
  * fixed error - self.alive
  * added 'logl' (log-list) command
  * updated output of command 'logd'
  * updated to conform with changes to memory logging in core

* comfoair:

  * removed lib.connection references for cleanup

* darksky:

  * added URL for data retrieval to webif
  * switched default to "ca" to have wind in kmh
  * added some more attributes to webif
  * set to deprecated for next plugin release, API ends 2021

* database:

  * updated to use newest version of datepicker

* dlms:

  * added parameter to allow listen only mode
  * extend webinterface with list of common obis codes

* ebus:

  * removed lib.connection references for cleanup

* ecmd:

  * removed lib.connection references for cleanup

* enocean:

  * added debug infos for powermeter devices
  * changed to new is_alive() syntax for python 3.9
  * updated to use newest version of datepicker
  * removed datepicker includes, which are no longer necessary for this plugin

* garminconnect:

  * updated to use newest version of datepicker

* gpio:

  * fix local variable 'err' referenced before assignment in line 126
  * implement datatables JS in webif
  * rename webif tables correctly
  * improve error handling on startup and bump version to 1.5.1

* hue:

  * Small BugFix in UpdateGoupItems

* husky:

  * added error/debug message if model, id or name cannot be extracted from json response
  * added logger to Mower class
  * degraded error message on missing model type to debug level

* ical:

  * adapted to new lib.network
  * made cycle to a class attribute (self._cycle)

* jsonread:

  * now has a webinterface
  * some minor text changes to metadata (plugin.yaml)
  * remove old readme.md
  * corrected plugin.yaml (it was not a valid yaml file any more)

* knx:

  * adjusted plugin to lib.network
  * added DPT 251.600 RGBW
  * fix webinterface fix mixup

* kodi:

  * make favourites type dict instead of str

* mailrcv: catch exception when trying to close imap even if it's not possible

* memlog:

  * updated to conform with changes to memory logging in core

* mpd:

  * adjusted plugin to lib.network

* mqtt:

  * updated to use newest version of datepicker

* neato:

  * added new function start_robot to enable single room cleaning; added new function get_map_boundaries to request
    available map boundaries (rooms) for a given map; added new function dismiss_current_alert to reset current alerts
  * fix for clean_room command
  * bugfix in metadata (plugin-function definition hat indentation error)
  * added option to clear errors/alarms in neato/vorwerk backend via plugin's webif
  * added english translation for webinterface
  * deactivate SSL verify
  * added return values for plugin commands
  * added function list available rooms to plugin webif
  * improved map cleaning control

* network:

  * adapted plugin to lib.network
  * improved plugin parameter handling
  * fixed starting server only on run()
  * adjusted logging

* nuki:

  * fixed get_local_ipv4_address handling

* nut:

  * catching exception if network is not available
  * added UPS via Synology disk station example to readme
  * fixed error occurring after exception of type "network not available"

* onewire:

  * improve error handling

* openweathermap:

  * corrected user_doc (replaced all references to darksky plugin)

* raumfeld

  * removed lib.connection references for cleanup
  * some cleanup

* raumfeld_ng:

  * Bugfix in poll_device (get_sh())
  * Added get_mediainfo to valid_list of rf_attr item attribute

* resol:

  * Catch wrong message sizes
  * fixed scheduler stop on plugin exit
  * robustness measures when Ethernet is temporary not available

* robonect:

  * corrected datatype for unix timestamp error_unix
  * extended by some MQTT commands
  * changed indent of mode item
  * changed "and not" to "or"
  * added keychecks to avoid exceptions
  * added buttons in webif to switch modes
  * don't try to iterate error list in case robonect has no wifi connection (error list is None then)
  * caching full error list
  * added mode to webservices set for automower (helps only, if webservices plugin is used)
  * added check for mqtt mode

* russound:

  * adjusted plugin to lib.network

* shelly:

  * add support for Shelly H&T

* simulation:

  * fix parameters

* smartvisu:

  * added parameter create_masteritem_file
  * adjusted web interface
  * improve descriptions for widget names and blocks

* sml:

  * removed lib.connection references for cleanup

* smlx:

  * changed from readme to user_doc docu, provide a requirements.txt
  * removed lib.connection references for cleanup

* snmp:

  * functional update of plugin incl enhancement of WebIF

* sonos:

  * added plugin webinterface
  * added name for SoCo EventServerThread
  * catching rare exception that could occur during automatic IP detection and invalid network connectivity
  * adapted behavior of play_snippet if stop() functionality is currently not supported by the respective speaker
  * upgrade to SoCo 0.22 framework
  * display number of online speakers on Webinterface

* speech:

  * adjusted plugin to lib.network

* squeezebox:

  * change struct wipecache to str as the value might also be a string like "queue"

* stateengine:

  * moved web interface to a separate file
  * change logging: general log is plugins.stateengine and se_item logs are logged to "stateengine" (without plugins. prefix)
  * improve log handling
  * handle problem when SE item has name, bump version to 1.9.2
  * improve logging and source for item update
  * fix docu example for south and se_use
  * lower case log directory
  * optional offset for sun_tracking function
  * moved webif to external file
  * new logger names, fix items having a name
  * corrected intentation in user_doc/13_sonstiges.rst
  * add offset and value for open lamella value parameters to improve sun_tracking function
  * replace sh.tools.dt2ts() by timestamp() for evaluating the start_time of the suspend state
  * change web visu - condition rectangle now has dynamic width
  * better sun_tracking offset handling
  * correct webif colors and conditionlist if no conditionsets given

* telegram:

  * add new attribut telegram_condition to suppress multiple messages upon update

* unifi:

  * moved dependency from lib.network to lib.utils

* uzsu:

  * outsource webif and fix webinterface problem with showing the whole dictionary when a rule contains a "<"
  * update webif to use datatables JS

* viessmann:

  * fixes webif includes
  * fix cyclic due calculation

* visu_websocket:

  * updated to conform with changes to memory logging in core
  * fix parameters in widget call

* webservices:

  * moveed and translated readme.md documentation to user_doc.rst
  * remove readme.md, create user_doc.rst, use sphinx-tabs

* withings_health:

  * updated to newest version of withings-api
  * moved webif to seperate file

* wol:

  * now has a web interface with items and interactive wol

* xiaomi_vac:

  * use datatables js in webif
  * fix problem with newer miio module (>=0.5.8) that doesn't accept return_list argument for clean_details method
  * Bump version to 1.1.2

* xmpp:

  * Try to reconnect when loosing connection


Outdated Plugins
----------------

The following plugins were already marked in version v1.6 as *deprecated*. This means that the plugins
are still working, but are not developed further anymore and are removed from the release of SmartHomeNG
in the next release. User of these plugins should switch to corresponding succeeding plugins.

* System Plugins

  * sqlite - switch to the **database** plugin
  * sqlite_visu2_8 - switch to the **database** plugin

* Gateway Plugins

  * tellstick - classic Plugin, not used according to survey in knx-user-forum

* Interface Plugins

  * netio230b - classic plugin, not used according to survey in knx-user-forum
  * smawb - classic plugin, not used according to survey in knx-user-forum

* Web Plugins

  * alexa - switch to the **alexa4p3** plugin
  * boxcar - classic Plugin, not used according to survey in knx-user-forum
  * mail - switch to the **mailsend** and **mailrcv** plugin
  * openenergymonitor - classic plugin, not used according to survey in knx-user-forum
  * wunderground - the free API is not provided anymore by Wunderground


The following plugins are marked as *deprecated* with SmartHomeNG v1.7, because neither user nor tester have been found:

* Gateway Plugins

  * ecmd
  * elro
  * iaqstick
  * snom
  * tellstick

* Interface Plugins

  * easymeter
  * netio230b
  * smawb
  * vr100

* Web Plugins

  * boxcar
  * nma

Moreover, the previous mqtt plugin was renamed to mqtt1 and marked as *deprecated*, because the new mqtt
plugin takes over the functionality. This plugin is based on the mqtt module and the recent core.


Retired Plugins
---------------

The following plugins have been retired. They had been deprecated in one of the preceding releases of SmartHomeNG.
They have been removed from the plugins repository, but they can still be found on github. Now they reside in
the plugin_archive repository from where they can be downloaded if they are still needed.

* ...


Weitere Änderungen
==================

Tools
-----

* ...


Documentation
-------------

* Changed Requirements for documentation build, added tab extension to sphinx, introduced MyST
* Documentation build should now run under Windows

