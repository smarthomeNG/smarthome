.. index:: Plugins; trovis557x
.. index:: trovis557x

==========
trovis557x
==========

Das Plugin liest Daten von SAMSON TROVIS 557x Automationssystemen (Heizungsreglern) über Modbus
aus. Unterstützt werden alle Modbus-Modelle: 5571, 5573, 5576, 5578 und 5579. Einzelne Teile des
Projekts lassen sich außerdem zur Anbindung des Reglers an Trovis View nutzen.

Voraussetzungen
================

Der Regler wird über eine Modbus-Verbindung angesprochen, seriell (RTU, z.B. über einen
USB/RS485-Adapter) oder per TCP über das Netzwerk. Die Stationsadresse muss am Regler passend zur
Konfiguration eingestellt sein (Trovis: PA6 - Modbus, ST.-NR; Werkseinstellung 255, laut
Modbus-Spezifikation muss der Wert kleiner oder gleich 247 sein).

Weitere Details zur Modbus-Einrichtung sind im
`Wiki des Projekts <https://github.com/Tom-Bom-badil/samson_trovis_557x/wiki>`_ beschrieben.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/trovis557x`
beschrieben.

Item-Attribute
--------------

**trovis557x_var** ordnet ein Item einem bestimmten Register oder Coil des Reglers zu. Der Wert ist
der Kurzname des gewünschten Werts bzw. Bits; die vollständige Liste der verfügbaren Kurznamen ist
im `Wiki des Projekts <https://github.com/Tom-Bom-badil/samson_trovis_557x/wiki>`_ dokumentiert.

**liste** muss bei jedem vom Plugin genutzten Item als leere Liste (``liste: []``) angelegt werden;
das Plugin füllt sie zur Laufzeit mit Buswert, umgerechnetem Wert und Einheit bzw. Listentext.

**werte** wird bei Registern verwendet, die stufenweise mit Werten belegt sind.

**invalid_to_zero** (optional) setzt den Wert 32767 (entspricht ungültig/nicht verfügbar) auf 0,
für ausgeschaltete oder nicht verfügbare Register.

Beispiele
=========

Das Plugin liefert unter ``shNG-items/trovis.yaml`` eine vollständige Beispiel-Items-Datei mit
Konfiguration für unterschiedliche Reglermodelle und Hydraulikschemata, die sich nach
``items/trovis.yaml`` kopieren und an die eigene Anlage anpassen lässt::

    heizung:
        regler:
            modell:
                desc: Modellbezeichnung
                type: num
                trovis557x_var: Geraetekennung
                liste: []
                visu_acl: ro

            seriennummer:
                desc: Regler-ID
                type: num
                trovis557x_var: Regler-ID
                liste: []
                visu_acl: ro
