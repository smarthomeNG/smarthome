.. index:: Plugins; rrd
.. index:: rrd

===
rrd
===

.. image:: webif/static/img/rrdtool-logo-dark.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Das `RRDTool <https://oss.oetiker.ch/rrdtool/>`_  ist ein weitverbreitetes Tool um Zeitreihen von Messdaten aufzuzeichnen.
Dieses Plugin stellt die Möglichkeit bereit Itemwerte an das RRDTool weiterzugeben.

Anforderungen
=============

Notwendige Software
-------------------

Das Python Paket ``rrdtool`` und die entsprechenden Libraries für das Betriebssystem müssen installiert sein. 
Letzteres muss manuell erfolgen:

.. code:: bash

    sudo apt-get install librrd-dev libpython3-dev

Das Python Paket wird über die ``requirements.txt`` automatisch beim Start installiert.


Vergleich zwischen Datenbank-Plugin, InfluxDB und rrdtool:
----------------------------------------------------------

RRD
+ ein stabiles, zuverlässiges Werkzeug
+ wird in vielen Datenprotokollierungs- und Grafiktools verwendet
- zähe Weiterentwicklung in den letzten Jahren
- Werte werden nur in bestimmten Abständen aufgezeichnet und nicht dann, wenn eine Änderung eintritt

Datenbank-Plugin
+ Unterstützung für viele verschiedene Datenbanken wie SQLite, MySQL/MariaDB usw.
+ genaue Protokollierung der Änderungszeiten
+ mehr Analysefunktionalität
+ im SmartHomeNG Kern gut integriert
- keine einstellbare Datenreduktion, nur Zeitbegrenzung der Aufzeichnung

InfluxDB-Plugin
+ Unterstützung für Influx Datenbank
+ speziell entwickelt für Zeitreihen
+ genaue Protokollierung der Änderungszeiten
+ unter Verwendung von Grafana sehr gute Analysefunktionalität
+ Datenreduktion voreinstellbar

Das RRD-Plugin und das Datenbank-Plugin können nur dann zusammen für ein Item verwendet werden,
wenn beim RRD Plugin die Bereitstellung der Series Funktion unterdrückt wird.

Konfiguration
=============

Die Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/rrd` beschrieben.


Der Plugin Parameter ``step`` bestimmt den Zyklus mit dem alle Itemwerte aufgezeichnet werden.
Werteänderungen von Items zwischen den ``step`` werden **nicht** berücksichtigt.

.. important:: Änderung gewünscht?
   Soll das noch geänderte werden das die Items auf jeden Fall aufgezeichnet und im Zeitbereich eines
   Step in die Datenbank geschrieben werden? 
   Funktioniert das mit der lib.rrdtool?

Funktionen
----------

Das Plugin stellt für jedes Item das für die Verwendung mit dem Plugin konfiguriert wurde eine Datenbankfunktion bereit.

``sh.item.db(function, start, end='now')``

Diese Funktion liefert Werte unter Berücksichtigung der nachfolgend erläuterten Funktion und dem Zeitrahmen ``start`` und ``end``.

Derzeit unterstützte Funktionen für die Datenaufbereitung sind:

   * `avg`: Durchschnittswert
   * 'raw': wie Durchschnittswert, aufgenommen um den Parameter ``raw`` bei der SmartVISU nicht ändern zu müssen
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
   * `m`: month
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

    Versorgung:
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

Aktuell hat das Plugin ein Webinterface zur Anzeige der Konfiguration der Items und des aktuellen Wertes.
