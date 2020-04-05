.. index:: Standard-Attribute; on_update
.. index:: on_update
.. index:: Standard-Attribute; on_change
.. index:: on_change


===========================
*on_update* und *on_change*
===========================

Attribut *on_update*
====================

Ermöglicht das Setzen des Wertes anderer Items, wenn das aktuelle Item ein Update erhält
(auch wenn sich der Wert des aktuellen Items dabei nicht ändert).
Das ist der Unterschied zu **on_change**, welches nur ausgelöst
wird wenn sich bei einem Update der Wert des Items auch ändert. **Seit SmartHomeNG v1.4**

Die Syntax ist wie folgt:

+-------------------------+----------------------------------------------------------------------+
|  <item> = <expression>  | <expression>  nutzt die gleiche syntax wie ein Ausdruck beim         |
|                         | eval-Attribut                                                        |
+-------------------------+----------------------------------------------------------------------+
|  <single expression>    | Wenn die zweite Form (ohne <item> = ) genutzt wird, muss die         |
|                         | Zuweisung innerhalb der expression erfolgen:                         |
|                         | Eine <single expression> der Form `sh.<item>(<expression>)` ist      |
|                         | weitestgehend äquivalent zur ersten Syntax Form.                     |
+-------------------------+----------------------------------------------------------------------+


- Expressions (eval Ausdrücke) können die gleiche Syntax nutzen wie das **eval** Attribut.
- Expressions können relative Item Adressierungen nutzen.
- Auch die Item Angabe in **<item> = <expression>** kann eine relative Angabe sein.
- Zu beachten ist, dass <item> eine reine Item Pfad Angabe ist, während in einem Ausdruck
  (wie auch bei eval), ein Item in der Form **sh.<item>()** adressiert werden muss.
- **on_update** kann zusammen mit **eval** im selben Item genutzt werden, wobei **eval** vor
  **on_update** ausgeführt wird. Dadurch enthält **value** in dem **on_update** eval-Ausdruck den
  aktualisierten Wert des Items. Im Gegensatz dazu enthält **value** im eval-Ausdruck des **eval**
  Attributs den vorangegangenen Wert des Items. Wenn im **on_update** Ausdruck auf den vorangegangenen
  Wert des Items zugegriffen werden soll, geht das mit der Item-Methode **prev_value()**. Um das
  Item selbst zu adressieren kann am einfachsten die relative Adressierung eingesetzt werden.
  Den vorangegangenen Wert des Items erhält man mit **sh..prev_value()**.

.. attention::

   Es ist zu beachten, dass die beiden Versionen des **on_update** Syntax nicht vollständig
   identisch sind. Der Unterschied tritt zutage, wenn die <expression> als Ergebnis **None**
   liefert.

   Die erste Version (<item> = <expression>) verhält sich analog zum **eval** Attribut:
   Wenn das Ergebnis der <expression> **None** ist, wird <item> nicht verändert. **None** kann
   hierbei bewusst eingesetzt werden, um einen Wert unverändert zu lassen und damit verhindern,
   dass <item> ungewollt weitere Trigger auslöst.

   In der zweiten Version (<single expression>) würde ein Ergebnis **None** dazu führen, dass
   das Ziel Item (sh.<item>) den Wert None zugewiesen bekommt.


Beispiel:

.. code-block:: yaml
   :caption: ../items/<filename>.yaml (Ausschnitt)

   itemA1:
       # eine einzelne Zuweisung
       on_update: itemB = 1                  # bei jedem Update von itemA1 (mit oder ohne Wertänderung)

   itemA2:
       # eine Liste mehrerer Zuweisungen
       on_change:
       - itemC = False                       # nur wenn sich der Wert von itemA2 ändert
       - itemD = sh.itemB()                  #
       - itemE = sh.itemB() if value else 0  #
       ...

   itemB:
       ...

   itemC:
       ...


Attribut *on_change*
====================

Ermöglicht das Setzen des Wertes anderer Items, wenn der Wert des aktuellen Items verändert wird.
Im Gegensatz zu **on_update** wird **on_change** nur ausgelöst, wenn sich beim Update
eines Items der Wert auch ändert. **Seit SmartHomeNG v1.4**

Der Syntax ist äquivalent zum Attribut **on_update**.


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
