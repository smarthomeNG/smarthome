=============================
Release 1.x - Month day, 2019
=============================

Es gibt eine Menge neuer Features im Core von SmartHomeNG und den Plugins.


Unterstützte Python Versionen
=============================

Die älteste offiziell unterstützte Python Version für SmartHomeNG Release 1.x ist Python 3.5.
(Siehe auch *Hard- u. Software Anforderungen* im Abschnitt *Installation* zu unterstützten Python Versionen)

Das bedeutet nicht unbedingt, dass SmartHomeNG ab Release 1.6 nicht mehr unter älteren Python Versionen läuft. Es
bedeutet, dass SmartHomeNG nicht mehr mit älteren Python Versionen getestet wird und das gemeldete Fehler mit älteren
Python Versionen nicht mehr zu Buxfixen führen.

Die meisten Funktionen werden auch unter Python 3.4 funktionieren. Es werden jedoch zunehmend Features eingesetzt, die
erste ab Python 3.5 zur Verfügung stehen.


Absolute minimum Python Version
===============================

Die Minimum Python Version in der SmartHomeNG startet wurde bei v3.4 belassen. Bei einer Neuinstallation wird jedoch
empfohlen auf einer der neueren Python Versionen (3.6 oder 3.7) aufzusetzen.



Bitte auch die Release Notes für Version 1.x unter `https://www.smarthomeNG.de/user/release <../../user/release/1_x.html>`_ beachten.




Bugfixes im CORE
----------------

* ...



Updates im CORE
---------------

* ...

* Items:

  * ...


* Logiken:

  * ...

* lib.shtime ...

* Module:

  * ...
  * http:

    * ...

  * admin:

    * ...

* Plugins:

  * ...



Neue Plugins
------------

Für Details zu den inhaltlichen Änderungen der einzelnen Plugins, bitte die Dokumentation des jeweiligen Plugins konsultieren.

* xxx:

  * ...



Plugin Erweiterungen
--------------------

* xxx:

  * ...




Veraltete Plugins
-----------------

Die folgenden Plugins wurden bereits in v1.6 als *deprecated* (veraltet) gekennzeichnet. Dieses Kennzeichen bedeutet,
dass die Plugins zwar noch funktionieren, aber nicht mehr weiterentwickelt werden und aus dem kommenden Release von
SmartHomeNG entfernt werden. Nutzer dieser Plugins sollten auf entsprechende Nachfolge-Plugins umstellen.

* System Plugins

  * sqlite - auf das **database** Plugin umstellen
  * sqlite_visu2_8 - auf das **database** Plugin umstellen

* Gateway Plugins

  * tellstick - classic Plugin, laut Umfrage nicht genutzt

* Interface Plugins

  * netio230b - classic Plugin, laut Umfrage nicht genutzt
  * smawb - classic Plugin, laut Umfrage nicht genutzt

* Web Plugins

  * alexa - auf das **alexa4p3** Plugin umstellen
  * boxcar - classic Plugin, laut Umfrage nicht genutzt
  * mail - auf die Plugins **mailsend** bzw. **mailrcv** umstellen
  * openenergymonitor - classic Plugin, laut Umfrage nicht genutzt
  * wunderground - das freie API wird durch Wunderground nicht mehr zur Verfügung gestellt


Dokumentation
-------------

* Anwender Dokumentation

  * ...
  * Allgemeine Updates


* Entwickler Dokumentation

  * Dokumentation zur Erstellung von Webinterfaces für Plugins erweitert
  * Allgemeine Updates
