=============================
Release 1.xx.x - xx. xxx 2026
=============================

.. only: comment

    Dieses Release ist ein Wartungs-Release. Außer Bugfixes gibt es einige neue Features im Core von SmartHomeNG,
    sowie einige neue Plugins.

Dieses Release ist ein Feature-Release. Es gibt eine Menge neuer Features im Core von SmartHomeNG und den Plugins.

|

.. only:: develop_branch

.. note::

        Diese Release Notes sind ein Arbeitsstand des **develop** Branches.

         - Berücksichtigt sind Commits im smarthome Repository bis inkl. x. xxxx 2026
           (...)
         - Berücksichtigt sind Commits im plugins Repository bis inkl. x. xxxx 2026
           (...)


Überblick
=========

Dieses ist neues Release für SmartHomeNG. Die Änderungen gegenüber dem Release v1.12.0 sind im Folgenden in diesen Release Notes beschrieben.


Minimum Python Version
----------------------

Die minimale Python-Version, die von SmartHomeNG unterstützt wird, ist **Python 3.10**.

Es ist ggf. möglich, SmartHomeNG auch auf früheren Python-Versionen laufen zu lassen. 
Dies ist aber nicht getestet, und möglicherweise nutzen z.B. einzelne Plugins Sprachfeatures,
die erst ab Python 3.10 unterstützt werden. 
Insofern kann für Versuche in dieser Hinsicht kein Support geleistet werden. 

Bei einer Neuinstallation wird jedoch empfohlen, auf einer der neueren
Python-Versionen (3.12 oder 3.13) aufzusetzen.


Unterstützte Python Versionen
-----------------------------

Offiziell unterstützt werden im SmartHomeNG Release 1.xx.0 die Python Versionen 3.10, 3.11, 3.12 und 3.13.
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
    * ...

* Modules:

  * modules. ...:

    * ...

* tools:

  * tools/...:

    * ...

|

Änderungen bei Plugins
======================

Allgmein
--------

* Workflows:

  * ...


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

* ...:

  * ...




Outdated Plugins
----------------

Die folgenden Plugins wurden in das plugin_archive Repository verschoben:

* Interface Plugins

  * ...


Die folgenden Plugins wurden als veraltet (deprecated markiert und werden in einem der nächsten Releases
aus dem Plugin-Repo entfernt und in das Archive-Repo verschoben:

* System Plugins

  * ...


|

Weitere Änderungen
==================

Dokumentation
-------------

* ...
