
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

**Ab SmartHomeNG v1.10** möglichen Angaben für die Dauer erweitert. Der Wert für **Dauer** kann auf folgende
Weise angegeben werden:

    - eine Zahl, die die Anzahl an Sekunden angibt

    - eine Zahl gefolgt von **h**, gibt die Anzahl an Stunden an
    - eine Zahl gefolgt von **m**, gibt die Anzahl an Minuten an
    - eine Zahl gefolgt von **s**, gibt die Anzahl an Sekunden an
    - Eine Kombination der Stunden, Minuten und Sekunden Angaben (z.B.: 2h30m45s)

|

Der Wert für **Wert** ist optional. Falls er weg gelassen wird, wird nach Ablauf der Dauer das Item auf den
Wert gesetzt, den es zum Zeitpunkt der auslösenden Wertänderung angenommen hat.

Der Trenner (Delimiter) zwischen **Dauer** und **Wert** ist ab SmartHomeNG v1.10 standardmäßig ein Semikolon.
Es kann jedoch auch der alte Delimiter (das Gleichheitszeichen) verwendet werden.


**Ab SmartHomeNG v1.10** werden die Konfigurationsmöglichkeiten erweitert:

Für **Dauer** und **Wert** können nun **eval** Ausdrücke angegeben werden. Bisher waren nur konstante Werte und
Itemnamen (absolut oder relativ) möglich.

.. code-block:: yaml

   myitem:
       type: num
       autotimer: sh.item.dauer() ; 1 + sh.item.wert()
       dauer:
           initial_value: 41
       wert:
           initial_value: 1

setzt nach der in *myitem.dauer* angegebenen Dauer (41 Sekunden) plus 1 Sekunde aus dem Ausdruck
den Wert des Items auf in *myitem.wert* (hier initial mit 1 angegebenen).
Die Angabe der Items kann auch als relative Angabe erfolgen
(bspw. *sh..dauer()*)

Der Wert für *dauer* kann auf folgende Weise angegeben werden:

1. eine Zahl, die die Anzahl an Sekunden angibt
2. eine Zahl gefolgt von **m**, gibt die Anzahl an Minuten an
3. eine Zahl gefolgt von **s**, gibt die Anzahl an Sekunden an
   (alternative Schreibweise zur Variante 1)

