
.. index:: Standard-Attribute; autotimer
.. index:: autotimer

*autotimer*
===========

Das Attribut setzt den Wert des Items nach einer Zeitspanne auf einen bestimmten Wert. Der Timer beginnt zu laufen,
wenn dem Item ein Wert zugewiesen wird. Wenn während der Autotimer läuft dem Item erneut ein Wert zugewiesen wird,
beginnt der Timer erneut zu laufen. Damit lässt sich z.B. ein Treppenhauslicht realisieren.

.. code-block:: yaml

   myitem:
       type: num
       autotimer: 5m ; 0

setzt nach 5 Minuten den Wert des Items auf 0.


Das allgemeine Format für die Angabe des **autotimer** Attributes ist:

.. code-block:: yaml

   myitem:
       autotimer: <Dauer> [; <Wert>]

**Ab SmartHomeNG v1.10** sind die möglichen Angaben für die Dauer erweitert. Der Wert für **Dauer** kann auf folgende
Weise angegeben werden:

    - eine Zahl, die die Anzahl an Sekunden angibt

    - eine Zahl gefolgt von **h**, gibt die Anzahl an Stunden an
    - eine Zahl gefolgt von **m**, gibt die Anzahl an Minuten an
    - eine Zahl gefolgt von **s**, gibt die Anzahl an Sekunden an
    - eine Kombination der Stunden, Minuten und Sekunden Angaben (z.B.: 2h30m45s)

Der Wert für **Wert** ist optional. Falls er weg gelassen wird, wird nach Ablauf der Dauer das Item auf den Wert gesetzt, den es zum Zeitpunkt der auslösenden Wertänderung angenommen hat.

Falls der Wert None ist, wird ebenfalls der zum Zeitpunkt des Triggers aktuelle Itemwert erneut gesetzt.

Der Trenner (Delimiter) zwischen **Dauer** und **Wert** ist ab SmartHomeNG v1.10 standardmäßig ein Semikolon.
Es kann jedoch auch der alte Delimiter (das Gleichheitszeichen) verwendet werden.


**Ab SmartHomeNG v1.11** werden die Konfigurationsmöglichkeiten erweitert:


Für **Dauer** und **Wert** können nun **eval** Ausdrücke angegeben werden, die zur Laufzeit entsprechend der Itemänderungen neu evaluiert werden.
Dabei können auch Item Properties genutzt werden.

.. code-block:: yaml

   myitem:
       type: num
       autotimer: sh.myitem.dauer() + 1 ; sh...wert.property.value  # oder sh...wert()
       dauer:
           initial_value: 41
       wert:
           initial_value: 1

setzt nach der in *myitem.dauer* angegebenen Dauer (41 Sekunden) plus 1 Sekunde aus dem Ausdruck
den Wert des Items auf in *myitem.wert* (hier initial mit 1 angegebenen).
Die Angabe der Items kann auch als relative Angabe erfolgen (bspw. *sh..dauer()*)


Wird der Wert des Intervalls während eines laufenden autotimers geändert, wird diese Wertänderung erst für die nächste
Ausführung des autotimers relevant. Wird der Wert während eines aktiven autotimers geändert, wird der neue aktualisierte
Wert nach Ablauf der Dauer geschrieben.

.. code-block:: yaml

   myitem2:
       type: str
       autotimer: str(sh..interval.property.value + sh..interval2.property.value * 2) + "m" ; sh...wert.property.last_change
       interval:
           type: num
           initial_value: 41
       wert:
           type: str


.. hint:

   Möchte man komplexere eval-Ausdrücke mit Rechenoperationen angeben, ist zu beachten, dass nur numerische Werte korrekt berechnet werden,
   nicht jedoch Angaben als String wie 1m oder 5s, etc. Eine Dauer von ``1s + 1h`` wird zu Fehlern führen, wodurch der Autotimer nicht ausgeführt wird.
