
.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup


=====================================================
Entwicklungsrichtlinien :bluesup:`under construction`
=====================================================

Im folgenden werden eine Hilfen und Richtlinien beschrieben, die wichtig sind, wenn das zu erstellende Plugin in
das globale Repository von SmartHomeHG aufgenommen werden soll.

|

Nutzung von git und GitHub
==========================

Eine recht umfassende Einführung (in englischer Sprache) in git ist auf `gitimmersion.com <https://gitimmersion.com>`_
zu finden.

Wenn das Plugin veröffentlicht werden soll, ist es sinnvoll so schnell wie möglich ein
`Konto auf github.com <https://github.com/users>`_ zu erstellen.

Falls die Kommandozeilenversion der Git-Software zu komplex erscheint, ist **SourceTree** von Atlassian eine gute
Client Software mit graphischer Oberfläche. Alternativ kann auch auf **GitHub Desktop** zurück gegriffen werden.
Beide Tools sind kostenlos erhältlich.

|

Die Repositories von SmartHomeNG
================================

Der Code von SmartHomeNG ist in zwei Repositories auf github.com gespeichert.

* **smarthomeNG/smarthome** enthält den Core von SmartHomeNG
* **smarthomeNG/plugins** enthält alle Plugins, die mit SmartHomeNG veröffentlicht werden.


Repositories und Branches
-------------------------

Jedes Repositry enthält mindestens zwei Branches:

  * **master**: enthält den stabilen Code, also die Releases von SmartHomeNG
  * **develop**: ist der Branch in dem die Entwicklung stattfindet, in den also neue Features und Plugins
    gemerged werden

Das Setup der Branches basiert auf `diesem Modell <https://nvie.com/posts/a-successful-git-branching-model/>`_

Eine ausführliche Beschreibung zur Nutzung des Workflows für SmartHomeNG findet sich
`[hier im Wiki <https://github.com/smarthomeNG/smarthome/wiki/Git-Workflow%28s%29-für-SmartHomeNG>`_


Getting the Source
------------------

  * you could fork the repository on GitHub or
  * get the repository: `git clone --recursive https://github.com/smarthomeNG/smarthome.git` (The --recursive option ensures, that a version of the plugins are checked out as well)
  * create your own (local) branch (from develop) `git checkout -b myplugin develop`

|

Code Stil
=========

Der Code sollte `pep 8 <https://www.python.org/dev/peps/pep-0008/>`_ entsprechen.
(Es ist ok den Fehler „E501-Zeile zu lang“ zu ignorieren.)

|

Start Coding
============

   * **copy** the sample plugin directory: `cp -r dev/sample_plugin plugins/myplugin`
   * **edit** the main file: `vi plugins/myplugin/__init__.py`


Tools
-----

Have a look at the following tools to test your code:


pep8
~~~~

   * Install pep8: `apt-get install pep8`
   * Test your code: `pep8 -qq --statistics yourcode.py`


autopep8
~~~~~~~~

   * `pip3 install autopep8`
   * `autopep8 yourcode.py -i`


flake8
~~~~~~

   * `pip3 install flake8`
   * `flake8 yourcode.py`

It can be used as a vim plugin. It checks the code every time I save the file. Most usefull!


Testen und Dokumentieren
------------------------

Bitte den Code des Plugins ausgiebig testen und dokumentieren!

In Ihrem Plugin-Verzeichnis sollte sich eine Datei **user_doc.rst** (aus dem Verzeichnis „sample_plugin“) befinden.
Bitte diese Datei mit die notwendigen Informationen befüllen. ``viplugins/myplugin/user_doc.rst``

Methoden und Funktionen sollten mit einem Docstring versehen werden, der den Zweck der Methode/Funktion, die
Aufrufparameter und den Rückgabewert beschreibt.

Weiterhin ist es sinnvoll **Unittests** für das Plugin zu erstellen.


Basic Rules
-----------

   * **only push to the develop branch**
   * changes to contents of the smarthomeNG/smarthome repository must be checked with the SmartHomeNG developer team.
   * changes to plugins from other developers must be checked with the developer.


Fork (description is deprecated, has to be updated)
---------------------------------------------------

   * Goto [SmartHome Repo](https://github.com/smarthomeNG/smarthome) logged in with your username/password.
   * Click on 'fork' in the right upper corner.
   * Change to your Terminal and enter `git clone https://USER:PASSWORD@github.com/USER/smarthome`
   * Checkout the develop branch `git checkout develop`
   * Change/create a file.
   * Add the file `git add FILE`
   * Commit the changes with a usefull comment: 'git commit'
   * Push your changes to your repository: `git pull && git push`
   * Create a pull request on GitHub: base: smarthomeNG/develop  compare: USER/develop


Merge (description is deprecated, has to be updated)
----------------------------------------------------

If you think your code is ready for prime time send me a **pull request via github**

Acitve commiters could merge the myplugin branch into develop with:

   * **chang** the active branch to develop: `git checkout develop`
   * **merge** your plugin into it: `git merge --no-ff myplugin`
   * (delete your branch: `git branch -d myplugin`)
   * **pusg** to github: `git push origin develop`


.git/config (description is deprecated, has to be updated)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Falls Probleme beim pushen auf GitHub bestehen, bitte die **config**-Datei im **.git** Verzeichnis überprüfen.
Sie sollte zum Beispiel folgendermaßen aussehen:

.. code-block:: ini

    [remote "origin"]
        url = https://github.com/smarthomeNG/smarthome
        fetch = +refs/heads/*:refs/remotes/origin/*

    [branch "master"]
        remote = origin
        merge = refs/heads/master

    [branch "develop"]
        remote = origin
        merge = refs/heads/develop

Falls der Code für GitHub verifizierbar signiert werden soll, muss noch die gpg Signierung auf GitHub und in der
Entwicklungsumgebung konfiguriert sein. In dem Fall gibt es noch die beiden folgenden Abschnitte in der git
**config**-Datei:

.. code-block:: ini

    [commit]
        gpgSign = true
    [user]
        signingkey = xxxxxxxxxxxxxxxx


Working with the git commandline client
---------------------------------------

Here are a few tips, if you are working with the commandline client of git:


Useful git commands
~~~~~~~~~~~~~~~~~~~

   * **list changes** since the release with the tag VERSIONTAG: `git log --pretty=format:"%s" <VERSIONTAG>..HEAD`
   * **undo commit** with the id XXXIDXXX: `git reset --hard XXXIDXXX && git push origin develop --force`
   * **copy commit** to current branch: `git cherry-pick <commit>`

   Follow the [commit Atom Feed](https://github.com/smarthomeNG/smarthome/commits/develop.atom)


Global settings
~~~~~~~~~~~~~~~

   * only push the current branch (not all): `git config --global push.default current`
   * adapt your user settings:
      * `git config --global user.name "Your Name"`
      * `git config --global user.email you@example.com`

