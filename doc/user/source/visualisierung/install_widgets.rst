.. index:: smartVISU; Installation von Widgets

========================
Installation von Widgets
========================


smartVISU Widget-Handling
=========================


Überblick
---------

Plugin Entwickler können mit ihrem Plugin smartVISU Widgets ausliefern, welche die Plugin Daten
visualisieren können. Diese Widgets werden durch das smartVISU Plugin automatisch in die Visu
installiert und stehen ohne weitere Anpassungen in der Visu zur Verfügung. Dadurch können die
Widgets auch direkt in der automatischen Generierung von smartVISU-Seiten eingesetzt werden.

Beispiele für Plugins, welche Widgets mitbringen
------------------------------------------------

- AVM
- Enigma2


Nutzung der Widgets
-------------------

Die README Datei des jeweiligen Plugins sollte Auskunft geben, wie die Widgets aufgerufen werden.
Im Idealfall liegen den Plugins auch Screenshots bei, damit man vorab einen Eindruck des Widgets
bekommt.

Wenn für das smartvisu-Plugin der Parameter ``handle_widgets: True`` gesetzt ist, kopiert es 
die Widgets aus den jeweiligen Plugin-Unterordnern "sv_widgets" in das 
smartVISU-Verzeichnis ./dropins/shwidgets und löscht dieses bei jedem Neustart. Wenn man an einem
Widget Veränderungen vornimmt, muss man in der smartVISU eine Kopie unter anderem Namen erzeugen (z.B.
im Verzeichnis .dropins/widgets oder ./pages/<meineSeiten>/widgets), um zu verhindern dass es bei 
Updates überschrieben wird. Dann muss man sicher stellen, dass der Name des modifizierten Widgets
in den smartVISU-Seiten verwendet wird. 


Einbindung von Widgets in Plugins
---------------------------------

Für Plugin Entwickler, die Widgets mit ihren Plugins ausliefern wollen, is die Lektüre der
`Entwickler Dokumentation des smartvisu Plugins <../../developer/plugins/visu_smartvisu/developer_doc>`_
empfohlen.

