.. index:: Items; relative Referenzen
.. index:: relative Referenzen

Relative Item Referenzen
########################

**Seit Release 1.3** von SmartHomeNG werden relative Item Referenzen unterstützt.

Damit können in **eval** und in **eval_trigger** Attributen von Items andere Items referenziert
werden ohne den vollständigen Item-Pfad anzugeben. Das ist besonders hilfreich, wenn man Item
Strukturen hat, die man mehrfach kopieren möchte, da man dann die entsprechenden **eval** und
**eval_trigger** Einträge nicht jedes mal anpassen muss. Auch die mit Release 1.4 hinzukommenden
Item Attribute **on_update** und **on_change** unterstützen die relative Item Referenzierung.

Relative Referenzen vermindern auch die Fehleranfälligkeit, da man Items, die auf höheren Ebenen
in den Pfadangaben vorkommen umbenennen kann ohne alle **eval** und in **eval_trigger**
Attribute zu kontrollieren/anzupassen.

Die relativen Referenzen werden beim Start von SmartHomeNG zu absoluten Item-Pfaden aufgelöst,
so dass ich zur Laufzeit keine Unterschiede ergeben, unabhängig davon ob die Items in den
Konfigurationsdateien durch relative oder absolute Referenzen angegeben wurden.

Für Plugins die in ihren Item Attributen relative Item-Pfad Angaben verwenden wollen, steht
eine Methode zur Verfügung, um dieses zu unterstützen. Dazu muss nur in der **parse_item**
Methode des Plugins für das entsprechende Item Attribut diese Methode aufgerufen werden.

Syntax der relativen Referenzen
===============================

- Relative Referenzen beginnen mit einem Punkt ( **.** )
- Ein **.** alleine würde das Item selbst referenzieren, was für sich alleine natürlich keinen Sinn macht
- Ein Unteritem (child) wird durch **.child** referenziert
- Um Items höherer Ebenen zu referenzieren, muss für jeden Level ein ein weiterer **.** hinzugefügt werden.
  **..** referenziert also das Parent-Item. Um das darüber liegende Item (Grandparent) zu referenzieren, muss
  ein weiterer **.** hinzugefügt werden. **...** referenziert also das Grandparent-Item, usw.

Theoretisch ist jedes Item des gesamten Item Baums über eine relative Referenz adressierbar. Dieses
ist jedoch schon aus Gründen der Übersichtlichkeit/Lesbarkeit nicht sinnvoll.

Beispiele
=========

Die folgenden Beispiele beziehen sich auf diese Item Struktur:

.. code-block:: yaml
   :caption: ../items/\*.yaml

   item_tree:
       grandparent:

           parent:

               my_item:
                   eval_trigger: ...

                   child:

                       grandchild:

               sister:




Folgende Beispiele zeigen, wie ausgehend vom Attribut **eval_trigger** des Items **my_item**
andere Items referenziert werden.

+-------------------------------------------------------+-------------------+----------------+
| **absolut**                                           | **relativ**       | **alternativ** |
+=======================================================+===================+================+
| item_tree.grandparent.parent.my_item                  | .                 | .self          |
+-------------------------------------------------------+-------------------+----------------+
| item_tree.grandparent.parent.my_item.child            | .child            |                |
+-------------------------------------------------------+-------------------+----------------+
| item_tree.grandparent.parent.my_item.child.grandchild | .child.grandchild |                |
+-------------------------------------------------------+-------------------+----------------+
| item_tree.grandparent.parent                          | ..                | ..self         |
+-------------------------------------------------------+-------------------+----------------+
| item_tree.grandparent.parent.sister                   | ..sister          |                |
+-------------------------------------------------------+-------------------+----------------+
| item_tree.grandparent                                 | ...               | ...self        |
+-------------------------------------------------------+-------------------+----------------+


Nutzung in `eval_trigger` und `eval`
====================================

Es ist darauf zu achten, dass im **eval** Attribut Items durch sh. *\<item\>* () angesprochen werden.

Angenommen **my_item** soll neu berechnet werden soll, falls **my_item.child** sich ändert
und zwar soll **my_item** den dreifachen Wert von **my_item.child** erhalten, so würden die
Attribute folgendermaßen aussehen:

.. code-block:: yaml
   :caption: ../items/\*.yaml

   my_item:
       eval: 3 * sh..child()
       eval_trigger: .child


