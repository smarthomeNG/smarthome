

.. index:: SmartHomeNG installieren

.. role:: bluesup
.. role:: redsup

========================
SmartHomeNG installieren
========================

SmartHomeNG ist eine in Python erstellte Anwendung. Daher muss bevor SmartHomeNG genutzt werden kann,
Python installiert werden. Außerdem muß der git Client installiert werden, um SmartHomeNG von Github
zu laden und zu installieren.


.. contents:: Schritte der Installation
   :local:


zusätzliche Linux Pakete installieren
=======================================

Zunächst müssen einige zusätzlichen Pakete installiert werden:

.. code-block:: bash

   sudo apt-get -y install dialog python3 python3-dev python3-setuptools unzip git-core build-essential python3-pip


SmartHomeNG Quellcode laden
===========================

SmartHomeNG Dateien vom github holen:

Die folgenden Kommandos mit dem User Account (smarthome) durchführen
unter dem später SmartHomeNG laufen soll, **nicht als root**.

.. code-block:: bash

   cd /usr/local
   sudo mkdir smarthome
   sudo chown -R smarthome:smarthome /usr/local/smarthome

   cd smarthome
   git clone git://github.com/smarthomeNG/smarthome.git .
   git clone git://github.com/smarthomeNG/plugins.git plugins

Bitte auf den **Punkt** am Ende des ersten **git clone** Kommandos achten!


Weitere Python Bibliotheken installieren
========================================

.. tabs::

   .. tab:: SmartHomeNG ab v1.7

      SmartHomeNG kann benötigte Pakete selbst nachinstallieren.

      Wenn SmartHomeNG in einer Python Umgebung gestartet wird in der nicht der minimale Set an Packages installiert ist,
      wird dieser installiert und die Informationen werden auf die Konsole ausgegeben (da das Logging dann noch nicht
      konfiguriert werden kann). Anschließend startet SmartHomeNG neu. Das sieht folgendermaßen aus.

      .. code-block:: bash

         $ python3 bin/smarthome.py

         test_requirements: 'ephem' not installed. Minimum v3.7 needed
         test_requirements: 'holidays' not installed. Minimum v0.9.11 needed
         test_requirements: 'psutil' not installed, any version needed
         test_requirements: 'python-dateutil' not installed. Minimum v2.5.3 needed
         test_requirements: 'requests' not installed. Minimum v2.20.0 needed
         test_requirements: 'ruamel.yaml' not installed. Minimum v0.13.7 needed

         Installing core requirements for the current user, please wait...
         Running in a virtualenv environment,
         installing core requirements only to actual virtualenv, please wait...

         core requirements installed

         Starting SmartHomeNG again...
         Daemon PID 4024

         $

      Danach kann der Core von SmartHomeNG vollständig initialisiert werden und Ausgaben erfolgen in smarthome-warnings.log

      Anschließend prüft SmartHomeNG ob die benötigten Pakete für die ladbaren Module und für die konfigurierten Plugins
      installiert sind. Falls nicht, werden diese jeweils installiert und SmartHomeNG startet sich erneut.

      .. note::

         Dieser Mechanismus sorgt auch dafür, dass Pakete die von später konfigurierten Plugins benötigt werden, automatisch
         nachinstalliert werden.

   .. tab:: SmartHomeNG vor v1.7

      Für den ersten Start müssen noch einige Python Packages nachgeladen werden.
      Im Unterordner ``requirements`` befindet sich dafür eine Datei ``base.txt``.
      In dieser Datei stehen die von SmartHomeNG grundlegend benötigten Bibliotheken.
      Diese können wie folgt installiert werden:

      .. code-block:: bash

         cd /usr/local/smarthome
         pip3 install -r requirements/base.txt --user

      .. attention::

          In früheren Beschreibungen wurde die globale Installation von Python Packages mit dem sudo Kommando
          beschrieben:

             sudo pip3 install -r requirements/base.txt

          Dieses funktioniert unter Debian Buster **NICHT** mehr. Zumindest unter Buster **muss** die Installation
          für den entsprechenden User mit **--user** erfolgen (wie oben beschrieben).


      .. note::

          Falls mehrere Python3 Versionen installiert sind, kann es zu Problemen kommen, da pip die Bibliotheken immer nur
          in eine der installierten Python 3 Versionen installiert.

          Um sicherzustellen, dass die Bibliotheken in die Python3 Version installiert werden, muss pip3 aus genau dieser
          Python3 Umgebung aufgerufen werden.

          Um das sicherzustellen, ist statt

          .. code-block:: bash

              pip3 install -r requirements/base.txt --user

          der folgende Befehl auszuführen:

          .. code-block:: bash

              <python used to start SmartHomeNG> -m pip3 install -r requirements/base.txt --user

      Jetzt ist SmartHomeNG installiert und kann konfiguriert werden.


