============================
Release 1.x.x - tt. mmm 2023
============================

Dieses Release ist ein Wartungs-Release. Außer Bugfixes gibt es einige neue Features im Core von SmartHomeNG,
sowie einige neue Plugins.

.. only: comment

    Dieses Release ist ein Feature-Release. Es gibt eine Menge neuer Features im Core von SmartHomeNG und den Plugins.


.. note::

    Diese Release Notes sind ein Arbeitsstand.

     - Berücksichtigt sind Commits im smarthome Repository bis incl. 22. Nov 2022
       (...)
     - Berücksichtigt sind Commits im plugins Repository bis incl. 27. Nov 2022
       (database: Added parameter to set ...)


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

* Items:

  * ...

* Logics:

  * ...

* Libs:

  * lib.model.smartplugin:

    * Preparing SmartPlugin for editable items

  * lib.scheduler:

    * Catch more exceptions outside scheduler to prevent thread end


* Modules:

  * admin:

    * Fix for reading of logfiles if folder contains files without extension .log

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




* Plugins:

  * cli:

    * Adjust web interface

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

  * executor:

    Remove eval capability, add script listbox, load, save and delete

  * ical:

    * Fixed decoding of calendar events that have the same identifiers, e.g. happens if single
      events of a calendar series are rescheduled once.

  * jsonread:

    * Adjusted requirements.txt

  * knx:

    * Improve structure (introduce globals, put webif in separate init file)
    * Introduce webif_pagelength and improve web interface
    * Improve web interface
    * Fix values being None for plugin with instance defined

  * mqtt:

    * Update webif_pagelength implementation, small webif adjustments

  * sonos:

    * Fix for mute does not work for coupled speakers. -> Fixed by making mute a group command.

  * stateengine:

    * Improve web interface - automatic refresh, show loglevel on item basis, show visu on button click.
      Needs most recent http module update (Nov, 8) to work correctly
    * Implement webif_pagelength from module, slight webif adjustments
    * Bump to v 1.9.3

  * uzsu:

    * Get webif_pagelength from module.yaml if possible, adjust webif accordingly
    * Bump to v1.6.4
    * Adjusted requirements.txt for scipy to run unit tests under Python 3.11



* tests:

  * ...

|

Änderungen bei Plugins
======================

Neue Plugins
------------

Für Details zu den neuen Plugins, bitte die Dokumentation des jeweiligen Plugins unter
http://www.smarthomeng.de/user/plugins_all.html konsultieren.

* <Name>: ...



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

* ...


Dokumentation
-------------

* Changed builddevdoc to use Python 3.9

* Sample Plugins:

  * Adjust mqtt and standard sample plugin to reflect the newest changes (webif_pagelength, additional
    column for responsive in datatables)

* http module:

  * Update documentation (include webif_pagelength updates, minor fixes, additional options to show/hide buttons, etc.)


