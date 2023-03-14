

=========================
*eval* und *eval_trigger*
=========================


.. index:: Standard-Attribute; eval
.. index:: eval

Attribut *eval*
===============

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

Die Auswertung des **eval** Ausdrucks wird gestartet, wenn:
 - dem Item ein neuer Wert zugewiesen wird (siehe Erläuterug im ersten Absatz)
 - sich der Wert des oder der Items aus dem **eval_trigger** ändert (siehe Erläuterug weiter unten)
 - ein **timer** verwendet wird und die angegebene Zeit abgelaufen ist
 - ein **autotimer** verwendet wird und die angegebene Zeit abgelaufen ist
 - ein **crontab** definiert ist und die zeitlichen Angaben zutreffen

Das Eval Attribut kann auch bis zu einem gewissen Grad Logiken
beinhalten. Wichtig ist, dass bei der Angabe eines **if** auch ein **else**
implementiert sein muss. Außerdem ist dem Item ein **sh.** voran zu
setzen. Die () Klammern hinter dem Item sind nötig, um den Item-Wert
abzufragen. Anstelle der Klammern kann auch property.value genutzt werden.

.. code-block:: yaml

   Temperatur:
       Trigger:
           # Wird wahr, wenn die Temperatur über 20 Grad wird und falsch, wenn nicht.
           type: bool
           eval: 1 if sh.Temperatur() > 20 else 0
           # alternativ eval: 1 if sh.Temperatur.property.value > 20 else 0
           eval_trigger: Temperatur

Weiter ist es möglich, direkt die Werte der eval_trigger im eval
entsprechend auszuwerten:

+-------------+-------------------------------------------------------------------------------+
| **Keyword** | **Beschreibung**                                                              |
+=============+===============================================================================+
|   sum       | Errechnet die Summe aller **eval_trigger** Items.                             |
+-------------+-------------------------------------------------------------------------------+
|   avg       | Errechnet den Mittelwert aller Items auf die sich **eval_trigger** bezieht.   |
+-------------+-------------------------------------------------------------------------------+
|   min       | Errechnet den Minimalwert aller Items auf die sich **eval_trigger** bezieht.  |
+-------------+-------------------------------------------------------------------------------+
|   max       | Errechnet den Maximalwert aller Items auf die sich **eval_trigger** bezieht.  |
+-------------+-------------------------------------------------------------------------------+
|   and       | Setzt den Wert des Items auf True, wenn alle Items auf die sich               |
|             | **eval_triggers** bezieht den Wert True haben.                                |
+-------------+-------------------------------------------------------------------------------+
|   or        | Setzt den Wert des Items auf True, wenn eines der Items auf die sich          |
|             | **eval_triggers** bezieht den Wert True haben.                                |
+-------------+-------------------------------------------------------------------------------+

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

zusätzliche Funktionen in eval Ausdrücken
-----------------------------------------

Bereits SmartHomeNG v1.3 wird das Python Modul `math <https://docs.python.org/3.4/library/math.html>`__
bereitgestellt und es können entsprechende Funktionen genutzt werden. Außerdem sind seit SmarthomeNG v1.7 die
:doc:`Items-API </referenz/logiken/logiken_items>` als **items** (z.B. items.return_item('bla')) und das
:doc:`shtime Modul </referenz/smarthomeng/feiertage_datum_zeit>` mittels **shtime** (z.B. shtime.now()) verfügbar.

Beispiel:

.. code-block:: yaml

   oneitem:
     type: num
     eval: math.ceil(sh.otheritem() / 60.0)

Aktuell stehen zusätzlich zum Python Standard Sprachumfang folgende Packages bzw. SmartHomeNG Libraries zur Nutzung
zur Vefügung:

    - **shtime** - die SmartHomeNG Library mit Zeit- und Datumsfunktionen
    - **items** - die SmartHomeNG Library mit Funktionen zum Umgang mit Items
    - **math** - das Python Package mit mathematischen Funktionen


Seit SmartHomeNG v1.3 können für **eval** auch :doc:`Relative Item Referenzen </referenz/items/attributes_relative_referenzen>`
genutzt werden. Dann müssen Bezüge auf andere Items nicht mehr absolut angegeben werden sondern können sich relative
auf andere Items beziehen.


