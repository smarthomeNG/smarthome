.. index:: Standard-Attribute; type
.. index:: type

.. index:: Items; Datentypen
.. index:: Datentypen

`type`
------

Das Attribut **type** legt den Datentyp des Items fest. Dadurch wird bestimmt, was für Daten in
dem Item gespeichert werden können und wie das Item verwendet werden kann.

Folgende mögliche Datentypen sind für Items definiert:

+----------+--------------------------------------------------------------------------------------+
| **type** | **Beschreibung**                                                                     |
+----------+--------------------------------------------------------------------------------------+
| bool     | Ein Wahrheitswert (on, 1, True or off, 0, False). Intern wird **True** und           |
|          | **False** benutzt, z.B. **if sh.item()**                                             |
+----------+--------------------------------------------------------------------------------------+
| num      | Eine Zahl (Ganzzahl oder Fließkomma)                                                 |
+----------+--------------------------------------------------------------------------------------+
| str      | Eine Zeichenkette                                                                    |
+----------+--------------------------------------------------------------------------------------+
| list     | Eine Liste/Array von Werten, findet bei bestimmten KNX Datenpunkten Anwendung        |
+----------+--------------------------------------------------------------------------------------+
| dict     | Ein Python Dictionary - Wenn in den Item Definitionen ein Wertzuweisung mit dem      |
|          | Attribut **value** erfolgen soll, muss unbedingt darauf geachtet werden, dass der    |
|          | angegebene Wert in Anführungszeichen gesetzt wird, damit yaml den Wert nicht als     |
|          | Datenstruktur interpretiert. (Also so: value: "{'k1': 'v1', 'k2': 'v2'}" )           |
+----------+--------------------------------------------------------------------------------------+
| foo      | allgemeiner Typ - Items dieses Typs können Daten beliebiger anderer Datentypen       |
|          | aufnehmen                                                                            |
+----------+--------------------------------------------------------------------------------------+
| scene    | Eine Szene - Die eigentliche Konfiguration der Szene für das jeweilige Item wird in  |
|          | einer eigenen Datei im Verzeichnis **../scenes** von SmartHomeNG gespeichert. Dort   |
|          | muss es für jede Szene (jedes Item vom Typ *scene* eine eigene Konfigurationsdatei   |
|          | mit dem Namen des Item-Pfades geben. Genaueres ist dem Abschnitt                     |
|          | **Konfiguration / Szenen** dieser Dokumentation zu entnehmen.                        |
+----------+--------------------------------------------------------------------------------------+

