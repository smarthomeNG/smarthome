
.. index:: ruamel_compat
.. index:: Tools; ruamel_compat

ruamel_compat
=============

Dieses Werkzeug für Entwickler prüft, was eine Version des Python Packages ``ruamel.yaml`` mit den YAML Dateien von
SmartHomeNG macht, bevor die zulässigen Versionen in ``lib/requirements.txt`` geändert werden. Jede YAML Datei eines
Korpus wird mit ``lib/shyaml.py`` geladen und gespeichert (wie es die Admin GUI beim Bearbeiten tut) und mit dem
Ergebnis von ruamel.yaml selbst verglichen. Der Bericht zeigt u.a. abweichend gelesene Daten, verlorene Kommentare
und geänderte Zeilen.

.. code::

   smarthome$ tools/ruamel_compat/ruamel_compat.py matrix 0.16.7 0.19.1 --corpus plugins --corpus etc

Die Bedienung und das Lesen des Berichts sind in ``tools/ruamel_compat/README.md`` beschrieben.
