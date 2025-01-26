
.. index:: Entwicklung; Logiken

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup


=====================================
Logiken :bluesup:`under construction`
=====================================

Eine Logik besteht aus einem Python Skript sowie einer Reihe von Parametern die den Aufruf (das Triggern) der Logik
steuern. Eine Logik kann während der Laufzeit von SmartHomeNG geladen und entladen werden. Dadurch sind Veränderungen
ein einer Logik möglich, ohne SmartHomeNG neu starten zu müssen.

Wird ein zusätzliches Python Modul in einer Logik benötigt, so kann eine ``requirements.txt`` im Verzeichnis ``logics`` erstellt 
und in dieser Datei Namen und Versionen für die Installation via PIP notiert werden.
In diesem Fall muss SmartHomeNG auf jeden Fall neu gestartet werden da die Überprüfung nur beim Start von SmartHomeNG erfolgt.


Einführung
==========

Das eigentliche Python Skript einer Logik muss im Verzeichnis ``../logics`` der SmartHomeNG Installation abgelegt
werden. Damit die Logik getriggert und ausgeführt wird, muss sie zusätzlich in der Konfigurationsdatei
``../etc/logic.yaml`` konfiguriert werden. Hier wird festgelegt, unter welchen Bedingungen eine bestimmte Logik
auszuführen ist.

Wenn eine Logik mit der Admin GUI erstellt wurde, ist sie nach dem ersten erfolgreichen Laden pausiert (disabled).
Damit die Logik ausgeführt werden kann, muss sie zuerst mit dem "Play"-Button enabeld werden. (Der "Play"-Button
wechselt dabei zum "Pause"-Button.)


Behandlung von Fehlern in der Logik
-----------------------------------

Syntaktische Fehler
~~~~~~~~~~~~~~~~~~~

Wenn eine Logik geladen wird, entweder beim Start von SmartHomeNG oder durch die Admin GUI, wird das Python Skript,
wie ein normales Python Programm, in einen Bytecode übersetzt. Falls hierbei ein grober syntaktischer Fehler auftritt,
wird die Logik nicht geladen und es wird ein entsprechender Fehler geloggt.

Beispiel: Folgende Test Logik

.. code-block:: python

    #!/usr/bin/env python3
    # test_logic.py

    logger.warning("Start der Logik")

    Hier steht Müll

    logger.warning("Ende der Logik")


erzeugt beim laden/übersetzen folgenden Logeintrag:

.. code-block:: text

    2022-01-24  12:51:26 ERROR    lib.logic            Exception: invalid syntax (test_logic.py, line 6)
    Traceback (most recent call last):
      File "/usr/local/shng_dev/lib/logic.py", line 1034, in _generate_bytecode
        self.bytecode = compile(code, self.pathname, 'exec')
      File "/usr/local/shng_dev/logics/test_logic.py", line 6
        Hier steht Müll
             ^
    SyntaxError: invalid syntax


Laufzeit Fehler
~~~~~~~~~~~~~~~

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


Template für eine neue Logik
----------------------------

Eine neue Logik sollte möglichst auf der folgenden Vorlage ``logic.tpl`` aufbauen.
Die Template Datei ist im Verzeichnis ``logics/`` abgelegt:

.. literalinclude:: /logics/logic.tpl
   :caption: /logics/logic.tpl
   :language: python

Um zum Beispiel eine Logik ``example`` zu erzeugen, muss zuerst die Datei ``logics/logic.tpl`` auf die
Datei ``logics/example.py`` kopiert werden und in der erstellten Datei der eigentliche Code der Logik erfasst werden.

Anschließend muss noch in der Konfigurationsdatei ``etc/logic.yaml`` die Konfiguration für die Logik festgelegt
werden.

Die Minimalkonfiguration sieht für das Beispiel folgendermaßen aus:

.. code-block:: yaml

    example:
        filename: example.py

Der Name der Logik wird durch den Namen des Abschnitts ``example`` in der Konfigurationsdatei festgelegt. Unter diesem
Namen wird die Logik innerhalb von SmartHomeNG angesprochen. Der Parameter ``filename`` legt fest, in welcher
Datei der Code für die Logik ``example`` gespeichert ist. Dafür kann im Prinzip ein beliebiger Dateiname gewählt
werden, solange die Extension ``.py`` ist. Um mögliche Verwirrungen zu vermeiden, wird jedoch empfohlen den
Namen der Logik und den Namen der Datei gleich zu wählen. Generell sollten Dateinamen nur aus Kleinbuchstaben
bestehen, da je nach verwendetem Betriebssystem das Dateisystem evtl. Case sensitiv ist und ``Example.py`` eine
andere Datei sein kann als ``example.py``.

Erst mit der Existenz dieser Konfiguration kann die Logik gestartet werden. Die Logik würde zwar noch nicht durch
ein normaler Ereignis innerhalb von SmartHomeNG getriggert, da keine Trigger definiert sind, die Logik kann jedoch
aus der Admin GUI getriggert werden.

Wenn die Logik zum Beispiel beim Start von SmartHomeNG getriggert werden soll, so muss noch der folgende ``crontab``
Parameter angebeben werden:

.. code-block:: yaml

    example:
        filename: example.py
        crontab: init


Verlassen einer Logik
---------------------

Normalerweise wird der aktuelle Lauf einer Logik dadurch beendet, dass das Ende des Codes der Hauptroutine
erreicht wird. In einigen Fällen kann es jedoch sinnvoll sein, die Logik mitten aus dem Code heraus oder as einer
Funktion heraus zu beenden/zu verlassen.

Dafür kann eine spezielle Exception ausgelöst werden. Das geschieht mit dem Befehl ``raise LeaveLogic()``.
Details hierzu sind in der :ref:`Referenz <logik_exceptions_leavelogic>` zu finden.


Beispiele
=========

Die folgende Beispielkonfiguration definiert 4 Logiken:

* Die erste Logik mit Namen ``InitSmartHomeNG`` befindet sich in der Datei ``logics/initsmarthomeng.py``.
  Das Attribut ``crontab: init`` weist SmartHomeNG an diese Logik direkt nach dem Start auszuführen.
* Die zweite Logik mit dem Namen ``Hourly`` befindet sich in der Datei ``logics/time.py``
  und das Attribut ``cycle: 3600`` weist SmartHomeNG an die Logik alle 3600 Sekunden (jede Stunde) auszuführen.
* Die dritte Logik mit Namen ``Gate`` befindet sich in der Datei ``logics/gate.py`` und das Attribut
  ``watch_item: gate.alarm`` weist SmartHomeNG an die Logik auszuführen, wenn der Wert des Items gate.alarm sich ändert.
* Die vierte Logik mit Namen ``disks`` befindet sich in der Datei ``logics/disks.py``. Der crontab Eintrag weist SmartHomeNG an
  diese Logik alle 5 Minuten auszuführen. Der Parameter ``usage_warning`` ist ein benutzerdefinierter Parameter, der
  in der Logik verwendet wird, um einen Schwellwert zu definieren.

.. code-block:: yaml
   :caption:  etc/logic.yaml

   InitSmarthomeNG:
       filename: initsmarthomeng.py
       crontab: init

   Hourly:
       filename: time.py
       cycle: 3600

   Gate:
       filename: gate.py
       watch_item: gate.alarm    # monitor for changes

   disks:
       filename: disks.py
       # 'crontab: run at start and every 5 minutes'
       crontab:
         - init
         - '0,5,10,15,20,25,30,35,40,45,50,55 * * *'
       usage_warning: 500