.. note::

   **eval** enthält 2 Punkte. Um das Item Objekt zu referenzieren **sh.** und **.child**
   für die relative Referenz. Nach dem Start von SmartHomeNG enthält das Attribut **eval** dann
   ``3 * sh.item_tree.grandparent.parent.my_item.child()``.


.. admonition:: Nutzung im Zusammenhang mit Item-Attributen

   Eine Besonderheit ist bei der Nutzung der relativen Adressierung im Zusammenhang mit Item-Attributen
   zu beachten:

   Wenn in einem eval-Parameter z.B. der Zugriff auf **item_tree.grandparent.parent.my_item.changed_by()**
   über relative Adressierung erfolgen soll, so würde das nach den obigen Beschreibungen so
   aussehen: **sh...changed_by()**

   Das würde jedoch nach Entfernung von 'sh.' und '()' als ```..changed_by``` interpretiert,
   also als ein Sister-Item namens 'changed_by'.

   In diesem Fall ist es notwendig, das Item selbst statt über ```.``` über die alternative
   Notation ```.self``` anzusprechen, also ```sh..self.changed_by()``` statt ```sh...changed_by()```
   zu verwenden.


Nutzung relativer Item Referenzen in Plugins
============================================

Relative Referenzen in Item-Attributen die durch Plugins definiert werden, können mit der
folgenden Methode zu absoluten Referenzen aufgelöst werden:


.. code-block:: python

    item.expand_relativepathes(attribute_name, begin_tag, end_tag)

Die Methode `expand_relativepathes()` hat die folgenden drei Parameter:

+----------------+-------------------------------------------------------------------+
| **Parameter**  | **Bedeutung**                                                     |
+================+===================================================================+
| attribute_name | Name des Attibutes, in dem die Referenzen aufgelöst werden sollen |
+----------------+-------------------------------------------------------------------+
| begin_tag      | Zeichen(kette), die den Beginn einer Item-Referenz kennzeichnet   |
+----------------+-------------------------------------------------------------------+
| end_tag        | Zeichen(kette), die das Ende einer Item-Referenz kennzeichnet     |
+----------------+-------------------------------------------------------------------+

Wenn das Attribut nur genau eine Referenz enthält, sind *begin_tag* und *end_tag* leer ( *''* ).

Wenn Das Attribut einen String enthält, in dem eine oder mehrere Item-Referenzen enthalten sind,
so muss über *begin_tag* und *end_tag* angegeben werden, woran die Item-Referenz erkannt werden
kann.

Die Auflösung zu absoluten Referenzen soll/muss in der **parse_item** Methode des Plugins erfolgen.

Beispiel
--------

Im Attribut **sv_widget** des Plugins **visu_smartvisu** sind eine oder mehrere Item-Referenzen
enthalten.

.. code-block:: yaml
   :caption: ../items/\*.yaml

    schreibtischleuchte:
        sv_widget: {{ basic.switch('id_schreibtischleuchte', 'wohnung.buero.schreibtischleuchte.onoff') }}


Die Item Referenz wird dadurch erkannt, dass sie in **'** Zeichen eingeschlossen ist. Für das
Attribut **sv_widget** muss der Aufruf also folgendermaßen lauten:

.. code-block:: python

    item.expand_relativepathes('sv_widget', "'", "'")


Da im Beispiel oben ein absoluter Item-Pfad angegeben ist, passiert nichts. Wenn der Item-Pfad
jedoch relativ wäre

.. code-block:: yaml
   :caption: ../items/\*.yaml

    schreibtischleuchte:
        sv_widget: {{ basic.switch('id_schreibtischleuchte', '.onoff') }}


würde bei dem Aufruf von `item.expand_relativepathes('sv_widget', "'", "'")` eine Auflösung
zum absoluten Pfad erfolgen.

Das **visu_smart_visu** Plugin unterstützt relative Item-Pfade in 4 Attributen. Die Methode
**parse_item** des **visu_smart_visu** Plugins sieht folgendermaßen aus:

.. code-block:: python

    def parse_item(self, item):
        item.expand_relativepathes('sv_widget', "'", "'")
        item.expand_relativepathes('sv_widget2', "'", "'")
        item.expand_relativepathes('sv_nav_aside', "'", "'")
        item.expand_relativepathes('sv_nav_aside2', "'", "'")

