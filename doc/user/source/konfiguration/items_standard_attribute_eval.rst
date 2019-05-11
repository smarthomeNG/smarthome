.. index:: Standard-Attribute; eval_trigger
.. index:: eval_trigger
.. index:: Standard-Attribute; eval
.. index:: eval

*eval* und *eval_trigger*
=========================

Attribut *eval*
---------------

Wenn ein Item einen neuen Wert zugewiesen bekommen soll (z.B. via KNX
oder Logik), wird der neue Wert zunächst in **value**
zwischengespeichert. Wenn ein Attribut **eval** existiert, so wird der
Ausdruck hinter **eval = …** ausgeführt und das Ergebnis dieses
Ausdrucks als neuer Wert ins Item übernommen. Sollten alter und neuer
Wert des Items unterschiedlich sein oder ist das Attribut
**enforce_updates** vorhanden und auf **True** gesetzt, dann werden
abhängige Logiken getriggert.

Im folgenden Beispiel liefert ein Sensor die Temperatur in Fahrenheit.
Das Item soll aber die Temperatur in °Celsius speichern.

.. code-block:: yaml

   Temperatur:
       # Formel (°F  -  32)  x  5/9 = °C
       type: num
       eval: (value - 32 ) * 5 / 9  # Aus 68°F werden somit 20°C

Das Eval Attribut kann auch bis zu einem gewissen Grad Logiken
beinhalten. Wichtig ist, dass bei der Angabe eines if auch ein else
implementiert sein muss. Außerdem ist dem Item ein **sh.** voran zu
setzen. Die () Klammern hinter dem Item sind nötig, um den Item-Wert
abzufragen.

.. code-block:: yaml

   Temperatur:
       Trigger:
           # Wird wahr, wenn die Temperatur über 20 Grad wird und falsch, wenn nicht.
           type: bool
           eval: 1 if sh.Temperatur() > 20 else 0
           eval_trigger: Temperatur

Weiter ist es möglich, direkt die Werte der eval_trigger im eval
entsprechend auszuwerten:

::

   | keyword | Beschreibung                                                            |
   | ------- | ----------------------------------------------------------------------- |
   |   sum   | Errechnet die Summe aller eval_trigger Items.                           |
   |   avg   | Errechnet den Mittelwert aller Items auf die sich eval_trigger bezieht. |
   |   min   | Errechnet den Minimalwert aller Items auf die sich eval_trigger bezieht.|
   |   max   | Errechnet den Maximalwert aller Items auf die sich eval_trigger bezieht.|
   |   and   | Setzt den Wert des Items auf True, wenn alle Items auf die sich         |
   |         | eval_triggers bezieht den Wert True haben.                              |
   |   or    | Setzt den Wert des Items auf True, wenn eines der Items auf die sich    |
   |         | eval_triggers bezieht den Wert True haben.                              |

Beispiel:

.. code-block:: yaml

   Raum:

       Temperatur:
           type: num
           name: average temperature
           eval: avg
           eval_trigger:
             - room_a.temp
             - room_b.temp

       Praesenz:
           type: bool
           name: movement in on the rooms
           eval: or
           eval_trigger:
             - room_a.presence
             - room_b.presence

Ab SmartHomeNG v1.3 wird das Python Modul
`math <https://docs.python.org/3.4/library/math.html>`__ bereitgestellt
und es können entsprechende Funktionen genutzt werden.

Beispiel:

.. code-block:: yaml

   oneitem:
     type: num
     eval: ceil(sh.otheritem() / 60.0)

Ab SmartHomeNG v1.3 können für **eval** auch relative `Relative Item
Referenzen <https://github.com/smarthomeNG/smarthome/wiki/Items:-Relative-Item-Referenzen>`__
genutzt werden. Dann müssen Bezüge auf andere Items nicht mehr absolut
angegeben werden sondern können sich relative auf andere Items beziehen.

Attribut *eval_trigger*
-----------------------

Das Attribut eval_trigger legt eine Abhängigkeit von anderen Items fest.
Sobald sich diese im Wert ändern, wird eine Neuberechnung gestartet. Das
obige Beispiel könnte so erweitert werden:

.. code-block:: yaml

   TemperaturFahrenheit:
       type: num
   TemperaturCelsius:
       # Formel (°F  -  32)  x  5/9 = °C
       type: num
       eval: (sh.TemperaturFahrenheit() - 32 ) * 5 / 9  # Aus 68°F werden somit 20°C
       eval_trigger: TemperaturFahrenheit

Hier gibt es nun ein Attribut **eval_trigger** mit dem Item Namen
**TemperaturFahrenheit**. Sobald sich dieses Item ändert, wird auch der
Wert von **TemperaturCelsius** neu berechnet.

Im Attribut **eval_trigger** kann eine Liste mehrerer Items angegeben
werden. Die Items müssen für das alte *.conf Format jeweils durch ein
‘\|’ voneinander getrennt werden. In der*.yaml kann eine Liste angegeben
werden (siehe oben). Der Ausdruck unter **eval** wird neu berechnet,
wenn sich eines dieser Items verändert. Die Items können auch mit einem
Stern generalisiert werden. Temperatur.\* bedeutet, dass alle
Kinderitems des Temperatur-Items zum Evaluieren des Items führen. Oder
\*.Trigger sorgt dafür, dass das Item durch alle Kind-Items mit dem
Namen “Trigger” aktualisiert werden kann, also z.B. durch
Temperatur.Trigger, Licht.OG.Trigger, etc.

Ab SmartHomeNG v1.3 können für **eval_trigger** auch relative `Relative
Item
Referenzen <https://github.com/smarthomeNG/smarthome/wiki/Items:-Relative-Item-Referenzen>`__
genutzt werden. Dann müssen Bezüge auf andere Items nicht mehr absolut
angegeben werden sondern können sich relative auf andere Items beziehen.
