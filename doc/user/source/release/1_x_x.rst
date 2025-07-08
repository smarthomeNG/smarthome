=============================
Release 1.xx.x - xx. xxx 2025
=============================

.. only: comment

    Dieses Release ist ein Wartungs-Release. Außer Bugfixes gibt es einige neue Features im Core von SmartHomeNG,
    sowie einige neue Plugins.

Dieses Release ist ein Feature-Release. Es gibt eine Menge neuer Features im Core von SmartHomeNG und den Plugins.

|

.. only:: develop_branch

.. note::

        Diese Release Notes sind ein Arbeitsstand des **develop** Branches.

         - Berücksichtigt sind Commits im smarthome Repository bis inkl. 7. Juli 2025
           (Implemented initialization for hysteresis ...)
         - Berücksichtigt sind Commits im plugins Repository bis inkl. 6. Juli 2025
           (...)


Überblick
=========

Dieses ist neues Release für SmartHomeNG. Die Änderungen gegenüber dem Release v1.11.0 sind im Folgenden in diesen Release Notes beschrieben.


Minimum Python Version
----------------------

Die absolute Minimum Python Version in der SmartHomeNG startet, ist **Python 3.8**.

Bereits für das SmartHomeNG Release 1.10 wurde die absolute Minimum Python Version auf **Python 3.8** angehoben, da der
Community Support für Python 3.7 am 27. Juni 2023 endete.

Bei einer Neuinstallation wird jedoch empfohlen auf einer der neueren Python Versionen (3.11 oder 3.12) aufzusetzen.


Unterstützte Python Versionen
-----------------------------

Offiziell unterstützt werden im SmartHomeNG Release 1.11.0 die Python Versionen 3.10, 3.11 und 3.12.
Automatisierte Tests von SmartHomeNG werden nur in den unterstützten Python Versionen durchgeführt.
(Siehe auch :ref:`Hard- u. Software Anforderungen <python_versionen>` im Abschnitt **Installation**
zu unterstützten Python Versionen)

|

Änderungen am Core
==================

Allgmein
--------

* github:

  * ...



Bugfixes im CORE
----------------

* ...


Updates in the CORE
-------------------

* ...


* bin

  * smarthome

    * ...

  * shngversion:

    * Bumped core version to 1.10.0.2 -> added support for asyncio in plugins



* Libs:

  *...:

    * ...

  * lib.item:
    * Remove 'eval:' from caller (if it exists) before calling update_item of a plugin
    * Remove 'eval:' from caller (if it exists) for autotimer
    * Implemented initialization for hysteresis item and extended documentation

* Modules:

  * modules. ...:

    * ...

* tools:

  * tools/postinstall:

    * Added handling for newer of Python to postinstall script

|

Änderungen bei Plugins
======================

Allgmein
--------

* Workflows:

  * Updated unittests to newer Ubuntu version
  * Updated build scripts for documentation to newer Ubuntu version
  * Updated workflows to build documentation to use a newer version of Ubuntu


.. _releasenotes_1_xx_x_neue_plugins:

Neue Plugins
------------

Für Details zu den neuen Plugins, bitte die Dokumentation des jeweiligen Plugins unter
http://www.smarthomeng.de/user/plugins_all.html konsultieren.

* ...: ...

.. _releasenotes_1_xx_x_updates_plugins:

Plugin Updates
--------------

Für Details zu den Änderungen an den einzelnen Plugins, bitte die Dokumentation des jeweiligen Plugins unter
http://www.smarthomeng.de/user/plugins_all.html konsultieren.

* enocean:

  * Completed decoding of EEP A5_08_01 and added decoding for A5_07_01
  * Temporary fix for unwanted plugin retrigger in combination with eval expressions

* hue2:

  * Changed requirement for zeroconf to resolve conflict
  * Revoked changed requirement for zeroconf to resolve conflict; xiaomi_vac: Changed requirement for
    zeroconf to resolve conflict

* hue3:

  * Added support for outdoor motion sensor
  * Bumepd version to 3.0.2

* nuki:

  * Added MQTT support for newer versions of the lock
  * New parameter 'mode' for operation types of plugin: 1 - MQTT, 2 - Nuki Bridge, 3 - MQTT and Nuki Bridge
  * Updates to documentation and logging

* philips_tv:

  * Minor webif fix

* rtr2:

  * Added comments to widgets

* sma_mb:

  * Update read methods for pymodbus and add crontab as poll time generator

* sonos:

  * Revert required minimum python version back to 3.8; upgraded SoCo to v0.30.9; catching exception for speakers
    with unknown ip address

* vicare:

  * Minor fix for online status after plugin restart; added specific log message if refresh token has expired

* xiaomi_vac:

  * Changed requirement for zeroconf to resolve conflict

|

Outdated Plugins
----------------

Die folgenden Plugins wurden in das plugin_archive Repository verschoben:

* Interface Plugins

  * avdevice
  * avm_smarthome


Die folgenden Plugins wurden als veraltet (deprecated markiert und werden in einem der nächsten Releases
aus dem Plugin-Repo entfernt und in das Archive-Repo verschoben:

* System Plugins

  * datalog
  * influxdata
  * memlog
  * operationlog
  * visu_smartvisu
  * visu_websocket

* Gateway Plugins

  * raumfeld

* Interface Plugins

  * husky

* Web/Cloud Plugins

  * alexa
  * darksky - the free API is not provided anymore - switch to the **piratewthr** or **openweathermap** plugin




Die folgenden Plugins wurden bereits in v1.6 als *deprecated* (veraltet) markiert. Das bedeutet, dass diese
Plugins zwar noch funktionsfähig sind, aber nicht mehr weiter entwickelt werden. Sie werden in einem kommenden
Release von SmartHomeNG entfernt werden. Anwender dieser Plugins sollten auf geeignete Nachfolge-Plugins
wechseln.

* System Plugins

  * sqlite_visu2_8 - switch to the **database** plugin

* Web Plugins

  * wunderground - the free API is not provided anymore by Wunderground - switch to the **piratewthr** or **openweathermap** plugin

|

Weitere Änderungen
==================

Dokumentation
-------------

* Modified README.md to reflect, that the JetBrains licenses expired
* Doku Fixes für logging

