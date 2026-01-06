:tocdepth: 5

.. index:: Zugriff auf Items; Logiken
.. index:: Logiken; Zugriff auf Items


=================
Zugriff auf Items
=================

.. index:: Item Wert; Logiken
.. index:: Logiken; Item Wert

Zugriff auf den Wert eines Items
================================

Um Zugriff auf Items zu erhalten, müssen Sie über die zentrale Instanz **sh** des Smarthome Objektes angesprochen
werden. Um zum Beispiel den Wert des  Items **path.item** zu erhalten, muss der Aufruf **sh.path.item()** lauten.
Der Wert wird über eine Methode des Items aufgerufen, weshalb der Name des Item Objektes um **()** ergänzt werden
muss. Um dem Item einen neuen Wert zuzuweisen, wird dieser einfach als Argument angegeben: **sh.path.item(neuer_wert)**.

.. attention::

   Zuweisung von Item-Werten:

   Es ist sehr wichtig, immer mit Klammern **()** auf die Items zuzugreifen! Wenn (fehlerhafter weise) das Item direkt
   zugewiesen wird, z.B. mit **sh.path.item = Wert**, dann wird das item-Objekt in SmartHomeNG überschrieben.
   Anschließend ist **sh.path.item** eine normale Variable und kein Item Objekt mehr.

   In diesem Fall kann die mitgelieferte Logik **check_items.py** verwendet werden, um auf Vorhandensein
   entsprechend beschädigter Items zu prüfen und diese wiederherzustellen. Alternativ werden die Items durch
   einen Neustart von SmartHomeNG neu erstellt.


Alternativ kann auch über die Item-Properties auf den Wert zugegriffen werden: **sh.path.item.propery.value**
gibt den Wert zurück, mit **sh.path.item.property.value = Wert** kann der Wert zugewiesen werden. Diese Variante
lässt sich wie eine normale Variablenzuweisung nutzen.

Beispiel
--------

Eine Logik sieht prinzipiell folgendermaßen aus:

.. code-block:: python
   :caption: /usr/local/smarthome/logics/testlogik1.py

   #!/usr/bin/env python3
   # testlogik1.py

   #Code der Logik:

   # Das Deckenlicht im Büro einschalten, falls es nicht eingeschaltet ist
   if not sh.buero.deckenlicht():
       sh.buero.deckenlicht('on')



.. include:: /referenz/items/properties.rst

.. include:: /referenz/items/methoden.rst

