==========================
Release 1.x - tt. mmm 2021
==========================

Es gibt eine Menge neuer Features im Core von SmartHomeNG und den Plugins.

.. note::

    Diese Release Notes sind ein Arbeitsstand.

     - Berücksichtigt sind Commits im smarthome Repository bis incl. 29. April 2021
       (...)
     - Berücksichtigt sind Commits im plugins Repository bis incl. ...
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

* Items:

  * ...

* Logics:

  * ...

lib.backup:

  * Added new struct files of ../etc directory to configuration backup

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

* Modules:

  * admin:

    * Display of structs in shngadmin is now sorted and grouped by plugin
    * Randomized calls to find blog articles on smarthomeng.de

  * websocket:

    * Changes to memory logging in core

* Plugins:

  * ...

* tests:

  * mock.core: Read core version from bin.shngversion.py


Änderungen bei Plugins
======================

New Plugins
-----------

For details of the changes of the individual plugins, please refer to the documentation of the respective plugin.

* <Name>: ...



Plugin Updates
--------------

* <name>:

  * ...


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

* ...
* ...


