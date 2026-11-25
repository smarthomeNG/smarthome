.. index:: Plugins; odlinfo
.. index:: odlinfo

=======
odlinfo
=======

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Dieses Plugin liefert die Gamma-Ortsdosisleistung (ODL) in µSv/h von Messstationen in Deutschland,
bereitgestellt vom Bundesamt für Strahlenschutz (BfS). Weitere Informationen unter
https://odlinfo.bfs.de.

.. important::

   Die Datensätze werden von der BfS-Schnittstelle nur stündlich aktualisiert. Der Parameter
   **cycle** sollte daher nicht deutlich kürzer als 3600 Sekunden gewählt werden, um die
   Schnittstelle nicht unnötig oft abzufragen.

Die Daten sind urheberrechtlich geschützt (Bundesamt für Strahlenschutz). Bei einer Veröffentlichung
ist die Quelle zu nennen, die Nutzungsbedingungen sind unter
https://www.imis.bfs.de/geoportal/resources/sitepolicy.html einzusehen. Die Datenschnittstelle
selbst darf nicht direkt verlinkt werden.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/odlinfo`
beschrieben.

Ein Item mit den Attributen **odl_station** und **odl_data_type** wird vom Plugin automatisch mit
den Messwerten der angegebenen Station aktualisiert.

Die odlinfo-Messstellenkennung einer Station lässt sich über die Karte auf https://odlinfo.bfs.de
ermitteln: Station auswählen und die Kennung aus der URL ablesen (z.B. für 86949 Windach:
https://odlinfo.bfs.de/DE/aktuelles/messstelle/091811461.html → ID = 091811461). Alternativ zeigt
das Webinterface des Plugins sowohl die internationale ID (z.B. DEZ1419) als auch die
odlinfo-Messstellenkennung (z.B. 091811461) aller Stationen an. Beide Formen können als Wert für
**odl_station** verwendet werden.

Web Interface
=============

Das Webinterface zeigt drei Reiter:

Stationen
---------

Listet alle über die Schnittstelle verfügbaren Messstationen mit ID, Messstellenkennung,
Postleitzahl, Name, aktuellem Messwert (Gesamt, kosmisch, terrestrisch), Einheit, Prüfstatus,
Messzeitraum und Status.

Items
-----

Zeigt die Items an, die über **odl_station** und **odl_data_type** mit einer Messstation verknüpft
sind, mit aktuellem Wert sowie Zeitpunkt der letzten Aktualisierung und Änderung.

Plugin-API
----------

Listet die öffentlichen Funktionen des Plugins mit Signatur und Beschreibung, wie sie z.B. in
Logiken aufgerufen werden können.
