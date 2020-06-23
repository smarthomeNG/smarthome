Logging - Best Practices
========================

Die im folgenden beschriebene Logging Konfiguration erzeugt zwei
Logfiles:

-  Ein Hauptlog (smarthome-warnings.log), welches alle WARNINGs, ERRORs
   und CRITICAL errors des Cores und aller Plugins empfängt
-  Ein Zusatzlog (smarthome-additional.log), welches frei konfigurierbar
   Logeinträge verschiedener Module und Plugins empfängt.

Das hat den Vorteil, dass das Hauptlog übersichtlich bleibt weil dort
nur Warnungen und Fehler eingetragen werden. Anderseits kann man für
einen oder mehrere Teile von SmartHomeNG der einen besonders
interessiert, den Loglevel auf INFO oder DEBUG hochsetzen, ohne den
Loglevel des Root-Loggers anzuheben und sich im Hauptlog durch Mengen
von Einträgen aller Plugins wühlen zu müssen, die einen nicht
interessieren.

Da der root-Logger zwangsweise ALLE Logmessages erhält, kann das
Hauptlog (smarthome-warnings) nur dadurch übersichtlich gehalten werden,
dass der Level des root-Loggers WARNING oder höher ist!

Wenn der root-Logger z.B. auf den Level DEBUG gesetzt würde, so würden
ALLE Logmessage in das Log geschrieben. Das wäre analog zum Debug-Mode
von SmartHomeNG.

Diese Best Practices haben folgende Abschnitte:

-  `Grundkonfiguration des
   Loggings <#grundkonfiguration-des-loggings>`__
-  `Konfiguration zusätzlicher
   Logausgaben <#konfiguration-zusätzlicher-logausgaben>`__
-  `Identifizieren von Neustarts im
   Zusatzlog <#identifizieren-von-neustarts-im-zusatzlog>`__
-  `Ein besserer simple-Formatter <#ein-besserer-simple-formatter>`__
   für das Hauptlog (und das Zusatzlog)

`Erweiterte Konfigurationen des
Loggings <#erweiterte-konfigurationen-des-loggings>`__ \* `Erweitertes
Logging für die Plugin
Entwicklung <#erweitertes-logging-für-die-plugin-entwicklung>`__

Grundkonfiguration des Loggings
-------------------------------

Die grundsätzliche Konfiguration des Loggings sieht dann so aus:

.. code-block:: yaml

   # etc/logging.yaml

   version: 1
   disable_existing_loggers: False
   formatters:
       shng_simple:
           format: '%(asctime)s %(levelname)-8s %(name)-19s %(message)s'
           datefmt: '%Y-%m-%d  %H:%M:%S'

       shng_detail:
           format: '%(asctime)s %(levelname)-8s %(module)-17s %(threadName)-12s %(message)s  --  (%(filename)s:%(funcName)s:%(lineno)d)'
           datefmt: '%Y-%m-%d %H:%M:%S %Z'

   handlers:
       console:
           class: logging.StreamHandler
           formatter: simple
           stream: ext://sys.stdout

       shng_warnings_file:
           class: logging.handlers.TimedRotatingFileHandler
           formatter: shng_simple
           level: WARNING
           when: midnight
           backupCount: 7
           filename: ./var/log/smarthome-warnings.log
           encoding: utf8

       shng_details_file:
           class: logging.handlers.TimedRotatingFileHandler
           formatter: shng_detail
           level: DEBUG
           when: midnight
           backupCount: 7
           filename: ./var/log/smarthome-details.log
           encoding: utf8

   loggers:
       __main__:
           level: WARNING
           handlers: [shng_details_file]

   root:
       level: WARNING
       handlers: [shng_warnings_file]

Sie loggt nur Warnungen und Fehler in das Hauptlog. Das Zusatzlog wird
nicht beschrieben. Diese Grundkonfiguration definiert drei handler
(Ziele für Logausgaben):

-  Die Konsole
-  Das Logfile **smarthome-warnings.log**, welches nur Warnungen und
   Fehler aufnimmt
-  Das Logfile **smarthome-additional.log**, welches prinzipiell alle
   Logmeldungen (von DEBUG bis CRITICAL) aufnimmt

Die beiden Handler die Logfiles schreiben, sind als rotierende Handler
ausgelegt, die in eigenen Dateien die Logeinträge der letzten sieben
Tage aufheben.

   **Note**: Die Rotation der Logfiles erfolgt um Mitternacht GMT, also
   nicht unbedingt um Mitternacht lokaler Zeit.

..

   **Note**: Die Änderungen in der Konfiguration werden erst bei einem
   Neustart von SmartHomeNG wirksam.

