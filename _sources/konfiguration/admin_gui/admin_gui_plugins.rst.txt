
.. index:: Konfiguration über die GUI; Plugins

.. role:: bluesup
.. role:: redsup


Konfiguration von Plugins
=========================

Die Konfiguration der Plugins findet im Menü **Plugins** durch Auswahl von **Konfiguration** statt.

hier können Plugins aus der Liste der installierten Plugins hinzukonfiguriert und ihre Parameter angepasst werden.

.. image:: /admin/assets/plugin-configlist.jpg
   :class: screenshot


Hinzufügen von Plugins
----------------------

Durch klicken auf den Button **Plugin hinzufügen** (oben rechts auf der Seite) wird ein Dialog geöffnet, in dem ein
Plugin ausgewählt werden kann, um es der aktuellen Konfiguration hinzuzufügen.

.. image:: /admin/assets/plugin-addlist.jpg
   :class: screenshot

Zum Hinzufügen die gewünschte Plugin Kategorie aufklappen und auf die Zeile mit dem gewünschten Plugin klicken. Dadurch
öffnet sich ein Dialog, in dem ein eindeutiger Name für diese Plugin Instanz gewählt werden muss. Bei Plugins, von
denen nur eine Instanz konfiguriert wird, kann einfach der Name des Plugins gewählt werden. Bei Plugins, von denen
mehrere Instanzen konfiguriert werden sollen, muss hier für jede Instanz ein individueller Name gewählt werden.

Plugins die neu hinzugefügt wurden, sind erstmal deaktiviert. Aktivieren kann man Sie dadurch, dass sie konfiguriert
werden.


Konfiguration eines Plugins
---------------------------

Durch klicken auf eine Zeile der bereits konfigurierten Plugins wird der zum Plugin gehörige Konfigurationsdialog
gestartet.

Die Liste der konfigurierbaren Parameter unterscheidet sich von Plugin zu Plugin. Allen Konfigurationen gemein ist
der Schiebeschalter oben links im Dialog. Wenn dieser nach links geschoben ist, ist das Plugin deaktiviert. Das
bedeutet, dass es beim nächsten Neustart von SmartHomeNG nicht geladen wird. Dadurch kann schnell ein Plugin aus
der aktiven Konfiguration entfernt werden, ohne die Einstellungen der Parameter des Plugins zu verlieren.

.. image:: /admin/assets/plugin-config.jpg
   :class: screenshot

Die Konfiguration der einzelnen Parameter geschieht analog zum Dialog der Systemkonfiguration.


