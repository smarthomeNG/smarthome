
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

Wenn das des hysteresis_input-Item einen Wert zwischen den beiden Schwellwerten annimmt
(also: unterer Schwellwert <= Itemwert <= oberer Schwellwert), findet beim Hysterese Item keine Änderung statt.
Der Wert erhält also kein Update.

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

Beispiele
=========

Das folgende Beispiel zeigt ein Item als Hysterese Glied mit oberem und unterem Schwellwert.

.. code-block:: yaml

   hysterese_item:
       type: bool
       hysteresis_input: ..hysterese_input
       hysteresis_upper_threshold: 6
       hysteresis_lower_threshold: 2.5

   hysterese_input:
       type: num
       ...


Das folgende Beispiel zeigt ein Item als Hysterese Glied mit oberem und unterem Schwellwert. Der obere Schwellwert
ist hier um ein Zeitglied ergänzt, so dass das Item erst **True** wird, wenn der obere Schwellwert für 30 Sekungen
überschritten wurde.

.. code-block:: yaml

   hysterese_item:
       type: bool
       hysteresis_input: ..hysterese_input
       hysteresis_upper_threshold: 6 % 30
       hysteresis_lower_threshold: 2.5

   hysterese_input:
       type: num
       ...

