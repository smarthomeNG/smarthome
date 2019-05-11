.. index:: struct

.. role:: bluesup
.. role:: redsup

struct.yaml :redsup:`new`
#########################

In dieser Konfigurationsdatei können eigene Item-Strukturen angelegt werden, die über das **struct** Attribut als Template
verwendet werden können.

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


Beim einfügen der Struktur bleibt das Attribut **struct** erhalten, so dass man zur Laufzeit sehen kann, dass die Struktur
zumindest in Teilen aus einem Template stammt.

Der Name, der im Template bereits angegeben war, wird durch die Angabe au der Datei items/item.yaml ersetzt.

Das **individual_item** wird in die Struktur des Templates eingefügt.
