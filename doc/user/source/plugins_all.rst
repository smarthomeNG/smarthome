Plugins
=======

Es gibt eine Vielzahl von Plugins, welche die Funktionalität von SmartHomeNG erweitern. Die
Informationen auf diesen Seiten wird aus den Metadaten-Dateien der Plugins ermittelt.

Ein Klick au den Plugin-Namen in den Plugin Listen führt zur **Konfigurationsdokumentation** des
jeweiligen Plugins. Falls zu dem Plugin keine Metadaten vorliegen, wird auf die (englischsprachige)
README Datei des jeweiligen Plugis verlinkt.

Einige Plugins verfügen über eine zusätzliche Dokumentation. Diese Plugins haben eigene Einträge
in der Navigationsleiste.

.. note::

   Diese Seiten werden vollständig automatisch aus den Plugins des Repositories generiert.
   Deshalb:
   
   - kann nur der Autor des jeweiligen Plugins sicherstellen, dass keine ungewünschten Mischungen der Sprache (Deutsch/Englisch) vorkommen.
   - kann keine Dokumentation für Plugins außerhalb des SmartHomeNG Plugin-Repositories in die Dokumentation aufgenommen werden.
   
   Hinweise auf weitere Plugins, die sich nicht im SmartHomeNG Repository befinden, sind auf der `entsprechenden Wiki Seite <https://github.com/smarthomeNG/smarthome/wiki/Plugins-außerhalb-des-SmartHomeNG-Repository>`_ zu finden.

Die Plugins sind in die folgenden Kategorien unterteilt:

.. toctree::
   :maxdepth: 1
   :glob:
   :titlesonly:

   /plugins_doc/plugins_system
   /plugins_doc/plugins_gateway
   /plugins_doc/plugins_interface
   /plugins_doc/plugins_protocol
   /plugins_doc/plugins_web
   /plugins_doc/plugins_unclassified


Wenn ein Plugin Autor die Informationen auf diesen Seiten aktualisieren möchte, muss er nur
die Metadaten Datei **plugin.yaml** in seinem Plugin aktualisieren. Beim nächsten Bau dieser
Dokumentation werden dann diese aktualisierten Informationen automatisch mit aufgenommen.

Wenn ein Plugin Autor eine Seite für sein Plugin links in die Navigation einklinken möchte, muss
er nur eine Datei **user_doc.rst** in seinem Plugin Verzeichnis anlegen. Das Vorgehen ist in
der Entwickler Dokumentation beschrieben.

Informationen zur Erstellung eigener Plugins sind in der Entwickler Dokumentation zu finden.
Die Entwickler Dokumentation ist nur in englischer Sprache verfügbar.

