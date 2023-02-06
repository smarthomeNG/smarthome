============================
Release 1.x.x - tt. mmm 2023
============================

Dieses Release ist ein Wartungs-Release. Außer Bugfixes gibt es einige neue Features im Core von SmartHomeNG,
sowie einige neue Plugins.

.. only: comment

    Dieses Release ist ein Feature-Release. Es gibt eine Menge neuer Features im Core von SmartHomeNG und den Plugins.


.. note::

    Diese Release Notes sind ein Arbeitsstand.

     - Berücksichtigt sind Commits im smarthome Repository bis incl. 5. Feb 2023
       (check_plugin.py:)
     - Berücksichtigt sind Commits im plugins Repository bis incl. 5. Feb 2023
       (Merge pull request #666 from ivan73/develop)


Überblick
=========

Dieses ist neues Release für SmartHomeNG. Die Änderungen gegenüber dem Release v1.9.3 sind im
folgenden in diesen Release Notes beschrieben.


Minimum Python Version
----------------------

Die absolute Minimum Python Version ist in der Dokumentation unter
:ref:`Hard- u. Software Anforderungen <python_versionen>` im Abschnitt **Python Versionen** dokumentiert.

Für das SmartHomeNG Release 1.10 wird die absolute Minimum Python Version evtl. auf **Python 3.8** angehoben.

Bei einer Neuinstallation wird jedoch empfohlen auf einer der neueren Python Versionen (3.9 oder 3.10) aufzusetzen.


Unterstützte Python Versionen
-----------------------------

Die älteste offiziell unterstützte Python Version für SmartHomeNG Release 1.9.x ist **Python 3.7**.
Automatisierte Tests von SmartHomeNG werden nur in den unterstützten Python Versionen durchgeführt.
(Siehe auch :ref:`Hard- u. Software Anforderungen <python_versionen>` im Abschnitt **Installation**
zu unterstützten Python Versionen)

|

Änderungen am Core
==================

Bugfixes in the CORE
--------------------

* ...


Updates in the CORE
-------------------

* Added Python 3.11 to unit tests

* Configuration:

  * logging.yaml.default: Modified LEVEL for plugins: to NOTICE to reflect the ability of plugins to log NOTICEs

* Items:

  * ...

* Logics:

  * ...

* Libs:

  * lib-daemon:

    * Fix for issue #498 - Error on restarting if SmartHomeNG is not running

  * lib.metadata:

    * Moved definition of global plugin parameter 'instance' from shngadmin to lib.metadata
    * Implemented global plugin parameter 'webif_pagelength' (takes definition from parameter with same name in module.http)

  * lib.model.smartplugin:

    * Preparing SmartPlugin for editable items
    * Minor fixes
    * Fix to create local _plg_item_dict and _item_lookup_dict for each plugin (that calls super().__init__)
    * Adjusted core version to 1.9.3.3
    * Adjust add_item functionality
    * add_item(): Updating parameter
    * add_item(): Prevent default parameters from being changed in method
    * Added SmartPlugin doc (to temporary location at lib.model)
    * add_item() corrected, get_device_commands() added and get_items() renamed to get_item_list()
    * Changed 'device_command' to 'mapping'
    * added get_item_mapping()
    * bumped core version to 1.9.3.4

  * lib.network:

    * Catch (ignore) errors if socket is no longer connected on shutdown

  * lib.plugin:

    * Implemented extended logging levels (NOTICE, DBGHIGH, DBGMED, DBGLOW) for plugins too

  * lib.scheduler:

    * Catch more exceptions outside scheduler to prevent thread end

  * lib.shpypi:

    * Bugfix

  * lib.smarthome:

    * Added reload_translations() to smarthome object to enable reload of translations during runtime through
      eval syntax-checker (evaluate: sh.reload_translations())

  * lib.translation:

    * Enhanced translations to accept module specific translations (for module/http)


* Modules:

  * admin:

    * Fix for reading of logfiles if folder contains files without extension .log
    * Updated module to reflect new url of documentation and allow access to documentation of defelop branch
    * Updated shngAdmin to v0.6.1
    * Moved definition of global plugin parameter 'instance' from shngadmin to lib.metadata

  * http:

    * Datatables: put responsive hide/show child into separate first column to avoid conflicts with truncate
      functionality in first column. Be aware: a new th/td html element needs to be put into all datatables!
    * Made top row/table responsive using javascript
    * Margins for autorefresh elements
    * Make headtable responsive - calculate table min-width automatically if not provided manually
    * Improve table td widths
    * Implement webif_pagelength to globally define standard page length of
      datatables (set to "auto fit to page height by default)
    * Implement option to disable buttons in header
    * Throw console warning if first column has some content (it should be empty!)
    * Make web interfaces more responsive (width of top table, height of header) - updates
    * Bump version to 1.7.0 (as lots of changes were made ;))
    * Show auto refresh options only if update_interval is defined
    * Avoid errors and warnings if auto refresh options are not shown as well as when table has no data
    * Add some more date/time formats for correct sorting
    * Fix header min-width calculation
    * Fix and improve responsive header
    * Webinterfaces: Bug fix for reload-button
    * Webinterfaces: Improved datatable implementation (fix responsive issues on tab load/change, include <div> above datatable in resize calculation)
    * Webinterfaces: Fix resize calculation.. consider all divs with class mb-2 for resize
    * Webinterfaces: Instant update table refresh if checkbox for autoupdate is activated

  * mqtt:

    * Fixed a runtime error "dictionary changed size during iteration"



* Plugins:

  * avdevice:

    * Fix web interface to work with newest datatables changes

  * avm:

    * Minor clean-up for user_doc and metadata

  * beolink:

    * Bugfix in webinterface

  * casambi:

    * Fixed switch on/off state readback due to API or firmware change
    * Added handling for networkLog events from backend as debug outputs
    * Separated WebIf into separate file
    * Cleaned-up user_doc
    * Added changelog to user_doc

  * cli:

    * Adjust web interface
    * Updates to documentation

  * database:

    * Include webif_pagelength from module.yaml, move column classes to dt init function
    * Minor webif fixes and improvements
    * Bump to v1.6.4
    * Simplify and improve web interface
    * Added parameter to set a default maxage for items w/o individual one
    * Optimized remove of log entries older as maxage (extreme speed increase)
    * Reimplemented cleanup (removal of orphans) to be able to run parallel to normal operation
    * Corrected download filename for csv dump
    * Implemented sql dump for sqlite3 databases
    * Bumped version to 1.6.5
    * Added orphan-tab to web interface; enhanced/fixed ude of http-module translations;
    * Bumped version to 1.6.7
    * Code cleanup
    * Updated user dorumentation
    * Bumped version to 1.6.8
    * Implemented separate db connection for maintenance (orphan handling) to fix problems with mysql driver (whiwch allows only one cursor per connection)
    * Fix showing of orphaned items if logcount is disabled.
    * Minor adjustments in metadata and documentation
    * Adjusted a log message

  * dlms:

    * Add logo to user_doc

  * enocean:

    * Separated WebIf from main file
    * New user_doc

  * executor:

    * Remove eval capability, add script listbox, load, save and delete
    * Enhancement - autocomplete for codemirror

  * gpio:

    * Fix minor typos, add user doc, implement webif_pagelength and correct automatic page length on browser window resize
    * Adjust webif_pagelength handling

  * helios:

    * Changes to Helios Modbus RTU plugin (metadata only)

  * helios_tcp:

    * Fixes to work with newer pymodbus versions

  * homeconnect:

    * Clean-up for code and metadata

  * hue2:

    * Implemented for lights: read from bridge für items with function 'dict'
    * Added Modell ID to web interface
    * bumped version to 2.2.2
    * Added more verbose log messages for deCONZ software bridge
    * Added function 'modify_scene'
    * Bumped version to 2.2.3
    * Incorporated fixes/additions from pr #667 for bridge discovery, typo for "hue_refence_light_id"
    * Implementation On-State retrieval for groups through parsing groups "any_on" state
    * Bump version to 2.2.3
    * Added handling for sensors and a couple of hue2_functions for sensors
    * Bump to v2.3.0
    * Added reading of some config parameters for sensors
    * Removed some logging

  * husky2:

    * Updated refresh of token

  * ical:

    * Fixed decoding of calendar events that have the same identifiers, e.g. happens if single
      events of a calendar series are rescheduled once.
    * Minor adaptions in user_doc

  * influxdb2:

    * Updates to documentation

  * join:

    * Added say and language parameters, see issue #673

  * jsonread:

    * Adjusted requirements.txt

  * knx:

    * Improve structure (introduce globals, put webif in separate init file)
    * Introduce webif_pagelength and improve web interface
    * Improve web interface
    * Fix values being None for plugin with instance defined
    * Adjust webif_pagelength handling, first preparation for automatic data update in webif

  * kostalmodbus:

    * Fixes to work with new version of pymodbus and add registers includes #658 and adds missing registeres for KSEM and Kostal inverters
    * Fixes to work with newer pymodbus versions

  * ksemmodbus:

    * Fixes to work with new version of pymodbus and add registers includes #658 and adds missing registeres for KSEM and Kostal inverters
    * Fixes to work with newer pymodbus versions

  * Modbus_tcp:

    * Fixes to work with newer pymodbus versions

  * mqtt:

    * Update webif_pagelength implementation, small webif adjustments
    * Adjust webif_pagelength handling, minor fixes in user_doc and webif

  * neato:

    * Log only one error if robot is not reachable via backend
    * Seperated WebInterface into separate file
    * Cleaned-up user_doc

  * network:

    * Minor adaptations in user_doc

  * onewire:

    * Several enhancements and fixes
    * Vastly extended webinterface
    * Uses functionallity of SmartPlugin from core 1.9.3.3
    * Bumped version to 1.9.0
    * Documentation updates
    * Implemented auto refresh for the webinterface
    * Added plugin parameter 'warn_after'
    * Disabled reload button in web interface (the web interface now does a complete auto update for all data)
    * Clean-up for user_doc and metadata
    * Streamlined handling of webif_pagelength
    * Changed to use new SmartPlugin (core v1.9.3.4)
    * Bumped version to 1.9.1

  * openweathermap:

    * Update Error-Handling mechanism and set version to 1.8.6
    * Improve error handling
    * Made API version configurable. Recently registered new users shall use API version 3.0 instead of version 2.5 which will run out
    * Degraded subsequent error messages following login errors to debug level to avoid spamming of the error log file.
    * Partly reverted API version configuration: Make only the OnceCall API configurable to 2.5 or 3.0, all other APIs(pollution, weather etc.) remain at version 2.5
    * Clean-up for user_doc and metadata

  * philips_tv:

    * Separated WebIf
    * Cleaned-up user_doc
    * Mark plugin as ready
    * Fixed translation in locale.yaml

  * pluggit:

    * Fixes to work with newer pymodbus versions

  * resol:

    * Catched socket timeout exception which occurs if ethernet is temporarily not available.
    * Extended user_doc

  * rtr2:

    * rtr2: v2.1.0 fixes the configuration of Kp and Ki for individual rtrs using the rtr2_controller_settings item attribute
    * Added english descriptions vor plugin parameters
    * Added a section to user_doc.rst from PR #648
    * Added 'cache: True' to item stellwert' in struct to prevent mis-regulations when restarting SmartHomeNG
    * Implemented autoupdate for webinterface
    * Bumped version to 2.2.0
    * Disabled reload button in web interface (the web interface now does a complete auto update for all data)
    * Added plugin-logo to user_doc.rst
    * Changed default values in metadata

  * sma_mb:

    * Fixes to work with newer pymodbus versions

  * smartvisu:

    * Updates to documentation

  * smlx:

    * Add files via upload

  * solarforecast:

    * Catch error, if solarforecast webservice is temporarily not reachable
    * Separated WebIf from main file
    * Cleaned-up user_doc and metadata

  * sonos:

    * Fix for mute does not work for coupled speakers. -> Fixed by making mute a group command.
    * Updated underlying SoCo framework to version 29.0, which amongst others fixes exception in unsubscribe function.
      Catched pipe error that could occur in play_snippet for local sound files.
    * Added play_sharelink command (to support Spotify sharelinks)
    * Added user_doc
    * Separated WebIf from main file


  * stateengine:

    * Improve web interface - automatic refresh, show loglevel on item basis, show visu on button click.
      Needs most recent http module update (Nov, 8) to work correctly
    * Implement webif_pagelength from module, slight webif adjustments
    * Bump to v 1.9.3
    * Fix log message for delay
    * Fix error on startup (important)
    * Fix metadata and implement webif in docu
    * Adjust webif_pagelength handling

  * tasmota:

    * Bumped to Version 1.3
    * Implement Cluster und Group Commands for Zigbee
    * Improved parsing of discovery message to detect and identify existing devices
    * Improved start of subscriptions to notice all discovery messages
    * Easy Zigbee data handling (more flat dict structure)
    * Define allowed attribute values for tasmota_zb_attr
    * Added support for SHT3x sensor connected to Tasmota device
    * Updated WebIF to latest http-module
    * Code Cleanup and beautifying for better readability

  * tankerkoenig:

    * Bumped to Version 2
    * Added support of items (No need for logic anymore) but keep recent public functions identical
    * Add WebIF
    * Reducing available functions
    * Named _full function back to old name
    * Added cast to float to rad value
    * Added check for Nonetype results

  * telegram:

    * v1.7.0 - control SH-item in the bot
    * Example in readme.rst.off
    * Bak to control-menu after "on" or "off"
    * Small optical cosmetics

  * trovis557x:

    * Changes to Samson Trovis 557x plugin (for new pymodbus versions)

  * uzsu:

    * Get webif_pagelength from module.yaml if possible, adjust webif accordingly
    * Bump to v1.6.4
    * Adjusted requirements.txt for scipy to run unit tests under Python 3.11
    * Adjust webif_pagelength handling to new parameter handling

  * xiaomi_vac:

    * Fix docu, adjust web interface, implement webif_pagelength from http module
    * Adjust webif_pagelength handling
    * Fix docu


* tests:

  * Updated core mockup for extended log levels for plugins

|

Änderungen bei Plugins
======================

Neue Plugins
------------

Für Details zu den neuen Plugins, bitte die Dokumentation des jeweiligen Plugins unter
http://www.smarthomeng.de/user/plugins_all.html konsultieren.

* piratewthr: ew weather plugin as a replacement for the darksky plugin. It is (almost) a dropin replacement



Plugin Updates
--------------

Für Details zu den Änderungen an den einzelnen Plugins, bitte die Dokumentation des jeweiligen Plugins unter
http://www.smarthomeng.de/user/plugins_all.html konsultieren.

* <name>:

  * ...


Outdated Plugins
----------------

Die folgenden Plugins wurden bereits in v1.6 als *deprecated* (veraltet) markiert. Das bedeutet, dass diese
Plugins zwar noch funktionsfähig sind, aber nicht mehr weiter entwickelt werden. Sie werden in einem kommenden
Release von SmartHomeNG entfernt werden. Anwender dieser Plugins sollten auf geeignete Nachfolge-Plugins
wechseln.

* System Plugins

  * backend - use the administration interface instead
  * sqlite_visu2_8 - switch to the **database** plugin

* Web Plugins

  * wunderground - the free API is not provided anymore by Wunderground


Die folgenden Plugins wurden in v1.7 als *deprecated* (veraltet) markiert, weil kein Nutzer oder Tester
dieser Plugins gefunden werden konnte:

* Gateway Plugins

  * ecmd
  * elro
  * iaqstick
  * snom
  * tellstick

* Interface Plugins

  * easymeter
  * smawb
  * vr100

* Web Plugins

  * nma

Weiterhin wurde das bisherige mqtt Plugin zu mqtt1 umbenannt und als *deprecated* markiert, da das neue mqtt
Plugin diese Funktionalität übernimmt. Das neue mqtt Plugin nutzt dazu das mqtt Modul des aktuellen Cores
von SmartHomeNG.


Retired Plugins
---------------

Die folgenden Plugins wurden *retired* (in den RUhestand geschickt). Sie waren in einem der vorangegangenen
Releases von SmartHomeNG als *deprecated* markiert worden. Diese Plugins wurden aus dem **plugins** Repository
entfernt, stehen jedoch als Referenz weiterhin zur Verfügung. Diese Plugins wurden in das **plugin_archive**
Repositiory aufgenommen.

* ...

|

Weitere Änderungen
==================

Tools
-----

* check_plugin.py:

  * Initial development version of check_plugin.py (a formal plugin checker)
  * Option added to check all plugins


Dokumentation
-------------

* Changed builddevdoc to use Python 3.9
* Updates to icons and widgets in docu "visu: automatich generation"
* fix and improve logging (filter) docu
* Corrected link for Google translation of documentation

* Sample Plugins:

  * Adjust mqtt and standard sample plugin to reflect the newest changes (webif_pagelength, additional
    column for responsive in datatables)

* http module:

  * Update documentation (include webif_pagelength updates, minor fixes, additional options to show/hide buttons, etc.)


