.. index:: install-hooks.sh
.. index:: Tools; install-hooks.sh
.. index:: Git Hooks; Qualitätssicherung

.. role:: greensup

install-hooks.sh :greensup:`Update`
====================================

Das Skript ``tools/install-hooks.sh`` richtet git-Hooks für die SmartHomeNG-Repositories
Core und/oder Plugins ein. Es fragt interaktiv ab, welche Repositories konfiguriert werden sollen.

.. hint::

  Das Aktivieren ist freiwillig und kann nach individuellen Vorlieben geschehen.

Warum das Ganze?
----------------

Durch einheitliche Formatierung des Quellcodes wird der Code insgesamt
lesbarer, da die einschlägigen Python-Konventionen der PEP8 überall 
eingehalten werden.

Das Linting (Syntaxprüfung) dient dazu, statisch erkennbare Fehler schon
vor der Veröffentlichung des Codes zu finden und beheben zu lassen.

Das Ausführen der Testsuiten dient dazu sicherzustellen, dass durch Änderungen
oder Erweiterungen am Code das definierte und gewünschte Verhalten nicht
verändert oder geplante Änderungen erfolgreich umgesetzt wurden.

Im Core ist dies sinnvoll, da bei diesem zentralen Element die Korrektheit
und Verständlichkeit des Codes besonders wichtig ist.

Bei den Plugins ist dies sinnvoll, da durch eine Vielzahl von unterschiedlichen
Autoren eine einheitliche Konvention das Lesen und Verstehen vereinfacht, und
gerade weniger versierten Autoren hilft, korrekten Code auf GitHub zu veröffentlichen.

Wie funktionieren die Hooks?
----------------------------

**pre-commit** (formatieren + Lint-Gate): 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Vor jedem Commit werden die
*staged* ``.py``-Dateien automatisch mit ``ruff format`` formatiert und neu
zum Commit hinzugefügt (``git add``). Anschließend prüft ``ruff check`` die
gleichen Dateien. Findet ruff Lint-Fehler, wird der Commit **abgelehnt**, da
die Code-Prüfung einen fehlerhaften PR blockiert.

.. code::

   ==> COMMIT REJECTED: ruff found lint errors in staged files.

       Fix the errors above, then:  git commit
       Bypass (use sparingly):      git commit --no-verify

       Note: ruff is a required CI check — errors will block your PR.

**pre-push** (pytest-Gate):
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Vor jedem ``git push`` wird die Testsuite
ausgeführt. Schlägt sie fehl, wird der Push **abgelehnt**.

.. code::

   ── pre-push gate (shng) ────────────────────────────────────────
     running tests/ ...

     pytest: OK
   ────────────────────────────────────────────────────────────────

Beide Hooks wechseln immer in das Wurzelverzeichnis des jeweiligen
Repositorys, bevor sie ruff bzw. pytest aufrufen, damit Importpfade und
``pyproject.toml`` korrekt aufgelöst werden.

Scope der Checks
----------------

+------------------+--------------------------------+---------------------+
| Repository       | ruff-Prüfbereich (pre-commit)  | pytest (pre-push)   |
+==================+================================+=====================+
| shng (Core)      | nur staged ``.py``-Dateien     | ``tests/``          |
|                  |                                | (gesamter Core)     |
+------------------+--------------------------------+---------------------+
| plugins          | nur staged ``.py``-Dateien     | ``plugins/*/tests`` |
|                  |                                | (alle Plugins)      |
+------------------+--------------------------------+---------------------+

ruff formatiert und prüft also nur die Dateien, die tatsächlich committet
werden — nicht das gesamte Repository.

Installation
------------

Das Skript muss einmalig pro Installation ausgeführt werden:

.. code::

   shng@computer:/usr/local/smarthome$ tools/install-hooks.sh

Es fragt anschließend, für welches Repository die Hooks installiert werden
sollen:

.. code::

   Install hooks for:
     c) shng core only
     p) plugins only
     b) both (default)

   Choice [b]:

Bei der Auswahl ``p`` oder ``b`` wird zusätzlich nach dem Pfad zum
Plugins-Repository gefragt (Standard: ``<shng-root>/plugins``):

.. code::

   Plugins repository [/usr/local/smarthome/plugins]:

Um Hooks nach Änderungen (z. B. an diesem Skript) zu aktualisieren, wird
``install-hooks.sh`` einfach erneut ausgeführt.

.. note::

   Die Hooks für den Core sind im Verzeichnis ``.githooks/`` des Repositorys
   abgelegt; ``install-hooks.sh`` aktiviert sie lediglich per
   ``git config core.hooksPath .githooks``. Für das Plugins-Repository
   werden die Hooks von ``install-hooks.sh`` generiert und direkt in
   ``plugins/.git/hooks/`` abgelegt. Nach einem erneuten ``git clone`` 
   (nicht ``git pull`` oder ``git checkout``) des Plugins-Repositorys
   muss ``install-hooks.sh`` deshalb erneut ausgeführt werden.

Ein zuvor evtl. vorhandener ``post-commit``-Hook wird beim Installieren
automatisch entfernt — er wurde durch den ``pre-commit``-Hook (Format + Lint
vor dem Commit statt informativ danach) abgelöst.

Push trotzdem erzwingen
-----------------------

In Ausnahmefällen kann der pre-commit- bzw. pre-push-Gate mit
``--no-verify`` übersprungen werden:

.. code::

   git commit --no-verify
   git push --no-verify

Dies sollte nur bewusst und begründet eingesetzt werden — die gleichen
Checks laufen verpflichtend in der CI (GitHub Actions) und blockieren den
Pull Request unabhängig vom lokalen Bypass.
