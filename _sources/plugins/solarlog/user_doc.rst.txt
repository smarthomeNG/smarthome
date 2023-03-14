
.. index:: Plugins; solarlog
.. index:: solarlog

========
solarlog
========

Dieses Plugin kann eine Webseite vom SolarLog-Protokolliergerät lesen und Werte zurückgeben.
Es wurde 2013 von Niko Will erstellt und 2019 von Bernd Meiners zu einem SmartPlugin umgebaut.
Es wurde 2017 von klab für SolarLog-Geräte mit Firmware >= 3.x neu geschrieben und 2020 von
Christian Michels in das alte Plugin integriert.

Requirements
============

Dieses Plugin hat keine Anforderungen oder Abhängigkeiten.

Todo
====

Webinterface mit den geparsten Daten aufbereiten

Konfiguration
=============

Diese Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/solarlog` beschrieben.


plugin.yaml
-----------

.. code-block:: yaml
    :caption: logic.yaml

    Solarlog:
       plugin_name: solarlog
       host: http://solarlog.fritz.box/

Attribute
~~~~~~~~~

- ``fw2x``: Gibt an, ob Firmware <= 2.x ist.
- ``host``: Gibt den Hostnamen des SolarLog an.
- ``cycle``: Bestimmt den Zyklus für die Abfrage des SolarLog.

items.yaml
----------

Die Format Details des SolarLog müssen bekannt sein, um die gültigen Werte für dieses Plugin zu definieren.
Das Plugin fordert lediglich die JavaScript-Dateien vom Gerät an und analysiert sie.
Ähnlich verhält es sich mit der Webseite, wenn die URL eines SolarLog im Browser aufgerufen wird.
Eine Beschreibung des Formats und der entsprechenden Variablen findet sich hier:
https://www.photonensammler.de/wiki/doku.php?id=solarlog_datenformat

solarlog
~~~~~~~~

Dies ist das einzige Attribut für Items. Um Werte aus dem SolarLog-Datenformat abzurufen,
müssen lediglich die Variablennamen wie auf der oben beschriebenen Site verwendet werden.

Wenn Werte aus einer Array-Struktur wie den PDC-Wert aus dem Sekundenstring des ersten Inverters verwendet
werden soll, muss der Variablenname underscore inverter-1 underscore string-1 verwendet werden:

``var [\_ inverter [\_ string]]``

In diesem Beispiel sollten Details zur Verwendung mit Firmware <= 2.x erläutert werden:

.. code :: yaml

    pv:
        pac:
            type: num
            solarlog: Pac
            database: yes
        kwp:
            type: num
            solarlog: AnlagenKWP
            soll:
                type: num
                solarlog: SollYearKWP
        inverter1:
            online:
                type: bool
                solarlog: isOnline
            inverter1_pac:
                type: num
                solarlog: pac_0
                database: yes
            out:
                type: num
                solarlog: out_0
                database: yes
            string1:
                string1_pdc:
                    type: num
                    solarlog: pdc_0_0
                    database: yes
                string1_udc:
                    type: num
                    solarlog: udc_0_0
                    database: yes
            string2:
                string2_pdc:
                    type: num
                    solarlog: pdc_0_1
                    database: yes
                string2_udc:
                    type: num
                    solarlog: udc_0_1
                    database: yes


In diesem Beispiel sollten Details zur Verwendung mit Firmware >= 3.x erläutert werden:

.. code :: yaml

   pv:
       w_gesamt_zaehler:
           type: num
           cache: 'on'
           solarlog: 101
       w_gesamt:
           type: num
           cache: 'on'
           solarlog: 102
       spannung_ac:
           type: num
           cache: 'on'
           solarlog: 103
       spannung_dc1:
           type: num
           cache: 'on'
           solarlog: 104
       wh_heute:
           type: num
           solarlog: 105
           cache: 'on'
       wh_gestern:
           type: num
           cache: 'on'
           solarlog: 106
       wh_monat:
           type: num
           cache: 'on'
           solarlog: 107
       wh_jahr:
           type: num
           cache: 'on'
           solarlog: 108
       wh_gesamt:
           type: num
           cache: 'on'
           solarlog: 109
       wp_generatorleistung:
           type: num
           cache: 'on'
           solarlog: 116


Das ``database: yes`` impliziert, dass auch ein Datenbank-Plugin konfiguriert ist.
Dienst zur Anzeige von Messwerten innerhalb einer Visu.

logic.yaml
----------

Derzeit gibt es keine Logik Konfiguration für dieses Plugin.

Funktionen
==========

Momentan werden von diesem Plugin keine Funktionen bereitgestellt.
