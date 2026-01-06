..index:: Logiken; Code-Files

logics/\*.py
============

.. _`logic program files`:

Übersicht
---------

Logiken werden in SmartHomeNG durch einfache Python Skripte bereitgestellt. Damit SmartHomeNG
die Skripte findet, müssen sie unter **../logics** abgelegt sein. Zusätzlich
müssen diese Logiken in der Datei **logic.yaml** im Verzeichnis  **../etc**
konfiguriert werden.


---------------------------------------
Logik Code im Verzeichnis **../logics**
---------------------------------------

Dieses Verzeichnis enthält die Logiken, welche von SmartHomeNG verwendet werden. Diese Logiken
schreibst Du bei Bedarf selbst.

Eine Logik ist grundsätzlich ein Python Skript. Es gibt jedoch einige zusätzliche Konventionen.
Wann und wie die Logik ausgeführt wird, wird in **../etc/logics.yaml** konfiguriert.

Falls das Blockly Plugin zum schreiben einer Logik genutzt wird, hat eine Logik zwei Dateien.
Eine Datei enthält den Blockly Code (Dateiendung **.blockly**) und die andere Datei enthält den
generierten Python Code (Dateiendung **.py**).

.. note::

   Ab SmartHomeNG v1.4 können Logiken vollständig in der graphischen Administrationsoberfläche
   **Backend** erstellt und konfiguriert werden.

   .. image:: ../assets/backend_logik_editor.jpg


Für weitere Details zur Konfiguration von Logiken, bitte die Seite :doc:`Logiken </konfiguration/logiken>` im Abschnitt Konfiguration lesen.

Für Details zur Erstellung von Logiken, bitte den Abschnitt :doc:`Logiken </logiken/logics>` dieser Dokumentation lesen.

