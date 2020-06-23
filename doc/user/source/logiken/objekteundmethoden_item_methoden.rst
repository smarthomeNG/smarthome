
.. role:: bluesup
.. role:: redsup

=============
Item Methoden
=============

Die grundsätzlichen Methoden, die jedes Item hat, sind unter **Items** beschrieben. Darüber
hinaus stehen die nachfolgend beschrieben Methoden zum Handling von Items zur Verfügung.

Die Nutzung des SmartHomeNG Objektes ``sh`` ist dabei als veraltet anzusehen. Die richtige
Methode ist die Nutzung des Item API. Das ``items`` Objekt kann wie folgt
genutzt werden:

.. code:: python

   from lib.item import Items
   items = Items.get_instance()

Nun können folgende Funktionen aufgerufen werden:

return_item(path)
=================

Liefert das Item Objekt für den angegebenen Pfad zurück.

.. code:: python

   items.return_item('erdgeschoss.flur')


return_items()
==============

Liefert sämtliche definierten Item Objekte zurück.

.. code:: python

   for item in items.return_items():
       logger.info(item.id())


match_items(regex)
==================

Liefert alle Items zurück, die der Regular Expression, dem Pfad und dem optionalen Attribut entsprechen.

.. code:: python

   for item in items.match_items('*.licht'):
       # Selektiere alle Items, deren Pfad mit 'licht' endet
       logger.info(item.id())

   for item in items.match_items('*.licht:special'):
       # Selektiere alle Items, deren Pfad mit 'licht' endet und die das Attribut 'special' haben
       logger.info(item.id())


find_items(configattribute)
===========================

In Abhängigkeit von ``configattribute`` werden wie folgt Items zurückgeliefert:

.. table::

   ====================  =========================================
   Attribut              Ergebnis
   ====================  =========================================
   ``Attribut``          Nur Items ohne Angabe von Instanz Kennung
   ``Attribut@``         Items mit und ohne Instanz Kennung
   ``Attribut@Instanz``  Items mit exakter Übereinstimmung von Attribut und Instanz Kennung
   ``@Instanz``          Items die mit dieser Instanz Kennung definiert worden sind
   ====================  =========================================


.. code:: python

   for item in items.find_items('my_special_attribute'):
       logger.info(item.id())


find_children(parentitem, configattribute)
==========================================

Diese Funktion liefert ausgehend vom Item ``parentitem`` alle Items mit passendem
``configattribute``. Dabei wird die Suche nach dem Attribut exakt so ausgeführt wie
in der Funktion ``find_items(configattribute)`` zuvor beschrieben.


