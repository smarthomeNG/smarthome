
.. index:: Standard-Attribute; hysteresis_input
.. index:: hysteresis_input
.. index:: Standard-Attribute; hysteresis_upper_threshold
.. index:: hysteresis_upper_threshold
.. index:: Standard-Attribute; hysteresis_lower_threshold
.. index:: hysteresis_lower_threshold


.. index:: Items; Hysterese
.. index:: Hysterese

=========
Hysterese
=========

Mit Hilfe der drei folgenden Attribute kann eine Hysterese konfiguriert werden.

|

`hysteresis_input`
==================

.. index:: Standard-Attribute; hysteresis_input
.. index:: hysteresis_input

Das Attribut **hysteresis_input** legt das Item fest, welches überwacht werden soll. Angegeben wird der Pfad eines
Items, welches als Eingabe Wert für die Hysterese dient. Der Wert dieses Items wird gegen die beiden Schwellwerte
verglichen. Das hier angegebene Item muss als **num** definiert sein.

Die Pfad Angabe kann als absoluter oder als relativer Itempfad erfolgen. Das Item, welches dieses Hysterese Attribut
verwendet, muss als **bool** definiert sein.

Oberhalb des oberen Schwellwertes
---------------------------------

Wenn der Wert des hysteresis_input-Items den oberen Schwellwert überschreitet, wird das Hysterese Item auf **True**
gesetzt. Das bedeutet, dass das Item bei Überschreitung von False auf True wechselt. Wenn das hysteresis_input-Item
anschließend weitere Werte oberhalb des oberen Schwellwertes annimmt, wird findet ein Update des Wertes True statt.

zwischen den Schwellwerten
--------------------------

Wenn das des hysteresis_input-Item einen Wert zwischen den beiden Schwellwerten annimmt,

    also: unterer Schwellwert <= Itemwert <= oberer Schwellwert

findet beim Hysterese Item keine Änderung statt. Der Wert erhält also kein Update.

Unterhalb des unteren Schwellwertes
-----------------------------------

Wenn der Wert des hysteresis_input-Items den untern Schwellwert unterschreitet, wird das Hysterese Item auf **False**
gesetzt. Das bedeutet, dass das Item bei Unterschreitung von Ture auf False wechselt. Wenn das hysteresis_input-Item
anschließend weitere Werte unterhalb des unteren Schwellwertes annimmt, wird findet ein Update des Wertes False statt.

|

`hysteresis_upper_threshold`
============================

.. index:: Standard-Attribute; hysteresis_upper_threshold
.. index:: hysteresis_upper_threshold

Das Attribut **hysteresis_upper_threshold** definiert den oberen Schwellwert für die Hysterese. Bei der
**Überschreitung** dieses Wertes im Item welches den zu überwachenden Eingabewert darstellt, wird dieses Item auf
**True** gesetzt.

Optional kann in diesem Attribut eine Dauer angegeben werden, welche die Überscheitung andauern muss, damit der Wert
des Items auf **True** gesetzt wird.

Das Item, welches dieses Hysterese Attribut verwendet, muss als **bool** definiert sein.

|

`hysteresis_lower_threshold`
============================

.. index:: Standard-Attribute; hysteresis_lower_threshold
.. index:: hysteresis_lower_threshold

Das Attribut **hysteresis_lower_threshold** definiert den unteren Schwellwert für die Hysterese. Bei der
**Unterschreitung** dieses Wertes im Item welches den zu überwachenden Eingabewert darstellt, wird dieses Item auf
**False** gesetzt.

Optional kann in diesem Attribut eine Dauer angegeben werden, welche die Unterscheitung andauern muss, damit der Wert
des Items auf **False** gesetzt wird.

Das Item, welches dieses Hysterese Attribut verwendet, muss als **bool** definiert sein.

|

Konfiguration
=============

.. code-block:: yaml

    hysterese_input:
        type: num
        name: 'z.B. Helligkeit'
        ...

    hysterese_item:
        type: bool
        name: 'z.B. Beschattung an/aus'
        hysteresis_input: ..hysterese_input
        hysteresis_upper_threshold: <oberer Schwellwert> % <Mindestdauer in Sekunden>
        hysteresis_lower_threshold: <unterer Schwellwert> % <Mindestdauer in Sekunden>

Der obere Schwellwert und der untere Schwellwert können als Integer oder Float Werte angegeben werden.
Die Angabe der Mindestdauer zu den Schwellwerten ist optional. Die Mindestdauer kann als Integer oder Float Wert
angegeben werden.

|

Beispiele
=========

Das folgende Beispiel zeigt ein Item als Hysterese Glied mit oberem und unterem Schwellwert und Werten für die
jeweiligen Mindestdauern für das Zeitglied.

.. code-block:: yaml

    helligkeit:
        type: num
        ...

    beschattung:
        type: bool
        hysteresis_input: ..helligkeit
        hysteresis_upper_threshold: 5000 % 60
        hysteresis_lower_threshold: 900.5 % 120


Das folgende Beispiel zeigt ein Item als Hysterese Glied mit oberem und unterem Schwellwert, jedoch ohne konfigurierte
Zeitglieder. Der TV-Status wechselt bei überschreiten eines Verbrauchs von 90 Watt auf True (eingeschaltet) und
wechselt bei unterschreiten eines Verbrauchs von 10 Watt auf False (ausgeschaltet):

.. code-block:: yaml

   tv_verbrauch:
       type: num
       ...

   tv_status:
       type: bool
       hysteresis_input: ..tv_verbrauch
       hysteresis_upper_threshold: 90
       hysteresis_lower_threshold: 10
