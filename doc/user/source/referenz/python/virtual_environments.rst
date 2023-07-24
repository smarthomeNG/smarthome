
.. index:: Virtual Python Environments
.. index:: Virtuelle Umgebungen

.. role:: bluesup
.. role:: greensup
.. role:: redsup

===============================================
Virtuelle Python Environments :bluesup:`Update`
===============================================

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
gespeichert. Außer den virtuallen Environments enthält das Verzeichnis auch Skripte zur Verwaltung der
virtuellen Environments.

Das postinstall Skript der SmartHomeNG Installation nimmt dieses Verzeichnis in den Pfad auf, so dass die Skripte
ohne Pfadangabe aufgerufen werden können.

|

Installation von venv bzw. virtualenv
=====================================

**venv** bzw. **virtualenv** wird am besten unter der Python Version installiert, für die später virtuelle
Environments erstellt werden sollen. (**venv** ist bei aktuellen Distributionen bereits auf dem System installiert)
Um zum Beispiel ein virtual Environment für Python 3.10 zu erstellen, ist der folgende Befehl auszuführen:

.. code-block:: bash

    $ pip3.10 install venv

bzw.

.. code-block:: bash

    $ pip3.10 install virtualenv

|

Erstellung von virtuellen Environments
======================================

Jetzt kann mit dem folgenden Befehl ein virtual Environment erstellt werden, welches den Namen **py_3.10** trägt:

.. code-block:: bash

    $ make_env 3.10

Während der Anlage wird das Environment aktiviert, um einige norwendige Python Packages in das Environment zu
installieren bzw. zu aktualisieren.

|

Das Environment wird mit dem Kommando

.. code-block:: bash

    $ source act 3.10

aktiviert.

In dem Environment sind nun nur die Packages **pip**, **setuptools** und evtl. **wheel** installiert. Weitere benötigte
Packages können ganz normal mit **pip3** nachinstalliert werden. (SmartHomeNG installiert wie bei einer kompletten
Neuinstallation die benötigten Packages).

Der Aufruf von

.. code-block:: bash

    (py_3.10) $ python3

führt nun dazu, dass Python 3.10 gestartet wird.

Um das virtuelle Environment zu deaktivieren, muss nur

.. code-block:: bash

    (py_3.10) $ deactivate

eingegeben werden.

|

Löschen eines virtuellen Environment
====================================

Wenn ein virtuelles Environment nicht mehr benötigt wird, wird einfach das entsprechende Verzeichnis rekirsiv gelöscht.
Bitte darauf achten, dass das Environment nicht aktiv ist. Bei Bedarf vor dem Löschen mit dem Befehl ``deactivate``
deaktivieren.

.. code-block:: bash

    $ cd /usr/local/smarthome/venvs
    $ rm -r py_3.10

|

.. index:: Virtuelle Environements als Dienst

Virtuelle Environements als Dienst
==================================

Wenn SmartHomeNG als Dienst eingerichtet werden und in einem virtuellen Environment laufen soll, muss die xxx-Datei
im Vergleich zur Beschreibung in der Komplettanleitung abgeändert werden. Es muss der Pfad zu Python in dem entsprechenden
Environment angegeben werden.

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
   ExecStart=/usr/local/smarthome/venvs/py_310/bin/python3 /usr/local/smarthome/bin/smarthome.py
   WorkingDirectory=/usr/local/smarthome
   User=smarthome
   PIDFile=/usr/local/smarthome/var/run/smarthome.pid
   Restart=on-failure
   TimeoutStartSec=900
   RestartForceExitStatus=5

   [Install]
   WantedBy=default.target
