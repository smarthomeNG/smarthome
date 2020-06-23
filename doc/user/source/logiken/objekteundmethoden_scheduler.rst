Scheduler Methoden
------------------

sh.scheduler.trigger() / sh.trigger()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Diese globale Funktion triggert eine Logic durch die Angabe ihres Namens.

.. code-block:: python

   sh.trigger(name [, by] [, source] [, value] [, dt])

- `name` (die Angabe von ist Pflicht) defniert die zu triggernde Logik.
- `by` Name der aufrufenden Logik
- `source` der eigentliche Grund für das Auslösen der Logik
- `value` Wert (des auslösenden Items)
- `dt` datetime Objekt (berücksichtigt Zeitzone), welches die Trigger-Zeit bestimmt.


.. note::

   Ab SmartHomeNG v1.4 darauf achten, dass eine Trennung der
   Namensräume für die Trigger stattgefunden hat. Wenn sh.trigger genutzt wird, muss dem Namen
   **logics.** vorangestellt werden.

   Also: statt ```sh.trigger('my_logic')``  -->  ```sh.sh.trigger('logics.my_logic')```



sh.scheduler.change()
^^^^^^^^^^^^^^^^^^^^^

Diese Methode ändert einige Laufzeit Optionen der Logik.

.. code-block:: python

   sh.scheduler.change('alarmclock', active=False)

disabled die Logik ‘alarmclock’. Außer dem active Flag, ist es möglich `cron` und `cycle` zu ändern.



