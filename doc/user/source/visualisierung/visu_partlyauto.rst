.. index:: smartVISU Autogenerierung; Manuell erstellte Visu Seiten
.. index:: smartVISU; Manuell erstellte Visu Seiten

Manuell erstellte Seiten
========================

Normalerweise werden durch das Plugin alle notwendigen Seiten für smartVISU generiert und im Bereich **pages** unter
**smarthome** abgelegt.

Diese Seiten werden in smartVISU dann folgendermaßen ausgewählt:

.. figure:: assets/config_fullauto.jpg
   :alt: Vollständige Autogenerierung


smartVISU bietet jedoch eine Möglichkeit um manuell erstellte Seiten und automatisch generierte Seiten zu mischen.

Dazu muss man in smartVISU einen ordner unter **pages** anlegen und die manuell erstellten Seiten dort hineinkopieren.
Anschließend muss man in smartVISU dann zur Darstellung diesen Bereich auswählen:

.. figure:: assets/config_partlyauto.jpg
   :alt: Teil-Autogenerierung


Beim Zugriff auf Seiten versucht smartVISU nun die entsprechende Seite aus dem unter **pages** angelegten Bereich zu
laden. Wird die angeforderte Seite dort nicht gefunden, versucht smartVISU die Seite aus dem Bereich **smarthome** zu
laden.

Man kann also SmartHomeNG die Seiten vollständig generieren lassen und eine Seite, die manuelle Modifikationen enthalten
soll aus dem Ordner **smarthome** in den unter **pages** angelegten Bereich kopieren und anschließend in dieser Kopie
die gewünschten Modifikationen vornehmen.

.. note::

   Die modifizierte Seite erhält keine Änderungen mehr aus SmartHomeNG.

   Falls Änderungen aus SmartHomeNG in diese Seite übernommen werden sollen, müssen diese aus der generierten Seite
   (im Ordner **smarthome**) in die manuell modifizierte Seite übernommen werden.

   Alternativ kann die generierte Seite erneut kopiert werden und die Änderungen können dort eingearbeitet werden,
   wie dieses ursprünglich erfolgt ist.

