:tocdepth: 7

###########
SmartHomeNG
###########

Developer documentation
=======================

SmartHomeNG [#f1]_ is a software that serves a basis for home automation.
It interconnects multiple devices using plugins to access their specific interfaces.

This documentation reflects the current Release |release|.

What can be done?
The door bell switch triggers a sensor that signals is changed state to SmartHomeNG. In turn
the TV set is muted and lights are switched on in the hallway. Or being absent an email is sent
to the home owner to announce a visitor and a picture or the door camera is attached to it.

The main documentation here within the code and all READMEs are kept in English.
`The SmarthomeNG Wiki <https://github.com/smarthomeNG/smarthome/wiki>`_ however mainly contains German documents.

If you are a user with a special problem where you will need a document of this wiki in English
please contact the `support forum at KNX-User-Forum <https://knx-user-forum.de/forum/supportforen/smarthome-py>`_
or the `chat on gitter.im <https://gitter.im/smarthomeNG/smarthome>`_ . Feel free to contribute in
any way you want and can.

.. note::

   Place **remarks** und **wishes for changes** regarding this developer documentation on
   `this feedback page <https://www.smarthomeng.de/feedback-zur-dokumentation>`_ .

.. [#f1] SmartHomeNG © Copyright 2016-2018 SmartHomeNG Team, is based on smarthome.py © 2011-2014 Marcus Popp.


.. toctree::
   :maxdepth: 6
   :hidden:
   :titlesonly:

   User Documentation (German) <https://www.smarthomeng.de/user>
   requirements.rst
   install
   build_doc


.. toctree::
   :maxdepth: 6
   :hidden:

   config
   items
   logics
   plugins_all


.. toctree::
   :maxdepth: 6
   :hidden:
   :titlesonly:

   logging
   tools
   development
   release/release
   genindex
   impressum
