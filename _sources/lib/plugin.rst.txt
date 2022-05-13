Plugins-API
===========

There are two ways to access the API

1. Directly

   Use it the following way to access the api, if you have no access to the sh object in your method or function:

   .. code-block:: python

       # to get access to the object instance:
       from lib.plugin import Plugins
       plugins = plugins.get_instance()

       # to access a method (eg. return_plugins()):
       plugins.return_plugins()

   This is the preferred method.


2. Through the main SmartHome object

   If you have access to the sh object in your method or function, you can use the following way:

   .. code-block:: python

       # to access a method (eg. return_plugins()):
       sh.plugins.return_plugins()


The API is implemented through the following module:


lib.plugin
----------

.. automodule:: lib.plugin
    :no-members:
    :noindex:


.. module:: lib.plugin

The API consists of two classes.


.. toctree::
   :maxdepth: 6
   :hidden:

   plugin_class_pluginwrapper
   plugin_class_plugins


class PluginWrapper
^^^^^^^^^^^^^^^^^^^

This class implements the Plugin itself:

.. autoclass:: PluginWrapper
   :no-members:
   :noindex:

:doc:`class PluginWrapper </lib/plugin_class_pluginwrapper>`


class Plugins
^^^^^^^^^^^^^

This class implements the loading and management of the plugins.

.. autoclass:: Plugins
   :no-members:
   :noindex:

:doc:`class Plugins </lib/plugin_class_plugins>`