Erstmaliger Start von SmartHomeNG
=================================


SmartHomeNG starten
-------------------

Nachdem SmartHomeNG nun installiert ist, kann SmartHomeNG erstmalig gestartet werden:

.. code-block:: bash

   cd /usr/local/smarthome
   python3 bin/smarthome.py

Auf der Shell (Konsole, Kommandozeile) sollte jetzt nur eine Zeile erscheinen wie:

.. code-block:: bash

   Daemon PID <PID-ID>

Das bedeutet, das SmartHomeNG nun im Hintergrund läuft und unter der Prozess ID ``<PID-ID>`` bekannt ist.


Überprüfen, ob SmartHomeNG läuft
-----------------------------------

Um festzustellen ob SmartHomeNG läuft, kann der folgende Befehl genutzt werden:

.. code-block:: bash

    ps -ef|grep smarthome|grep bin

Es sollte eine Zeile ausgegeben werden, die etwa so aussieht:

.. code-block:: bash

    smartho+ 28373     1  1 12:45 ?        00:00:02 python3 bin/smarthome.py

Die Zeile zeigt an, dass unter dem User **smarthome** (hier zu smartho+ abgekürzt) unter der PID **28373** seit **12:45**
Uhr SmartHomeNG (**python3 bin/smarthome.py**) ausgeführt wird.

Erfolgt keine Ausgabe, so läuft SmartHomeNG nicht. In diesem Fall bitte den Angaben im Abschnitt :doc:`../../fehlersuche`
nachlesen.


.. note::

   SmartHomeNG kann zur Zeit nur ein einziges Mal auf einem Rechner ausgeführt werden. Versucht man dies mehrfach,
   so kann die Version die als letztes gestartet wurde oft keine Netzwerkverbindungen aufbauen.
   Ein solcher Fall kann schnell auftreten, wenn SmartHomeNG als Daemon eingerichtet wird und aber zusätzlich ein Start
   von der Kommandozeile erfolgt.


.. attention::

    SmartHomeNG ist jetzt noch nicht so eingerichtet, dass es beim Neustart des Rechners automatisch mit gestartet wird.
    Diese Einrichtung als Dienst sollte erst vorgenommen werden, nachdem die Erstkonfiguration von SmartHomeNG
    abgeschlossen ist.



Initiale Konfiguration per GUI
==============================

Zur Konfiguration per GUI muss SmartHomeNG laufen. Der Start wurde in den vorangegangenen Schritten durchgeführt
und es wurde getestet ob SmartHomeNG läuft.



SmartHomeNG konfigurieren
-------------------------

Nachdem SmartHomeNG erfolgreich gestartet wurde, kann zur Konfiguration per Browser auf die Administrationsoberfläche
zugegriffen werden. Dazu im Browser die url ``<ip des SmartHomeNG Rechners>:8383`` eingeben.

Beim ersten Start erscheint folgende Login Seite:

.. image:: /admin/assets/login.jpg
   :class: screenshot

