:tocdepth: 4

.. index:: Visualisierung mit smartVISU
.. index:: smartVISU

###############################################
Visualisierung mit smartVISU :greensup:`Update`
###############################################


=========
Überblick
=========

Bis zum SmartHomeNG Release v1.7 wurde die Unterstützung für die smartVISU über die Plugins
visu_smartvisu und visu_websocket implementiert.

- Das erste Plugin (**visu_websocket**) implementiert das Websocket Protokoll über das die smartVISU
  Seiten im Browser mit SmartHomeNG kommunizieren.
- Das zweite Plugin (**visu_smartvisu**) implementiert die Möglichkeit zur automatischen Generierung
  von smartVISU Seiten. Weiterhin ermöglicht dieses Plugin die Installation von Widgets in die smartVISU,
  die die Entwickler von SmartHomeNG Plugins geschrieben und ihren Plugins beigefügt haben.

Mit dem Release v1.8 ändert sich hier einiges:

- Die Kommunikation über das Websocket Protokoll wird von einem neuen Core-Modul übernommen und das
  bisher genutzte Plugin **visu_websocket** ist nun **deprecated**. Das Plugin wird mit dem Release v1.9
  retired werden.
- Das Plugin zur Generierung der smartVISU Seiten **visu_smartvisu** wird durch ein neues Plugin **smartvisu**
  ersetzt, welches zusätzliche Funktionalitäten bietet. Das bisher genutzte Plugin **visu_smartvisu** ist
  nun **deprecated**. Das Plugin wird mit dem Release v1.9 retired werden.

  Das neue Plugin **smartvisu** unterstützt smartVISU ab v2.8. Die Unterstützung für smartVISU v2.7 entfällt.

Das **smartvisu** Plugin implementiert die selben Funktionen wie das bisherige **visu_smartvisu** Plugin:

- eine erweiterte Möglichkeit zum automatischen Generieren von smartVISU Seiten
- die Fähigkeit zur Widget Installation in die smartVISU, die es Plugin Entwicklern ermöglicht,
  mit ihrem  Plugin smartVISU Widgets auszuliefern.

Zusätzlich bietet das neue Plugin folgende Funktionalitäten:

- zur Unterstützung des Widget Assistenten der smartVISU erstellt es eine aktuelle Liste der
  SmartHomeNG Items
- bei der Generierung der Seiten für die Visualisierung wird geprüft, ob veraltete Widgets der smartVISU genutzt werden

..
    - structure definition file ...


===========================
Generierung der Visu Seiten
===========================

Die Generierung der Visu Seiten erfolgt (wenn sie konfiguriert ist) beim Start von SmartHomeNG durch ein Plugin.
Mit der Version 1.8 von SmartHomeNG gibt es hier einige Neuerungen.

.. hint::

    Die folgenden Informationen (auch die über die Navigation links zugänglichen Seiten) setzen voraus, dass ein
    Grundverständnis der smartVISU vorhanden ist.

.. toctree::
   :maxdepth: 4
   :hidden:
   :titlesonly:

   changes_in_1.8
   automatic_generation
   item_attributes
   install_widgets
   plugin_widgets


.. index:: smartVISU; Definition der Navigationsstruktur

============================================
Optionale Definition der Navigationsstruktur
============================================

Ab SmartHomeNG v1.8 ist es möglich an zentraler Stelle die Struktur der Navigation zu definieren. Diese
zentralen Definitionen haben Vorrang vor der Struktur, die sich durch die Abarbeitung des Item-Trees ergibt.

Weitergehende Informationen sind unter :doc:`/visualisierung/automatic_generation` im Abschnitt
**Navigation Structure Definition** zu finden.


.. index:: smartVISU; Kommunikation mit der Visu

==========================
Kommunikation mit der Visu
==========================

Die Kommunikation zwischen SmartHomeNG und der smartVISU (Visualisierung im Browser) erfolgt über das Websocket
Protokoll. Eine direkte Kommunikation zwischen dem smartVISU Server und SmartHomeNG findet zur Laufzeit nicht
statt.

.. toctree::
   :maxdepth: 4
   :hidden:
   :titlesonly:

   websocket_communication
   reverse_proxy

