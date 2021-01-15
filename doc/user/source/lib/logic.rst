Logics-API
==========

There are two ways to access the API

1. Directly

   Use it the following way to access the api, if you have no access to the sh object in your method or function:

   .. code-block:: python

       # to get access to the object instance:
       from lib.logic import Logics
       logics = Logics.get_instance()

       # to access a method (eg. enable_logic()):
       logics.enable_logic(name)


2. Through the main SmartHome object

   If you have access to the sh object in your method or function, you can use the following way:

   .. code-block:: python

       # to access a method (eg. enable_logic()):
       sh.logics.enable_logic(name)


The API is implemented through the following library:


lib.logic
---------

.. automodule:: lib.logic
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

