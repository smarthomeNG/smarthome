
.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup

.. index:: Struktur; Logiken
.. index:: Logiken; Struktur

==========
Exceptions
==========

Laufzeit Fehler
===============

Nachdem eine Logik erfolgreich geladen wurde, können bei der Ausführung der Logik Laufzeit Fehler auftreten.
Falls ein Laufzeitfehler nicht innerhalb der Logik abgefangen wird, führt er zur Beendigung des aktuellen
Laufes der Logik und es wird ein entsprechender Fehler geloggt. Die Logik bleibt jedoch geladen und wird, wenn sie
getriggert wird, erneut ausgeführt.

Beispiel: Folgende Test Logik

.. code-block:: python

    #!/usr/bin/env python3
    # test_logic.py

    logger.warning("Start der Logik")

    var = int('abc')

    logger.warning("Ende der Logik")


erzeugt zur Laufzeit folgenden Logeintrag:

.. code-block:: text

   2022-01-24  13:55:14 ERROR    logics.test_logic    In der Logik ist ein Fehler aufgetreten:
      Logik 'test_logic', Datei '/usr/local/shng_dev/logics/test_logic.py', Zeile 6
      Hauptroutine der Logik, Exception: invalid literal for int() with base 10: 'abc'


.. index:: Logiken; LeaveLogic
.. _logik_exceptions_leavelogic:

Exception LeaveLogic
====================

Normalerweise wird der aktuelle Lauf einer Logik dadurch beendet, dass das Ende des Codes der Hauptroutine
erreicht wird.

In einigen Fällen kann es jedoch sinnvoll sein, die Logik mitten aus dem Code heraus oder as einer Funktion heraus
zu beenden/zu verlassen.

Dafür kann eine spezielle Exception ausgelöst werden. Das geschieht mit dem Befehl ``raise LeaveLogic()``:

.. code-block:: python

   ...

   if logik_beenden:
      raise LeaveLogic()

   ...

Optional kann der Exception ein Grund als Parameter mitgegeben werden.

.. code-block:: python

   ...

   if logik_beenden:
      raise LeaveLogic('Die Logik sollte beendet werden')

   ...

Falls ein Grund angegeben wird, erfolgt ein Logeintrag mit dem Level INFO, der das Verlassen und diesen Grund loggt.

