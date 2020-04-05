.. index:: items; functions
.. index:: functions; items

.. role:: bluesup
.. role:: redsup


Functions of an item
====================

Each defined item offers the following methods, which can be used in **eval** expressions or logics.


+--------------------------------+-------------------------------------------------------------------------------+
| **Function**                   | **Description**                                                               |
+================================+===============================================================================+
| autotimer(time, value, compat) | Sets a timer for each value change of the item. Specified is the time         |
|                                | (**time**) that should elapse until the item is set to the value (**value**). |
|                                | The time is given in seconds. An indication of the duration in minutes is     |
|                                | possible as in '10m'. For the meaning and effect of **compat** please read    |
|                                | the used documentation page **autotimer** under Configuration/Std.-Attributes |
+--------------------------------+-------------------------------------------------------------------------------+
| fade(end, step, delta)         | Dimms the item with the defined increment (int or float) and timedelta        |
|                                | (int or float in seconds) to a specified value. For example:                  |
|                                | **sh.living.light.fade(100, 1, 2.5)** changes the light in the living room    |
|                                | with a step size of **1** and a time delta of **2.5** seconds **100** down.   |
+--------------------------------+-------------------------------------------------------------------------------+
| return_children()              | Returns the item paths of the directly subordinate items.                     |
|                                | Called like this: for child in sh.item.return_children(): ...                 |
+--------------------------------+-------------------------------------------------------------------------------+
| return_parent()                | Returns the item path of the parent item.                                     |
|                                | Called like this: sh.item.return_parent()                                     |
+--------------------------------+-------------------------------------------------------------------------------+
| timer(time, value, compat)     | Works like **autotimer()**, except that the action is executed only once.     |
|                                | For the meaning and effect of **compat** please read the used documentation   |
|                                | page **autotimer** under Configuration/Std.-Attributes.                       |
+--------------------------------+-------------------------------------------------------------------------------+



Furthermore, the following functions are supported, but **from SmartHomeNG v1.6** should not longer be used.
Please use the corresponding properties introduced in SmartHomeNG v1.6 instead.

Since these functions are deprecated, the documentation hasn't been translated to english.

+------------------------+------------------------------------------------------------------------------+
| **Function**           | **Description**                                                              |
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