Da bisher kein Password festgelegt ist, brauchen Benutzername und Password nicht eingegeben zu werden. Es kann einfach
auf anmelden geklickt werden.


Anschließend erscheint die Startseite von SmartHomeNG (Da kein Password festgelegt ist, ist der Button **Abmelden**
ausgegraut):

.. image:: /admin/assets/system-info.jpg
   :class: screenshot


Nun kann mit der Konfiguration begonnen werden, wie sie unter :doc:`Konfiguration </konfiguration/admin_gui/admin_gui>` beschrieben
ist. Nach Abschluß der Konfiguration muss SmartHomeNG neu gestartet werden. Dieses kann aus der GUI heraus erfolgen.



Erstmalige Konfiguration per Kommandozeile (für Fortgeschrittene)
====================================================================

Die Konfiguration kann mit der graphischen Oberfläche (Administrations-Interface) oder (für Fortgeschrittene) durch
Anpassung der Konfigurationsdateien vorgenommen werden. Dieses ist hier im folgenden kurz beschrieben. Eine ausführlichere
Beschreibung findet sich im Abschnitt :doc:`../../konfiguration/konfiguration` .

Mit der Grundinstallation werden einige Konfigurationsdateien mitgeliefert die den gleichen Namen tragen wie die
benötigten Dateien aber zusätzlich noch die Endung **.default**. Wenn SmartHomeNG beim Start eine benötigte
Konfigurationsdatei sucht, aber noch keine vorhanden ist, so wird eine Kopie von der mitgelieferten **.default**
Datei erstellt und diese weiter verwendet. Gelingt dies nicht, so bricht SmartHomeNG beim Start ab.

Es werden für einen Systemstart folgende Konfigurationsdateien benötigt:

- **smarthome.yaml**
- **holidays.yaml**
- **plugin.yaml**
- **logging.yaml**
- **logic.yaml**
- **module.yaml**

Der Inhalt von **.yaml** Dateien ist speziell formatierter Text und sollte nur mit einem Editor
bearbeitet werden, der Dateien im UTF-8 Format (ohne BOM) schreiben kann.
(z.B. **nano**, **Notepad++**)

Kommentare können mit einem ``#`` begonnen werden. Die Einrückungen müssen Leerzeichen sein
und bestimmten die Position eines Elementes in der Objekthierarchie.

.. note::

   Damit die Änderungen wirksam werden, die mit einem Editor durchgeführt wurden, muss SmartHomeNG
   unbedingt neu gestartet werden.
   (Eine Ausnahme bildet hier nur die **logic.yaml** da es möglich ist mit
   dem Logikeditor im Admin Interface diese Logiken zur Laufzeit neu
   zu laden.)

Im folgenden werden diese Dateien und deren Inhalt genauer beschrieben.

smarthome.yaml
--------------

In der **smarthome.yaml** stehen die allgemeinen Konfigurationseinstellungen der SmartHomeNG Installation, wie z.B. die
Koordinaten des Standortes. Die Koordinaten werden benötigt um unter anderem Sonnenaufgang und Sonnenuntergang zu berechnen.
Die Koordinaten für einen Standort kann man z.B. auf http://www.mapcoordinates.net/de ermitteln.

.. code-block:: yaml

   # etc/smarthome.yaml

   # Airport Berlin Tegel
   lat: 52.5588327
   lon: 13.2884374
   elev: 35

   tz: 'Europe/Berlin'

   # Version 1.5
   #deprecated_warnings: True

   # Version 1.4
   #
   # the default_language is used, where multiple languages are supported (de, if not specified)
   #default_language: de

   # Version 1.3
   # db: Format: <name>:<python-module>, list of database-entries is possible
   # db:
   #   - sqlite:sqlite3
   #   - mysql:pymysql
   # module_paths = /usr/local/python/lib    # list of path-entries is possible

   # Version 1.3: control type casting when assiging values to items
   # assign_compatibility = latest            # latest or compat_1.2 (compat_1.2 is default for shNG v1.3)

