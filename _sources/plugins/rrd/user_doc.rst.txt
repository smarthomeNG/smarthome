.. index:: Plugins; rrd
.. index:: rrd


===
rrd
===


Das `RRDTool <https://oss.oetiker.ch/rrdtool/>`_  ist ein weitverbreitetes Tool um Zeitreihen von Messdaten aufzuzeichnen. 
Dieses Plugin stellt die Möglichkeit bereit Itemwerte an das RRDTool weiterzugeben.



Anforderungen
=============

Notwendige Software
-------------------

Das Paket Rrdtool und die entsprechenden Python Libraries müssen installiert sein.

.. code:: bash

    sudo apt-get install librrd-dev libpython3-dev


Vergleich zwischen Datenbank-Plugin und rrdtool:
------------------------------------------------

Das RRD-Plugin und das Datenbank-Plugin können nicht zusammen für ein einzelnes Element verwendet werden.

RRD
+ ein stabiles, zuverlässiges Werkzeug
+ wird in vielen Datenprotokollierungs- und Grafiktools verwendet
- Die Entwicklung hat in den letzten Jahren nicht stattgefunden

Datenbank-Plugin
+ Unterstützung für viele verschiedene Datenbanken wie SQLite, MySQL/MariaDB usw.
+ genaue Protokollierung der Änderungszeiten
+ mehr Analysefunktionalität

Konfiguration
=============

Die Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/rrd` beschrieben.


plugin.yaml
-----------

Zu den Informationen, welche Parameter in der ../etc/plugin.yaml konfiguriert werden können bzw. müssen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/rrd>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).


items.yaml
----------

Zu den Informationen, welche Attribute in der Item Konfiguration verwendet werden können bzw. müssen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/rrd>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).


logic.yaml
----------

Zu den Informationen, welche Konfigurationsmöglichkeiten für Logiken bestehen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/rrd>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

Funktionen
----------

Zu den Informationen, welche Funktionen das Plugin bereitstellt (z.B. zur Nutzung in Logiken), bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/rrd>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

Das Plugin stellt für jedes Item das für die Verwendung mit dem Plugin konfiguriert wurde eine Datenbankfunktion bereit.

``sh.item.db(function, start, end='now')``

Diese Funktion liefert Werte unter Berücksichtigung der nachfolgend erläuterten Funktion und dem Zeitrahmen ``start`` und ``end``.

Unterstützte Funktionen für die Datenaufbereitung sind:

   * `avg`: Durchschnittswert
   * `max`: Maximalwert
   * `min`: Minimalwert
   * `last`: Letzter eingetragener Wert

Für das Zeitintervall müssen *relative* Anfangs- und Endzeitpunkte zum aktuellen Zeitpunkt angegeben werde.
Der Vorgabewert für das Ende ist ``now`` was einer relativen Verschiebung um ``0`` entspricht.

Die relativen Start- und Endzeitpunkte werden definiert durch ``<Nummer><Intervalleinheit>``
Für die Intervalleinheit können folgende Kennzeichnungen verwendet werden:

   * `i`: minute
   * `h`: hour
   * `d`: day
   * `w`: week
   + `m`: month
   * `y`: year

Beispiele
=========

.. code-block:: yaml

    Aussen:
        name: Aussen
        Temperatur:
            type: num
            rrd: init
            rrd_min: 'yes'
            rrd_max: 'yes'

    Wohnzimmer:
        Temperatur:
            type: num
            rrd: 'yes'

    Versorgung
        Wasser:
            type: num
            rrd_type: counter

Um das Minimum der letzten 24 Stunden zu ermitteln:

.. code-block:: python

    sh.Aussen.Temperatur.db('min', '1d')

Um die Durchschnittstemperatur einer Woche zu ermitteln die vor genau 7 Tagen endete:

.. code-block:: python
    
    sh.Aussen.Temperatur.db('avg', '2w', '1w')


Web Interface
=============

Aktuell hat das Plugin kein Webinterface