Programm Module
===============

Abgesehen vom Hauptprogramm das in ``bin/smarthome.py`` liegt, nutzt SmartHomeNG noch unterstützende Programm Module
die sich im Verzeichnis ``lib/`` befinden. Sollte ein Programm Modul Bibliotheken nutzen, die nicht mit der Standard
Installation von Python mitgeliefert werden, so müssen diese in ``lib/requirements.txt`` eingetragen werden.

Im folgenden eine Beschreibung der Programm Module von SmartHomeNG:


.. toctree::
   :maxdepth: 2
   :titlesonly:

   /lib/config
   /lib/constants
   /lib/daemon
   /lib/item_conversion
   /lib/log
   /lib/metadata
   /lib/module
   /lib/scene
   /lib/shyaml
   /lib/translation


Die folgenden Programm Module können ebenfalls für die Plugin Entwicklung verwendet und referenziert werden:


.. toctree::
   :maxdepth: 5
   :titlesonly:

   /lib/connection
   /lib/db
   /lib/logutils
   /lib/network
   /lib/orb
   /lib/tools
   /lib/utils
