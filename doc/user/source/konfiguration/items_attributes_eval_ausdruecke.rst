.. index:: eval Ausdrücke

eval Ausdrücke
##############

Eval Syntax
===========

Der Syntax eines **eval** Ausdrucks ist der Syntax einer `Python conditional expression <https://www.python.org/dev/peps/pep-0308/>`_

Dieser Syntax wird bei den Item Attributen **eval**, **on_change** und **on_update** verwendet.

Zu beachten ist, dass der Syntax einer if-Bedingung in einer Python conditional Expression folgender ist:

``eval: <expression-if-true> if <condition> else <expression-if-false>``


Beispiel:

``eval: value if value>0 else 0``

Die Expression setzt den Item-Wert auf den bisherigen Wert, falls er >0 ist, sonst wird der Wert auf 0 gesetzt.
Damit findet eine Zuweisung statt und on_change bzw. on_update Trigger werden ausgelöst.

Wenn das Beispiel folgendermaßen formuliert wird:

``eval: 0 if value <0 else None``

Hätte es auf den Item-Wert letztlich die selben Auswirkungen: Hier wird der Item-Wert auf 0 gesetzt, falls der Wert <0 ist,
sonst (None) wird keine Aktion ausgeführt (damit bleibt der Wert unverändert erhalten).
Damit werden on_change bzw. on_update Trigger nur ausgelöst, wenn der Wert vorher <0 war. Bei Erhalt des Wertes (None),
werden keine Trigger ausgelöst.



Gemeinsame Verwendung von eval und on\_\.\.\. Item Attributen
-------------------------------------------------------------

Bei Verwendung des **eval** Attributes zusammen mit **on_change** oder **on_update** in der
selben Item Definition ist zu beachten, dass value unterschiedliche Werte hat/haben kann.

Im Ausdruck des **eval** Attributes hat value den alten Wert des Items. Nach Abschluss dieser
Berechnung, wird dem Item das Ergebnis zugewiesen. Anschließend werden die Ausdrücke für
**on_change** und **on_update** berechnet. Zu diesem Zeitpunkt hat das Item (und damit
**value**) bereits den neuen Wert.

Wenn in **eval** Ausdrücken in **on_change** oder **on_update** Attributen auf den alten Wert
des Items zugegriffen werden soll, muss dazu die Item Funktion **prev_value()** genutzt werden.
Auf den alten Wert des aktuellen Items kann ohne die Angabe der vollständigen Item Pfades durch
den Ausdruck **sh.self.prev_value()** zugegriffen werden.


.. attention::

   Bei **eval** Ausdrücken (wie sie in den Item Attributen **eval**, **on_update** und **on_change**
   verwendet werden) ist zu beachten, dass bei Verwendung von **if** auch immer ein **else**
   Zweig angegeben werden muss!

   Wenn man jedoch ein Item nur verändern möchte wenn die **if** Bedingung erfüllt ist und sonst
   unverändert lassen möchte, muss als **else** Zweig der Ausdruck **else None** angegeben werden.
   **None** bewirkt, dass das Item unverändert bleibt, und somit auch keine Trigger ausgelöst werden.


Eval Trigger
------------

Ein häufiger Fehler bei der Nutzung von **eval** im Zusammenspiel mit **eval_trigger** ist,
bei **eval_trigger** auch den vollen Python-Pfad zu einem SmartHomeNG Item zu verwenden, wie
im **eval** Ausdruck.

Richtig ist es, bei **eval_trigger** nur der Item-Pfad zu nutzen (ohne führendes **sh.** und
ohne folgende **()**).


**Korrekt**:

- eval: **sh.** my.value **()**
- eval_trigger: my.value | my.other.value

**Falsch**:

- eval: sh.my.value
- eval_trigger: **sh.** my.value | **sh.** my.other.value

