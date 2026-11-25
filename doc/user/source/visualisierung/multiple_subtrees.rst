
.. role:: redsup
.. role:: bluesup
.. role:: darkbluesup
.. role:: greensup
.. role:: blacksup

Seiten aus mehreren Sub-Trees
=============================

Items aus mehreren unterschiedlichen Sub-Trees können zusammen in eine Seite der
Visualisierung generiert werden.

Alle Widgets, die unterhalb eines Items definiert werden, welches ein **sv_page** Attribut hat, werden in eine
Visu Seite generiert. Wenn in einem anderen Teilbaum des Item-Trees eine weitere **sv_page** Definition mit dem
selben Seiten Namen (**name:**) erfolgt, werden die Widgets aus dem zweiten Teilbaum an die erste Seite angefügt.

Falls es erwünscht ist zwei Navigationseinträge mit dem selben Namen zu haben (z.B. **Bad**)  wenn die Navigation
durch Trenner "Erdgeschoss" und "Obergeschoss" strukturiert ist, so muss an den Namen der Definition für den
zweiten Teilbaum nur ein Leerzeichen angefügt werden:

.. code:: yaml

    myitems:
        eg:
            bad:
                sv_page: room
                name: Bad

        ...

        og:
            bad:
                sv_page: room
                name: "Bad "

