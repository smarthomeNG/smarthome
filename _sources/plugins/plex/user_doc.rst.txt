.. index:: Plugins; plex
.. index:: plex

====
plex
====

Das Plugin sendet Push-Benachrichtigungen an Plex-Clients wie RasPlex. Getestet wurde es mit
RasPlex; das Benachrichtigungsmodul sollte darüber hinaus mit OpenELEC sowie XBMC/Kodi Frodo und
neuer kompatibel sein.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/plex`
beschrieben.

Item-Attribute
--------------

**plex_host** registriert ein Item als Ziel-Client für Benachrichtigungen; der Wert ist der
Hostname oder die IP-Adresse des Plex-Clients. **plex_port** (optional, Standard 3005) legt den
Port auf diesem Client fest.

Alle Items mit gesetztem **plex_host** werden bei jedem Aufruf von **notify()** gleichzeitig
benachrichtigt; eine gezielte Auswahl einzelner Clients je Aufruf ist nicht möglich. Die Funktion
**notify()** wird aus Logiken heraus aufgerufen (z.B. ``sh.plex.notify(title, message, image)``)
und ist mit ihren Parametern unter :doc:`/plugins_doc/config/plex` beschrieben.
