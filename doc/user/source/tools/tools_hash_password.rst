
.. index:: hash_password
.. index:: Tools; hash_password

hash_password.py
================

Dieses Skript gibt einen gesalzenen Hash eines Passworts aus, z.B. für die Parameter ``hashed_password`` und
``service_hashed_password`` des :doc:`http Moduls </konfiguration/module/module_http>` in der ``etc/module.yaml``
oder für ``hashed_password`` des cli Plugins.

Das Passwort wird zweimal ohne Anzeige abgefragt. Es erscheint daher weder auf der Kommandozeile noch in der
History der Shell.

.. code::

   smarthome$ tools/hash_password.py
   Password:
   Repeat password:
   pbkdf2_sha256$600000$...$...

Den gleichen Hash erzeugt die Funktion **Password-Hash erzeugen** auf der Seite **Dienste** der Admin GUI.
