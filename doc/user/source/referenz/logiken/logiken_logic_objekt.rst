
.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup

====================================
Die Objekte **logic** und **logics**
====================================

.. index:: logic Objekt; Logiken
.. index:: Logiken; logic Objekt

Das ``logic`` Objekt
====================

Dieses Objekt bietet Zugriff auf das aktuelle Logikobjekt. Es ist möglich, während der Laufzeit die meisten
logischen Attribute (wie crontab, cycle, ...) abzufragen und ändern. Diese Änderungen gehen nach dem Neustart
von SmartHomeNG verloren, da sie nicht in die Konfigurationsdatei ``etc/logic.yaml`` geschrieben werden.

Ein Zugriff auf das Objekt ``logic`` ist nur aus der Logik selbst zur Laufzeit möglich.


Definierte Methoden des Logikobjekts:

+----------------------+--------------------------------------------------------------------------------------------------------+
| Methode              | Erläuterung                                                                                            |
+======================+========================================================================================================+
| ``logic.id()``       | Diese Methode liefert dem Namen der Logik wie in **../etc/logic.yaml** angegeben.                      |
+----------------------+--------------------------------------------------------------------------------------------------------+
| ``logic.last_run()`` | Diese Methode liefert den letzten Lauf dieser Logik (vor aktuellen Lauf).                              |
+----------------------+--------------------------------------------------------------------------------------------------------+
| ``logic.disable()``  | Konfigurierte Logiken sind standardmäßig aktiv und werden entsprechend der Konfiguration ausgeführt.   |
|                      | Diese Methode deaktiviert die Logik, sodass deren Ausführung unterbunden wird. (Ab SmartHomeNG v1.3)   |
+----------------------+--------------------------------------------------------------------------------------------------------+
| ``logic.enable()``   | Eine bereits deaktivierte Logik kann mit dieser Methode wieder aktiviert werden. (Ab SmartHomeNG v1.3) |
+----------------------+--------------------------------------------------------------------------------------------------------+


Vordefinierte Attribute des Logikobjekts:

+--------------------------------+-----------------------------------------------------------------------------------------+
| Attribut                       | Erläuterung                                                                             |
+================================+=========================================================================================+
| ``logic.name``                 | Das Attribut logic.name liefert das selbe Ergebnis wie die Methode logic.id()           |
+--------------------------------+-----------------------------------------------------------------------------------------+
| ``logic.crontab``              | Das Attribut liefert das aktuelle **crontab** Setting dieser Logik.                     |
+--------------------------------+-----------------------------------------------------------------------------------------+
| ``logic.cycle``                | Das Attribut liefert das aktuelle **cycle** Setting dieser Logik.                       |
+--------------------------------+-----------------------------------------------------------------------------------------+
| ``logic.prio``                 | Das Attribut liefert das aktuelle **prio** Setting dieser Logik.                        |
+--------------------------------+-----------------------------------------------------------------------------------------+
| ``logic.filename``             | Das Attribut liefert den Dateinamen des Python Skripts dieser Logik.                    |
+--------------------------------+-----------------------------------------------------------------------------------------+
| ``logic.<parameter>``          | Liefert den konfigurierten Parameter <parameter> oder den Wert einer                    |
|                                | in einem vorherigen Lauf dieser Logik persistieren Variabl                              |
+--------------------------------+-----------------------------------------------------------------------------------------+

Zusätzlich gibt es noch das Dictionary ``trigger``, welches Infromationen dazu enthält, wodurch der aktuelle Lauf
der Logik getriggert wurde.



.. index:: trigger dict; Logiken
.. index:: Logiken; trigger dict

Das ``trigger`` Dictionary
--------------------------

Das ``trigger`` dict ist ein Python-Dictionary, welches als Laufzeitumgebung einige Informationen über das
Ereignis liefert, das die Logik ausgelöst hat.

Das Dictionary enthält folgende Informationen:

+-------------------------------+--------------------------------------------------------------------------------------------------------+
| Attribut/Funktion             | Erläuterung                                                                                            |
+===============================+========================================================================================================+
| ``trigger['by']``             | Auslöser (``Scheduler``, ``Item``, etc.)                                                               |
+-------------------------------+--------------------------------------------------------------------------------------------------------+
| ``trigger['source']``         | enthält beim Auslöser ``Item`` den Pfad des Items, welches die Logik getriggert hat und beim           |
|                               | Auslöser ``Scheduler`` die Information ob es ein ``cron`` oder ein ``cycle`` Eintrag war.              |
+-------------------------------+--------------------------------------------------------------------------------------------------------+
| ``trigger['source_details']`` | Falls eine Logik aus einem Item heraus getriggert wurde (also trigger['by'] == Item ist), enthält      |
|                               | ``trigger['source_details']`` weitere Details zum Auslöser (Beispiel: 'knx:1.1.241:ga=3/3/5')          |
|                               | Falls der Auslöser der Scheduler war, enthält ``trigger['source_details']`` die Zyklus Teit oder den   |
|                               | auslösenden ``crontab`` Eintrag.                                                                       |
+-------------------------------+--------------------------------------------------------------------------------------------------------+
| ``trigger['dest']``           |                                                                                                        |
+-------------------------------+--------------------------------------------------------------------------------------------------------+
| ``trigger['value']``          | enthält den Wert des Items, dass die Logik getriggert hat.                                             |
+-------------------------------+--------------------------------------------------------------------------------------------------------+


.. index:: logics Objekt; Logiken
.. index:: Logiken; logics Objekt

Das ``logics`` Objekt
=====================

Zugriff auf das Logics-API über das logics Objekt:

+---------------------------------+---------------------------------------------------------------------------------------------------------+
| Methode                         | Erläuterung                                                                                             |
+=================================+=========================================================================================================+
| logics.<method>                 | ermöglicht den Zugriff auf das Logics API, welches unter **APIs von SmartHomeNG** im Abschnitt          |
|                                 | **Entwicklung** beschrieben ist. Im folgenden sind einige Beispiele aufgeführt.                         |
+---------------------------------+---------------------------------------------------------------------------------------------------------+
| logics.scheduler_add()          | Hinzufügen eines Scheduler Eintrages für den logics-Namensraum. Der Syntax entspricht der               |
|                                 | scheduler.add() Methode.                                                                                |
+---------------------------------+---------------------------------------------------------------------------------------------------------+
| logics.scheduler_change()       | Ändern eines Scheduler Eintrages im logics-Namensraum. Der Syntax entspricht der scheduler.change()     |
|                                 | Methode.                                                                                                |
+---------------------------------+---------------------------------------------------------------------------------------------------------+
| logics.scheduler_remove()       | Löschen eines Scheduler Eintrages im logics-Namensraum. Der Syntax entspricht der scheduler_remove()    |
+---------------------------------+---------------------------------------------------------------------------------------------------------+
| logics.trigger()                | Triggern einer im Logik                                                                                 |
+---------------------------------+---------------------------------------------------------------------------------------------------------+
| logics.set_config_section_key() | Setzt den Wert eines Schlüssels für eine angegebene Logik (Abschnitt) permanent in ../etc/logic.yaml    |
+---------------------------------+---------------------------------------------------------------------------------------------------------+

Der vollständige Syntax der Methoden kann im Abschnitt :doc:`Entwicklung/APIs von SmartHomeNG </entwicklung/APIs>`
dem **Logics-API** entnommen werden.

