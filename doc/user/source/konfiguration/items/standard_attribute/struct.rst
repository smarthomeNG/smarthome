
.. index:: Standard-Attribute; struct
.. index:: struct; Item-Struktur Template

.. index:: Items; Item-Struktur Template
.. index:: Items; struct
.. index:: Items; Template
.. index:: Item-Struktur Template

.. role:: bluesup
.. role:: redesup

`struct` :bluesup:`Update`
--------------------------

Eine Reihe von Plugins benötigt eine bestimmte Item Struktur bzw. eine größere Zahl an Items um sinnvoll zu funktionieren.
Diese Items müssen dazu innerhalb des Item-Trees als Teilbaum angelegt werden (zum Teil auch mehrfach).

**Seit SmartHomeNG v1.6** können Plugin jetzt diese Strukturen als Templates zur Verfügung stellen, die dann mit Hilfe
des **struct**-Attributs in den Item-Tree eingefügt werden können. Dazu muss bei dem Item an dessen Stelle der Teilbaum
eingefügt werden soll, der Name des Templates (der Item-Struktur) angegeben werden.

Weitere Informationen zu **structs** sind auf der Seite :doc:`Konfiguration/structs </konfiguration/item_structs>`
zu finden.


Selbst definierte Item-Strukturen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Zusätzlich zu den Item-Strukturen, die Plugins als Template mitbringen, können eigene Strukturen angelegt werden. Diese
Strukturen werden in der Konfigurationdatei **../etc/struct.yaml** abgelegt werden.
(Siehe :doc:`Konfiguration/Konfigurationsdateien/struct.yaml </konfiguration/konfigurationsdateien/struct>`)

