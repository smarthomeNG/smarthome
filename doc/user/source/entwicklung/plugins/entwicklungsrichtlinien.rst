
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

Nutzung von git und github
==========================

Eine recht umfassende Einführung (in englischer Sprache) in git ist auf `gitimmersion.com <https://gitimmersion.com>`_
zu finden.

Wenn das Plugin veröffentlicht werden soll, ist es sinnvoll so schnell wie möglich ein
`Konto auf Github.com <https://github.com/users>`_ zu erstellen.

Falls die Kommandozeilenversion der Git-Software zu komplex erscheint, ist SourceTree von Atlassian eine gute Client
Software mit graphischer Oberflächt. Alternativ kann auch auf github-Desktop zurück gegriffen werden. Beide Tools
sind kostenlos erhältlich.


Die Repositories von SmartHomeNG
================================

Repositories and Branches
-------------------------

SmartHomeNG is located in two repositories:

* **smarthomeNG/smarthome** contains the core of SmartHomeNG
* **smarthomeNG/plugins** contains the plugins of SmartHomeNG

Each repositry consist of two main branches:

  * __master__: it contains the stable/release code
  * __develop__: is the branch where new features and plugins are merged into

The branch setup is based on [this model](http://nvie.com/posts/a-successful-git-branching-model/).

A detailed description (in german language) about the way the workflow is used for SmartHomeNG can be found in the [here in the wiki](https://github.com/smarthomeNG/smarthome/wiki/Git-Workflow%28s%29-für-SmartHomeNG)


Getting the Source
------------------

  * you could fork the repository on github or
  * get the repository: `git clone --recursive https://github.com/smarthomeNG/smarthome.git` (The --recursive option ensures, that a version of the plugins are checked out as well)
  * create your own (local) branch (from develop) `git checkout -b myplugin develop`

|

Coding style
============

Your code should conform to [pep 8](http://www.python.org/dev/peps/pep-0008/). (I'm ignoring "E501 line too long".)

|

Start Coding
============

   * __copy__ the sample plugin directory: `cp -r dev/sample_plugin plugins/myplugin`
   * __edit__ the main file: `vi plugins/myplugin/__init__.py`


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

In Ihrem Plugin-Verzeichnis sollte sich eine Datei __user_doc.rst__ (aus dem Verzeichnis „sample_plugin“) befinden.
Bitte diese Datei mit die notwendigen Informationen befüllen. ``viplugins/myplugin/user_doc.rst``

Methoden und Funktionen sollten mit einem Docstring versehen werden, der den Zweck der Methode/Funktion, die
Aufrufparameter und den Rückgabewert beschreibt.


Basic Rules
-----------

   * __only push to the develop branch__
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
   * Create a pull request on github: base: smarthomeNG/develop  compare: USER/develop


Merge (description is deprecated, has to be updated)
----------------------------------------------------

If you think your code is ready for prime time send me a __pull request via github__

Acitve commiters could merge the myplugin branch into develop with:

   * __change__ the active branch to develop: `git checkout develop`
   * __merge__ your plugin into it: `git merge --no-ff myplugin`
   * (delete your branch: `git branch -d myplugin`)
   * __push__ to github: `git push origin develop`


.git/config (description is deprecated, has to be updated)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have problems pushing, you could check the repo git config. Mine looks like this:
<pre>
[remote "origin"]
    url = https://github.com/smarthomeNG/smarthome
    fetch = +refs/heads/*:refs/remotes/origin/*

[branch "master"]
    remote = origin
    merge = refs/heads/master

[branch "develop"]
    remote = origin
    merge = refs/heads/develop
</pre>


