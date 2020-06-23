Plugin documentation files
==========================

There are three documentation files that can (and should) be created for a plugin.


README.md
---------

The classic documentation file in markdown format, containing basic information how a plugin
can be configured and used.


user_doc.rst / user_doc.md
--------------------------

The **user_doc** file can be created in restructured text (rST) or markdown format. You should
prefer the restructured text format because it is more feature rich. The user documentation should
be written in **German**. Only it the plugin author does not speak German, the user documentation
can be written in English. The reason for this is, that the user documentation is going to become
multilingual at a later point in time and the translation source has to be **one** language.

This file is dynamically integrated in the user documentation for SmartHomeNG when it is beeing built.

.. important::

   The first Heading of the **user_doc.rst** / **user_doc.md** or **developer_doc.rst** / **developer_doc.md**
   MUST be the short-name of the plugin in lower case.

   It is used as the entry in the navigation bar of the documentation. Choosing an other top level
   header for these files would make the documentations navigation inconsistent.


For example:

The **backend** plugin has a file **user_doc.rst**. This file is integrated in the navigation
tree of the user documentation. The entry can be seen, if the corresponding plugin category is selected:

.. image:: assets/backend_user_doc_tree.png


When selecting the entry in the navigation pane, the page is displayed:

.. image:: assets/backend_user_doc_page.png


This page can contain images. The images should be stored in a folder named **assets** within
the plugin folder.

In restructured text (rST) files, the images can then be included by the statement:

  .. code::

    .. image:: assets/<picture-filename>



developer_doc.rst / developer_doc.md
------------------------------------

The **developer_doc** file can be created in restructured text (rST) or markdown format. You
should prefer the restructured text format because it is more feature rich. The user documentation
should be written in **English**.

This file is dynamically integrated in the developer documentation for SmartHomeNG when it is beeing built.

For example:

The **visu_websocket** and the **visu_smartvisu** plugins have pages for the developer documentation:

.. image:: assets/visu_developer_doc_tree.jpg

