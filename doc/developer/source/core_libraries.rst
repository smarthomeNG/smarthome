Libraries
=========

Neben dem Haupt-Programm welches in ``bin/smarthome.py`` gespeichert ist, gibt es eine Reihe von Support-Libraries
in SmartHomeNG. Falls eine Library Pythoen Packages benötigt, die nicht in der Standard Python Installation enthalten
sind, muss die Abhängigkeit in der Datei ``../lib/requirements.txt`` dokumentiert werden.

Im folgenden sind die Beschreibungen der Funktionen der einzelnen Libraries aufgeführt:

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


Die folgenden Libraries sind "öffentlicher". Die können auch in der Entwicklung von Plugins und
Logiken verwendet werden:

.. toctree::
   :maxdepth: 5
   :titlesonly:

   /lib/db
   /lib/logutils
   /lib/network
   /lib/orb
   /lib/tools
   /lib/utils
