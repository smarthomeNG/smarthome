
.. index:: Standard-Attribute; cycle
.. index:: cycle

cycle
=====

Das Attribut definiert ein regelmäßiges Aufrufen des Items (und damit der verknüpften Logik oder Eval-Funktion).

.. code-block:: yaml

   myitem:
       type: num
       cycle: 10 ; 0
       enforce_updates: 'true'

ruft das Item alle 10 Sekunden auf und sorgt dadurch für das triggern von verknüpften Logiken und/oder Eval-Funktionen.
Dazu muss ``enforce_updates`` auf ``true`` stehen, damit das Triggern erfolgt, auch wenn sich der Wert des Items nicht
ändert.

Gleichzeitig wird bei jedem Aufruf von ``cycle``, also hier alle 10 Sekunden, der Wert des Items auf 0 gesetzt.
Wenn mit diesem Item Logiken und/oder Eval-Funktionen verknüpft sind, muss ``enforce_updates`` auf ``true``
stehen, damit das Triggern erfolgt, auch wenn sich der Wert des Items nicht ändert.


Das allgemeine Format für die Angabe des **cycle** Attributes ist:

.. code-block:: yaml

   myitem:
       cycle: <Dauer> [; <Wert>]

Der Wert für **Dauer** kann auf folgende Weise angegeben werden:

    - eine Zahl, die die Anzahl an Sekunden angibt
    - eine Zahl gefolgt von **m**, gibt die Anzahl an Minuten an

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
       cycle: sh.item.dauer() ; 1 + sh.item.wert()
       dauer:
           initial_value: 41
       wert:
           initial_value: 1


Der Wert für *dauer* kann auf folgende Weise angegeben werden:

1. eine Zahl, die die Anzahl an Sekunden angibt
2. eine Zahl gefolgt von **m**, gibt die Anzahl an Minuten an
3. eine Zahl gefolgt von **s**, gibt die Anzahl an Sekunden an
   (alternative Schreibweise zur Variante 1)

Zu beachten ist, dass der zu setzende Wert nur bei der Initialisierung berechnet wird und für die weiteren Zyklen
konstant ist.




.. hint:

  Die Syntax ``cycle: 10 ; None`` funktioniert nicht so, wie das bei ``eval: None`` funktioniert. Es gibt keine
  Möglichkeit, mit ``cycle`` nur zu triggern, aber keinen neuen Wert zuzuweisen.

  Wenn die Angabe des Wertes weg gelassen wird, wird als zu setzender Wert der Wert angenommen, den das Item zum
  Zeitpunkt der Initialisierung hat.

