Section `plugin:`
-----------------

The global metadata section ``plugin:`` has the following keys:

.. code:: yaml

    # Metadata for the Smart-plugin
    plugin:
        # Global plugin attributes
        type: web                   # plugin type (gateway, interface, protocol, system, cloud, un-classified)
        description:
            de: 'Plugin für ...'
            en: 'Plugin for ...'
        maintainer: msinn           # Optional: Who maintains this plugin?
    #   tester:                     # Optional: Who tests this plugin?
        state: qa-passed
        keywords: weather           # keywords, where applicable
        documentation: https://github.com/smarthomeNG/...        # url of additional wiki page (in addition to README.md of plugin
    #    support: https://knx-user-forum.de/forum/supportforen/smarthome-py      # url of the support thread or forum

        version: 1.4.3
        sh_minversion: 1.3a
    #    sh_maxversion:              # maximum shNG version to use this plugin (leave empty if latest)
        multi_instance: true        # plugin supports multi instance (if not specified, False is assumed)

        class_name: <plugin_class>   # Name of the class that implements the plugin

Description of the keys in the section ``plugin:``

    - **type:** The plugin type (classification: gateway, interface, protocol, system, cloud, or *empty* for un-classified
    - **description:** Multi language Text describing what the plugin does. It is used for generating the plugin pages within this documentation - The texts in the different languages are specified in sub-entries in the form <language>: <text>. Use the standard two letter codes for specifying the language (de, en, fr, pl, ..)
    - **maintainer:** Who maintains the plugin?
    - **tester:** Optional: List of testers of the plugin
    - **state:** State of the plugin development (valid entries are: **develop**, ** **ready**, **qa-passed**)
    - **keywords:** List of keywords (space separated)
    - **documentation:** url pointing to additional information/documentation (besides the README.md file)
    - **support:** url pointing to a support thread or forum

    - **version:** Version number of the plugin. It is checked against the version number defined in the Python source code
    - **sh_minversion:** Minimum SmartHomeNG version this plugin is compatible with. If *sh_minversion* is left empty, SmartHomeNG assumes that the plugin is compatible with every version of SmartHomeNG [Test not yet implemented]
    - **sh_maxversion:** Maximum SmartHomeNG version this plugin is compatible with (or empty, if compatible with the actual version of SmartHomeNG) [Test not yet implemented]
    - **multi_instance:** Is the plugin multi-instance capable?
    - **restartable:** Is the plugin restartable?  (valid entries are: **True**, ** **False**, **unknown**)
    - **class_name:** Name of the Python class to initialize (the class that implements the plugin)

    - **classpath:** **Usually not specified.** Only needed, if the plugin resides outside the ``/plugins`` folder

