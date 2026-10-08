
.. index:: Virtual Python Environments
.. index:: Virtuelle Umgebungen

.. role:: bluesup
.. role:: greensup
.. role:: redsup

=============================
Virtuelle Python Environments
=============================

Virtual Environments sind isolierte und unabhängige Umgebungen, die den Code und die Abhängigkeiten eines Projekts
enthalten. Mit virtuellen Environments kann man parallel Umgebungen schaffen, in denen zum Beispiel Python Packages in
unterschiedlichen Versionen installiert sind.

Falls auf dem Computer mehrere Python Versionen installiert sind, ist es auch möglich parallel Umgebungen zu
schaffen, die unter unterschiedlichen Python Versionen laufen. Dieses ist besonders hilfreich, wenn man bei der
Entwicklung von SmartHomeNG oder von Plugins testen möchte, wie sich SmartHomeNG (bzw. das Plugin) unter verschiedenen
Python Versionen verhält.

Es gibt eine Reihe von Tools, um virtuelle Environments zu erstellen. Die verbreitetesten Tools sind **virtualenv**
und **venv**.

**venv** gibt es seit Python 3.3. Es ist Bestandteil der Python Installation. Allerdings ist es in
einigen Umgebungen (z.B. älteren Debian Distributionen) nicht in der Standard Python Installation enthalten
und muss dann separat installiert werden.

**virtualenv** bietet eine größere Funktionalität als **venv**. Die Funktionalität von **venv** ist eine Untermenge
der Funktionalität von **virtualenv**. **virtualenv** ist Vergleich zu **venv** schneller und es ist erweiterbar.
Für den Einsatz im Kontext von SmartHomeNG wird diese größere Funktionalität jedoch nicht benötigt.

Da **venv** Teil der Python Distribution ist, wird empfohlen diesem den Vorzug vor **virtualenv** zu geben. Im
Folgenden wird auch nur vom Einsatz von **venv** ausgegangen.

|

Die virtuellen Environments werden standardmäßig im Unterverzeichnis ``venvs`` des SmartHomeNG Basisverzeichnises
gespeichert. Die Skripte zur Verwaltung der virtuellen Environments (``make_venv``, ``act``) liegen im Verzeichnis
``tools``.

Das ``tools/postinstall`` Skript der SmartHomeNG Installation nimmt sowohl ``tools`` als auch ``venvs`` in den Pfad
auf, so dass die Skripte ohne Pfadangabe aufgerufen werden können.

|

Installation von venv bzw. virtualenv
=====================================

**venv** ist ein Modul der Python Standardbibliothek und wird nicht mit ``pip`` installiert. Auf Debian und Ubuntu
ist es in einem separaten Paket enthalten, das (falls nicht schon durch die Komplettanleitung geschehen) mit

.. code-block:: bash

    $ sudo apt-get install python3-venv

installiert wird. Es muss zu der Python Version passen, für die später virtuelle Environments erstellt werden
sollen.

**virtualenv** ist für SmartHomeNG nicht nötig. Falls es trotzdem genutzt werden soll, wird es mit ``pip`` installiert:

.. code-block:: bash

    $ pip3.13 install virtualenv

|

Erstellung von virtuellen Environments
======================================

Jetzt kann mit dem folgenden Befehl ein virtual Environment für Python 3.13 erstellt werden, welches den Namen
**py_shng3.13** trägt:

.. code-block:: bash

    $ make_venv 3.13 shng3.13

Der erste Parameter ist die Python Version, mit der das Environment erstellt wird, der zweite der frei wählbare Name
des Environments (das Verzeichnis heißt ``py_<Name>``). Es wird empfohlen, den Namen unabhängig von der Python Version
zu wählen (hier: ``shng`` plus Python Version), damit Environment und Python Version nicht verwechselt werden und
mehrere Environments mit unterschiedlichen Python Versionen nebeneinander bestehen können.

Während der Anlage wird das Environment aktiviert, um einige norwendige Python Packages in das Environment zu
installieren bzw. zu aktualisieren.

|

Das Environment wird mit dem Kommando

.. code-block:: bash

    $ source act shng3.13

aktiviert.

In dem Environment sind nun nur die Packages **pip**, **setuptools** und evtl. **wheel** installiert. Weitere benötigte
Packages können ganz normal mit **pip3** nachinstalliert werden. (SmartHomeNG installiert wie bei einer kompletten
Neuinstallation die benötigten Packages).

Der Aufruf von

.. code-block:: bash

    (py_shng3.13) $ python3

führt nun dazu, dass Python 3.13 gestartet wird.

Um das virtuelle Environment zu deaktivieren, muss nur

.. code-block:: bash

    (py_shng3.13) $ deactivate

eingegeben werden.

|

Neue Installation mit eigenem Environment
=========================================

Eine neue SmartHomeNG Installation (z.B. eine zweite Installation zum Testen, in einem anderen Verzeichnis) bekommt ein
eigenes Environment. Beispiel für die Installation in ``/usr/local/shng2`` mit Python 3.13:

