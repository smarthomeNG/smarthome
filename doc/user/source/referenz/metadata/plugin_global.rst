
.. role:: redsup
.. role:: bluesup

.. index:: Plugin Metadaten
.. index:: Metadaten; Plugin
.. index:: Plugin Metadaten; Globale Metadaten

plugin
------

Der globale Metadaten Abschnitt ``plugin:`` kennt die folgenden Schlüsselbegriffe:

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
        documentation: https://github.com/smarthomeNG/...        # url of additional wiki page (in addition to user_doc.rst of plugin
    #    support: https://knx-user-forum.de/forum/supportforen/smarthome-py      # url of the support thread or forum

        version: 1.4.3
        sh_minversion: 1.7           # minimum shNG version to use this plugin (leave empty if no special requirement)
    #    sh_maxversion:              # maximum shNG version to use this plugin (leave empty if latest)
    #    py_minversion: 3.6          # minimum Python version needed for this plugin (leave empty if no special requirement)
    #    py_maxversion:              # maximum Python version to use this plugin (leave empty if no special requirement)
        multi_instance: true        # plugin supports multi instance (if not specified, False is assumed)

        configuration_needed: true  # False: The plugin will be enabled by the Admin GUI without configuration

        classname: <plugin_class>   # Name of the class that implements the plugin

Beschreibung der Schlüsselbegriffe im Abschnitt ``plugin:``

    - ``type:`` Beschreibt den Typ des Plugins (gültige Werte: ``gateway``, ``interface``, ``protocol``, ``system``, ``cloud`` oder *leer* für ein nicht klassifiziertes Plugin
    - ``description:`` Mehrsprachiger Text, der die Funktion das Plugins beschreibt. Die Beschreibung wird bei der
      Generierung des Dokumentations-Seiten des Plugins verwendet - Die Texte in den verschiedenen Sprachen werden
      als Unter-Einträge in der Form <Sprache>: <Text> erfasst. Zur Identifikation der Sprache werden die 2-stelligen
      Länder-Kürzel verwendet (``de``, ``en``, ``fr``, ``pl``, ...)

      ``de`` und ``en`` müssen angegeben werden. Weitere Sprachen sind optional.
    - ``maintainer:`` Hier kann angegeben werden, wer das Plugin pflegt und weiterentwickelt
    - ``tester:`` Optional können hier die Nutzer angegeben werden, die sich bereit erklärt haben das Plugin zu testen
    - ``state:`` Entwicklungs-Status des Plugins (gültige Werte: ``develop``, ``ready``, ``qa-passed``)
    - ``keywords:`` Liste der Schlüsselwörter die das Plugin beschreiben (durch Leerzeichen getrennt)
    - ``documentation:`` url die auf eine weiterführende Dokumentation verweist (damit sind nicht die Dateien user_doc.rst, developer_doc.rst oder die veraltete README.md gemeint)
    - ``support:`` url die auf einen Support Thread oder ein Support Forum verweist

    - ``version:`` VersionsNumber des Plugins. Sie wird beim Laden mit der Versionsnummer die im Code definierert ist verglichen.
    - ``sh_minversion:`` Minimale SmartHomeNG Version mit der das Plugin kmpatibel ist. Falls `sh_minversion`` leer ist, nimmt SmartHomeNG an, dass das Plugin mit jeder älteren Version von SmartHomeNG kompatibel ist.
    - ``sh_maxversion:`` Maximale SmartHomeNG Version mit der das Plugin kmpatibel ist. Falls `sh_maxversion`` leer ist, nimmt SmartHomeNG an, dass das Plugin mit jeder neueren Version von SmartHomeNG kompatibel ist.
    - ``py_minversion:`` Minimale Python Version mit der das Plugin kmpatibel ist. Falls `py_minversion`` leer ist, nimmt SmartHomeNG an, dass das Plugin mit jeder älteren Python Version komatibel ist die von SmartHomeNG unterstützt wird.
    - ``py_maxversion:`` Maximale Python Version mit der das Plugin kmpatibel ist. Falls `py_maxversion`` leer ist, nimmt SmartHomeNG an, dass das Plugin mit jeder neueren Python Version komatibel ist die von SmartHomeNG unterstützt wird.
    - ``multi_instance:`` Ist das Plugin in der Lage in mehreren Instanzen gestartet zu werden? (``True``, ``False``)
    - ``configuration_needed:`` Normalerweise wird in der Admin GUI ein Plugin im Status disabled hinzugefügt und muss erst konfiguriert werden.
      Wenn dieser Parameter auf ``False`` gesetzt wird, wird das Plugin im Status ``enabled`` hinzugefügt. Das ist sinnvoll bei Plugins, die
      ohne Konfiguration lauffähig sind. (``True``, ``False``)
    - ``restartable:`` Is the Plugin Restart bzw. Reload fählg?  (gültige Werte: ``True``, ``False``, ``unknown``)
    - ``classname:`` Name der Python Klasse die das Plugin implementiert un die zum Start des Plugins initialisiert wird

    - ``classpath:`` **Wird normalerweise nicht angegeben** - Nur angeben, wenn das Plugin außerhalb des ``../plugins`` Verzeichnisses gespeichert ist,

