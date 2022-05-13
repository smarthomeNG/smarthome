
.. index:: Stateengine; Ausführungszeitpunkt

====================
Ausführungszeitpunkt
====================

Beispiel
--------

Im Beispiel ist ein Item im Zustand 1 namens ``on_enter_or_stay`` angelegt.
In diesem Item befinden sich diverse Aktionen, die jedes Mal ausgeführt werden,
wenn der Zustand aktiv wird oder bleibt.

.. code-block:: yaml

    #items/item.yaml
    raffstore1:
        automatik:
            struct: stateengine.general
                rules:
                    state1:
                        name: Zustand 1

                        on_enter_or_stay:
                            name: Ausführen immer wenn ein Zustand aktiv ist
                            <... Aktionen ...>

Aktionsausführung
-----------------

Um festzulegen, wann die Aktionen eines Zustands ausgeführt
werden, gibt es vier Ereignisse, denen die Aktionen zugeordnet
werden können. Für jedes dieser Ereignisse wird ein Item unterhalb
des Zustands-Items angelegt, in dem die jeweiligen Aktionen
als Attribute definiert werden.

-  **on_enter**: Aktionen, die nur beim erstmaligen Aktivieren des
   Zustands ausgeführt werden

-  **on_stay**: Aktionen, die nur ausgeführt werden, wenn der Zustand
   zuvor bereits aktiv war und weiterhin aktiv bleibt.

-  **on_enter_or_stay**: Aktionen, die ausgeführt werden, wenn der
   Zustand aktiv ist, unabhängig davon, ob er bereits zuvor aktiv
   war oder nicht.

-  **on_leave**: Aktionen, die ausgeführt werden, direkt bevor ein
   anderer Zustand aktiv wird.
