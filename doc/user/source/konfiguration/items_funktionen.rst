.. index:: Items; Funktionen
.. index:: Funktionen; Items

.. role:: bluesup
.. role:: redsup


Funktionen eines Items :bluesup:`update`
========================================


Jedes definierte Item bietet die folgenden Methoden an, die unter anderem in **eval** Ausdrücken
genutzt werden können.

+--------------------------------+------------------------------------------------------------------------------+
| **Funktion**                   | **Beschreibung**                                                             |
+================================+==============================================================================+
| autotimer(time, value, compat) | Setzt einen Timer bei jedem Werte-Wechsel der Items. Angegeben wird die      |
|                                | Zeit (**time**) die vergehen soll, bis das Item auf den Wert (**value**)     |
|                                | gesetzt wird. Die Zeitangabe erfolgt in Sekunden. Eine Angabe der Dauer in   |
|                                | Minuten ist wie in '10m' möglich. Die Bedeutung und Wirkungsweise von        |
|                                | **compat** bitte auf der Seite                                               |
|                                | :doc:`autotimer <./items_standard_attribute_autotimer>` nachlesen.           |
+--------------------------------+------------------------------------------------------------------------------+
| fade(end, step, delta)         | Blendet das Item mit der definierten Schrittweite (int oder float) und       |
|                                | timedelta (int oder float in Sekunden) auf einen angegebenen Wert auf oder   |
|                                | ab. So wird z.B.: **sh.living.light.fade(100, 1, 2.5)** das Licht im         |
|                                | Wohnzimmer mit einer Schrittweite von **1** und einem Zeitdelta von **2,5**  |
|                                | Sekunden auf **100** herunterregeln.                                         |
+--------------------------------+------------------------------------------------------------------------------+
| return_children()              | Liefert die Item-Pfade der direkt untergeordneten Items zurück. Aufruf:      |
|                                | for child in sh.item.return_children(): ...                                  |
+--------------------------------+------------------------------------------------------------------------------+
| return_parent()                | Liefert den Item-Pfad des übergeordneten Items zurück.                       |
|                                | Aufruf: sh.item.return_parent()                                              |
+--------------------------------+------------------------------------------------------------------------------+
| timer(time, value, compat)     | Funktioniert wir **autotimer()**, ausser dass die Aktion nur einmal          |
|                                | ausgeführt wird. Die Bedeutung und Wirkungsweise von **compat** bitte auf    |
|                                | der Seite :doc:`autotimer <./items_standard_attribute_autotimer>` nachlesen. |
+--------------------------------+------------------------------------------------------------------------------+



Weiterhin werden die folgenden Funktionen unterstützt, die jedoch **ab SmartHomeNG v1.6** nicht mehr genutzt werden sollen.
Bitte stattdessen die entsprechenden in SmartHomeNG v1.6 eingeführten Properties benutzen.

+------------------------+------------------------------------------------------------------------------+
| **Funktion**           | **Beschreibung**                                                             |
+========================+==============================================================================+
| id()                   | Liefert den item-Pfad des Items zurück. Aufruf: sh.item.id()                 |
+------------------------+------------------------------------------------------------------------------+
| last_update()          | Liefert ein *datetime* Objekt mit dem Zeitpunkt des letzten Updates des      |
|                        | Items zurück. Im Gegensatz zu **last_change()** wird dieser Zeitstempel auch |
|                        | verändert, wenn sich bei einem Update der Wert des Items nicht ändert.       |
+------------------------+------------------------------------------------------------------------------+
| last_change()          | Liefert ein *datetime* Objekt mit dem Zeitpunkt der letzten Änderung des     |
|                        | Items zurück.                                                                |
+------------------------+------------------------------------------------------------------------------+
| age()                  | Liefert das Alter des Items seit der letzten Änderung des Wertes in Sekunden |
|                        | zurück.                                                                      |
+------------------------+------------------------------------------------------------------------------+
| update_age()           | Liefert das Alter des Items seit dem letzten Update in Sekunden zurück. Das  |
|                        | Update Age wird auch gesetzt, wenn sich bei einem Update der Wert des Items  |
|                        | nicht ändert. (Neu **ab SmartHomeNG v1.4**)                                  |
+------------------------+------------------------------------------------------------------------------+
| changed_by()           | Liefert einen String zurück, der auf das Objekt hinweist, welches das Item   |
|                        | zuletzt geändert hat.                                                        |
+------------------------+------------------------------------------------------------------------------+
| prev_value()           | Liefert den Wert des Items zurück, den es vor der letzten Änderung hatte.    |
+------------------------+------------------------------------------------------------------------------+
| prev_update()          | Liefert ein *datetime* Objekt mit dem Zeitpunkt des vorletzten Updates des   |
|                        | Items zurück. Im Gegensatz zu **prev_change()** wird dieser Zeitstempel auch |
|                        | verändert, wenn sich bei einem Update der Wert des Items nicht ändert.       |
+------------------------+------------------------------------------------------------------------------+
| prev_change()          | Liefert ein *datetime* Objekt mit dem Zeitpunkt der vorletzten Änderung des  |
|                        | Items zurück.                                                                |
+------------------------+------------------------------------------------------------------------------+
| prev_update_age()      | Liefert das Alter des vor-vorangegangenen Wertes in Sekunden zurück.         |
+------------------------+------------------------------------------------------------------------------+
| prev_age()             | Liefert das Alter des vorangegangenen Wertes in Sekunden zurück.             |
+------------------------+------------------------------------------------------------------------------+

