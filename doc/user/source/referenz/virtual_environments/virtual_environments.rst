
====================
Virtual Environments
====================

Virtual Environments sind isolierte und unabhängige Umgebungen, die den Code und die Abhängigkeiten eines Projekts
enthalten.

Mit virtuellen Environments kann man parallel Umgebungen schaffen, in denen zum Beispiel Python Packages in
unterschiedlichen Versionen installiert sind.

Falls auf dem Computer mehrere Python Versionen installiert sind, ist es auch möglich parallel Umgebungen zu
schaffen, die unter unterschiedlichen Python Versionen laufen. Dieses ist besonders hilfreich, wenn man bei der
Entwicklung von SmartHomeNG oder von Plugins testen möchte, wie sich SmartHomeNG (bzw. das Plugin) unter verschiedenen
Python Versionen verhält.

Es gibt eine Reihe von Tools, um virtuelle Environments zu erstellen. Die verbreitetesten Tools sind **virtualenv**
und **venv**.

**venv** gibt es seit Python 3.3. Es ist Bestandteil der Python Installation. Allerdings ist es in
einigen Umgebungen (z.B. Debian) nicht in der Standard Python Installation enthalten und muss dann separat installiert
werden.

**virtualenv** bietet eine größere Funktionalität als **venv**. Die Funktionalität von **venv** ist eine Untermenge
der Funktionalität von **virtualenv**. **virtualenv** ist Vergleich zu **venv** schneller und es ist erweiterbar.

|

Installation von virtualenv
===========================

Im folgenden wird davon ausgegangen, dass die Environments im Unterverzeichnis **environments** des Users **smarthome**
erstellt/gespeichert werden.

.. code-block:: bash

    smarthome@SmartHomeNG:~$ mkdir environments

    smarthome@SmartHomeNG:~$ cd environments

    smarthome@SmartHomeNG:~/environments$


**virtualenv** wird am besten unter der Python Version installiert, für die später virtuelle Environments erstellt
werden sollen. Um zum Beispiel ein virtual Environment für Python 3.9 zu erstellen, ist der folgende Befehl auszuführen:

.. code-block:: bash

    smarthome@SmartHomeNG:~/environments$ pip3.9 install virtualenv

|

Erstellung von virtual Environments
===================================

Jetzt kann mit dem folgenden Befehl ein virtual Environment erstellt werden, welches den Namen **py_39** trägt:

.. code-block:: bash

    smarthome@SmartHomeNG:~/environments$ python3.9 -m virtualenv py_39

Jetzt sollte noch ein Shell Skript angelegt werden, mit dem das Environment aktiviert werden kann. Für das Environment
**py_39** sollte es **act_39** heissen und kann mit:

.. code-block:: bash

    smarthome@SmartHomeNG:~/environments$ nano act_39

angelegt werden und der folgende Text kann dort eingefügt werden:

.. code-block:: bash
    :caption: act_39

    #!/bin/bash
    #
    # Environment erzeugt mit:
    #   $ pip3.9 install virtualenv
    #   $ python3.9 -m virtualenv py_39
    #
    # Aktivieren mit:
    #  $ source act_39
    #
    # Deaktivieren mit:
    #   $ deactivate
    #


Anschließend nicht vergessen, das Skript ausführbar zu machen.

.. code-block:: bash

    smarthome@SmartHomeNG:~/environments$ chmod +x act_39

Nun kann mit dem Aufruf von

.. code-block:: bash

    smarthome@SmartHomeNG:~/environments$ source act_39
    (py_39) smarthome@SmartHomeNG:~/environments$

das Environment aktiviert werden. Das **source** ist wichtig, weil das Environment sonst bei Beendigung der
Skriptes **act_39** wieder beendet wird. Der geänderte Prompt zeigt an, dass das Virtual Environment **py_39**
aktiv ist. Bitte daran denken, den Pfad mit anzugeben, falls das aktuelle Verzeichnis nicht **environments ist:

.. code-block:: bash

    smarthome@SmartHomeNG:/usr/local/smarthome$ source /home/smarthome/environments/act_39

|

In dem Environment sind nun nur die Packages **pip**, **setuptools** und **wheel** installiert. Weitere benötigte
Packages können ganz normal mit **pip3** nachinstalliert werden. (SmartHomeNG installiert wie bei einer kompletten
Neuinstallation die benötigten Packages).

Der Aufruf von

.. code-block:: bash

    (py_39) smarthome@SmartHomeNG:~$ python3

führt nun dazu, dass Python 3.9 gestartet wird.

Um das virtuelle Environment zu deaktivieren, muss nur

.. code-block:: bash

    (py_39) smarthome@SmartHomeNG:~$ deactivate
    smarthome@SmartHomeNG:~$

eingegeben werden.

