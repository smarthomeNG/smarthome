.. index:: install-hooks.sh
.. index:: Tools; install-hooks.sh
.. index:: Git Hooks; Qualitätssicherung

install-hooks.sh
================

Das Skript ``tools/install-hooks.sh`` richtet Git-Hooks für beide Repositorys —
SmartHomeNG-Core und Plugins — mit einem einzigen Aufruf ein.

Wozu dienen die Hooks?
----------------------

Nach jedem ``git commit`` (**post-commit**) werden automatisch ruff und pytest
ausgeführt. Das Ergebnis wird ausgegeben, blockiert den Commit aber nicht
nachträglich.

Vor jedem ``git push`` (**pre-push**) werden ruff und pytest erneut ausgeführt.
Schlägt einer der beiden Checks fehl, wird der Push **abgelehnt**. Der Entwickler
muss die Fehler beheben und kann den Push danach wiederholen.

.. code::

   ── pre-push gate (shng) ────────────────────────────────────────
     ruff  : OK
     pytest: OK
   ────────────────────────────────────────────────────────────────

Beide Hooks wechseln immer in das SmartHomeNG-Wurzelverzeichnis, bevor sie
ruff und pytest aufrufen, damit Importpfade und ``pyproject.toml`` korrekt
aufgelöst werden.

Scope der Checks
----------------

+------------------+----------------------------+---------------------------+
| Repository       | ruff-Prüfbereich           | pytest                    |
+==================+============================+===========================+
| shng (Core)      | ``lib/  tests/  bin/``     | Gesamte Testsuite         |
|                  | ``modules/  tools/``       |                           |
+------------------+----------------------------+---------------------------+
| plugins          | ``plugins/``               | Gesamte Testsuite         |
+------------------+----------------------------+---------------------------+

Installation
------------

Das Skript muss einmalig pro Klon ausgeführt werden:

.. code::

   smarthome@<yourcomputer>:/usr/local/smarthome$ tools/install-hooks.sh

Liegt das Plugins-Repository an einem nicht-standardmäßigen Ort, kann der Pfad
als erstes Argument übergeben werden:

.. code::

   smarthome@<yourcomputer>:/usr/local/smarthome$ tools/install-hooks.sh /pfad/zu/plugins

Das Skript gibt eine Zusammenfassung der installierten Hooks aus:

.. code::

   SmartHomeNG git hook installer
     shng root   : /usr/local/smarthome
     plugins root: /usr/local/smarthome/plugins
     ruff        : /usr/local/smarthome/venvs/shng/bin/ruff
     pytest      : /usr/local/smarthome/venvs/shng/bin/pytest

   === shng: activating .githooks/ ===
     git config core.hooksPath .githooks  → done
     hooks: post-commit (informational), pre-push (blocking)

   === plugins: writing hooks to /usr/local/smarthome/plugins/.git/hooks/ ===
     post-commit (informational) → written
     pre-push    (blocking)      → written

   Installation complete.

.. note::

   Die Hooks für den Core sind im Verzeichnis ``.githooks/`` des Repositorys
   versioniert. Für das Plugins-Repository werden die Hooks von
   ``install-hooks.sh`` generiert und in ``plugins/.git/hooks/`` abgelegt
   (nicht versioniert). Nach einem erneuten Klonen des Plugins-Repositorys
   muss ``install-hooks.sh`` deshalb erneut ausgeführt werden.

Push trotzdem erzwingen
-----------------------

In Ausnahmefällen kann der pre-push-Gate mit ``--no-verify`` übersprungen
werden:

.. code::

   git push --no-verify

Dies sollte nur bewusst und begründet eingesetzt werden.
