#############
Konfiguration
#############

.. toctree::
   :maxdepth: 5
   :hidden:
   :titlesonly:

   konfigurationsdateien.rst
   items.rst
   module.rst
   plugins.rst
   logiken.rst
   logging.rst
   szenen.rst


=========
Überblick
=========

Die Codebasis von SmartHomeNG ist in der Programmiersprache Python geschrieben. Python ist

* kostenlos
* einfach zu erlernen
* elegant in der Anwendung
* objektorientiert
* Open-Source-Software
* plattformunabhängig (allerdings werden derzeit bei SmartHomeNG Linux-Besonderheiten genutzt so dass z.B. Windows derzeit nicht genutzt werden kann)
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

Passende Editoren sind z.B.

+-----------+---------------------------------------------------------------------+
| Plattform | Editor                                                              |
+===========+=====================================================================+
| Linux     | emacs (nano oder vi ginge zur Not auch)                             |
+-----------+---------------------------------------------------------------------+
| Windows   | `Notepad++ <http://www.notepad-plus-plus.org>`_                     |
+-----------+---------------------------------------------------------------------+
| Mac       | `BBEdit <https://www.barebones.com/products/bbedit/download.html>`_ |
+-----------+---------------------------------------------------------------------+


Ein guter Editor unterstützt dann auch mit der richtigen Syntaxeinfärbung.

.. code-block:: Python

   def foo(a):
      bar = a
      d = 5
      x = a
      s = 'text'


Eine Liste guter Einführungen zu Python sind hier: `Python <https://github.com/smarthomeNG/smarthome/wiki/Python>`_ zu finden.


Verzeichnisse in SmartHomeNG
============================

Die Verzeichnisse sind im Hauptverzeichnis von smarthome zu finden, für gewöhnlich im Verzeichnis **"/usr/local/smarthome"**.

+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
| Verzeichnis | Beschreibung / Inhalt                                                                                                                         |
+=============+===============================================================================================================================================+
|bin          | Hauptmodul von SmarthomeNG                                                                                                                    |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|dev          | Grundgerüst und Infos zur Pluginentwicklung                                                                                                   |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|doc          | Wird einmal die Dokumentation enthalten                                                                                                       |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|etc          | enthält mindestens **smarthome.yaml**, **plugin.yaml** und **logic.yaml**. In diesen Dateien befindet sich die Konfiguration des Grundsystems |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|examples     | Beispiele für Items                                                                                                                           |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|items        | Items                                                                                                                                         |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|lib          | Modulbibliothek für das Hauptprogramm                                                                                                         |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|logics       | Jede Logik bekommt hier eine kleine Datei mit Python Code                                                                                     |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|plugins      | Modulbibliothek für die Plugins. Jedes Plugin hat sein eigenes Unterverzeichnis                                                               |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|scenes       | Gespeicherte Szenen                                                                                                                           |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|tests        | Hilfsprogramme zum Testen von Modulen des Systems                                                                                             |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|tools        | Hilfsprogramme                                                                                                                                |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+
|var          | Daten die vom SmartHomeNG zur Laufzeit gespeichert und gelesen werden  also z.B. Logdateien, cache, sqlite Datenbank, etc.                    |
+-------------+-----------------------------------------------------------------------------------------------------------------------------------------------+


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
Seite :doc:`items_standard_attribute_autotimer`



plugin.yaml
^^^^^^^^^^^

Die Datei **plugin.yaml** enthält die Konfigurationsanweisungen für alle Plugins, die benutzt werden sollen.

.. code-block:: yaml
   :caption: ../etc/plugin.yaml

   # plugin.yaml
   knx:
      class_name: KNX
      class_path: plugins.knx
      host: 127.0.0.1
      port: 6720
   #   send_time: 600 # update date/time every 600 seconds, default none
   #   time_ga: 1/1/1 # default none
   #   date_ga: 1/1/2 # default none
   visu:
       class_name: WebSocket
       class_path: plugins.visu_websocket
   cli:
       class_name: CLI
       class_path: plugins.cli
       ip: 0.0.0.0
       update: True
   sql:
       class_name: SQL
       class_path: plugins.sqlite


Seit Version 1.2 (Master Branch) gibt es ein neues Plugin (Backend) für SmartHomeNG. Dabei kann
man über einen Browser das gleiche (und mehr) erreichen, wie früher über das CLI-Plugin. Das
Backend Plugin bindet man folgendermaßen ein:

.. code-block:: yaml
   :caption: Auszug aus ../etc/plugin.yaml

   BackendServer:
       class_name: BackendServer
       class_path: plugins.backend
       updates_allowed: True
       user: admin
       password: xxxx
       language: de
       threads: 8
       #ip: 0.0.0.0
       #port: 8383


Die weitere Einrichtung und Konfiguration von Plugins ist unter `Plugins <plugins.html>`_ beschrieben.


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


Detaillierte Infos zur crontab Konfiguration finden sich unter :doc:`items_standard_attribute_crontab`.

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
Eine genaue Beschreibung des Aufbaus findet sich unter :doc:`items_standard_attribute_eval` .

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

Der Dienst kann über den entsprechenden Befehl "systemctl" neu gestartet werden.


.. code-block:: bash

   sudo systemctl restart smarthome.service

.. note::

   Der Service **smarthome.service** muss vorher eingerichtet werden. Die Einrichtung ist in der
   Komplettanleitung unter :doc:`../installation/komplettanleitung_shng_daemon` beschrieben.


Weiterführende Themen
---------------------

`UZSU (Universelle Zeitschaltuhr) <https://github.com/smarthomeNG/smarthome/wiki/UZSU-%28Universelle-Zeitschaltuhr%29>`_

