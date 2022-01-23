
.. index:: Entwicklung; Logiken

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup


Logiken :bluesup:`under construction`
=====================================


Einführung
----------

Logiken in SmartHomeNG sind in Python geschriebene Skript. Sie werden im Unterordner ``logics/`` abgelegt
und definiert in ``etc/logic.yaml``.
Die Konfigurationsdatei ``etc/logic.yaml`` beschreibt für SmartHomeNG unter welchen Bedingungen eine bestimmte Logik auszuführen ist.

Die Vorlage für das Skript einer Logik kann folgendermaßen aussehen:


.. literalinclude:: /logics/logic.tpl
   :caption: /logics/example_logic.py
   :language: python


> - - - - - - - - - - - - - - - - - - - -


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


