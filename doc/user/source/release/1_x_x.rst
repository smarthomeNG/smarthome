=============================
Release 1.9.5 - tt. März 2023
=============================

Dieses Release ist ein Wartungs-Release. Außer Bugfixes gibt es einige neue Features im Core von SmartHomeNG,
sowie einige neue Plugins.

.. only: comment

    Dieses Release ist ein Feature-Release. Es gibt eine Menge neuer Features im Core von SmartHomeNG und den Plugins.

|

    .. note::

        Diese Release Notes sind ein Arbeitsstand.

         - Berücksichtigt sind Commits im smarthome Repository bis incl. 25. März 2023
           (documentation: fix for table introduced with latest commit)
         - Berücksichtigt sind Commits im plugins Repository bis incl. 23. März 2023
           (smartvisu: Removed old documentation link from metadata)


Überblick
=========

Dieses ist neues Release für SmartHomeNG. Die Änderungen gegenüber dem Release v1.9.4 sind im
folgenden in diesen Release Notes beschrieben.


Minimum Python Version
----------------------

Die absolute Minimum Python Version in der SmartHomeNG startet, ist **Python 3.7**.

Für das SmartHomeNG Release 1.10 wird die absolute Minimum Python Version auf **Python 3.8** angehoben, da der
Community Support für Python 3.7 am 27. Juni 2023 endete.

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

Allgmein
--------

* Workflows:

  * Replaced deprecated 'set-output'
  * (re)joined pr_unittests into unittests.yml
  * Disabled seperate pr_unittests workflow


Updates in the CORE
-------------------

* ...

* Libs:

  * lib.connection:

    * Added extended deprecation warning (lib will be removed in SmartHomeNG v1.10.0)

  * lib.metadata:

    * Fix for empty plugin parameter sectionand section not declared NONE

  * lib.network:

    * Log some more for insights on wrong parameter passing from plugins on callbacks

  * lib.plugin:

    * Fix for wrong cwd on Plugin load

  * lib.shpypi:

    * Adressing requirements file with absolute path to fix bug, when current working directory is not
      the SmartHomeNG base directory
    * Added warning, if plugin_name: is not in lowercase

  * lib.smarthome:

    * Fix in stop(), if SmartHomeNG is killed during initialization

  * lib.systeminfo:

    * Changed read_macosinfo() to be compatible with more MacOS versions
    * Added text, that testing cpu speed could take several minutes on slow machines
    * Ensure initialization of cpu_speed_class for display in shngadmin

  * lib.triggertimes:

    * Catch a possible error with event related calculations, resulting now in invalid time

* Modules:

  * admin:

    * Removed old shngadmin version
    * Update shngadmin to v0.6.6:

      * Added new loglevels to list of loggers
      * Fixed translation glitch in SmartHomeNG status display; Displays info, if running in virtual environment

    * Added handling, if 'documentation' in plugin metadata is explicitly se to None

  * http:

    * Webinterfaces: fix docstring and issue when text is None/Null

  * websocket:

    * Fixed bug for wss protocol handling
    * Added setting for protocol_over_reverseproxy to smartvisu payload protocol handling
    * Bumped version to v1.1.1
    * Changed loglevel for error 1011 on ping timeout in sv payload protocol
    * Changed loglevel in sv payload protocol when sending (url-)command to visu

* tests:

  * ...

|

Änderungen bei Plugins
======================

Allgmein
--------

* Workflows:

  * Replaced deprecated 'set-output'
  * (re)joined pr_unittests into unittests.yml
  * Disabled seperate pr_unittests workflow


Neue Plugins
------------

Für Details zu den neuen Plugins, bitte die Dokumentation des jeweiligen Plugins unter
http://www.smarthomeng.de/user/plugins_all.html konsultieren.

* <Name>: ...



Plugin Updates
--------------

Für Details zu den Änderungen an den einzelnen Plugins, bitte die Dokumentation des jeweiligen Plugins unter
http://www.smarthomeng.de/user/plugins_all.html konsultieren.

* avm:

  * Larger rework of plugin
  * Bumed version to 2.0.1
  * Added version 1.6.8 from SmartHomeNG v1.9.3 master as 'previous version'
  * Fix for RGB lightbulb (fritzdect 500): set on/off state to off and dim level to 0 if device is not
    connected (same behavior as in plugin version 1.6.8)
  * Multiple fixes
  * Bumed version to 2.0.1

* database:

  * Added info to 'Could not connect to the database' log entry

* enocean:

  * Catch exception that occurs, if Tx Enocean item is defined without tx_id_offset attribute
    Output error log in this case
  * small improvements in comments and status info

* lirc:

  * Introduce web interface
  * Bump version to 1.5.1

* modbus_tcp:

  * Corrected version number in __init__.py

* onewire:

  * Fixed debug messages
  * Added a "sleep-time" for testing to improve sensor reading for parasite powered sensors

* piratewthr:

  * Bugfix

* smartvisu:

  * New parameter 'protocol_over_reverseproxy'
  * Bumped version to 1.8.10
  * Removed parameter 'protocol_over_reverseproxy'
  * Removed old documentation link from metadata

* uzsu:

  * Changed requirements for numpy

* webpush:

  * Added shng varpath to parameters
  * Changed to correct doc link
  * Re-removed superfluous doc link

* Diverse Plugins:

  * Changed readme.md class_path/class_name -> plugin_name


Outdated Plugins
----------------

Die folgenden Plugins wurden bereits in v1.6 als *deprecated* (veraltet) markiert. Das bedeutet, dass diese
Plugins zwar noch funktionsfähig sind, aber nicht mehr weiter entwickelt werden. Sie werden in einem kommenden
Release von SmartHomeNG entfernt werden. Anwender dieser Plugins sollten auf geeignete Nachfolge-Plugins
wechseln.

* System Plugins

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

* plugin_metadata_checker:

  * Added handling, if 'documentation' in plugin metadata is explicitly se to None



Dokumentation
-------------

* Added description for using virtual environemnts
* Added new log levels to user documentation



