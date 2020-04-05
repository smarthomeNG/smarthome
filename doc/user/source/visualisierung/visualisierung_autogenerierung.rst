.. index:: smartVISU; Autogenerierung

========================
Automatische Generierung
========================


Überblick
=========

Im Vergleich zum Visu Plugin der vorhergehenden smarthome.py/SmartHomeNG Releases, wurden die
Möglichkeiten zur automatischen Generierung von Seiten für die smartVISU stark erweitert.
Unterstützt werden smartVISU v2.7, v2.8 und v2.9.

Die zusätzlichen Attribute, die in der item.conf Datei für die Items konfiguriert werden können,
sind in der README Datei des Plugins :doc:`../plugins/visu_smartvisu/README` beschrieben.

Diese Seite und die zugehörien Unterseiten sollen einige der Möglichkeiten aufzeigen, die sich
durch die Erweiterungen bieten. Es ist auch möglich einen Teil der Seiten generieren zu lassen
und einen anderen Teil der Seiten manuell zu erstellen.


Anzeige von zusätzlichen Informationen in der Navigation
--------------------------------------------------------

In der Navigation können eine Reihe zusätzlicher Informationen angezeigt werden.

Die Details sind auf der Seite :doc:`./navigation_zusatzinfos` beschrieben.


Generierung einer Konfigurations-Navigation
-------------------------------------------

Zusätzlich zum Aufbau einer Navigation über die Seiten der Räume, kann eine Navigation über
mehrere Konfigurationsseiten aufgebaut werden.

Die Details sind auf der Seite :doc:`./navigation_configurationseiten` beschrieben.


Trenner in der Navigation
-------------------------

Die Navigation kann durch Trenner unterteilt werden, um die Übersichtlichkeit zu erhöhen.

Die Details sind auf der Seite :doc:`./navigation_trenner` beschrieben.


Unterschiedliche Visu-Styles
----------------------------

Zusätzlich zum von bisherigen Releases unterstützen Standard-Style, wird der Style **black**
unterstützt.

Die Details sind auf der Seite :doc:`./visu_styles` beschrieben.


Unterschiedliche Blockgrößen
----------------------------

Die Blöcke in denen Widgets angezeigt werden, hatten in den bisherigen Releases eine fest
definierte (Mindest-)Größe. Jetzt stehen drei unterschiedliche Mindestgrößen zur Verfügung.

Die Details sind auf der Seite :doc:`./visu_blockgroessen` beschrieben.


Unterschiedliche Blocktypen
---------------------------

Die Blöcke in denen Widgets angezeigt werden, hatten in den bisherigen Releases einen festen
Typ. Nun ist ein Typ **Dual** hinzugekommen.

Die Details sind auf der Seite :doc:`./visu_blocktypen` beschrieben.


Manuell erstellte Seiten
------------------------

In smartVISU können manuell erstellte oder modifizierte Seiten in die Autogenerierung eingemischt werden.

Die Details sind auf der Seite :doc:`./visu_partlyauto` beschrieben.


.. toctree::
   :maxdepth: 4
   :hidden:
   :titlesonly:

   navigation_zusatzinfos
   navigation_configurationseiten
   navigation_trenner
   visu_styles
   visu_blockgroessen
   visu_blocktypen
   visu_partlyauto

