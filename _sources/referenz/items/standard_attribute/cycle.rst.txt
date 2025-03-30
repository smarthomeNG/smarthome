
.. index:: Standard-Attribute; cycle
.. index:: cycle

cycle :redsup:`neu`
===================

Das Attribut definiert ein regelmäßiges Aufrufen des Items (und damit der verknüpften Logik oder Eval-Funktion).

.. code-block:: yaml

   myitem:
       type: num
       cycle: 10 ; 0
       enforce_updates: true

setzt das Item alle 10 Sekunden auf den Wert 0 und sorgt dadurch für das Triggern von verknüpften Logiken und/oder Eval-Funktionen.
Dazu muss ``enforce_updates`` auf ``true`` stehen, damit das Triggern erfolgt, auch wenn sich der Wert des Items nicht
ändert.

Das allgemeine Format für die Angabe des **cycle** Attributes ist:

.. code-block:: yaml

   myitem:
       cycle: <Dauer> [; <Wert>]

Der Wert für *dauer* kann auf folgende Weise angegeben werden:

    - eine Zahl, die die Anzahl an Sekunden angibt

    - eine Zahl gefolgt von **h**, gibt die Anzahl an Stunden an
    - eine Zahl gefolgt von **m**, gibt die Anzahl an Minuten an
    - eine Zahl gefolgt von **s**, gibt die Anzahl an Sekunden an
    - eine Kombination der Stunden, Minuten und Sekunden Angaben (z.B.: 2h30m45s)

Der Wert für **Wert** ist optional.

.. hint:

  Die Syntax ``cycle: 10 ; None`` funktioniert nicht so, wie das bei ``eval: None`` funktioniert. Es gibt keine
  Möglichkeit, mit ``cycle`` nur zu triggern, aber keinen Wert zuzuweisen.

  Wenn die Angabe des Wertes weg gelassen wird, wird als zu setzender Wert der Wert angenommen, den das Item zum
  Zeitpunkt der auslösenden Wertänderung hat.

Der Trenner (Delimiter) zwischen **Dauer** und **Wert** ist ab SmartHomeNG v1.10 standardmäßig ein Semikolon.
Es kann jedoch auch der alte Delimiter (das Gleichheitszeichen) verwendet werden.

**Ab SmartHomeNG v1.11** werden die Konfigurationsmöglichkeiten erweitert:

Für **Dauer** und **Wert** können nun **eval** Ausdrücke angegeben werden, die zur Laufzeit entsprechend der Itemänderungen neu evaluiert werden.
Dabei können auch Item Properties genutzt werden.

.. hint:

  Falls bei der Auswertung des eval-Ausdrucks für die Zeit ein Fehler auftritt, wird der cycle eingestellt. Falls eine Item-Referenz im eval-Ausdruck angegeben ist, wird bei einer Änderung des referenzierten Items der eval-Ausdruck erneut ausgewertet.

  Ein eval-Ausdruck für den Item-Wert wird bei jedem Trigger erneut ausgewertet. Wenn hierbei ein Fehler auftritt, wird None zurückgegeben und der aktuelle Itemwert erneut gesetzt


Wird der Wert des Intervalls in einem referenzierten Item geändert, beginnt das neue cycle-Intervall sofort (ein vorher länger gesetztes Intervall wird abgebrochen)

Beispiel: Angenommen, aktuell ist cycle auf 1 Stunde gestellt und SHNG startet um 10:00 Uhr.
Die nächste Ausführung des Schedulers wäre somit auf (ca.) 11:00 Uhr errechnet.
Wird nun um 10:30 Uhr das Intervall auf 10 Minuten geändert, ist der nächste Ausführungszeitpunkt des Schedulers 10:40 Uhr.

.. code-block:: yaml

   myitem:
       type: num
       cycle: sh.myitem.dauer() ; 1 + sh...wert()
       dauer:
           type: num
           initial_value: 41
       wert:
           type: num
           initial_value: 1

   myitem2:
       type: str
       cycle: str(sh..interval.property.value + sh..interval2.property.value * 2) + "m" ; sh...wert.property.last_change
       interval:
           type: num
           initial_value: 41
       wert:
           type: str

.. hint:

 Möchte man komplexere eval-Ausdrücke mit Rechnoperationen angeben, ist zu beachten, dass nur numerische Werte korrekt berechnet werden,
 nicht jedoch Angaben als String wie 1m oder 5s, etc. Ein cycle-Intervall von ``1s + 1h`` wird zu unerwarteten Ergebnissen führen.