.. tip::

   Im Abschnitt **Logiken** ist auf der Seite :doc:`Feiertage, Daten und Zeiten </referenz/smarthomeng/feiertage_datum_zeit>`
   beschrieben, welche Feiertags- und Datums-Funktionen in Logiken benutzt werden können. Diese Funktionen können auch
   in eval Attributen genutzt werden können.


.. tip::

   Im Abschnitt **Beispiele** sind auf der Seite :doc:`eval und eval_trigger Beispiele </beispiele/eval>`
   weitere ausführliche Beispiele zu finden.


Nutzung von Userfunctions
-------------------------

Bei komplexeren Berechnungen kann es sinnvoll sein, diese in eine :doc:`Userfunction </referenz/userfunctions/userfunctions>`
auszulagern und im eval Ausdruck nur die :doc:`Userfunction </referenz/userfunctions/userfunctions>` aufzurufen.
Das bietet sich besonders an, wenn die gleiche Berechnung in mehreren Items durchgeführt werden soll.

Ein weiterer Vorteil von Userfunctions ist, dass Userfunctions modifiziert und neu geladen werden können, ohne SmartHomeNG
komplett neu starten zu müssen. Das hilft besonders während der Entwicklung.


Eval Syntax
-----------

Der Syntax eines **eval** Ausdrucks ist der Syntax einer `Python conditional expression <https://www.python.org/dev/peps/pep-0308/>`_

Dieser Syntax wird bei den Item Attributen **eval**, **on_change** und **on_update** verwendet.

Zu beachten ist, dass der Syntax einer if-Bedingung in einer Python conditional Expression folgender ist:

``eval: <expression-if-true> if <condition> else <expression-if-false>``


Beispiel:

.. code-block:: yaml

   eval: value if value>0 else 0

Die Expression setzt den Item-Wert auf den bisherigen Wert, falls er >0 ist, sonst wird der Wert auf 0 gesetzt.
Damit findet eine Zuweisung statt und on_change bzw. on_update Trigger werden ausgelöst.

Wenn das Beispiel folgendermaßen formuliert wird:

.. code-block:: yaml

   eval: 0 if value<0 else None

Hätte es auf den Item-Wert letztlich die selben Auswirkungen: Hier wird der Item-Wert auf 0 gesetzt, falls der Wert <0 ist,
sonst (None) wird keine Aktion ausgeführt (damit bleibt der Wert unverändert erhalten).
Damit werden on_change bzw. on_update Trigger nur ausgelöst, wenn der Wert vorher <0 war. Bei Erhalt des Wertes (None),
werden keine Trigger ausgelöst.


.. index:: Standard-Attribute; eval_trigger
.. index:: eval_trigger

Attribut *eval_trigger*
=======================

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

Im Attribut **eval_trigger** kann eine Liste mehrerer Items angegeben werden.
(Die Items müssen für das alte *.conf Format jeweils durch ein ‘\|’ voneinander getrennt werden.)
Der Ausdruck unter **eval** wird neu berechnet, wenn sich eines dieser Items verändert. Die Items können auch mit
einem Stern generalisiert werden. ``temperatur.\*`` bedeutet, dass alle Kinderitems des Temperatur-Items zum
Evaluieren des Items führen. Oder ``\*.trigger`` sorgt dafür, dass das Item durch alle Kind-Items mit dem
Namen “trigger” aktualisiert werden kann, also z.B. durch ``temperatur.trigger``, ``Licht.OG.trigger``, etc.

Seit SmartHomeNG v1.3 können für **eval_trigger** auch :doc:`Relative Item Referenzen </referenz/items/attributes_relative_referenzen>` genutzt werden. Dann müssen Bezüge auf andere Items nicht mehr absolut
angegeben werden sondern können sich relative auf andere Items beziehen.

.. note::

    Ein häufiger Fehler bei der Nutzung von **eval** im Zusammenspiel mit **eval_trigger** ist,
    bei **eval_trigger** auch den vollen Python-Pfad zu einem SmartHomeNG Item zu verwenden, wie
    im **eval** Ausdruck.

    Richtig ist es, bei **eval_trigger** nur den Item-Pfad zu nutzen (ohne führendes **sh.** und
    ohne folgende **()**).


    **Korrekt**:

    - eval: **sh.** my.item **()** oder sh.my.item.property.value
    - eval_trigger: my.item | my.other.item

    **Falsch**:

    - eval: sh.my.item
    - eval_trigger: **sh.** my.item | **sh.** my.other.item


