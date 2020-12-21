Virtuelle Umgebungen
====================

Wenn außer SmartHomeNG noch weitere Software mit Python auf dem gleichen System läuft, 
kann es sinnvoll sein die einzelnen Python Umgebungen voneinander zu trennen und eine
virtuelle Umgebung zu nutzen.

Dazu gibt es verschiedene Ansätze. Zwei Artikel in englisch über 
`Pipenv & Virtual Environments <https://docs.python-guide.org/dev/virtualenvs/>`__ und
`Why the Need for Virtual Environments <https://realpython.com/python-virtual-environments-a-primer/>`__ 
sind lesenswert. Eine Übersicht findet sich auf 
`Stackoverflow <https://stackoverflow.com/questions/41573587/what-is-the-difference-between-venv-pyvenv-pyenv-virtualenv-virtualenvwrappe>`__.

Danach werden aktuell (Stand November 2020) empfohlen:

* `Python Packaging <https://packaging.python.org/>`__ -->
  `Pipenv <https://packaging.python.org/tutorials/managing-dependencies/>`__
* `Python.org <Python.org>`__ --> `venv <https://docs.python.org/3/library/venv.html>`__
* `Real Python <https://realpython.com/intro-to-pyenv/>`__ --> `Pyenv <https://github.com/pyenv/pyenv#installation>`__


Venv
----

Venv ist im Standardumfang von Python3 enthalten. Es findet vor allem dann Verwendung, wenn nur ein einziger
Python Interpreter installiert und genutzt werden soll.

Zunächst in den Basisordner von SmartHomeNG wechseln. Dort wird dann eine virtuelle Umgebung mit Namen **env**
erstellt und aktiviert. Pip wird aktualisiert und die Basisabhängigkeiten von SmartHomeNG installiert.

.. code-block:: bash

   cd /usr/local/smarthome                         # Eventuell an anderes Basisverzeichnis anpassen 
   python3 -m venv env
   source env/bin/activate                         # Aktivieren der virtuellen Umgebung für diese Shell
   python3 -m pip install pip --upgrade            # Pip für virtuelle Umgebung aktualisieren
   python3 -m pip install -r requirements/base.txt # Installieren der Bibliotheken für die Basis von SmartHomeNG

Nun sollten die Abhängigkeiten für die Basis von SmartHomeNG erfüllt sein.
Einige Plugins brauchen eventuell weitere Bibliotheken. Jedes Plugin bringt eine eigene 
``requirements.txt`` Datei mit. Die benötigten Bibliotheken können installiert werden mit:

.. code-block:: bash

   cd /usr/local/smarthome                            # Eventuell an anderes Basisverzeichnis anpassen 
   source env/bin/activate                            # Aktivieren der virtuellen Umgebung für diese Shell
   pip install -r plugins/pluginname/requirements.txt # Installieren der Bibliotheken für das Plugin <pluginname>

Es gilt daran zu denken, das es Python Bibliotheken gibt, die weitere Pakete benötigen die nur mit 
apt installiert werden können. In diesem Fall sollte es einen Hinweis in der Readme des Plugins geben.

Jedes mal wenn man SmartHomeNG mit einer virtuellen Umgebung nutzen will,
muß diese in der aktuellen Shell aktiviert werden:

.. code-block:: bash

   cd /usr/local/smarthome                         # Eventuell an anderes Basisverzeichnis anpassen 
   source env/bin/activate                         # Aktivieren der virtuellen Umgebung für diese Shell

Die virtuelle Umgebung kann deaktiviert werden durch den Befehl ``deactivate`` in der aktuellen Shell.

Pyenv
------

Pyenv ist in der Lage mit unterschiedlichen Python Versionen umzugehen. Das ist dann sinnvoll um einen
Code mit verschiedenen Interpretern laufen zu lassen und zu testen.
Da Pyenv nicht im Lieferumfang von Python enthalten ist, muß es extra installiert werden. 
Die Anweisungen und Nutzungsbeschreibung finden sich im `Github Repo <https://github.com/pyenv/pyenv>`__
für das Pyenv Projekt.

Pyenv steht in einer für `Windows portierten Version <https://github.com/pyenv-win/pyenv-win>`__
zur Verfügung. Diese kann sogar mit Pip installiert werden.

Pipenv
------

Pipenv kombiniert Pip mit virtuellen Umgebungen und kann Pyenv automatisch verwenden,
um verschiedene Versionen von Python für jedes Projekt zu installieren und zu verwenden.

Unter `Pipenv: A Guide to the New Python Packaging Tool <https://realpython.com/pipenv-guide/>`__ 
gibt es eine englischsprachige Einführung.



