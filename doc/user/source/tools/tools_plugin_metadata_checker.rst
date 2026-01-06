.. index:: Metadata Checker
.. index:: Plugin Metadata; plugin_metadata_checker
.. index:: Tools; Metadata Checker

plugin_metadata_checker.py
==========================

Dieses Tool erlaubt es Plugin Autoren die Metadaten Definition ihrer Plugins auf Vollständigkeit und in Teilen
auf inhaltliche Richtigkeit zu überprüfen. Das Tool hat eine ganze Reihe von möglichen Optionen:

.. code::

   smarthome$ python3 tools/plugin_metadata_checker.py

   plugin_metadata_checker.py v1.7.6 - Checks the care status of plugin metadata

   usage: plugin_metadata_checker.py
                                     [-la | -lcl | -lsm | -lst | -li | -lc | -lip | -lia | -d DISP_PLUGIN | -dd DISPD_PLUGIN | -c CHECK_PLUGIN | -cl | -clc | -cli | -v]

   optional arguments:
     -la, --list_all       list plugin information of all plugins
     -lcl, --list_classic  list plugin information of classic plugins
     -lsm, --list_smart    list plugin information of smart plugins
     -lst, --list_state    list plugin information grouped by plugin state
     -li, --list_inc       list information of plugins with incomplete metadata
     -lc, --list_compl     list information of plugins with complete metadata
     -lip                  list info of plugins with incomplete parameter data
     -lia                  list info of plugins with incomplete item attribute
                           data
     -d DISP_PLUGIN        display the metadata of a plugin
     -dd DISPD_PLUGIN      display the metadata of a plugin with description
     -c CHECK_PLUGIN       check the metadata of a plugin
     -cl, --check_list     check the metadata of all plugins
     -clc, --check_clist   check the metadata of plugins with all metadata
                           sections
     -cli, --check_ilist   check the metadata of all plugins, list only
                           incomplete plugins
     -v, --list_versions   list versions instead od metadata checks

   smarthome$


Um ein einzelnes Plugin zu prüfen, muss das Tool mit der Option -c und dem Plugin Namen aufgerufen werden. Im
Idealfall sieht das Ergebnis aus wie im folgenden Beispiel beim knx Plugin:

.. code::

   smarthome$ python3 tools/plugin_metadata_checker.py -c knx

   plugin_metadata_checker.py v1.7.6 - Checks the care status of plugin metadata

   Check metadata of smart plugin 'knx'

   Metadata is complete (0 errors, 0 warnings and 0 hints)

   smarthome$


Falls Hinweise, Warnungen oder Fehler existieren, werden diese mit einer weitergehenden Beschreibung aufgelistet
und das Ergebnis sieht ähnlich aus wie beim folgenden Beispiel beim smartvisu Plugin:

.. code::

   smarthome$ python3 tools/plugin_metadata_checker.py -c smartvisu

   plugin_metadata_checker.py v1.7.6 - Checks the care status of plugin metadata

   Check metadata of smart plugin 'smartvisu'

   ERROR:   An invalid development state is given for the plugin

            Set'state:' to one of the followind valid values ['develop', 'rea
            dy', 'qa-passed']

            The state'qa-passed' should only be set by the shNG core team

   1 errors, 0 warnings and 0 hints

   smarthome$


