
Allgemeines zur Konfiguration
=============================

Die Codebasis von SmartHomeNG ist in der Programmiersprache Python geschrieben. Python ist

* kostenlos
* einfach zu erlernen
* elegant in der Anwendung
* objektorientiert
* Open-Source-Software
* plattformunabhängig (allerdings werden derzeit bei SmartHomeNG Linux-Besonderheiten genutzt so dass z.B. Windows derzeit nur bedingt genutzt werden kann)
* multi-threaded

Wichtig für den Einsteiger ist es zu wissen, dass Python peinlich genau auf Einrückungen achtet. Etwas wie

.. code-block:: text

   def foo(a):
       bar = a
     d = 5
       x = a
       s = 'text'

führt unweigerlich zu Fehlern. Auch ist ein Mischen von **TAB** und **Leerzeichen** oftmals eine Fehlerquelle.
Um diese Quellen von Ärgernissen auszuschalten, macht es Sinn einen Editor zu verwenden,
den man von vorne herein auf **UTF-8 ohne BOM** und umwandeln von **TAB in 4 Leerzeichen** einstellen kann.

Für Konfigurationsdateien gilt analog das Gleiche. Die Konfiguration erfolgt über YAML Dateien.
Wichtig für den Einsteiger ist es zu wissen, dass auch YAML peinlich genau auf Einrückungen achtet und das
Einrückungen nur durch Leerzeichen erfolgen dürfen. **TAB**s sind in YAML Dateien unzulässig. Der
Übersichtlichkeit halber wird empfohlen Einrückungen jeweils mit **4 Leerzeichen** vorzunehmen.


Passende Editoren für Python und YAML Dateien sind z.B.

+-------------+-----------------------------------------------------------------------+
| Plattform   | Editor                                                                |
+=============+=======================================================================+
| Linux       | emacs (nano oder vi ginge zur Not auch)                               |
|             |                                                                       |
| Linux (GUI) | `Atom <http://www.atom.io>`_                                          |
+-------------+-----------------------------------------------------------------------+
| Windows     | `Notepad++ <http://www.notepad-plus-plus.org>`_                       |
|             |                                                                       |
|             | `Atom <http://www.atom.io>`_                                          |
|             |                                                                       |
|             | `Visual Studio Code <https://code.visualstudio.com>`_                 |
+-------------+-----------------------------------------------------------------------+
| Mac         | `BBEdit <https://www.barebones.com/products/bbedit/download.html>`_   |
|             |                                                                       |
|             | `Atom <http://www.atom.io>`_                                          |
+-------------+-----------------------------------------------------------------------+


Ein guter Editor unterstützt dann auch mit der richtigen Syntaxeinfärbung.

.. code-block:: Python

   def foo(a):
      bar = a
      d = 5
      x = a
      s = 'text'



----------------------------
Verzeichnisse in SmartHomeNG
----------------------------

