.. index:: Logiken; Konfigurationsdatei /etc/logic.yaml
.. index:: Konfigurationsdateien; /etc/logic.yaml

.. _`logic.yaml`:

logic.yaml
==========

Logiken in SmartHomeNG sind Python Skripte (wie der Core von SmatHomeNH auch). Diese Skripte
werden im Verzeichnis **../logics** abgelegt. Um SmartHomeNG wissen zu lassen, wann eine
Logik gestartet werden soll und welches Python Skript dann genutzt werden soll, muss jede Logik
in der Datei **../etc/logic.yaml** konfiguriert werden:

.. code-block:: yaml
   :caption: logic.yaml

   MyLogic:
       filename: logic.py
       crontab: init
       watch_item: mydoorcontact

Mit dem Beispiel oben, würde SmartHomeNG in ``/usr/local/smarthome/logics/`` nach der Datei
``logic.py`` suchen. Die Logik würde einmal beim Start von SmartHomeNG ausgeführt und wenn sich
der Wert des Items `watch_item` ändert.

.. note::

   Ab SmartHomeNG v1.6 können Logiken vollständig im Admin Interface erstellt und konfiguriert werden.

Details zur Konfiguration von Logiken finden sich :doc:`hier <../logiken>` .
