
.. role:: redsup
.. role:: bluesup
.. role:: darkbluesup
.. role:: greensup
.. role:: blacksup

.. index:: smartVISU; Automatische Generierung

========================
Automatische Generierung
========================

Im Vergleich zum **visu_smartvisu** Plugin der vorhergehenden SmartHomeNG Releases, wurden die
Möglichkeiten zur automatischen Generierung von Seiten für die smartVISU erweitert. Die
bisherigen Features sind mit einer Ausnahme auch im neuen **smartvisu** Plugin vorhanden. Die
Version 3 des Nutzdaten Protokolls wurde nicht erneut implememtiert. Daher entfällt die Unterstützung
für smartVISU v2.7. Unterstützt werden nun smartVISU v2.8 und v2.9 und folgende.

Neu hinzugekommen sind folgende Features:

- **Deprecated Widget Warnings**: Ab dem auf v2.9.2 folgenden Release liefert die smartVISU informationen
  welche Widgets der smartVISU als veraltet (deprecated) gekennzeichnet wurden und welche Widgets entfernt
  wurden.
- **Navigation Structure Definition**: Bisher wurde die Navigation der smartVISU strikt in der Reihenfolge
  erzeugt, in der die Items beim Start von SmartHomeNG eingelesen werden. Nun ist es möglich, diese
  Navigations-Struktur (inclusive Icons und Sidebar Infos) in einer zentralen Datei zu konfigurieren und
  damit die Reihenfolge aus den Item-Definitionen zu übersteuern.
- **Pages from multiple sub-trees**: Items aus mehreren unterschiedlichen Sub-Trees können zusammen in eine
  Seite der Visualisierung generiert werden.


Die zusätzlichen Item Attribute, die vom **smartvisu** Plugin zur Nutzung in den Item Definitionen definiert
werden, sind auf der Seite :doc:`item_attributes` im Detail beschrieben.


Diese Seite und die zugehörien Unterseiten sollen einige der Möglichkeiten aufzeigen, die sich durch die
Erweiterungen bieten. Es ist auch möglich einen Teil der Seiten generieren zu lassen und einen anderen Teil der
Seiten manuell zu erstellen.


