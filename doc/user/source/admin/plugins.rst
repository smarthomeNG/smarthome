
.. index:: Admin GUI; Plugins
.. index:: Plugins; Admin GUI

#######
Plugins
#######


===========================
Liste der geladenen Plugins
===========================

Unter **Plugins** wird eine Liste der geladenen Plugins mit einer Reihe von Informationen zu den Plugins angezeigt.
Rechts in der jeweiligen Zeile sind Icons über die (falls vorhanden)

- das Web Interface des Plugins gestartet werden kann,
- die Konfigurations-Dokumentation zu dem Plugin aufgerufen werden kann,
- die weitergehende Anwender-Dokumentation des Plugins aufgerufen werden kann,
- der Support Thread zu dem Plugin im SmartHomeNG Forum aufgerufen werden kann,
- eine Übersicht über relevante Blog Artikel angezeigt werden kann

.. image:: assets/plugins.jpg
   :class: screenshot


.. note::

   Webinterfaces von Plugins können die durch das Admin Interface genutzte Art der Authentifizierung noch nicht
   erkennen/nutzen. Deshalb erscheint beim ersten Aufruf eines Web Interfaces der Basic-Auth Anmeldedialog des Browsers
   und es muss eine Anmeldung mit Username/Passwort des Admin Interfaces erfolgen.



.. index:: Plugin Konfiguration

====================
Plugin Konfiguration
====================

Über diese Funktion können weitere installierte Plugins zur SmartHomeNG Instanz hinzu konfiguriert oder
bestehende Konfigurationen geändert werden. Weiterhin ist es auch möglich Plugins aus der Konfiguration
zu entfernen.

Wenn ein Plugin nur kurzfristig außer Betrieb genommen werden soll, so kann es über einen Schalter disabled
werden. Dadurch kann es später einfach wieder in betrieb genommen werden, ohne die Konfiguration erneut
durchführen zu müssen.


Liste der konfigurierten Plugins
================================

Die Liste der konfigurierten Plugins zeigt alle Konfigurationen an, die in ../etc/plugin.yaml gespeichert sind. Der
Schiebeschalter links in jeder Zeile zeigt ob das Plugin aktiviert ist. Falls nicht, ist es nicht geladen bzw. wird bei
einem Neustart nicht geladen.

Durch anklicken einer Zeile, wird ein Dialog aktiviert um die Konfiguration des jeweiligen Plugins anzupassen.

.. image:: assets/plugin-configlist.jpg
   :class: screenshot

Falls eine Plugin Konfiguration geändert wird oder eine neue Plugin Konfiguration hinzugefügt wird, wird der Button am
unteren Ende der Liste aktiviert, mit dem SmartHomeNG neu gestartet werden kann um die Änderungen zu aktivieren.


Konfiguration eines Plugins
===========================

Über den Schiebeschalter oben links kann die Plugin Konfiguration aktiviert oder deaktiviert werden. Die Änderung
wird nach einem Neustart von SmartHomeNG aktiv.

Default Werte werden in grau angezeigt. Um zu den Standardwerten zurückzukehren, muss nur der Feldinhalt gelöscht werden,
bzw. bei Auswahl Listen der Wert über das **x** neben dem Wert gelöscht werden.

.. image:: assets/plugin-config.jpg
   :class: screenshot

Falls eine Konfiguration nicht nur deaktiviert, sondern endgültig gelöscht werden soll, so kann das über den
**Löschen** Button erfolgen.