.. code-block:: bash

    $ git clone https://github.com/smarthomeNG/smarthome.git /usr/local/shng2
    $ git clone https://github.com/smarthomeNG/plugins.git /usr/local/shng2/plugins
    $ cd /usr/local/shng2
    $ bash tools/make_venv 3.13 shng3.13
    $ source tools/act shng3.13
    (py_shng3.13) $ python3 bin/smarthome.py

``make_venv`` legt das Environment in ``venvs/py_shng3.13`` der jeweiligen Installation an, ``act`` aktiviert es.
Beide Skripte beziehen sich auf die Installation, in der sie liegen, auch wenn sie mit Pfad aufgerufen werden.

.. note::

    Das Skript ``tools/postinstall`` aus der Komplettanleitung erzeugt ebenfalls ein Environment, trägt aber
    zusätzlich ``PATH`` und ``source act shng`` in die ``~/.bashrc`` ein - und zwar nur, wenn dort noch kein Eintrag
    vorhanden ist. Bei einer zweiten Installation unter demselben Benutzer ist deshalb ``make_venv`` direkt
    aufzurufen, damit die ``~/.bashrc`` der ersten Installation unverändert bleibt.

Ein Environment kann auch ohne ``make_venv`` mit ``python3 -m venv <Verzeichnis>`` an beliebiger Stelle angelegt
werden. Entscheidend ist nur, dass SmartHomeNG mit dem ``python3`` aus diesem Environment gestartet wird (nach
``source <Verzeichnis>/bin/activate`` oder mit vollem Pfad ``<Verzeichnis>/bin/python3 bin/smarthome.py``).

Beim ersten Start legt SmartHomeNG fehlende Konfigurationsdateien (``smarthome.yaml``, ``logging.yaml``,
``plugin.yaml``, ``module.yaml``, ``logic.yaml``, ``admin.yaml``, ``holidays.yaml``) im Verzeichnis ``etc``
aus den Vorlagen ``templates/*.default`` an.

|

Wie SmartHomeNG das Environment nutzt
=====================================

SmartHomeNG prüft beim Start, ob die benötigten Python Packages installiert sind, und installiert fehlende
Packages selbst. Für ein Environment gilt dabei:

* **Welches pip:** Es wird das ``pip3`` aus dem Verzeichnis des Python Interpreters verwendet, mit dem SmartHomeNG
  gestartet wurde. Läuft SmartHomeNG im Environment, landen die Packages also im Environment.
* **Core Requirements:** Diese werden geprüft, bevor ``etc/smarthome.yaml`` gelesen wird. Fehlen Packages, werden sie
  installiert und SmartHomeNG startet sich anschließend neu. Der Pfad zum pip Kommando kann hierfür nur über den
  Kommandozeilenparameter ``-p`` / ``--pip3_command`` vorgegeben werden.
* **Module und Plugins:** Danach werden die Requirements der Module und der konfigurierten Plugins geprüft und
  gegebenenfalls installiert. Für diese Installationen wird ein Eintrag ``pip_command`` in ``etc/smarthome.yaml``
  berücksichtigt.
* **Option ``--user``:** In einem Environment ruft SmartHomeNG pip ohne ``--user`` auf, da pip diese Option dort
  ablehnt. Außerhalb eines Environments wird ``--user`` verwendet. Das pip Protokoll steht in
  ``var/log/pip3_outout.log`` und ``var/log/pip3_error.log``.
* **Requirements Dateien:** Die Dateien in ``requirements/`` (z.B. ``core.txt``, ``base.txt``, ``all.txt``) werden bei
  Bedarf aus den ``requirements.txt`` des Cores, der Module und der Plugins erzeugt (siehe
  :doc:`/tools/tools_build_requirements`) und nicht von Hand bearbeitet.

|

Löschen eines virtuellen Environment
====================================

Wenn ein virtuelles Environment nicht mehr benötigt wird, wird einfach das entsprechende Verzeichnis rekirsiv gelöscht.
Bitte darauf achten, dass das Environment nicht aktiv ist. Bei Bedarf vor dem Löschen mit dem Befehl ``deactivate``
deaktivieren.

.. code-block:: bash

    $ cd /usr/local/smarthome/venvs
    $ rm -r py_shng3.13

|

.. index:: Virtuelle Environements als Dienst

Virtuelle Environements als Dienst
==================================

Wenn SmartHomeNG als Dienst eingerichtet werden und in einem virtuellen Environment laufen soll, muss die
``smarthome.service`` Datei im Vergleich zur Beschreibung in der Komplettanleitung abgeändert werden. Es muss der
Pfad zu Python in dem entsprechenden Environment angegeben werden.

Zum Einrichten den Texteditor starten mit

.. code-block:: bash

   sudo nano /etc/systemd/system/smarthome.service

und folgenden Text hineinkopieren:

.. code-block:: bash

   [Unit]
   Description=SmartHomeNG daemon
   After=network.target
   After=knxd.service
   After=knxd.socket

   [Service]
   Type=forking
   ExecStart=/usr/local/smarthome/venvs/py_shng3.13/bin/python3 /usr/local/smarthome/bin/smarthome.py
   WorkingDirectory=/usr/local/smarthome
   User=smarthome
   PIDFile=/usr/local/smarthome/var/run/smarthome.pid
   Restart=on-failure
   TimeoutStartSec=900
   RestartForceExitStatus=5

   [Install]
   WantedBy=default.target
