.. index:: Plugins; cli (CommandLine Interface)
.. index:: cli

cli
###

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/cli` beschrieben.


Weiterführende Informationen
============================

Das CLI Plugin bietet einen Zugriff über Telnet auf SmartHomeNG.

Über das Plugin können diverse Befehle an SmartHomeNG zur Auflistung, Debugging und Manipulation
von Items, Logiken, Plugins und internen Objekten geschickt werden.


Plugin Konfigurationsparameter
==============================

Das Plugin kann über die folgende Konfiguration in der Datei etc/plugins.conf akitviert werden:

.. code-block: yaml
   cli:
       plugin_name: cli
       # ip: 0.0.0.0
       # port: 2323
       update: True



+--------------+------------------------------------------------------------------------------+
| Paramter     | Erläuterung                                                                  |
+==============+==============================================================================+
| plugin_name  | Referenziert das Plugin                                                      |
+--------------+------------------------------------------------------------------------------+
| ip           | Bei Verwendung mehrerer Netzwerke/Netzwerk Adapter: Netzwerk an das das CLI  |
|              | Plugin gebunden werden soll.                                                 |
+--------------+------------------------------------------------------------------------------+
| port         | Port der auf Verbindungen lauschen soll (default: 2323).                     |
+--------------+------------------------------------------------------------------------------+
| update       | Wenn der Parameter True konfiguriert wird, dürfen über das CLI-Plugin Daten  |
|              | geändert werden.                                                             |
+--------------+------------------------------------------------------------------------------+



Zugriff auf die CLI
===================

Linux
-----

`telnet localhost 2323`

Zugriff via Windows / Putty
---------------------------

In Putty bitte folgende Settings beachten, damit der Zugriff auf das CLI Plugin funktioniert:

Session:

- Connection type -> RAW wählen (nicht Telnet!)
- Host Namen des Servers eintragen, Port 2323 (oder wie er in der plugin.conf konfiguriert ist)


Terminal:

- Implicit CR in every LF -> Haken setzen

Connection - Telnet:

- Keyboard sends Telnet special commands -> Haken setzen
- Return key sends Telnet New Line instead of ^M -> Haken entfernen


CLI Befehle
===========

+--------------------------+----------------------------------------------------------------------------------------------+
| Befehl                   | Erläuterung                                                                                  |
+==========================+==============================================================================================+
| help <group>, h <group>  | Zeigt allgemeine Hilfe oder Hilfe für eine Guppe von Kommandos <item, log, logic, scheduler> |
+--------------------------+----------------------------------------------------------------------------------------------+
| if                       | Listet die Items der obersten Ebene                                                          |
+--------------------------+----------------------------------------------------------------------------------------------+
| if <item>                | Listet das angegebene Item und alle Child-Items dazu mit Werten auf                          |
+--------------------------+----------------------------------------------------------------------------------------------+
| ii <item>                | Dumpt Detail-Information über das angegebene Item - Kommando Alias: dump                     |
+--------------------------+----------------------------------------------------------------------------------------------+
| il                       | Listet alle Items mit Werten - Kommando Alias: la                                            |
+--------------------------+----------------------------------------------------------------------------------------------+
| iup                      | Alias for iupdate - Kommando Alias: up                                                       |
+--------------------------+----------------------------------------------------------------------------------------------+
| iupdate <item> = <value> | Weist dem Item einen neuen Wert zu - Kommando Alias: update                                  |
+--------------------------+----------------------------------------------------------------------------------------------+
| ld <logic>               | Disabled die angegebene Logic - Kommando Alias: dl                                           |
+--------------------------+----------------------------------------------------------------------------------------------+
| le <logic>               | Enabled die angegebene Logic - Kommando Alias: el                                            |
+--------------------------+----------------------------------------------------------------------------------------------+
| li <logic>               | Logic Information - Dumpt Details über die angegebene Logik                                  |
+--------------------------+----------------------------------------------------------------------------------------------+
| ll                       | Listet alle Logiken und ihre nächste Ausführungszeit - Kommando Alias: lo                    |
+--------------------------+----------------------------------------------------------------------------------------------+
| logc <log>               | Löscht das Memory-Log                                                                        |
+--------------------------+----------------------------------------------------------------------------------------------+
| logd <log>               | Dumpt das Memory-Log                                                                         |
+--------------------------+----------------------------------------------------------------------------------------------+
| lr <logic>               | Führt ein Reload für die angegebene Logik aus - Kommando Alias: rl                           |
+--------------------------+----------------------------------------------------------------------------------------------+
| lrr <logic>              | Führt ein Reload für die angegebene Logik aus und triggert diese - Kommando Alias: rr        |
+--------------------------+----------------------------------------------------------------------------------------------+
| lt <logic>               | Triggert die angegebene Logik - Kommando Alias: tr                                           |
+--------------------------+----------------------------------------------------------------------------------------------+
| rt                       | Zeit die Laufzeit von SmaertHomeNG an (return runtime)                                       |
+--------------------------+----------------------------------------------------------------------------------------------+
| si <task>                | Zeigt Details für den angegebene Scheduler Task an                                           |
+--------------------------+----------------------------------------------------------------------------------------------+
| sl                       | Listet alle Scheduler Tasks nach Namenauf                                                    |
+--------------------------+----------------------------------------------------------------------------------------------+
| st                       | Listet alle Scheduler Tasks nach Ausführungszeit auf                                         |
+--------------------------+----------------------------------------------------------------------------------------------+
| tl                       | Listet die aktuellen Thread Namen auf                                                        |
+--------------------------+----------------------------------------------------------------------------------------------+
| quit, q                  | Beendet die CLI Session                                                                      |
+--------------------------+----------------------------------------------------------------------------------------------+

