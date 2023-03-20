============================
Release 1.x.x - tt. mmm 2023
============================

Dieses Release ist ein Wartungs-Release. Außer Bugfixes gibt es einige neue Features im Core von SmartHomeNG,
sowie einige neue Plugins.

.. only: comment

    Dieses Release ist ein Feature-Release. Es gibt eine Menge neuer Features im Core von SmartHomeNG und den Plugins.

|

    .. note::

        Diese Release Notes sind ein Arbeitsstand.

         - Berücksichtigt sind Commits im smarthome Repository bis incl. 18. März 2023
           (modules.websocket: Added setting for protocol_over_reverseproxy...)
         - Berücksichtigt sind Commits im plugins Repository bis incl. 18. März 2023
           (smartvisu: New parameter 'protocol_over_reverseproxy'...)


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

  * lib.metadata:

    * Fix for empty plugin parameter sectionand section not declared NONE

  * lib.network:

    * Log some more for insights on wrong parameter passing from plugins on callbacks

  * lib.plugin:

    * Fix for wrong cwd on Plugin load

  * lib.shpypi:

    * Adressing requirements file with absolute path to fix bug, when current working directory is not
      the SmartHomeNG base directory

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

  * websocket:

    * Fixed bug for wss protocol handling
    * Added setting for protocol_over_reverseproxy to smartvisu payload protocol handling
    * Bumped version to v1.1.1

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

* database:

  * Added info to 'Could not connect to the database' log entry

* modbus_tcp:

  * Corrected version number in __init__.py

* onewire:

  * Fixed debug messages

* smartvisu:

  * New parameter 'protocol_over_reverseproxy'
  * Bumped version to 1.8.10

* webpush:

  * Added shng varpath to parameters
  * Changed to correct doc link
  * Re-removed superfluous doc link


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

* ...


Dokumentation
-------------

* ...
* ...


