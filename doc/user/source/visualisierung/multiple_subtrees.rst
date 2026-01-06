
.. role:: redsup
.. role:: bluesup
.. role:: darkbluesup
.. role:: greensup
.. role:: blacksup

Seiten aus mehreren Sub-Trees
=============================

Ab SmartHomeNG v1.8 können Items aus mehreren unterschiedlichen Sub-Trees zusammen in eine Seite der
Visualisierung generiert werden.

Bisher wurden alle Widgets die unterhalb eines Items definiert wurden, welches ein **sv_page** Attribut hat
in eine Visu Seite generiert. Wenn in einem anderen Teilbaum des Item-Trees ein weitere **sv_page** Definition
mit dem selben Seiten Namen (**name:**) erfolgte, wurde eine weitere Seite generiert, die in der Navigation den
selben Namen hatte wie die erste Seite.

Nun werden die Widgets aus dem zweiten Teilbaum in diesem Fall nicht mehr in eine eigene Seite generiert,
sondern an die erste Seite angefügt.

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

