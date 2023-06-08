
.. index:: Admin GUI; Items
.. index:: Items; Admin GUI

=====
Items
=====

Unter **Items** können die in SmartHomeNG Eigenschaften der eingelesenen Items angezeigt werden. Außerdem können die zur
Verfügung stehenden Itemstruktur-Templates angezeigt werden.


.. index:: Itemtree
.. index:: Items; Itemtree
.. index:: Items; Item Baum

Item Baum
=========

Hier kann die Baum-Struktur der geladenen Items angezeigt werden. Außerdem können die Eigenschaften und Attribute eines
ausgewählten Items angezeigt werden.

.. note::

    Die Baum-Struktur zeigt die in SmartHomeNG geladenen Items an. Wenn während der Laufzeit von SmartHomeNG Änderungen
    an den Item Definitionen in den Konfigurationsdateien vorgenommen werden, so wird dieses hier bis zu einem Neustart
    von SmartHomeNG nicht sichtbar.


.. image:: assets/items-itemtree.jpg
   :class: screenshot

Der Item Baum kann die Items mit dem vollen Pfad-Namen oder verkürzt nur mit dem Item Namen (wie im Screenshot oben)
anzeigen. Das gewünschte Verhalten kann unter System/Konfiguration im Tab Admin Modul eingestellt werden. Dort kann
auch eingestellt werden, ab wieviel eingegebenen Zeichen die Suche beginnen soll.

In den rechts angezeigten Item Informationen kann der Wert des Items live angepasst werden.


Item Monitoring
---------------

Auf dem Tab **Überwachte Items** können die Item Werte und deren Veränderungen gemonitored werden. Dazu werden vorher
die Items im Item-Tree ausgewählt und mit dem Button **Überwachen** über den Items Details die Überwachung aktiviert
bzw. deaktiviert.

Diese Überwachung kann bei der Entwicklung von Logiken, eval-Ausdrücken oder User-Functions hilfreich sein, da die
Veränderung von Items, welche an völlig unterschiedlichen Stellen im Item-Tree definiert sind, übersichtlich in einer
Tabelle dargestellt wird.


.. image:: assets/items-item-monitoring.jpg
   :class: screenshot


|

Item Konfiguration
==================

Hier können Dateien zur Definition von Items bearbeitet werden. Auf der linken Seite können Item-Konfigurationsdateien
angelegt, gelöscht oder zur Bearbeitung ausgewählt werden.

.. image:: assets/items-configuration.jpg
   :class: screenshot

Eine Dialog-gestützte Konfiguration von Items (analog zur Plugin Konfiguration) wird in einem kommenden Release von
SmartHomeNG hinzu kommen.


Es können Item Struktur Templates angelegt werden, um sich wiederholende Strukturen einfacher zu verwalten. Item
Strukturen können in Plugins und individuell für die Installation von SmartHomeNG angelegt werden.


Struktur Templates
==================

Hier werden alle zur Verfügung stehenden Struktur Templates angezeigt. Das sind die Struktur Templates die von Plugins
definiert werden, die aktuell in SmartHomeNG konfiguriert sind und die in ../etc/structs.yaml konfigurierten Strukturen.
Strukturen aus Plugins sind daran zu erkennen, dass der Name der Item Struktur mit dem Namen des Plugins beginnt, an den
sich mit einem Punkt getrennt der eigentliche Name der Struktur anschließt.

.. image:: assets/items-structtemplates.jpg
   :class: screenshot


Struktur Konfiguration
======================

Hier können eigene Struktur Templates konfiguriert werden, die in der Datei ../etc/structs.yaml gespeichert werden.

.. image:: assets/items-struct-configuration.jpg
   :class: screenshot


.. index:: Struktur Templates
.. index:: Items; Struktur Templates

