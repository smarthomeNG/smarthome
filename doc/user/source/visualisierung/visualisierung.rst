:tocdepth: 4

.. role:: redsup
.. role:: bluesup
.. role:: darkbluesup
.. role:: greensup
.. role:: blacksup

.. index:: Visualisierung mit smartVISU
.. index:: smartVISU; Visualisierung mit smartVISU

############################
Visualisierung mit smartVISU
############################


=========
Überblick
=========

Die Unterstützung für die smartVISU besteht aus zwei Teilen:

- Die Kommunikation über das Websocket Protokoll, über das die smartVISU Seiten im Browser mit SmartHomeNG
  kommunizieren, wird vom Core-Modul **websocket** übernommen.
- **Das smartvisu Plugin muss geladen sein**. Es aktiviert das Nutzdatenprotoll für die smartVISU im
  Websocket Modul. Wenn dieses Plugin nicht geladen ist, reagiert das Websocket Modul nicht auf Kommandos von der
  smartVISU.

Das **smartvisu** Plugin unterstützt smartVISU ab v2.8 und bietet folgende Funktionen:

- eine erweiterte Möglichkeit zum automatischen Generieren von smartVISU Seiten
- die Fähigkeit zur Widget Installation in die smartVISU, die es Plugin Entwicklern ermöglicht,
  mit ihrem  Plugin smartVISU Widgets auszuliefern.
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
   features
   navigation_structure
   multiple_subtrees
   deprecated_widgets
   top_navigation
   item_attributes
   beispiel
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