Konfiguration zusätzlicher Logausgaben
--------------------------------------

Um zusätzliche Logausgaben zu konfigurieren, muss nur der Abschnitt
**logger:** der Logging Konfiguration angepasst/erweitert werden.

Die meisten Plugins schreiben ihre Logausgaben in einen eigenen Logger,
falls dieser in **logging.yaml** definiert ist. Die Logausgaben werden
dann in diesen eigenen Logger und in den root-Logger geschrieben. Die
Konfiguration des root-Loggers verhindert, das INFO und DEBUG ausgaben
ins Hauptlog kommen.

Welche Ausgaben in das Zusatzlog kommen, wird durch die Konfiguration
der einzelnen Logger festgelegt. Prinzipiell kann das Zusatzlog ja alle
Loglevel aufnehmen.

Um zum Beispiel für das Plugin **mqtt** INFO Logausgaben zu schreiben,
muss ein zusätzlicher Logger folgendermaßen konfiguriert werden:

.. code-block:: yaml

   # Ausschnitt aus etc/logging.yaml

   loggers:
       plugins.mqtt:
           handlers: [shng_details_file]
           level: INFO

Dieser Logger schreibt in das Zusatzlog und zwar bis zum Level INFO.

Wenn jetzt noch zusätzlich für das Plugin **enogw** DEBUG Logausgaben
geschrieben werden sollen, muss ein weiterer Logger folgendermaßen
konfiguriert werden:

.. code-block:: yaml

   # Ausschnitt aus etc/logging.yaml

   loggers:
       plugins.mqtt:
           handlers: [shng_details_file]
           level: INFO

       plugins.enogw:
           handlers: [shng_details_file]
           level: DEBUG

Nun werden INFO Logs des mqtt Plugins, sowie DEBUG und INFO Logs des
enogw Plugins in das Zusatzlog geschrieben.

Identifizieren von Neustarts im Zusatzlog
-----------------------------------------

Im Hauptlog werden zwei Zeilen

.. code-block:: bash

   2018-11-10  01:03:23 WARNING  __main__            --------------------   Init SmartHomeNG 1.6   --------------------
   2018-11-10  01:03:23 WARNING  __main__            Running in Python interpreter 'v3.6.5 final' (pid=18624) on linux platform

bei jedem Start von SmartHomeNG geschrieben, um die Neustarts im Log
einfacher auffinden zu können. Diese Zeile gibt es im Zusatzlog
standardmäßig nicht.

Wenn man diese Zeile auch im Zusatzlog haben möchte, muss man die
WARNINGs des main-Loggers auch in das Zusatzlog lenken. Das geschieht
indem man den logger ``__main__`` folgendermaßen konfiguriert:

.. code-block:: yaml

   # Ausschnitt aus etc/logging.yaml

   loggers:
       __main__:
           handlers: [shng_details_file]
           level: WARNING

       plugins.mqtt:
           handlers: [shng_details_file]
           level: INFO

       plugins.enogw:
           handlers: [shng_details_file]
           level: DEBUG

Ein besserer simple-Formatter
-----------------------------

In der Standardkonfiguration des Loggings wurde von SmartHomeNG wird
bisher nach Datum und Loglevel der Threadname vor der eigentlichen
Logmessage ausgegeben:

.. code-block:: yaml

   formatters:
     simple:
       format: '%(asctime)s %(levelname)-8s %(threadName)-12s %(message)s'
       datefmt: '%Y-%m-%d  %H:%M:%S'

Folgende Einstellung (wie oben im Beispiel bereits angegeben) schreibt
statt des Thread Names (der nicht besonders hilfeich ist), den Python
Modul Namen in das log (also z.B.: lib.plugin, plugins.knx, …):

.. code-block:: yaml

   formatters:
     shng_simple:
       format: '%(asctime)s %(levelname)-8s %(name)-19s %(message)s'
       datefmt: '%Y-%m-%d  %H:%M:%S'

Das ist hilfreicher um zu identifizieren woher die Logmessage stammt.

Erweiterte Konfigurationen des Loggings
---------------------------------------

Mit den obigen Hinweisen hat man eine übersichtliche Log Umgebung und
Konfiguration, die den meisten Anforderungen genügt. Wenn man dennoch
darüber hinausgehende Anforderungen hat, kann man dieses Logging Modell
auch noch erweitern.

Logging Filter
~~~~~~~~~~~~~~

Filter können dazu genutzt werden, nur bestimmte Logeinträge anzuzeigen bzw.
diese eben auch zu verstecken. Hierzu wird zuerst ein Filter angelegt:

