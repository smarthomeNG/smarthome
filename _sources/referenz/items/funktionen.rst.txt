.. index:: Items; Funktionen
.. index:: Funktionen; Items

.. role:: bluesup
.. role:: redsup


Funktionen eines Items
======================


Jedes definierte Item bietet die folgenden Methoden an, die unter anderem in **eval** Ausdrücken und Logiken
genutzt werden können.

+--------------------------------+--------------------------------------------------------------------------------+
| **Funktion**                   | **Beschreibung**                                                               |
+================================+================================================================================+
| autotimer(time, value)         | Setzt einen Timer bei jedem Werte-Wechsel der Items. Angegeben wird die Zeit   |
|                                | (**time**) die vergehen soll, bis das Item auf den Wert (**value**) gesetzt    |
|                                | wird. Die Zeitangabe erfolgt in Sekunden. Eine Angabe der Dauer in Minuten     |
|                                | ist wie in '10m' möglich.                                                      |
+--------------------------------+--------------------------------------------------------------------------------+
| fade(end, step, delta, caller, | Blendet das Item mit der definierten Schrittweite (int oder float) und         |
|   stop_fade, continue_fade,    | timedelta (int oder float in Sekunden) auf einen angegebenen Wert auf oder     |
|   instant_set, update)         | ab. So wird z.B.: **sh.living.light.fade(100, 1, 2.5)** das Licht im           |
|                                | Wohnzimmer mit einer Schrittweite von **1** und einem Zeitdelta von **2,5**    |
|                                | Sekunden auf **100** herunter regeln. Bei manueller Änderung wird der Prozess  |
|                                | gestoppt. Dieses Verhalten kann jedoch durch stop_fade oder continue_fade      |
|                                | geändert werden. Genaueres dazu ist in den Beispielen unten zu finden.         |
+--------------------------------+--------------------------------------------------------------------------------+
| remove_timer()                 | Entfernen eines vorher mit der Funktion timer() gestarteten Timers ohne dessen |
|                                | Ablauf abzuwarten und die mit dem Ablauf verbundene Aktion auszuführen.        |
+--------------------------------+--------------------------------------------------------------------------------+
| return_children()              | Liefert die Item-Pfade der direkt untergeordneten Items zurück. Aufruf:        |
|                                | for child in sh.item.return_children(): ...                                    |
+--------------------------------+--------------------------------------------------------------------------------+
| return_parent()                | Liefert den Item-Pfad des übergeordneten Items zurück.                         |
|                                | Aufruf: sh.item.return_parent()                                                |
+--------------------------------+--------------------------------------------------------------------------------+
| timer(time, value)             | Funktioniert wir **autotimer()**, ausser dass die Aktion nur einmal ausgeführt |
|                                | wird.                                                                          |
+--------------------------------+--------------------------------------------------------------------------------+


Weitere Funktionen sollten **nicht** mehr genutzt werden, dafür gibt es die :doc:`Properties </referenz/items/properties>`.


Beispiele für die Nutzung von Funktionen
----------------------------------------

Die Funktionen von Items können in Logiken, in eval Ausdrücken (Attribute eval, on_change, on_update) und
beim Schreiben von Plugins verwendet werden.

Die folgende Beispiel Logik nutzt einige der oben beschriebenen Funktionen:

.. code-block:: python
   :caption:  logics/sample.py

   # getting the parent of item
   sh.item.return_parent()

   # get all children for item and log them
   for child in sh.item.return_children():
      logger.debug( ... )

   # set the item after 10 minutes to 42
   sh.item.autotimer('10m', 42)

   # disable autotimer for item
   sh.item.autotimer()

   # will in- or decrement the living room light to 100 by a stepping of ``1`` and a timedelta of ``2.5`` seconds.
   # As soon as the item living.light gets changed manually, the fader stops.
   sh.living.light.fade(100, 1, 2.5)

Die folgenden Beispiele erläutern die fade-Funktion im Detail. stop_fade und continue_fade werden als
reguläre Ausdrücke angegeben/verglichen (case insensitive).
Beispiel 1: Der Fade-Prozess wird nur gestoppt, wenn ein manueller Item-Wert über das Admin-Interface
eingegeben wurde. Wird das Item von einem anderen Caller aktualisiert, wird normal weiter gefadet.
Beispiel 2: Der Fade-Prozess wird durch sämtliche manuelle Item-Änderungen gestoppt, außer die Änderung
kommt von einem Caller, der "KNX" beinhaltet.
Beispiel 3: Der Fade-Prozess wird bei jeder manuellen Item-Änderung gestoppt. Die erste Wertänderung
findet erst nach Ablauf der delta Zeit statt, in dem Fall wird der Wert also (erst) nach 2,5 Sekunden um 1 erhöht/verringert.
Beispiel 4: Wird die Fade-Funktion für das gleiche Item erneut mit anderen Werten aufgerufen und
der update Parameter ist auf True gesetzt, dann wird das Fading "on the fly" den neuen Werten angepasst.
So könnte während eines Hochfadens durch Setzen eines niedrigeren Wertes der Itemwert direkt abwärts gefadet werden.
Auch die anderen Parameter werden für den aktuellen Fade-Vorgang überschrieben/aktualisiert.

   .. code-block:: python
      :caption:  logics/fading.py

      # erstes Beispiel
      sh.living.light.fade(100, 1, 2.5, stop_fade=["admin:*"])

      # zweites Beispiel
      sh.living.light.fade(100, 1, 2.5, continue_fade=["KNX"])

      # drittes Beispiel
      sh.living.light.fade(100, 1, 2.5, instant_set=False)

      # viertes Beispiel
      sh.living.light.fade(100, 1, 2.5, update=True)
      sh.living.light.fade(5, 2, 5.5, update=True)

Der folgende Beispiel eval Ausdruck sorgt dafür, dass ein Item den zugewiesenen Wert nur dann übernimmt,
wenn die Wertänderung bzw. das Anstoßen der eval Funktion über das Admin Interface erfolgt ist und das
letzte Update vor der aktuellen Triggerung über 10 Sekunden zurück liegt.

.. code-block:: python

  eval: value if sh..self.triggered_by().startswith('admin') and sh..self.update_age() > 10 else None
