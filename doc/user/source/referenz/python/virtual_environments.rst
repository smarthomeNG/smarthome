
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

Da **venv** Teil der Python Distribution ist, wird empfohlen diesem den Vorzug vor **virtualenv** zu geben.

|

Die virtuellen Environments sollten in einem Unterverzeichnis zum Home Verzeichnis des Users **smarthome**
gespeichert werden. Dieses Verzeichnis sollte zur einfacheren Handhabung der virtuellen Environments in
den PATH aufgenommen werden.

Empfohlen  wird das Verzeichnis **environments** zu nennen.


.. code-block:: bash

    $ mkdir ~/environments

Zur Anlage eines Environments muss diese Verzeichnis das aktuelle Arbeitsverzeichnis sein.


.. code-block:: bash

    $ cd ~/environments

|

Installation von venv bzw. virtualenv
=====================================

Im folgenden wird davon ausgegangen, dass die Environments im Unterverzeichnis **environments** des Users **smarthome**
erstellt/gespeichert werden.

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

Jetzt kann mit dem folgenden Befehl ein virtual Environment erstellt werden, welches den Namen **py_310** trägt:

.. code-block:: bash

    $ cd ~/environments
    $ python3.10 -m venv py_310

|

Das Environment wird mit dem Kommande

.. code-block:: bash

    $ source /home/smarthome/environments/py_310/bin/activate
    (py_310) $

aktiviert. Eine Vereinfachung des Aufrufes ist weiter unten beschrieben.

In dem Environment sind nun nur die Packages **pip**, **setuptools** und evtl. **wheel** installiert. Weitere benötigte
Packages können ganz normal mit **pip3** nachinstalliert werden. (SmartHomeNG installiert wie bei einer kompletten
Neuinstallation die benötigten Packages).

Der Aufruf von

.. code-block:: bash

    (py_310) $ python3

führt nun dazu, dass Python 3.10 gestartet wird.

Um das virtuelle Environment zu deaktivieren, muss nur

.. code-block:: bash

    (py_310) $ deactivate
    $

eingegeben werden.

|

Vereinfachtes Aktivieren der Environments
=========================================

Die Aktivierung der eingerichteten virtuellen Environments kann vereinfacht werden, wenn ein Skript mit dem Namen
**act** und dem folgenden Inhalt im Verzeichnis **environments** angelegt wird.

.. code-block:: bash

    #!/bin/bash

    # test if script is called with 'source'
    (return 0 2>/dev/null) && sourced=1 || sourced=0

    if [ "$sourced" -eq "0" ]; then
        echo
        echo ERROR: The script MUST be called with \'source\', like: \'source act $1\'
        echo
        exit
    fi

    if test -f "/home/smarthome/environments/py_$1/bin/activate"; then
        echo
        source /home/smarthome/environments/py_$1/bin/activate
        echo "Activating virtual environment py_$1 (`python3 -V`)"
        echo
        echo To deactivate the virtual environment simply type the command \'deactivate\'
    else
        echo
        echo "ERROR: Virtual environment py_$1 does not exist"
    fi
    echo

Anschließend nicht vergessen das Skript mit ``chmod 775 act`` ausführbar zu machen.

Nun kann ein existierendes Environment (z.B, py_39) einfach mit dem Befehl ``source act 39`` aktiviert werden.
Das Verzeichnis ``/home/smarthome/environments`` sollte in den Pfad aufgenommen werden, damit ``act`` aus jedem
Verzeichnis heraus aufgerufen werden kann, ohne den vollständigen Pfad angeben zu müssen.

Das ``source`` im Aufruf ist wichtig, weil das Environment sonst bei Beendigung der Skriptes ``act`` wieder beendet wird.

Der geänderte Prompt zeigt an, dass das Virtual Environment **py_39** aktiv ist.

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
   ExecStart=/home/smarthome/environments/py_310/bin/python3 /usr/local/smarthome/bin/smarthome.py
   WorkingDirectory=/usr/local/smarthome
   User=smarthome
   PIDFile=/usr/local/smarthome/var/run/smarthome.pid
   Restart=on-failure
   TimeoutStartSec=900
   RestartForceExitStatus=5

   [Install]
   WantedBy=default.target
