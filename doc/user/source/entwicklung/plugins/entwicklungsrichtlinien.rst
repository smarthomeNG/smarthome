
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


Die Quellen finden/installieren
-------------------------------

  * Sie können auf GitHub einen Fork der Repositories erstellen

oder

  * Sie holen sich das Repository direkt:

    * ``git clone https://github.com/smarthomeNG/smarthome.git .``
    * ``git clone https://github.com/smarthomeNG/plugins.git plugins``

  * Sie erstellen Ihren eigenen (lokalen) Branch (von Develop):

    ``git checkout -b myplugin Develop``

|


Code Stil
=========

Der Code sollte `pep 8 <https://www.python.org/dev/peps/pep-0008/>`_ entsprechen.
(Es ist ok den Fehler „E501-Zeile zu lang“ zu ignorieren.)

|


Programmieren beginnen
======================

  * **Kopieren** Sie das Beispiel-Plugin-Verzeichnis: ``cp -r dev/sample_pluginplugins/myplugin``
  * **Bearbeiten** Sie die Hauptdatei: `vi plugins/myplugin/__init__.py`


Tools
-----

Schauen Sie sich die folgenden Tools an, um Ihren Code zu testen:


pep8
~~~~

   * Pep8 installieren: ``apt-get install pep8``
   * Testen Sie Ihren Code: ``pep8 -qq –statistics yourcode.py``


autopep8
~~~~~~~~

   * ``pip3 install autopep8``
   * ``autopep8 yourcode.py -i``


flake8
~~~~~~

   * ``pip3 install flake8``
   * ``flake8 yourcode.py``

flake8 kann als Vim-Plugin verwendet werden. Der Code wird jedes Mal überprüft, wenn die Datei gespeichert wird.


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

   * Nur Pull Requests gegen den **develop Branch** des jeweiligen Repositories stellen
   * Änderungen an Inhalten des smarthomeNG/smarthome-Repositorys müssen mit dem SmartHomeNG-Entwicklerteam
     (möglichst vor der Entwicklung) abgeklärt werden.
   * Änderungen an Plugins anderer Autoren/Maintainer müssen mit dem jeweiligen Autoren/Maintainer abgeklärt werden.


Fork erstellen
--------------

    * Gehen Sie aif GitHub zum `SmartHome Repo <https://github.com/smarthomeNG/smarthome/>`_ und melden Sie sich mit
      Ihrem Benutzernamen/Passwort an
    * Klicken Sie rechts oben auf „Fork“.
    * Wechseln Sie zu Ihrem Terminal und geben Sie „git clone https://USER:PASSWORD@github.com/USER/smarthome“ ein
    * Checken Sie den Entwicklungszweig „git checkout Develop“ aus
    * Wiederholen Sie dieses für das `Plugin Repo <https://github.com/smarthomeNG/plugins/>`_

    * Eine Datei ändern/erstellen.
    * Fügen Sie die Datei „git add FILE“ hinzu
    * Übernehmen Sie die Änderungen mit einem nützlichen Kommentar: „git commit“
    * Übertragen Sie Ihre Änderungen in Ihr Repository: „git pull && git push“.
    * Erstellen Sie eine Pull-Request auf GitHub: Basis: smarthomeNG/develop, Vergleich: USER/develop


Merge (description is deprecated, has to be updated)
----------------------------------------------------

Wenn Sie glauben, dass Ihr Code für die Hauptsendezeit bereit ist, senden Sie einen **Pull-Request über Github**

Mitglieder des Core Teams von SmartHomeNG können dann den Pull-Request prüfen und in das Repository mergen.


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


Arbeiten mit dem Git-Befehlszeilen-Client
-----------------------------------------

Hier ein paar Tipps, wenn Sie mit dem Kommandozeilen-Client von Git arbeiten:

Nützliche Git-Befehle
~~~~~~~~~~~~~~~~~~~~~

  * **Liste der Änderungen** seit der Veröffentlichung mit dem Tag VERSIONTAG: git log –pretty=format:“%s“ <VERSIONTAG>..HEAD
  * **Commit** mit der ID XXXIDXXX **rückgängig machen**: git reset –hard XXXIXXX && git push origin Develop –force
  * **Commit** in den aktuellen Zweig **kopieren**: git Cherry-pick <commit>

Folgen Sie dem `Commit Atom Feed <https://github.com/smarthomeNG/smarthome/commits/develop.atom>`_


Globale Einstellungen
~~~~~~~~~~~~~~~~~~~~~

  * Nur den aktuellen Zweig pushen (nicht alle): ``git config –global push.default current``
  * Passen Sie Ihre Benutzereinstellungen an:
    * ``git config –global user.name „Ihr Name“``
    * ``git config –global user.email you@example.com``


