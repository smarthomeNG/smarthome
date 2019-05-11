Items-API
=========

There are two ways to access the API

1. Directly

   Use it the following way to access the api, if you have no access to the sh object in your
   method or function:

   .. code-block:: python

       # to get access to the object instance:
       from lib.item import Items
       items = Items.get_instance()

       # to access a method (eg. to get the list of Items):
       items.return_items()

   This is the preferred method.


2. Through the main SmartHome object

   If you have access to the sh object in your method or function, you can use the following way:

   .. code-block:: python

       # to access a method (eg. to get the list of Items):
       sh.items.return_items()


The API is implemented through the following module:


lib.item
--------

.. automodule:: lib.item
    :no-members:


.. module:: lib.item

The API consists of two classes.


class Item
^^^^^^^^^^

This class implements the item itself:

.. autoclass:: Item
   :no-members:

:doc:`class Item </lib/item_class_item>`


class Items
^^^^^^^^^^^

This class implements the loading and management of the items in form of the item-tree.

.. autoclass:: Items
   :no-members:

:doc:`class Items </lib/item_class_items>`

