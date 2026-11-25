.. index:: Plugins; luxtronic2
.. index:: luxtronic2

==========
luxtronic2
==========

Das Plugin bindet Heizungssteuerungen mit Luxtronic 2.0 Regler über das Netzwerk an SmartHomeNG an
und liest bzw. schreibt deren Parameter-, Attribut- und Berechnungswerte.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/luxtronic2` beschrieben.


Item-Attribute
---------------

Die Ausgabe der Heizungssteuerung ist in drei Bereiche gegliedert, auf die mit jeweils eigenem
Item-Attribut zugegriffen wird:

**lux2_p**
    Parameter: Werte, mit denen die Heizung gesteuert wird (lesend und schreibend). Da das Protokoll
    nicht vollständig dokumentiert ist, ist nicht bei jedem Parameter bekannt, welche Funktion er hat.

**lux2_a**
    Attribute: nur lesbare Werte, vermutlich Sichtbarkeits- bzw. Freigabe-Flags einzelner Parameter.

**lux2_c**
    Berechnete Werte: nur lesbar, z.B. der aktuelle Betriebszustand oder Laufzeiten.

Welcher Wert unter welchem Index angesprochen wird, hängt vom individuellen Ausbau der Heizungsanlage
ab und muss anhand der Ausgabe der eigenen Heizung ermittelt werden.

**lux2** greift auf denselben Index wie **lux2_c** zu, gibt den Wert aber automatisch dekodiert zurück:
Index 119 (Betriebszustand) wird als Text statt als Zahl geliefert, die Indizes 10, 11, 12, 15, 19, 20,
151, 152 und 159 werden durch zehn geteilt zurückgegeben. Für folgende Indizes ist außerdem eine
Bedeutung dokumentiert:

=====  =====================================
Index  Bedeutung
=====  =====================================
14     Temperatur Heißgas
16     Temperatur Mittelwert
18     Temperatur Warmwasser SOLL
56     Betriebsstunden Verdichter
57     Impulse Verdichter
60     Betriebsstunden Zusatzheizung
63     Betriebsstunden Wärmepumpe Gesamt
64     Betriebsstunden Wärmepumpe Heizung
65     Betriebsstunden Wärmepumpe Warmwasser
119    Betriebs-Modus
159    Temperatur Zuluft
=====  =====================================


Beispiele
=========

::

    heating:
        temp_outside:
            type: num
            lux2: 10
        state_numeric:
            type: num
            lux2_c: 119
        state:
            type: str
            lux2: 119
