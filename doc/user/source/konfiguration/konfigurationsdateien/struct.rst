
.. role:: bluesup
.. role:: redsup

.. index:: structs; struct.yaml

struct.yaml :bluesup:`update`
=============================

In dieser Konfigurationsdatei können eigene Item-Strukturen angelegt werden, die über das **struct** Attribut als
Template verwendet werden können.

.. note::

    Weitergehende Informationen zu structs sind unter :doc:`Konfiguration/struct </konfiguration/item_structs>` und in
    der Entwicklerdokumentation unter **Development of Plugins** / **Plugin Metadata** zu finden.


Hierbei gibt die oberste Ebene den Namen der Templates an. Darunter können Item Strukturen definiert werden, wie man es
auch in der Item Definition in den items.yaml Dateien machen würde. Das folgende Beispiel zeigt die Definition von zwei
Strukturen (**my_struct_01** und **my_struct_02**):

.. code-block:: yaml
    :caption: etc/struct.yaml

    my_struct_01:
        name: Name der Item Struktur

        item_01:
            name: Erstes Item
            type: num
            ...
        item_02:
            name: Zweites Item
            type: bool
            ...
            subitem:
                name: Sub-Item
                type: str
                ...


    my_struct_02:
        name: Name der zweiten Item Struktur
        type: bool

        item_a:
            name: Item A
            type: num
            ...
        item_b:
            name: Item B
            type: str
            ...

Wenn jetzt in der Item Definition diese Strukturen referenziert werden:

.. code-block:: yaml
    :caption: items/items.yaml

    my_tree:
        my_complex_data:
            name: Geänderter Name für meine komplexen Daten
            struct: my_struct_01

            individual_item:
                name: Individuelles Item
                type: str
                ...


entsteht im Item-Tree die selbe Struktur, als wenn man folgendes direkt in die item.yaml eingetragen hätte:

.. code-block:: yaml
    :caption: items/items.yaml

    my_tree:
        name: Geänderter Name für meine komplexen Daten
        struct: my_struct_01

        item_01:
            name: Erstes Item
            type: num
            ...
        item_02:
            name: Zweites Item
            type: bool
            ...
            subitem:
                name: Sub-Item
                type: str
                ...
        individual_item:
            name: Individuelles Item
            type: str
            ...


Beim Einfügen der Struktur bleibt das Attribut **struct** erhalten, so dass man zur Laufzeit sehen kann, dass die Struktur
zumindest in Teilen aus einem Template stammt.

Der Name, der im Template bereits angegeben war, wird durch die Angabe au der Datei items/item.yaml ersetzt.

Das **individual_item** wird in die Struktur des Templates eingefügt.


.. index:: structs; Verschachtelte structs

Verschachtelte struct Definitionen
----------------------------------

Ab SmartHomeNG v1.7 können Strukturdefinitionen verschachtelt werden. Wie Items, die mithilfe des Attributs **struct:**
auf eine Strukturdefinition verweisen, können dies jetzt auch Strukturen tun.

In Strukturen wird das **struct** Attribut **nur** auf der obersten Ebene als Referenz ausgewertet.

SmartHomeNG löst alle Unterstrukturreferenzen vor dem Laden des Item Trees auf, um das Laden der Item Definitionen
zu beschleunigen.

.. note::

   Bitte beachten: Wenn Unterstrukturdefinitionen aufgelöst werden, gibt es zwei Unterschiede zu der Art und Weise,
   wie Item Definitionen geladen werden. Die Unterschiede treten nur dann zutage, wenn Strukturen / Unterstrukturen
   Attribute re-definieren. (Siehe hierzu auch :doc:`Konfiguration/structs </konfiguration/item_structs>`


Re-Definieren von Attributen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beim Definieren von Items ist es möglich, dasselbe Attribut für ein Item in mehreren Item YAML-Dateien zu definieren.
Beim Lesen der Item Definition gewinnt die Attributdefinition, welche zuletzt eingelesen wird. In Struktur- /
Unterstrukturdefinitionen gewinnt die zuerst eingelesene Attributdefinition.

Beim Auflösen von Unterstrukturen sollte normalerweise die Definition der Struktur der oberen Ebene gewinnen. Dies
ermöglicht ein "Überschreiben" von Attributwerten, die in einer Unterstruktur definiert wurden. Dazu muss das Attribut
in der Struktur der oberen Ebene vor dem **struct**-Attribut definiert werden. Wenn das Attribut nach dem
**struct**-Attribut definiert ist, gewinnt die Definition in der Unterstruktur. Regel: "first wins"


Re-Definieren von list-Attributen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bei der Neudefinition von Attributen, bei denen es sich um Listen handelt, erfolgt kein "Überschreiben". Stattdessen
werden die Listen zusammengefügt. Die Reihenfolge der Listeneinträge wird durch die Reihenfolge bestimmt, in der die
Attributdefinitionen eingelesen werden.



