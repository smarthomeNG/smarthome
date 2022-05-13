
.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup

Methoden zum Zugriff auf Items
==============================

Die im folgenden beschriebenen Methoden waren ursprünglich Teil des smarthome Objektes ``sh``.
Die Nutzung des ``sh`` Objektes für Items wird nicht weitergeführt. Es ist besser das Item API wie folgt zu nutzen:

.. code:: python

   from lib.item import Items
   items = Items.get_instance()

.. note::

   Bei Ausführung einer Logik ist das ``items`` Objekt bereits initialisiert und kann ohne die oben beschriebene
   Initialisierung dirket genutzt werden.


Mit dem ``items`` Objekt können nun die folgenden Funktionen verwendet werden:


return_item(path)
-----------------

Liefert ein Item Objekt für den angegebenen Pfad zurück. Beispiel:

.. code-block:: python

   logger.info(items.return_item('first_floor.bath'))


return_items()
--------------

Liefert alle Item Objekte zurück

.. code-block:: python

   for item in items.return_items():
      logger.info(item.id())


match_items(regex)
------------------

Liefert alle Item Objekte deren Pfad mit einem regulären Ausdruck gefunden wird und die optional ein bestimmtes Attribut aufweisen.

.. code-block:: python

   for item in items.match_items('*.lights'):     # selects all items ending with 'lights'
       logger.info(item.id())

   for item in items.match_items('*.lights:special'):     # selects all items ending with 'lights' and attribute 'special'
       logger.info(item.id())


find_items(configattribute)
---------------------------

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


find_children(parentitem, configattribute)
------------------------------------------

Liefert alle Kind Item Objekte eines Elternitems mit einem gegebenen ``configattribute``.
Die Suche nach dem ``configattribute`` wird genauso durchgeführt wie in ``find_items(configattribute)`` weiter oben.

.. code:: python

   for item in items.find_children('my_special_attribute'):
       logger.info(item.id())
