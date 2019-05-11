
.. role:: bluesup

##########################################
SmartHomeNG installieren :bluesup:`update`
##########################################

- Schritte der Installation:
    - zusätzliche Pakete installieren
    - Quellcode laden
    - Weitere Python Bibliotheken
    - Erstmalige Konfiguration erstellen,
      die verschiedenen Konfigurationsdateien
    - SmartHomeNG starten
    - Admin Interface nutzen


zusätzliche Pakete installieren
-------------------------------

Zunächst müssen einige zusätzlichen Pakete erfüllt werden:

.. code-block:: bash

   sudo apt-get -y install dialog python3 python3-dev python3-setuptools unzip git-core build-essential
   sudo apt-get install python3-pip


Dann noch Pythons Paketmanager PIP auf den neuesten Stand bringen:

.. code-block:: bash

   sudo python3 -m pip install --upgrade pip


Quellcode laden
---------------

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

..
   folgende Zeile noch notwendig?
   python3 tools/build_requirements.py


Bitte auf den Punkt am Ende des ersten **git clone** Kommandos achten!

Weitere Python Bibliotheken
---------------------------

Für den ersten Start müssen noch einige Python Packages nachgeladen werden.
Im Unterordner ``requirements`` befindet sich dafür eine Datei ``base.txt``.
In dieser Datei stehen die von SmartHomeNG grundlegend benötigten Bibliotheken.
Diese können wie folgt installiert werden:

.. code-block:: bash

   cd /usr/local/smarthome
   sudo pip3 install -r requirements/base.txt

Vermutlich wird es eine Warnung geben, das die Bibliothek ``six`` nicht installiert wurde oder
eine zu alte Version. Das liegt an einer indirekten Abhängigkeit von
``cherrypy -> cheroot --> six (>= 1.11.0``
In diesem Fall kann ``six`` aktualisiert werden durch

.. code-block:: bash

   cd /usr/local/smarthome
   sudo pip3 install six>=1.11.0 --upgrade


Erstmalige Konfiguration
------------------------

Mit der Grundinstallation werden einige Konfigurationsdateien mitgeliefert die den gleichen Namen
tragen wie die benötigten Dateien aber zusätzlich noch die Endung **.default**.
Wenn SmartHomeNG beim Start eine benötigte Konfigurationsdatei sucht, aber noch keine vorhanden ist,
so wird eine Kopie von der mitgelieferten **.default** Datei erstellt und diese weiter verwendet.
Gelingt dies nicht, so bricht SmartHomeNG beim Start ab.

Es werden für einen Systemstart folgende Konfigurationsdateien benötigt:

- **smarthome.yaml**
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
   dem Logikeditor im Backend Plugin oder dem Logikeditor im Admin diese Logiken zur Laufzeit neu
   zu laden.)

Im folgenden werden diese Dateien und deren Inhalt genauer beschrieben.

smarthome.yaml
~~~~~~~~~~~~~~

In der **smarthome.yaml** stehen die allgemeinen Konfigurationseinstellungen der SmartHomeNG Installation, wie z.B. die
Koordinaten des Standortes. Die Koordinaten werden benötigt um unter anderem Sonnenaufgang / -untergang zu berechnen.
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
~~~~~~~~~~~~

In der **logging.yaml** finden sich die Anweisungen, wie Ereignisse die während des Programmablaufes von
SmartHomeNG auftreten geloggt also notiert werden sollen.

Diese recht umfangreiche Datei sollte zunächst nicht geändert werden. Später kann sie angepaßt werden um
komplexe Ausführungsketten detailliert zu untersuchen.

Zunächst ist wichtig, das in der Grundkonfiguration zwei Dateien erzeugt werden:

- ./var/log/smarthome-warnings.log und
- ./var/log/smarthome-details.log

In der ersten Datei findet man nach dem ersten Start von SmartHomeNG etwas ähnliches wie folgende Informationen:

.. code-block:: bash

   YYYY-MM-dd  hh:mm:ss WARNING  __main__            --------------------   Init SmartHomeNG 1.6  --------------------
   YYYY-MM-dd  hh:mm:ss WARNING  __main__            Running in Python interpreter 'v3.5.3 final' (pid=????) on linux platform
   YYYY-MM-dd  hh:mm:ss WARNING  plugins.cli         CLI: You should set a password for this plugin.
   YYYY-MM-dd  hh:mm:ss WARNING  lib.item            load_itemdefinitions(): For testing the joined item structs are saved to /usr/local/smarthome/etc/structs_joined.yaml

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

In der Zweiten Datei finden sich zusätzliche Informationen die für die Erstkonfiguration die hier beschrieben wird nicht entscheidend sind.

Da nach dem ersten Start von SmartHomeNG ohnehin die default Datei übernommen wird, ist hier kein Handlungsbedarf etwas anzupassen.

plugin.yaml
~~~~~~~~~~~

In der **plugin.yaml** stehen die Plugins die verwendet werden sollen, sowie ihre Konfigurationsparameter.

Wenn keine Datei **plugin.yaml** existiert, wird beim ersten Start von SmartHomeNG die mitgelieferte Datei **plugin.yaml.default**
kopiert. In dieser Datei ist ein minimaler Set von Plugins konfiguriert, so dass z.B. per Browser oder mit der smartVISU auf die
SmartHomeNG Instanz zugegriffen werden kann.

