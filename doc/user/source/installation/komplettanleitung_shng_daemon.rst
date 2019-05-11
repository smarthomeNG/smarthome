SmartHomeNG als Dienst einrichten
=================================

Um SmartHomeNG als Dienst zu betreiben muß eine Startup-Datei
für **systemd** erstellt werden.

.. warning::
    Bevor man als **Neuling** SmartHomeNG als Dienst einrichtet,
    sollte man das System verstanden haben und es sollte
    fehlerfrei laufen.

Zum Einrichten den Texteditor starten mit

.. code-block:: bash

   sudo nano /lib/systemd/system/smarthome.service

und folgenden Text hineinkopieren:

.. code-block:: bash

   [Unit]
   Description=SmartHomeNG daemon
   After=network.target
   After=knxd.service
   After=knxd.socket

   [Service]
   Type=forking
   ExecStart=/usr/bin/python3 /usr/local/smarthome/bin/smarthome.py
   User=smarthome
   PIDFile=/usr/local/smarthome/var/run/smarthome.pid
   Restart=on-abort

   [Install]
   WantedBy=default.target

Der so vorbereitete Dienst kann über den **systemctl** Befehl gestartet
werden.

.. code-block:: bash

   sudo systemctl start smarthome.service

Im Log schauen, ob keine Fehlermeldung beim Starten geschrieben wurde.

.. code-block:: bash

   tail /usr/local/smarthome/var/log/smarthome-warnings.log

Wenn alles ok ist, kann der Autostart aktiviert werden:

.. code-block:: bash

   sudo systemctl enable smarthome.service

Bei Systemstart wird nun SmartHomeNG automatisch gestartet.

Um den Dienst wieder auszuschalten und den Neustart bei Systemstart zu
verhindern nutzt man:

.. code-block:: bash

   sudo systemctl disable smarthome.service

Um zu sehen, ob SmartHomeNG läuft, genügt ein

.. code-block:: bash

   sudo systemctl status smarthome.service

Läuft es noch nicht und man möchte sozusagen manuell starten reicht ein:

.. code-block:: bash

   sudo systemctl start smarthome.service

Ein Neustart von SmartHomeNG würde mit

.. code-block:: bash

   sudo systemctl restart smarthome.service

funktionieren, ein Stop von SmartHomeNG entsprechend

.. code-block:: bash

   sudo systemctl stop smarthome.service
