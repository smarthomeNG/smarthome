
.. index:: Plugin Checker
.. index:: check_plugin.py

.. role:: redsup
.. role:: bluesup

============================
Plugin-Checker :redsup:`neu`
============================

Mit der SmartHomeNG Version 1.9.4 ist ein Tool hinzugekommen, welches Entwickler von Plugins unterstützt. Der
Plugin-Checker führt eine Reihe von formalen Prüfungen durch und gibt Hinweise, wie Fehler und Warnungen beseitigt
werden können.

Das Tool prüft beim Aufruf für ein Plugin:

- die Metadaten (nahezu vollständig)
- den Code des Plugins (bisher nur eine rudimentäre Prüfung)
- die Dokumentation user_doc.rst (bisher nur eine rudimentäre Prüfung)

Der Plugin-Checker liegt im ``tools`` Verzeichnis von SmartHomeNG und wird folgendermaßen aufgerufen:

.. code-block:: bash

    $ tools/check_plugin.py <Optionen> <Pluginname>

Der Name das Plugins entspricht dem Namen der Verzeichnisses in dem das Plugin liegt. Standardmäßig werden Metadaten,
Code und Dokumentation geprüft. Falls nur eine Teil-Prüfung durchgeführt werden soll, kann die Prüfung durch die
Angabe einer Option eingeschränkt werden.

.. code-block:: bash

    $ tools/check_plugin.py

    check_plugin.py v0.6.3 - Check plugin for formal errors or improvement potential

    usage: check_plugin.py [-all] [-m | -d | -c | -cd] [pluginname]

    positional arguments:
      pluginname  name of the plugin to check

    optional arguments:
      -all        check all plugins
      -m          check only the metadata of a plugin
      -d          check only the documentation of a plugin
      -c          check only the code of a plugin
      -cd         check only the code and documentation of a plugin

.. note::

    Der Umfang der Prüfungen wird successive von Release zu Release ausgebaut.

