:tocdepth: 5

.. index:: Plugins; smartvisu (smartVISU Unterstützung)
.. index:: smartVISU; smartvisu Plugin

=========
smartvisu
=========

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Das Plugin stellt das Bindeglied zur smartVISU dar. Es implementiert das Nutzdatenprotokoll, welches über Websockets
Daten zwischen der smartVISU und SmartHomeNG austauscht.

Außerdem ermöglicht es das smartvisu Plugin, Seiten für
die smartVISU aus den Item Definitionen von SmartHomeNG zu generieren.


Einführung
==========

Das Plugin verfügt über folgende Features:

- es kann mit Hilfe einiger Item Attribute Seiten für die smartVISU generieren
- es kann Widgets, die in Plugins enthalten sind in die smartVISU installieren
- zur Unterstützung des Widget Assistenten der smartVISU erstellt es eine aktuelle Liste der SmartHomeNG Items
  in der smartVISU
- Es aktiviert das Nutzdatenprotoll für die smartVISU im neuen Websocket Modul. Wenn dieses Plugin nicht geladen ist,
  reagiert das Websocket Modul nicht auf Kommandos von der smartVISU

Mit dem Plugin **smartvisu** können aus der Definition der Items in SmartHomeNG automatisch Seiten für die
smartVISU erstellt werden. Diese Visu Seiten werden im Verzeichnis ``smarthome`` des ``pages`` Verzeichnisses
der smartVISU erstellt. Das Plugin unterstützt smartVISU Versionen ab v2.8.

.. note::

    Damit die generierten Seiten abgelegt werden können, muss SmartHomeNG Schreibrechte auf die smartVISU Verzeichnisse
    haben. Deshalb bitte unbedingt darauf achten, dass die Berechtigungen und Gruppen Zugehörigkeit so gesetzt sind,
    wie es in der Komplettanleitung im Abschnitt **smartVISU installieren** beschrieben ist.


Das smartvisu Plugin ist der Ersatz für das Plugin visu_smartvisu, welches nun deprecated ist und in einem der
kommenden Releases aus SmartHomeNG entfernt wird.

Das smartvisu Plugin funktioniert sowohl mit dem neuen websocket Modul, als auch mit dem alten visu_websocket Plugin.
Die default_acl Einstellung funktioniert nur im Zusammenspiel mit dem websocket Modul.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/smartvisu` beschrieben.


Weiterführende Informationen
============================

.. note::

    Wird das Plugin pausiert und anschließend der Start Button für das Plugin gedrückt (der sichtbar ist, wenn die
    Admin GUI im Entwickler Modus läuft), werden die Visu Seiten erneut generiert und die Widgets werden erneut kopiert.


Nutzdaten Protokoll
-------------------

Die Kommunikation zwischen der smartVISU und SmartHomeNG findet über Websockets statt. Dazu wird der Websocket Server
des Websocket Moduls von SmartHomeNG genutzt.

Das Nutzdaten Protokoll wird durch das smartvisu Plugin implementiert/aktiviert. Für Entwickler ist das Nutzdaten
Protokoll im folgenden beschrieben.

.. toctree::
  :titlesonly:

  user_doc/websocket_visu_requests.rst
  user_doc/websocket_shng_requests.rst


Automatische Seitengenerierung
------------------------------

Das Plugin dient dazu beim Start von SmartHomeNG automatisch Seiten für die smartVISU zu genrieren. Die Möglichkeiten
hierzu sind unter :doc:`/visualisierung/automatic_generation` beschrieben-


Mischung von generierten und manuell erstellten Seiten
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In der smartVISU ist es möglich generierte und manuell erstellte Seiten zu mischen. Dazu muss in der
smartVISU unter ``pages`` ein weiteres Verzeichnis (z.B. mit dem Namen ``manuell`` angelegt werden und
diese Seiten müssen in der Konfiguration der smartVISU unter **Benutzeroberfläche** anstelle der ``smarthomeNG``
Seiten ausgewählt werden.

smartVISU prüft dann, ob eine angeforderte Seite unter ``manuell`` vorhanden ist und benutzt diese Seite. Falls
die angeforderte Seite unter ``manuell`` nicht gefunden wird, wird sie aus den ``smarthome`` Seiten geladen.


Das Vorgehen hierzu ist auch unter :doc:`/visualisierung/automatic_generation` im Abschnitt
**Manuell erstellte Seiten** beschrieben.

Weitere Dokumentation
---------------------

Alle weiteren Informationen zur Visualisierung mit smartVISU sind unter :doc:`/visualisierung/visualisierung`
beschrieben.

