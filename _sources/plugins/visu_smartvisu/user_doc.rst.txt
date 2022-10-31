
.. index:: Plugins; visu_smartvisu (smartVISU Unterstützung)
.. index:: visu_smartvisu
.. index:: smartVISU; visu_smartvisu Plugin

==============
visu_smartvisu
==============

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Mit dem Plugin **visu\_smartvisu** können aus der Definition der Items
in SmartHomeNG automatisch Visuseiten erstellt werden. Diese Visu Seiten
werden im Verzeichnis ``smarthome`` des ``pages`` Verzeichnisses der smartVISU
erstellt. Das Plugin unterstützt smartVISU Versionen von v2.7 bis zur releasten
v2.9 (master branch).


.. attention::

    Dieses Plugin ist veraltet (deprecated) und wird nicht mehr weiter gepflegt. Es wird dringend empfohlen stattdessen
    das Plugin **smartvisu** zu nutzen, welches einen erweiterten Funktionsumfang hat.

    Dieses Plugin wird in einem der kommenden Releases aus SmartHomeNG entfernt werden.

.. Ab SmartHomeNG v1.7.x werden
    die Visu Seiten im Verzeichnis ``smarthomeng`` erstellt! Dazu bitte beim
    entsprechenden Plugin die Doku lesen.

.. .. important::
       Änderung ab SmartHomeNG v1.7.x:

       Ab SmartHomeNG v1.7.x werden die Visu Seiten nicht mehr im Verzeichnis ``pages/smarthome``, sondern
       im Verzeichnis ``pages/smarthomeng`` erstellt.

       Ein evtl. existierendes Verzeichnis ``smarthome`` im ``pages`` Verzeichnis der smartVISU bitte löschen
       um Verwechselungen und den Aufruf veralteter Visu Seiten zu vermeiden.


Mischung von generierten und manuell erstellten Seiten
------------------------------------------------------

In der smartVISU ist es möglich generierte und manuell erstellte Seiten zu mischen. Dazu muss in der
smartVISU unter ``pages`` ein weiteres Verzeichnis (z.B. mit dem Namen ``manuell`` angelegt werden und
diese Seiten müssen in der Konfiguration der smartVISU unter **Benutzeroberfläche** anstelle der ``smarthome``
Seiten ausgewählt werden.

smartVISU prüft dann, ob eine angeforderte Seite unter ``manuell`` vorhanden ist und benutzt diese Seite. Falls
die angeforderte Seite unter ``manuell`` nicht gefunden wird, wird sie aus den ``smarthome`` Seiten geladen.

Das Vorgehen hierzu ist auch unter **Visualisierung/Manuell erstellte Seiten** beschrieben.


Empfohlenes Vorgehen für manuell erstellte Seiten
-------------------------------------------------

Bei dem Wunsch einzelne Seiten manuell zu erstellen, ist es empfehlenswert zum Anfang die gesamten Seiten
generieren zu lassen und dabei dir vollständige Navigation aufzubauen. Anschließend können einzelne Seiten aus
dem Bereich ``smarthome`` in den Bereich ``manuell`` kopiert und manuell angepasst werden. Alternativ können
diese Seiten unter ``manuell`` auch vollständig manuell erstellt werden.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/visu_smartvisu` beschrieben.


Weiterführende Informationen
============================

Genauer sind die Möglichkeiten unter :doc:`/visualisierung/visualisierung` beschrieben.
