==========================
Release 1.x - tt. mmm 2022
==========================

Es gibt eine Menge neuer Features im Core von SmartHomeNG und den Plugins.

.. note::

    Diese Release Notes sind ein Arbeitsstand.

     - Berücksichtigt sind Commits im smarthome Repository bis incl. ...
       (...)
     - Berücksichtigt sind Commits im plugins Repository bis incl. ...
       (...)


Überblick
=========

Dieses ist neues Release für SmartHomeNG. Die Änderungen gegenüber dem Release v1.9.1 sind im
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
(Siehe auch :ref:`Hard- u. Software Anforderungen <python_versionen>` im Abschnitt **Installation**
zu unterstützten Python Versionen)


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

  * lib. ...:

* Modules:

  * ...:

    * ...

* Plugins:

  * ...

* tests:

  * ...


Änderungen bei Plugins
======================

New Plugins
-----------

For details of the changes of the individual plugins, please refer to the documentation of the respective plugin.

* zigbee2mqtt: Plugin to control devices which are linked to Zigbee Gateway equipped with Zigbee2MQTT firmware.
  Communication is handled through the MQTT module of SmartHomeNG.



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

  * backend - use the administration interface instead
  * sqlite_visu2_8 - switch to the **database** plugin

* Web Plugins

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
  * smawb
  * vr100

* Web Plugins

  * nma

Moreover, the previous mqtt plugin was renamed to mqtt1 and marked as *deprecated*, because the new mqtt
plugin takes over the functionality. This plugin is based on the mqtt module and the recent core.


Retired Plugins
---------------

The following plugins have been retired. They had been deprecated in one of the preceding releases of SmartHomeNG.
They have been removed from the plugins repository, but they can still be found on github. Now they reside in
the **plugin_archive** repository from where they can be downloaded if they are still needed.

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


