.. index:: Plugins; thz
.. index:: thz

===
thz
===

Abfrage von Tecalor- oder Stiebel-Eltron-Wärmepumpen (integrierte Wärmepumpen LWZ/THZ 30x/40x).

.. important::

   Dieses Plugin ist als **develop** gekennzeichnet. Es kann sein, dass es noch nicht alle
   Funktionen unterstützt oder noch fehlerhaft ist.


Voraussetzungen
================

Das Plugin benötigt ``pySerial`` sowie eine serielle Schnittstelle, die mit dem Wartungsport der
Wärmepumpe verbunden ist. Eine Beschreibung der Verkabelung findet sich unter
http://robert.penz.name/heat-pump-lwz.

Getestet wurde das Plugin mit der THZ 404 SOL (Softwarestand 5.39, Software-IDs 5993 und 7278)
sowie der THZ 303i (Softwarestand 4.39). Laut Berichten aus dem FHEM-Forum funktioniert der
zugrunde liegende Perl-Code auch mit weiteren Modellen (303, 304, 403).


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/thz` beschrieben.

Für schreibbare Parameter gilt der jeweilige Parametername inklusive der im Wärmepumpen-Handbuch
angegebenen Parameternummer (Präfix ``pXX``). Details zu deren Bedeutung sind dem Handbuch der
Wärmepumpe zu entnehmen.
