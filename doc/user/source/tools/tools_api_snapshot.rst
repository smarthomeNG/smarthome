
.. index:: api_snapshot
.. index:: Tools; api_snapshot

api_snapshot.py
===============

Dieses Skript für Entwickler vergleicht die öffentliche API von SmartHomeNG zwischen zwei git-Refs oder Verzeichnissen
und gibt an, welche Stufe der Versionsnummer (major, minor, patch) die Änderungen nach Semantic Versioning erfordern.
Welche Namen zur öffentlichen API gehören, ist in ``tools/api_surface.yaml`` festgelegt und in ``doc/dev/public_api.md``
beschrieben. Die Analyse ist statisch, der Code der verglichenen Stände wird nicht ausgeführt.

.. code::

   smarthome$ tools/api_snapshot.py diff origin/master HEAD
   smarthome$ tools/api_snapshot.py diff origin/master HEAD --format markdown --fail-on major

Mit ``--fail-on major`` bzw. ``--fail-on review`` endet das Skript mit dem Exit-Code 1, wenn die Änderungen
mindestens diese Stufe erfordern (z.B. für Workflows).
