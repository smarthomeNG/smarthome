.. index:: Items; Konfigurationsdateien /items/*.yaml
.. index:: Konfigurationsdateien; /items/*.yaml

items/\*.yaml
=============

.. _`item configuration files`:


---------------------------------------------
Item Definitionen im Verzeichnis **../items**
---------------------------------------------

Die Items repräsentieren das Herz der Konfiguration von SmartHomeNG. Auf ein Item kann von jeder Logik,
jedem Plugin und jedem eval-Ausdruck zugegriffen werden.

Im Verzeichnis **../items** kann eine beliebige Anzahl von Konfigurationsdateien erzeugt werden und jede
Konfigurationsdatei kann eine beliebige Anzahl von Item Definitionen enthalten. Das Verzeichnis enthält yaml
Dateien (oder Dateien im alten .conf Format) mit den Definitionen der Items, die durch SmartHomeNG genutzt
werden sollen. Der Name der yaml Datei kann beliebig sein, solange die Extension `.yaml` ist.

Die Konfigurationsdateien werden in alphabetischer Reihenfolge verarbeitet. Wenn ein Item in mehreren Dateien
definiert ist, werden die Definitionen (Attribute) aus später verarbeiteten Dateien in die bereits eingelesene
Item Definition eingearbeitet. Wenn dabei ein bereits definiertes Attribut erneut definiert wird, so "gewinnt"
die später eingelesene Definition.

Wenn eine yaml Datei einen syntaktischen Fehler enthält, wird die **gesamte** Datei nicht verarbeitet. Im Log
von SmartHomeNG wird vermerkt, dass die yaml Datei fehlerhalft ist, und wo (welche Zeile) der Fehler vermutet
wird.


Weitere Details zur Konfiguration von Items sind :doc:`hier <items>` zu finden.