Gemeinsame Verwendung von eval und on\_\.\.\. Item Attributen
-------------------------------------------------------------

Bei Verwendung des **eval** Attributes zusammen mit **on_change** oder **on_update** in der
selben Item Definition ist zu beachten, dass value unterschiedliche Werte hat/haben kann.

Im Ausdruck des **eval** Attributes hat value den alten Wert des Items. Nach Abschluss dieser
Berechnung, wird dem Item das Ergebnis zugewiesen. Anschließend werden die Ausdrücke für
**on_change** und **on_update** berechnet. Zu diesem Zeitpunkt hat das Item (und damit
**value**) bereits den neuen Wert.

Wenn in **eval** Ausdrücken in **on_change** oder **on_update** Attributen auf den alten Wert
des Items zugegriffen werden soll, muss dazu die Item Funktion **prev_value()** oder das
Item Property **property.last_value** genutzt werden.
Auf den alten Wert des aktuellen Items kann ohne die Angabe der vollständigen Item Pfades durch
den Ausdruck **sh..self.prev_value()** zugegriffen werden.


.. attention::

   Bei **eval** Ausdrücken (wie sie in den Item Attributen **eval**, **on_update** und **on_change**
   verwendet werden) ist zu beachten, dass bei Verwendung von **if** auch immer ein **else**
   Zweig angegeben werden muss!

   Wenn man jedoch ein Item nur verändern möchte wenn die **if** Bedingung erfüllt ist und sonst
   unverändert lassen möchte, muss als **else** Zweig der Ausdruck **else None** angegeben werden.
   **None** bewirkt, dass das Item unverändert bleibt, und somit auch keine Trigger ausgelöst werden.

   Diese Art, per ``None`` Werte nicht zuzuweisen, funktioniert **nur** bei ``eval``; bei anderen Attributen wie z.B. ``cycle`` kann dies nicht genutzt werden.


Abfrage des Auslösers eines **eval** Ausdrucks
----------------------------------------------

Zu dem Zeitpunkt, wo ein **eval** Ausdruck ausgeführt wird, bezieht sich das Property ``last_update_by`` **nicht** auf
die aktuellste Auslösung des Items, sondern auf das letzte Update davor. Möchte man nun aber abfragen, durch welches
Item, Plugin oder durch welche Logik die Ausführung des eval Ausdrucks angestoßen wurde,
muss das seit SmartHomeNG 1.9.1 implementierte Property ``last_trigger_by`` genutzt werden.

Dabei findet folgender zeitlicher Ablauf statt:

    - Aktualisieren des Itemwerts oder Veränderung eines Triggeritems (eval_trigger)
    - Setzen und Aktualisieren der ``last_trigger_by`` und dazu passenden Properties
    - Ausführen des eval Ausdrucks
    - Ist das Ergebnis des eval Ausdrucks **None**, passiert nichts weiter. Das Item wird nicht aktualisiert,
      ``last_update_by`` ändert sich ebenfalls nicht.
    - Ist das Ergebnis des eval Ausdrucks ein erlaubter Wert, wird dieser ins Item geschrieben.
      ``last_update_by`` und/oder ``last_change_by`` werden entsprechend aktualisiert.

Details zu den verschiedenen Abfragemöglichkeiten sind unter :doc:`Properties </referenz/items/properties>` zu finden.

.. attention::

   Möchte man in einem **eval** Ausdruck abfragen, wodurch der Ausdruck ausgelöst wurde, muss **property.last_trigger_by**
   genutzt werden. Das **property.last_update_by** wird erst danach (oder bei None gar nicht) aktualisiert.

.. tip::

  War die Auflösung eines **eval** Ausdrucks nicht erfolgreich (weil z.B. die Syntax falsch ist oder ein Item nicht
  gefunden werden konnte), wird beim ``last_trigger_by`` den Caller- und Source-Angaben noch ein None (als "dest") hinten
  angehängt. Der Wert beinhaltet somit ``<caller>:<source>:None``.
