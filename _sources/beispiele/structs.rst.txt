
.. index:: structs; Beispiele
.. index:: Beispiele; structs

.. role:: bluesup
.. role:: redsup


structs (Item Strukturen)
=========================

Durch folgende Einträge in der Datei **../etc/struct.yaml** werden diverse Templates bereit gestellt,
auf die von Items referenziert werden kann. Es gibt hier auch keine erkennbare Unterscheidung zwischen
Structs und Sub-Structs, alle Deklarationen sind gleichwertig und können nach Belieben verschachtelt werden.

.. code-block:: yaml
    :caption: etc/struct.yaml

    sub_struct1:
        item_in_struct:
            type: str

            child_in_struct:
                type: foo
                eval_trigger: a

    sub_struct2:
        item_in_struct:
            type: num
            eval_trigger: b

            child_in_struct:
                type: num
                eval_trigger:
                    - c

    main_struct1:
        item_in_struct:
            type: bool
            eval_trigger: d

        struct:
            - sub_struct1
            - sub_struct2

    main_struct2:
        struct: sub_struct2

        item_in_struct:
            type: dict
            eval_trigger:
                - e


Wird nun das main_struct1 in einem Item namens test1 referenziert,
ergibt sich dadurch beim Laden von SmarthomeNG folgende Struktur. Zu beachten ist hier vor allem, dass

- item_in_struct den Typ bool erhält, weil hier das übergeordnete struct wegen der Regel "first wins" gewinnt.
- eval_trigger des item_in_struct nicht zur Liste wird, weil keine Einträge als solche definiert sind.
  Auch hier gilt die Regel "first wins", weshalb das eval_trigger aus dem sub-struct ignoriert wird.
- child_in_struct den Typ foo erhält, weil auch bei gleichrangingen sub-structs die Regel "first wins" gilt.
- Die eval_trigger Einträge beider (sub-)structs auch ohne **merge\*** Eintrag kombiniert werden,
  weil zumindest einer der Einträge als Liste deklariert ist.

.. code-block:: yaml
    :caption: Ergebnis beim Start von SmarthomeNG

    test1:
        item_in_struct:
            type: bool
            eval_trigger: d

            child_in_struct:
                type: foo
                eval_trigger:
                  - a
                  - c


Beim Einbinden von main_struct2 in das item test2 ergibt sich beim Laden von SmarthomeNG folgende Struktur.
Zu beachten ist hier vor allem, dass

- item_in_struct den Typ num erhält, weil hier das sub-struct wegen der Regel "first wins" gewinnt.
- eval_trigger des item_in_struct nicht zur Liste wird, weil das sub-struct keine Liste deklariert hat.
  Das übergeordnete struct hat eval_trigger zwar als Liste definiert, das Attribut wird aber aufgrund der Deklaration
  nach dem struct Aufruf gemäß der Regel "first wins" ignoriert.

.. code-block:: yaml
    :caption: Ergebnis beim Start von SmarthomeNG

    test2:
        item_in_struct:
            type: num
            eval_trigger: b

            child_in_struct:
                type: num
                eval_trigger: c


In diesem Beispiel wird in der **items** Datei das type Attribut, das auch in den structs vorkommt, ebenfalls deklariert.
Ob das vor oder nach dem struct Attribut erfolgt, spielt keine Rolle, da hier die Regel "item wins" zu tragen kommt.

.. code-block:: yaml
    :caption: items/item.yaml

    test1:
        item_in_struct:
            type: foo

        struct:
            - main_struct1
            - main_struct2

    test2:
        item_in_struct:
            type: foo
            eval_trigger:
                - merge*
                - x

            child_in_struct:
                type: foo
                eval_trigger:
                    - y
                    - z

        struct: main_struct2


Dies führt nun zu einem leicht veränderten Ergebnis. Zu beachten ist hier, dass

- item_in_struct in beiden Fällen den Typ foo erhält, weil hier das Item aufgrund der Regel "item wins" gewinnt.
- eval_trigger im test2.item_in_struct zu einer Liste mit den Einträgen von sub-struct2 und dem Item wird.
  Wäre in test2 das struct vor item_in_struct eingebunden, würden die eval_trigger Einträge nicht zu einer Liste verschmelzen,
  weil im sub-struct das Attribut nicht als Liste deklariert ist ("first wins" Regel).
- eval_trigger im child_in_struct bei test2 nicht mit den struct Einträgen kombiniert wird, da der Eintrag **merge\*** fehlt.

.. code-block:: yaml
    :caption: Ergebnis beim Start von SmarthomeNG

    test1:
        item_in_struct:
            type: foo
            eval_trigger: d

            child_in_struct:
                type: foo
                eval_trigger:
                  - a
                  - c

    test2:
        item_in_struct:
            type: foo
            eval_trigger:
                - x
                - b

            child_in_struct:
                type: num
                eval_trigger:
                    - y
                    - z