.. code-block:: yaml

   %YAML 1.1
   ---
   BackendServer:
       plugin_name: backend
       #updates_allowed: False

   cli:
       plugin_name: cli
       ip: 0.0.0.0
       #port: 2323
       update: True
       #hashed_password: 1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c48337$

   # Bereitstellung eines Websockets zur Kommunikation zwischen SmartVISU und SmartHomeNG
   websocket:
       plugin_name: visu_websocket
       #ip: 0.0.0.0
       #port: 2424
       #tls: no
       #wsproto: 4
       #acl: rw

   # ... etc.

Die Konfiguration weiterer Plugins ist auskommentiert vorhanden, um die Nutzung
dieser Plugins möglichst einfach zu gestalten.

Wenn man jetzt bereits weiß, welche Plugins man benötigt, dann kann die default-Datei als Arbeitsgrundlage dienen
und die benötigten Plugins können aktiviert werden.
Alternativ kann die Konfiguration auch später über das Admin Interface stattfinden.

Jedes Plugin kann weitere Abhängigkeiten von Bibliotheken mit sich bringen. Diese sind einzeln zu installieren mit

.. code-block:: bash

   cd /usr/local/smarthome
   sudo pip3 install -r plugins/<plugin-name-hier-einsetzen>/requirements.txt

.. note::

   Beim Start von SmartHomeNG wird die Datei **requirements/all.txt** erstellt.

   Es kann allerdings dann zu einem Abbruch des Starts von SmartHomeNG kommen, da beim Start automatisch nur die beiden
   Requirements-Dateien erstellt werden. Die benötigten Python Packages werden dabei nicht automatisch installiert, da
   hierzu erweiterte Rechte (sudo) benötigt werden.
   
   Es lassen sich über diese Datei zwar sämtliche benötigten Abhängigkeiten installieren, jedoch rät das Entwicklungsteam
   ausdrücklich davon ab alle Abhängigkeiten zu installieren.


logic.yaml
~~~~~~~~~~

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

Da derzeit noch keine Logiken benötigt werden, ist auch hier kein Handlungsbedarf zum Editieren. SmartHomeNG erstellt auch hier aus der default-Datei eine logic.yaml.

module.yaml
~~~~~~~~~~~

In dieser Datei sind Module konfiguriert, die von Plugins benötigt werden aber dennoch nicht zur Kernfunktionalität von SmartHomeNG gehören.
Für die Grundkonfiguration ist dies das http Modul, das z.B. vom backend oder dem admin Interface genutzt wird.

Auch hier ist kein Handlungsbedarf, die Beschreibung ist ebenfalls der Vollständigkeit halber enthalten.


SmartHomeNG starten
-------------------

Nachdem die Grundlagen für den Betrieb des Kerns von SmartHomeNG nun beschrieben sind, kann SmartHomeNG erstmalig gestartet werden:

.. code-block:: bash

   cd /usr/local/smarthome
   python3 bin/smarthome.py

Wie zuvor beschrieben werden nun Konfigurationsdateien eingelesen und bei Bedarf auf den defaults übernommen.
Auf der Shell (Konsole, Kommandozeile) sollte jetzt nur eine Zeile erscheinen wie:

.. code-block:: bash

   Daemon PID ????

Das bedeutet, das SmartHomeNG nun im Hintergrund läuft und unter der Prozess ID ``????`` bekannt ist. Auch über den Shell Befehl

.. code-block:: bash

   sudo ps ax | grep smarthome

sollte eine Zeile augegeben werden mit

.. code-block:: bash

   ???? ?        Sl     0:01 python3 bin/smarthome.py

.. note::

   SmartHomeNG kann zur Zeit nur ein einziges Mal auf einem Rechner ausgeführt werden. Versucht man dies mehrfach,
   so kann die Version die als letztes gestartet wurde oft keine Netzwerkverbindungen aufbauen.
   Ein solcher Fall kann schnell auftreten, wenn SmartHomeNG als Daemon eingerichtet wird und aber zusätzlich ein Start
   von der Kommandozeile erfolgt.


Admin Interface
~~~~~~~~~~~~~~~
   
Viele Einstellungen in den Konfigurationsdateien, die manuell mit dem Editor ausgeführt werden, sind bereits über das
Admin Interface möglich.

Unter ``System --> Konfiguration --> Allgemein`` lassen sich die Inhalte der ``smarthome.yaml`` ändern sowie unter
``System --> Konfiguration --> Http Modul`` und ``System --> Konfiguration --> Admin Modul`` die Zugangsdaten und Parameter
für Webserver und Admin Interface ändern. Die Änderungen müssen explizit gesichert werden und anschließend
muß über ``Core neu starten`` ein Neustart von SmartHomeNG initiiert werden.

Unter ``Plugins --> Konfiguration --> Plugin hinzufügen`` lassen sich Plugins hinzufügen und konfigurieren. An gleicher Stelle
können sie auch ausgeschaltet oder gelöscht werden. Auch hier gilt das nach Änderungen SmartHomeNG neu gestartet werden muß damit die
Änderungen wirksam werden.

Auch wichtig ist ``Logs --> Logs anzeigen`` denn hier lassen sich die letzten Logdateien bequem untersuchen auf Auffälligkeiten.
Sollte es sein, das hier steht ``FILE NOT FOUND!`` so ist es sehr wahrscheinlich, das SmartHomeNG gerade neu startet oder aber
wegen einer Fehlkonfiguration oder einer fehlenden Bibliothek nicht gestartet werden kann.
In diesem Fall sollte man sich z.B. die letzten 50 Einträge der Logdatei unter ``/usr/local/smarthome/var/log/smarthome-warnings.log``
auf der Shell anzeigen lassen mit ``tail -n 50 /usr/local/smarthome/var/log/smarthome-warnings.log``.




