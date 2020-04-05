.. index:: New; Web Interface

.. role:: redsup
.. role:: bluesup


Web Interface :bluesup:`update`
===============================

This documentation is valid vor SmartHomeNG versions beyond v1.4.2. It does not work on v1.4.2
and below. Web interfaces are implemented trough the http module. The http module has to be configured and must be
running for the web interfaces to work.

A web interface of a plugin allows to implement the diepaly of plugins data or even the configuration of a plugin
through a browser. To reach the web interface from the admin interface, a button is displayed in the list of plugins.

SmartHomeNG allows to implement a web interface in a very simple fashion. The sample plugin has a full implementation
of a webinterface, to which only the data display ha to be added to a template file. The template engine (Jinja2)
includes the data from Python when rendering the html page from the template.

The standard template for web interfaces has head part with the following information:

  - an icon
  - the name, version and state of the plugin
  - a block on the right top which kan be used to display global information (parameters, ....) of the plugin
  - an area for buttons (below the block with global information)

Following the head part, the rest of the display area is structured by up to 4 tabs, depending on the information
to be displayed.


An empty webinterface looks like this:

.. image:: assets/sample_plugin_webIf.jpg



Detailed description for creating webinterfaces can be found on the following pages:

.. toctree::
   :maxdepth: 1
   :titlesonly:

   webinterface_extend_plugin
   webinterface_filling_webinterface
   webinterface_multilanguage
   webinterface_automatic_update
   webinterface_3rdparty_components