.. code-block:: yaml

   filter:
       meinfilter:
           (): lib.logutils.Filter
           module: "[sS]tate[eE]ngineLogger"
           name: "plugins.stateengine.licht.test"
           msg: "(.*)Item (.*) not found!"
           #invert: True

Dieser Filter muss nun beim entsprechenden Handler noch referenziert werden:

.. code-block:: yaml

   handlers:
       stateengine_file:
           class: logging.handlers.TimedRotatingFileHandler
           formatter: shng_simple
           filename: ./var/log/stateengine.log
           filters: [meinfilter]

Wichtig sind dabei die eckigen Klammern, auch wenn nur ein Filter referenziert
wird. Und ja, es können hier durch Beistrich auch mehrere Filter gelistet
werden. Schließlich muss der Handler noch im entsprechenden logger eingetragen
werden.

.. code-block:: yaml

   loggers:
        plugins.stateengine:
            handlers: [stateengine_file]
            level: DEBUG

Dies führt dazu, dass nicht mehr alle DEBUG Informationen des Loggers vom
Stateengine Plugin in die Datei stateengine.log geschrieben werden. Auf Grund
des Filters werden sämtliche Einträge ignoriert, die..
- vom Modul StateEngine (s und e können sowohl groß, als auch klein geschrieben
werden) stammen
- vom Logger mit dem Namen 'plugins.stateengine.licht.test' stammen
- am Ende der Zeile "Item <beliebiger Eintrag> not found!" beinhalten

Hätte man im Filter "invert: True" angegeben, würden alle Einträge ignoriert
werden, die NICHT den oben genannten Kriterien entsprechen.

Ein weiteres Filterbeispiel, das z.B. alle Logeinträge zwischen 20:00 und 08:00
morgens filtert und somit nicht ins Log schreibt. Wie im Beispiel zu sehen,
können auch mehrere Angaben zu einem Filterattribut (hier timestamp) als Liste
deklariert werden.

.. code-block:: yaml

  filter:
      filter_nacht:
          (): lib.logutils.Filter
          timestamp: ['(.*)\s2[0-4]:(.*)', '(.*)\s0[0-8]:(.*)']

Erläuterung der RegEx:
Es werden beliebige Einträge für Jahr-Monat-Tag akzeptiert. Anschließend folgt
ein Leerzeichen und der relevante Filtercode. '2[0-4]{1}' filtert alles zwischen
20 und 24 Uhr und '0[0-8]{1}' alles zwischen 00 und 08 Uhr.

.. code-block:: yaml

  filter:
      filter_abend_mai:
          (): lib.logutils.Filter
          timestamp: '^[0-9]{4}-05-[0-9]{1,2}\s2[0-4]{1}:(.*)'

Erläuterung der RegEx:
Da das Datum als YYYY-MM-DD HH:MM:SS angegeben wird, können natürlich auch
nur in bestimmten Monaten Einträge geschrieben werden. Für die Fälle, in denen
jemand gerne eine Logdatei pro Kalendermonat hätte ;)

Erweitertes Logging für die Plugin Entwicklung
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Für die Entwicklung von Plugins kann es hilfreich sein, wenn man im Log
sehen kann, aus welchem Teil des Plugins die Logmessage kommt. Dazu kann
man einen Formatter schreiben, der die Funktion/Methode, die das Log
geschrieben hat, mit anzeigt.

Dazu erzeugt man einen zusätzlichen Formatter als Kopie aus dem
(verbesserten) simple Formatter und nennt ihn ``funcname``. Dann fügt
man den Platzhalter ``%(funcName)-16s`` in den Format-String ein, der
den Funktionsnamen ausgibt.

.. code-block:: yaml

   formatters:
       simple:
           format: '%(asctime)s %(levelname)-8s %(name)-16s %(message)s'
           datefmt: '%Y-%m-%d  %H:%M:%S'
       funcname:
           format: '%(asctime)s %(levelname)-8s %(name)-16s %(funcName)-16s %(message)s'
           datefmt: '%Y-%m-%d  %H:%M:%S'

Damit dieser neue Formatter auch genutzt wird, muss er noch im Handler
``file_additional`` an Stelle des ``simple`` Formatters eingetragen
werden:

.. code-block:: yaml

   handlers:
       shng_details_file:
           class: logging.handlers.TimedRotatingFileHandler
           formatter: funcname
           level: DEBUG
           when: midnight
           backupCount: 7
           filename: ./var/log/smarthome-details.log
           encoding: utf8

Das bewirkt, dass im Zusatzlog die Funktionsnamen mit geloggt werden,
während im Warnings-Log das Logging unverändert das ``simple`` Format
nutzt.