Es bietet sich an die default-Datei zu kopieren nach smarthome.yaml und die Daten oben auf den eigenen Standort
anzupassen. Alternativ kann diese Anpassung später über das Admin Interface durchgeführt werden.


logging.yaml
------------

In der **logging.yaml** finden sich die Anweisungen, wie Ereignisse die während des Programmablaufes von
SmartHomeNG auftreten geloggt also notiert werden sollen.

Diese recht umfangreiche Datei sollte zunächst nicht geändert werden. Später kann sie angepasst werden um
komplexe Ausführungsketten detailliert zu untersuchen.

Zunächst ist wichtig, das in der Grundkonfiguration zwei Dateien erzeugt werden:

- ./var/log/smarthome-warnings.log und
- ./var/log/smarthome-details.log

In der ersten Datei findet man nach dem ersten Start von SmartHomeNG etwas ähnliches wie folgende Informationen:

.. code-block:: text

    YYYY-MM-dd  hh:mm:ss WARNING  __main__             --------------------   Init SmartHomeNG 1.7   --------------------
    YYYY-MM-dd  hh:mm:ss WARNING  __main__             Running in Python interpreter 'v3.7.3 final' (pid=????) on linux platform
    YYYY-MM-dd  hh:mm:ss WARNING  lib.shtime           Nutze Feiertage für Land 'DE', Provinz 'HH', State 'None', 1 benutzerdefinierte Feiertagsdefinition(en) definiert
    YYYY-MM-dd  hh:mm:ss WARNING  plugins.cli          CLI: You should set a password for this plugin.


Vorne steht Datum und Uhrzeit, dann der Loglevel (ERROR, WARNING, INFO), dann je nach Setup in der Datei logging.yaml
noch Name bzw. Modul oder Thread und ein Meldungstext der den Logeintrag beschreibt.

Dabei sind im Beispiel ``YYYY-MM-dd hh:mm:ss`` Zeitangaben die von der aktuellen Startzeit abhängen und ``????`` ist die Prozess-ID anhand derer SmartHomeNG identifiziert werden kann.
Die ersten beiden Zeile werden immer in dieser Form auftreten, alles weitere hängt von der tatsächlichen Konfiguration ab.

Sollte ein Plugin konfiguriert werden, das noch weitere Bibliotheken benötigt, so würde SmartHomeNG an dieser Stelle einen kritischen Fehler
melden und sich beenden.

.. note::

   Der erste Blick bei ungewohntem Verhalten oder Funktionsschwierigkeiten sollte immer dieser Datei gelten.
   Wichtig ist es nach CRITICAL, ERROR und WARNING zu schauen und zu versuchen diese zu vermeiden.
   Meldungen der Level INFO und DEBUG sind normal und brauchen erstmal nicht weiter beachtet zu werden.

   Deshalb schreibt SmartHomeNG standardmäßig zwei Logs (**smarthome-warnings.log** und **smarthome-details.log**).
   Das erste Log ist so konfiguriert, dass es aus allen konfigurierten Logs nur die Einträge folgender Log-Level
   enthält: CRITICAL, ERROR und WARNING. **smarthome-details.log** enthält dem gegenüber Log Einträge bis zum Level DEBUG.


In der zweiten Datei finden sich zusätzliche Informationen die für die Erstkonfiguration die hier beschrieben wird nicht
entscheidend sind.

Da nach dem ersten Start von SmartHomeNG ohnehin die default Datei übernommen wird, ist hier kein Handlungsbedarf etwas
anzupassen.


plugin.yaml
-----------

In der **plugin.yaml** stehen die Plugins die verwendet werden sollen, sowie ihre Konfigurationsparameter.

Wenn keine Datei **plugin.yaml** existiert, wird beim ersten Start von SmartHomeNG die mitgelieferte Datei **plugin.yaml.default**
kopiert. In dieser Datei ist ein minimaler Set von Plugins konfiguriert, so dass z.B. per Browser oder mit der smartVISU auf die
SmartHomeNG Instanz zugegriffen werden kann.