Die Verzeichnisse sind im Hauptverzeichnis von SmartHomeNG zu finden, für gewöhnlich im Verzeichnis `/usr/local/smarthome``.

+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| Verzeichnis  | Beschreibung / Inhalt                                                                                                       |
+==============+=============================================================================================================================+
| ``bin``      | Hauptmodul von SmarthomeNG                                                                                                  |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``dev``      | Grundgerüst und Infos zur Pluginentwicklung                                                                                 |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``doc``      | Wird einmal die Dokumentation enthalten                                                                                     |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``etc``      | enthält mindestens **smarthome.yaml**, **plugin.yaml** und **logic.yaml**.                                                  |
|              | In diesen Dateien befindet sich die Konfiguration des Grundsystems                                                          |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``examples`` | Beispiele für Items                                                                                                         |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``items``    | Items                                                                                                                       |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``lib``      | Modulbibliothek für das Hauptprogramm                                                                                       |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``logics``   | Jede Logik bekommt hier eine kleine Datei mit Python Code                                                                   |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``plugins``  | Modulbibliothek für die Plugins. Jedes Plugin hat sein eigenes Unterverzeichnis                                             |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``scenes``   | Gespeicherte Szenen                                                                                                         |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``tests``    | Hilfsprogramme zum Testen von Modulen des Systems                                                                           |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``tools``    | Hilfsprogramme                                                                                                              |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+
| ``var``      | Daten die vom SmartHomeNG zur Laufzeit gespeichert und gelesen werden  also z.B. Logdateien, cache, sqlite Datenbank, etc.  |
+--------------+-----------------------------------------------------------------------------------------------------------------------------+


Dateien im Verzeichnis *../etc*
-------------------------------

Während der Installation sind im Unterverzeichnis **etc** bereits drei Dateien erstellt worden:
**smarthome.yaml**, **plugin.yaml** und **logic.yaml**.


smarthome.yaml
^^^^^^^^^^^^^^

In der Datei **smarthome.yaml** wird notiert, wo sich die Installation befindet und welche
Zeitzone als Basis genommen werden soll:

.. code-block:: yaml
   :caption: ../etc/smarthome.yaml

   # smarthome.yaml
   lat: '50.123'
   lon: '14.67'
   elev: 36
   tz: Europe/Berlin

   # ab Version 1.3
   # module_paths = /usr/local/python/lib    # list of path-entries is possible

   # ab Version 1.3: control type casting when assiging values to items
   # assign_compatibility = latest            # latest or compat_1.2 (compat_1.2 is default for shNG v1.3)


Mit dieser Version können auch zusätzliche Modulpfade konfiguriert werden, in denen Drittanbieter-Bibliotheken
abgelegt sind (`module_paths` Einstellung). Somit können Bibliotheken, beispielsweise in Logiken, verwendet
werden die nicht direkt mit ausgeliefert bzw. installiert werden. Es kann ein oder mehrere absolute Pfade
angegeben werden.

Außerdem kann der Datentyp einer Wertzuweisung bei der Nutzung von `autotimer` und `cycle` beeinflusst
werden. Weiterführende Informationen gibt es im Abschnitt **Datentyp der Wertzuweisung** auf der
Seite :doc:`/referenz/items/standard_attribute/autotimer`



plugin.yaml
^^^^^^^^^^^

Die Datei **plugin.yaml** enthält die Konfigurationsanweisungen für alle Plugins, die benutzt werden sollen.

.. code-block:: yaml
   :caption: ../etc/plugin.yaml

   # plugin.yaml
   knx:
      plugin_name: knx
      host: 127.0.0.1
      port: 6720
   #   send_time: 600 # update date/time every 600 seconds, default none
   #   time_ga: 1/1/1 # default none
   #   date_ga: 1/1/2 # default none
   visu:
       plugin_name: visu_websocket
   cli:
       plugin_name: cli
       ip: 0.0.0.0
       update: True
   sql:
       plugin_name: sqlite_visu2_8


Seit Version 1.2 (Master Branch) gibt es ein neues Plugin (Backend) für SmartHomeNG. Dabei kann
man über einen Browser das gleiche (und mehr) erreichen, wie früher über das CLI-Plugin.

Allerdings ist das Plugin inzwischen veraltet und wird in einer der kommenden Versionen von SmartHomeNG entfernt, da
es inzwischen ein erheblich leistungsfähigeres Administrationsinterface für SmartHomeNG gibt.

Das Backend Plugin bindet man folgendermaßen ein:

.. code-block:: yaml
   :caption: Auszug aus ../etc/plugin.yaml

   BackendServer:
       plugin_name: backend
       updates_allowed: True
       user: admin
       password: xxxx
       language: de
       threads: 8
       #ip: 0.0.0.0
       #port: 8383


Die weitere Einrichtung und Konfiguration von Plugins ist unter `Plugins <plugins.html>`_ beschrieben.


..
   Using an older version of a plugin
   ----------------------------------

   If you are not using the newest version of the SmartHomeNG core, if may be necessary to use an
   older version of a plugin. Some plugins come with embedded older versions. To load an older
   version of the plugin, you have to specify the parameter `plugin_version` in the configuration
   section of the plugin.

   To find out, if a plugin comes with an older version (or versions), take a look at the plugin's
   directory. if you find a subdirectory with the name starting with ``_pv_`` the plugin comes with
   an older (previous) version. The rest of the folder name specifies the version number. If you
   find a subfolder ``_pv_1_3_0``, it contains the v1.3.0 of the plugin. To load that version, just
   add ``plugin_version: 1.3.0`` to the plugin configuration.



logic.yaml
^^^^^^^^^^

In der Datei **logic.yaml** werden die Logiken eingetragen. Der Name jeder Logik kommt
zwischen zwei eckige Klammern, der Eintrag **filename** verweist auf die Python-Datei die dann aufgerufen
wird, wenn die Logik abgearbeitet werden soll. **crontab** schreibt fest, dass die Logik zu bestimmten
Zeiten ausgeführt werden soll. watch_item bestimmt, welche Items die Logik aufrufen können:

.. code-block:: yaml
   :caption: ../etc/logic.yaml

   # logic.yaml
   InitSmarthomeNG:
       filename: InitSmartHomeNG.py
       crontab: init

   Beispiellogik:
       # Umgebungsvariablen des Systems werden aktualisiert, z.B. Diskusage
       filename: Beispiel.py
       watch_item:
       - '*:Logikaufruf'
       - item1.*
       - parent.item2
       # run on start of SmartHomeNG and every 5 minutes afterwards
       crontab:
       - init
       - 0,5,10,15,20,25,30,35,40,45,50,55 * * *


Detaillierte Infos zur crontab Konfiguration finden sich unter :doc:`/referenz/items/standard_attribute/crontab`.

Für die weitere Konfiguration von Logiken geht es unter :doc:`logiken` weiter.


Weitere Dateien
^^^^^^^^^^^^^^^

Zusätzlich sind ab der Version 1.2 auch noch **logging.yaml**, **plugin.yaml.default** und
**smarthome.yaml.default** zu finden. Während sich der Inhalt der **.default** Dateien als
Beispieldatei selbst erklärt, ist die **logging.yaml** noch erklärungsbedürftig:
Im gesamten Programmcode sind Anweisungen verteilt, die bestimmte Programmzustände loggen,
also mit notieren.

Im einfachsten Fall sind das einfache Meldungen die z.B. den Start eines
Plugins melden oder aber das setzen eines Items durch die Visu oder aber das Ausführen einer
Datenbank Komprimierung. Es sind aber auch Meldungen dabei, die über Fehler berichten, z.B. wenn
ein Item das über die Visu aktualisiert werden soll, gar nicht existiert oder wenn zum Beispiel
ein Plugin einen Fehler bei der Abfrage von Daten eines Stromzählers meldet.

Mit der **logging.yaml** kann man ziemlich fein steuern von welchen Modulen man welche Meldungen
bekommen möchte. Sucht man beispielsweise einen hartnäckigen Fehler in einem neuen Plugin **Foo**,
dann kann man das Logging für alle anderen Plugins gezielt reduzieren so das man sich aufs Wesentliche
konzentrieren kann.

Weitere Informationen gibt es unter `Konfiguration - Logging <logging.html>`_


Dateien im Verzeichnis *../items*
---------------------------------

Hier finden sich die Dateien mit den Items. Es ist egal, wie viele Dateien hier abgelegt wurden.
Alle Dateien die die Endung .yaml besitzen, werden beim Start von SmartHomeNG gelesen und in die
Struktur von SmartHomeNG eingebaut.
Eine genaue Beschreibung des Aufbaus findet sich unter :doc:`/referenz/items/standard_attribute/eval` .

**Aus Gründen der Übersichtlichkeit macht es durchaus Sinn, die .yaml-Dateien nach Räumen oder
nach thematischen Gesichtspunkten aufzusplitten und die jeweiligen Items dort zu parametrieren.**

**Beispielsweise:**

* eg_kueche.yaml
* eg_wohnzimmer.yaml
* og_schlafzimmer_eltern.yaml
* og_schlafzimmer_ryan.yaml
* terrasse.yaml
* kwl.yaml
* zentralheizung.yaml
* ...

**Wichtig: Wenn eine Item-Datei oder eine Logic-Datei neu erstellt oder geändert worden ist
oder ein neues Plugin implementiert werden soll, muss SmartHomeNG neu gestartet werden.**

SmartHomeNG kann über die Option **-r** neu gestartet werden.

.. code-block:: bash

   cd /usr/local/smarthome
   python3 bin/smarthome.py -r


Wenn SmartHomeNG als Dienst eingerichtet ist, kann der Dienst kann über den entsprechenden Befehl "systemctl"
neu gestartet werden.

.. code-block:: bash

   sudo systemctl restart smarthome.service

.. note::

   Der Service **smarthome.service** muss vorher eingerichtet werden. Die Einrichtung ist in der
   Komplettanleitung unter :doc:`../installation/komplettanleitung/08_shng_daemon` beschrieben.

