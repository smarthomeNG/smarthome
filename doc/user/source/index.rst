:tocdepth: 1

===========
SmartHomeNG
===========

Anwenderdokumentation
=====================

SmartHomeNG [#f1]_ ist ein System das als Metagateway zwischen verschiedenen "Dingen" fungiert und
dient der Verbindung unterschiedlicher Geräte-Schnittstellen. Die Standard-Schnittstelle eines
Gerätes wird durch das Metagateway so um viele zusätzliche Schnittstellen erweitert. So ist es
möglich dass die Klingel mit der Musikanlage und TV spricht, und dessen Wiedergabe unterbricht
oder bei Abwesenheit eine Nachricht per Email verschickt.

Das System kann flexibel durch Plugins erweitert werden, wobei die Plugins in folgende Kategorien klassifiziert sind:

- **Gateway**: Anbindung von Devices eines Bus-Systems wie KNX, HomeMatic, EnOcean, 1-wire, DMX, Philips Hue, ...
- **Interface**: Anbindung einzelner Devices wie AVM Fritzboxen, Heizungssteuerungen, div. AV Devices, ...
- **Web-/Cloud-Dienst**: Anbindung an diverse Web- bzw. Cloud-Dienste, wie Mail, Prowl, Wetter-Dienste, Alexa, ...
- **Protokoll**: Unterstützung diverser Protokolle wie TCP/IP, MQTT, XMPP
- **System**: Systemnahe Erweiterungen wie Datenbank Anbindung, Visu Anbindung, universelle Zeitschaltuhr,
  Stateengine (endlicher Automat), ...

Diese Dokumentation reflektiert das aktuelle Release:

- **Version des Core**: |release|
- **Version der Plugins**: |version|

Die Entwickler-Dokumentation (für Entwickler von Plugins und den Core von SmartHomeNG), sowie
die READMEs der Plugins sind in Englisch gehalten.

Die Anwenderdokumentation steht auf Deutsch zur Verfügung. Die Entwicklerdokumentation hingegen, ist in Englisch
verfasst.

Hilfe zu SmartHomeNG gibt es im `Supportforum im KNX-User-Forum <https://knx-user-forum.de/forum/supportforen/smarthome-py>`_
oder im `Chat auf gitter.im <https://gitter.im/smarthomeNG/smarthome>`_ .

.. note::

   **Anmerkungen** und **Änderungswünsche** zu dieser Anwenderdokumentation bitte auf
   `dieser Feedback Seite <https://www.smarthomeng.de/feedback-zur-dokumentation>`_ hinterlassen.

.. [#f1] SmartHomeNG © Copyright 2016-2020 SmartHomeNG Team, basiert auf smarthome.py © 2011-2014 Marcus Popp.

..    :titlesonly:

.. toctree::
   :maxdepth: 1
   :hidden:

   einleitung.md
   installation/installation.rst
   konfiguration/konfiguration.rst
   plugins_all.rst
   logiken/logics.rst
   visualisierung/visualisierung.rst
   admin/admin.rst
   beispiele/beispiele.rst
   tools/tools.rst
   fehlersuche
   faq
   Entwickler Dokumentation (Englisch) <https://www.smarthomeng.de/developer>
   release/release
   genindex
   impressum
   datenschutz