.. code-block:: yaml

   %YAML 1.1
   ---
   cli:
       plugin_name: cli
       ip: 0.0.0.0
       #port: 2323
       update: True
       #hashed_password: 123456789abcdef123456789abcdef123456789abcdef

   # Bereitstellung eines Websockets zur Kommunikation zwischen SmartVISU und SmartHomeNG
   websocket:
       plugin_name: visu_websocket
       #ip: 0.0.0.0
       #port: 2424
       #tls: no
       #wsproto: 4
       #acl: rw

   database:
       plugin_name: database
       driver: sqlite3
       connect:
       -   database:./var/db/smarthomeng.db
       -   check_same_thread:0
   # ... etc.

Die Konfiguration weiterer Plugins ist vorhanden aber mit Kommentaren ``#`` ausser Kraft gesetzt, um die erstmalige Nutzung
dieser Plugins möglichst einfach zu gestalten.

Wenn man jetzt bereits weiß, welche Plugins man benötigt, dann kann die default-Datei als Arbeitsgrundlage dienen
und die benötigten Plugins können aktiviert werden.
Alternativ kann die Konfiguration auch später über das Admin Interface stattfinden.

Jedes Plugin kann weitere Abhängigkeiten von Bibliotheken mit sich bringen. Diese sind einzeln zu installieren mit

.. code-block:: bash

   cd /usr/local/smarthome
   pip3 install -r plugins/<plugin-name-hier-einsetzen>/requirements.txt --user

.. note::

   Beim Start von SmartHomeNG wird die Datei **requirements/all.txt** erstellt.

   Es kann allerdings dann zu einem Abbruch des Starts von SmartHomeNG kommen, da beim Start automatisch nur die beiden
   Requirements-Dateien erstellt werden. Die benötigten Python Packages werden dabei nicht automatisch installiert.

   Es lassen sich über diese Datei zwar sämtliche benötigten Abhängigkeiten installieren, jedoch rät das Entwicklungsteam
   ausdrücklich davon ab alle Abhängigkeiten zu installieren.


logic.yaml
----------

SmartHomeNG kann benutzerdefinierte Python-Anweisungen ausführen.
Diese werden in eigenen Python Dateien im Verzeichnis **logics** abgelegt.
In der Konfigurationsdatei ist beispielsweise beschrieben welche Skriptdateien für
SmartHomeNG bekannt sein sollen,
wann sie ausgeführt werden sollen und ob sie aktiv sind oder nicht.

.. code-block:: yaml

   %YAML 1.1
   ---
   #
   # etc/logic.yaml
   #
   ex_logging:
       filename: example_logging.py

   ex_persist:
       filename: example_persistance.py

Da derzeit noch keine Logiken benötigt werden, ist auch hier kein Handlungsbedarf zum Editieren.
SmartHomeNG erstellt auch hier aus der default-Datei eine logic.yaml.

module.yaml
-----------

In dieser Datei sind Module konfiguriert, die von Plugins benötigt werden aber dennoch nicht zur Kernfunktionalität von SmartHomeNG gehören.
Für die Grundkonfiguration ist dies das http Modul, das z.B. vom Admin Interface genutzt wird.

Auch hier ist kein Handlungsbedarf, die Beschreibung ist ebenfalls der Vollständigkeit halber enthalten.


SmartHomeNG starten
-------------------


Nachdem die Konfiguration für den Betrieb des Kerns von SmartHomeNG nun erfolgt ist, muss SmartHomeNG (neu) gestartet
werden:

.. code-block:: bash

   cd /usr/local/smarthome
   python3 bin/smarthome.py


Admin Interface
---------------

Die weitere Konfiguration kann auch über die GUI erfolgen, wie im Abschnitt `SmartHomeNG konfigurieren <#smarthomeng-konfigurieren>`__
beschrieben.
