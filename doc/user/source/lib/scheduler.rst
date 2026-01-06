Scheduler-API
=============

There are two ways to access the API

1. Directly

   Use it the following way to access the api, if you have no access to the sh object in your method or function:

   .. code-block:: python

       # to get access to the object instance:
       from lib.scheduler import Scheduler
       scheduler = Scheduler.get_instance()

       # to access a method (eg. to trigger a logic):
       scheduler.trigger(...)

2. Through the main SmartHome object

   If you have access to the sh object in your method or function, you can use the following way:

   .. code-block:: python

       # to access a method (eg. to trigger a logic):
       sh.scheduler.trigger(...)


The API is implemented through the following library:


lib.scheduler
-------------

.. automodule:: lib.scheduler
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

