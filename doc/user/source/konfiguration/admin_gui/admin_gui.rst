
.. index:: Konfiguration über die GUI

.. role:: bluesup
.. role:: redsup

==========================
Konfiguration über die GUI
==========================

SmartHomeNG kann vollständig über die graphische Oberfläche konfiguriert werden. Für einen Teil der Konfiguration stehen
Dialoge zur Verfügung, die Erläuterungen zu den einzelnen Einstellungen geben und evtl. vorhandene Standardwerte
anzeigen. Für den Rest der Konfiguration stehen Editoren zur Verfügung, mit denen die jeweiligen YAML Dateien bearbeitet
werden können.

.. note::

   Die Beschreibung der vollständigen Funktionalität der graphischen Administrationsoberfläche  befindet sich im
   Abschnitt :doc:`Administrations-Interface </admin/admin>`

Um eine SmartHomeNG Installation zu erhalten die etwas sinnvolles tun kann, müssen mindestens folgende Konfigurationen
durchgeführt werden:

- :doc:`Systemkonfiguration </konfiguration/admin_gui/admin_gui_system>`
- :doc:`Konfiguration von Plugins </konfiguration/admin_gui/admin_gui_plugins>`
- :doc:`Konfiguration von Items </konfiguration/admin_gui/admin_gui_items>`


Konfigurations-Dialoge
======================

Konfigurations-Dialoge bestehen standardmäßig aus 4 Spalten:

- **Parameter**: Name der Parameter
- **Wert**: Zu konfigurierender Wert für die Parameter - Dieses können Freitext-Felder oder Drop-Down Listen sein

  Wenn in einem Dialogfeld kein Wert eingegeben ist, wird dort der in diesem Fall verwendete Standardwert angezeigt.

  Inhalte von Feldern die als Drop-Down Liste dargestellt werden, können durch klicken auf das **x** neben dem Inhalt
  gelöscht werden.
- **Typ**: Datentyp der einzugebenden Werte
- **Beschreibung**: Erläuterung der Parameter

.. hint::

   Wenn unter **Dienste** die Sprache der graphischen Oberfläche umgestellt wird, ändert sich auch die Sprache der
   Beschreibungstexte.

Die Dialoge können nach jeder der 4 Spalten sortiert werden. Dieses ist bei längeren Dialogen hilfreich, da es das
auffinden eines gesuchten Parameters erleichtert.


Editoren für YAML Konfigurationen
=================================

Für die Teile der SmartHomeNG Konfiguration für die keine Konfigurations-Dialoge zur Verfügung stehen (Items, Strukturen,
Szenen), gibt es auf der jeweiligen Konfigurationsseite der GUI ein Editor mit dem die YAML Konfigurationen bearbeitet
werden können.


.. toctree::
   :maxdepth: 5
   :hidden:
   :titlesonly:

   admin_gui_system
   admin_gui_plugins
   admin_gui_items



