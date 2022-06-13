============================
Release 1.x.x - tt. mmm 2022
============================

Dieses Release ist ein Wartungs-Release. Außer Bugfixes gibt es einige neue Features im Core von SmartHomeNG,
sowie Updates zu einigen Plugins.

.. only: comment

    Dieses Release ist ein Feature-Release. Es gibt eine Menge neuer Features im Core von SmartHomeNG und den Plugins.


.. note::

    Diese Release Notes sind ein Arbeitsstand.

     - Berücksichtigt sind Commits im smarthome Repository bis incl. 28. Mai 2022
       (Documentation undates; bump version to 1.9.2.2)
     - Berücksichtigt sind Commits im plugins Repository bis incl. 27. Mai 2022
       (remove Travis-CI settings)


Überblick
=========

Dieses ist neues Release für SmartHomeNG. Die Änderungen gegenüber dem Release v1.9.2 sind im
folgenden in diesen Release Notes beschrieben.


Minimum Python Version
----------------------

Die absolute Minimum Python Version in der SmartHomeNG startet, ist **Python 3.6**.

Für das SmartHomeNG Release 1.10 wird die absolute Minimum Python Version auf **Python 3.7** angehoben, da der
Community Support für Python 3.6 am 23. Dezember 2021 endete.

Bei einer Neuinstallation wird jedoch empfohlen auf einer der neueren Python Versionen (3.8 oder 3.9) aufzusetzen.


Unterstützte Python Versionen
-----------------------------

Die älteste offiziell unterstützte Python Version für SmartHomeNG Release 1.9.x ist **Python 3.7**.
Automatisierte Tests von SmartHomeNG werden nur in den unterstützten Python Versionen durchgeführt.
(Siehe auch :ref:`Hard- u. Software Anforderungen <python_versionen>` im Abschnitt **Installation**
zu unterstützten Python Versionen)

|

Allgemeine Änderungen
=====================

* Die automatisierten Unit Tests von SmartHomeNG wurden von Travis auf Github Workflows umgestellt.

|

Änderungen am Core
==================

Bugfixes in the CORE
--------------------

* ...


Updates in the CORE
-------------------

* ...

* Items:

  * ...

* Logics:

  * ...

* Libs:

  * lib.db:

    * Fixed deprecation warnings

  * lib.item:

    * Fixed deprecation warnings

  * lib.logic:

    * Implemented r/o attributes as properties
    * Implemented some logic properties to distinguish them from the list of local variables of that logic

  * lib.metadata:

    * Fixed deprecation warnings

  * lib.scheduler:

    * Setting up a global environment when executing a logic (containing e.g. logger and logic variables)

  * lib.smarthome:

    * Fixed deprecation warnings

  * lib.userfunction:

    * Bugfix

* Modules:

  * modules.admin:

    * Bugfix to show logs with old and new naming convention
    * Loglevels adjusted in api_loggers.py

* Plugins:

  * ...

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


* avm:

  *Improvement for HKRs: Allow set temperature to be set directly to value 126.5 (off/frost protection mode).

* backend:

  * Fixed deprecation warnings

* casambi:

  * Minor fix for casambi_id (now integer instead of num)

* database:

  * Reinserted 'duplicate_use' to metadata for item_attribute 'database'

* hue2:

  * Changed requirements to resolve conflict with appletv plugin

* knx:

  * Fixed deprecation warnings

* nut:

  * Fixed initialization of parent class (smartPlugin)

* resol:

  * Minor improvement-> cleaned-up update_item method

* sonos:

  * Added appdirs to requirements.txt (needed for SoCo framework)
  * improved webinterface - list discovered speakers

* telegram:

  * Restrict version be <14.0 since then async will be used


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

* ...
* ...


