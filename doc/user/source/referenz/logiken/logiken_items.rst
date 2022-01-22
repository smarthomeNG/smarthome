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
   entsprechend beschädigter Items zu prüfen und diese wiederherzustellen. Alternativ werden die Items nach
   einem Neustart von SmartHomeNG neu erstellt.


Alternativ kann auch über die Item-Properties auf den Wert zugegriffen werden: **sh.path.item.propery.value**
gibt den Wert zurück, mit **sh.path.item.property.value = Wert** kann der Wert zugewiesen werden. Diese Variante
lässt sich wie eine normale Variablenzuweisung nutzen.

Beispiel
========

Eine Logik sieht prinzipiell folgendermaßen aus:

.. code-block:: python
   :caption: /usr/local/smarthome/logics/testlogik1.py

   #!/usr/bin/env python3
   # testlogik1.py

   #Code der Logik:

   # Das Deckenlicht im Büro einschalten, falls es nicht eingeschaltet ist
   if not sh.buero.deckenlicht():
       sh.buero.deckenlicht('on')



weiteres
========

Methoden zum Zugriff auf Items
------------------------------

Die Nutzung des ``sh`` Objektes für Items wird nicht weitergeführt. Es ist besser das Item API wie folgt zu nutzen:

.. code:: python

   from lib.item import Items
   items = Items.get_instance()

Mit dem ``items`` Objekt können nun die folgenden Funktionen verwendet werden:


items.return_item(path)
~~~~~~~~~~~~~~~~~~~~~~~

Liefert ein Item Objekt für den angegebenen Pfad zurück. Beispiel:

``items.return_item('first_floor.bath')``

items.return_items()
~~~~~~~~~~~~~~~~~~~~

Liefert alle Item Objekte zurück

.. code-block:: python

   for item in items.return_items():
      logger.info(item.id())

items.match_items(regex)
~~~~~~~~~~~~~~~~~~~~~~~~

Liefert alle Item Objekte deren Pfad mit einem regulären Ausdruck gefunden wird und die optional ein bestimmtes Attribut aufweisen.

.. code-block:: python

   for item in items.match_items('*.lights'):     # selects all items ending with 'lights'
       logger.info(item.id())

   for item in items.match_items('*.lights:special'):     # selects all items ending with 'lights' and attribute 'special'
       logger.info(item.id())

items.find_items(configattribute)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Abhängig von ``configattribute`` werden die folgenden Items zurückgegeben:

.. table::

   ======================  =========================================================
   Attribut                Ergebnis
   ======================  =========================================================
   ``attribute``           Nur Items bei denen keine Instanz ID angegeben ist
   ``attribute@``          Items mit oder ohne Instanz ID
   ``attribute@instance``  Items mit einem bestimmten Attribut und einer Instanz ID
   ``@instance``           Items mit einer bestimmten Instanz ID
   ======================  =========================================================


.. code:: python

   for item in items.find_items('my_special_attribute'):
       logger.info(item.id())

find\_children(parentitem, configattribute):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Liefert alle Kind Item Objekte eines Elternitems mit einem gegebenen ``configattribute``.
Die Suche nach dem ``configattribute`` wird genauso durchgeführt wie in ``find_items(configattribute)`` weiter oben.

...

- Methoden
- Item Werte und Attribute

