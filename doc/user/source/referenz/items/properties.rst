.. index:: Items; Properties
.. index:: Properties; Items

.. role:: bluesup
.. role:: redsup


Properties eines Items
======================

Jedes definierte Item bietet die folgenden Properties an, die unter anderem in **eval** Ausdrücken
genutzt werden können. Alle Properties sind zumindest lesend (r/o) zugreifbar. Einige Properties können
auch beschrieben (r/w) werden.

Properties sind **ab SmartHomeNG v1.6** verfügbar.


Properties werden in Logiken und eval-Ausdrücken folgendermaßen abgerufen:

.. code::

    var = sh.<Item-Pfad>.property.<Property-Name>

    # Beispiel zur Abfrage des Names eines Items:
    var = sh.wohnung.testitem.property.name


Werte für Properties, die auch geschrieben werden können (z.B. in Logiken), werden folgendermaßen gesetzt:

.. code::

    sh.<Item-Pfad>.property.<Property-Name> = value

    # Beispiel zur Abfrage des Names eines Items:
    sh.wohnung.testitem.property.name = 'Neuer Name'


+----------------------+------------+----------+------------------------------------------------------------------------------+
| **Property**         | **Access** | **Type** | **Beschreibung**                                                             |
+======================+============+==========+==============================================================================+
| attributes           | r/o        | list     | Liefert die Namen der plugin-spezfischen Attribute als Liste                 |
|                      |            |          | Auf die Werte dieser Attribute kann über dynamische Properties zugegriffen   |
|                      |            |          | werde. (Siehe Ende dieser Tabelle)                                           |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| defined_in           | r/o        | str      | Liefert den Dateinamen in dem das Item definiert wurde zurück                |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| enforce_updates      | r/w        | bool     | Setzt oder löscht den **enforce_updates** Status                             |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| eval                 | r/w        | str      | Erlaubt das Abfragen oder Setzen der eval Expression                         |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| eval_unexpanded      | r/w        | str      | Erlaubt das Abfragen oder Setzen der eval Expression. Beim Beschreiben des   |
|                      |            |          | Properties werden evtl. enthaltene relative Item Referenzen zur Nutzung      |
|                      |            |          | expandiert (analog zum Laden aus Item Konfigurationsdateien).                |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_change          | r/o        | datetime | Liefert ein *datetime* Objekt mit dem Zeitpunkt der letzten Änderung des     |
|                      |            |          | Items zurück.                                                                |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_change_age      | r/o        | float    | Liefert das Alter des Items seit der letzten Änderung des Wertes in Sekunden |
|                      |            |          | zurück.                                                                      |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_change_by       | r/o        | str      | Liefert einen String zurück, der auf das Objekt hinweist, welches das Item   |
|                      |            |          | zuletzt geändert hat.                                                        |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_update          | r/o        | datetime | Liefert ein *datetime* Objekt mit dem Zeitpunkt des letzten Updates des      |
|                      |            |          | Items zurück. Im Gegensatz zu **last_change()** wird dieser Zeitstempel auch |
|                      |            |          | verändert, wenn sich bei einem Update der Wert des Items nicht ändert.       |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_update_age      | r/o        | float    | Liefert das Alter des Items seit dem letzten Update in Sekunden zurück. Das  |
|                      |            |          | Update Age wird auch gesetzt, wenn sich bei einem Update der Wert des Items  |
|                      |            |          | nicht ändert.                                                                |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_update_by       | r/o        | str      | Liefert einen String zurück, der auf das Objekt hinweist, durch welches das  |
|                      |            |          | Item zuletzt ein Update erfahren hat.                                        |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| last_value           | r/o        | str      | Liefert den Wert des Items zurück, den es vor der letzten Änderung hatte.    |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| name                 | r/w        | str      | Erlaubt das Abfragen oder Setzen des Namens des Items                        |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| on_change            | r/o        | list     | Liefert die Liste der **on_change** Ausdrücke des Items zurück               |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| on_change_unexpanded | r/w        | list     | Liefert die Liste der **on_change** Ausdrücke des Items zurück, in der       |
|                      |            |          | relative Item Referenzen nicht expandiert sind. Beim Beschreiben des         |
|                      |            |          | Properties werden evtl. enthaltene relative Item Referenzen zur Nutzung      |
|                      |            |          | expandiert (analog zum Laden aus Item Konfigurationsdateien).                |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| on_update            | r/o        | list     | Liefert die Liste der **on_update** Ausdrücke des Items zurück               |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| on_update_unexpanded | r/w        | list     | Liefert die Liste der **on_update** Ausdrücke des Items zurück, in der       |
|                      |            |          | relative Item Referenzen nicht expandiert sind. Beim Beschreiben des         |
|                      |            |          | Properties werden evtl. enthaltene relative Item Referenzen zur Nutzung      |
|                      |            |          | expandiert (analog zum Laden aus Item Konfigurationsdateien).                |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| path                 | r/o        | str      | Liefert den Pfad des Items zurück                                            |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_change          | r/o        | datetime | Liefert ein *datetime* Objekt mit dem Zeitpunkt der vorletzten Änderung des  |
|                      |            |          | Items zurück.                                                                |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_change_age      | r/o        | float    | Liefert das Alter des vorangegangenen Wertes in Sekunden zurück.             |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_change_by       | r/o        | str      | Liefert einen String zurück, der auf das Objekt hinweist, welches das Item   |
|                      |            |          | das vorletzte mal geändert hat.                                              |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_update          | r/o        | datetime | Liefert ein *datetime* Objekt mit dem Zeitpunkt des vorletzten Updates des   |
|                      |            |          | Items zurück. Im Gegensatz zu **prev_change()** wird dieser Zeitstempel auch |
|                      |            |          | verändert, wenn sich bei einem Update der Wert des Items nicht ändert.       |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_update_age      | r/o        | float    | Liefert das Alter des vor-vorangegangenen Wertes in Sekunden zurück.         |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_update_by       | r/o        | str      | Liefert einen String zurück, der auf das Objekt hinweist, durch welches das  |
|                      |            |          | Item das vorletzte mal ein Update erfahren hat.                              |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| prev_value           | r/o        | str      | Liefert den Wert des Items zurück, den es vor der vorletzten Änderung hatte. |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| trigger              | r/w        | list     | Erlaubt das Abfragen oder Setzen der Liste der Trigger (eval_trigger) des    |
|                      |            |          | Items.                                                                       |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| trigger_unexpanded   | r/w        | list     | Erlaubt das Abfragen oder Setzen der Liste der nicht expandierten Trigger    |
|                      |            |          | (eval_trigger) des Items. Beim Beschreiben des Properties werden evtl.       |
|                      |            |          | enthaltene relative Item Referenzen zur Nutzung expandiert (analog zum       |
|                      |            |          | Laden aus Item Konfigurationsdateien).                                       |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| type                 | r/o        | str      | Liefert den Typ des Items zurück                                             |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| value                | r/w        | str      | Das Property value stellt eine Alternative zur Abfrage/Zuweisung durch       |
|                      |            |          | var= **item()** / **item(** value **)** dar.                                 |
+----------------------+------------+----------+------------------------------------------------------------------------------+
| <dynamic property>   | r/o        | str      | Als dynamische Properties werden die plugin-spezifischen Attribute unter-    |
|                      |            |          | stützt. So kann z.B. aus der smartVISU auf die KNX Sendeadresse eines Items  |
|                      |            |          | **schaltaktor** zugegriffen werden: **schaltaktor.property.knx_send**        |
|                      |            |          | Dyn. Properties sind erst in SmartHomeNG Releases nach v1.6.1 implementiert. |
+----------------------+------------+----------+------------------------------------------------------------------------------+
