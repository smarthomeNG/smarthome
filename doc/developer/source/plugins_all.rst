Plugins
=======

There are a lot of plugins to extend the functionality of SmartHomeNG. The information on these
pages are gathered from the metadata file of the plugins. The entries in the navigation pane
link to the README of the corresponding plugin.


The plugins are subclassed to the following categories:

.. toctree::
   :maxdepth: 1
   :glob:
   :titlesonly:

   /plugins_doc/plugins_system
   /plugins_doc/plugins_gateway
   /plugins_doc/plugins_interface
   /plugins_doc/plugins_protocol
   /plugins_doc/plugins_web
   /plugins_doc/plugins_unclassified
   modules
   
   
If a plugin author wants the information in this documentation to be updated, he just
needs to update the ``plugin.yaml`` metadata file in his plugin. On the next build of this
documentation, the updated information is going to be picked up.

