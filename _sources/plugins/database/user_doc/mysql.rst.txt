
.. index:: database; MySQL installieren
.. index:: database; MariaDB installieren

.. role:: redsup

========================================
MySQL/MariaDB Installation :redsup:`neu`
========================================

Diese Seite beschreibt die Installation und Grundeinrichtung eines MySQL/MariaDB Servers für die
Nutzung mit dem ``database`` Plugin.

Aktuelle Debian- und Ubuntu-Versionen liefern MariaDB als Standard-Implementierung von MySQL im
eigenen Repository aus, eine zusätzliche Paketquelle ist nicht notwendig:

.. code-block:: bash

   sudo apt-get install mariadb-server

Mit dem folgenden Befehl kann kontrolliert werden, ob der Server läuft:

.. code-block:: bash

   systemctl status mariadb

.. code-block:: text

    ● mariadb.service - MariaDB 11.8.3 database server
         Loaded: loaded (/usr/lib/systemd/system/mariadb.service; enabled; preset: enabled)
         Active: active (running) since ...
           Docs: man:mariadbd(8)
                 https://mariadb.com/kb/en/library/systemd/

Der Server ist nach der Installation sofort einsatzbereit, der lokale **root**-Zugriff erfolgt
standardmäßig passwortlos über den Unix-Socket (``sudo mariadb``), nicht über ein gesetztes
Passwort. Zum Absichern der Installation (u.a. Testdatenbank entfernen, anonyme Nutzer entfernen)
kann optional

.. code-block:: bash

   sudo mariadb-secure-installation

ausgeführt werden. Der Assistent fragt dabei unter anderem, ob die Unix-Socket-Authentifizierung
für root beibehalten werden soll - diese Frage kann mit **Ja** beantwortet werden, sofern kein
root-Passwort gewünscht ist.

Anschließend wird eine Datenbank und ein eigener Benutzer für SmartHomeNG angelegt (Passwort bitte
durch ein eigenes ersetzen):

.. code-block:: bash

   sudo mariadb -e "CREATE DATABASE shng CHARACTER SET utf8mb4;"
   sudo mariadb -e "CREATE USER 'shng'@'localhost' IDENTIFIED BY 'shng_password';"
   sudo mariadb -e "GRANT ALL PRIVILEGES ON shng.* TO 'shng'@'localhost';"
   sudo mariadb -e "FLUSH PRIVILEGES;"

.. hint::

   Soll auch von einem anderen Rechner im Netzwerk auf den Server zugegriffen werden, muss statt
   ``'shng'@'localhost'`` z.B. ``'shng'@'%'`` (oder eine feste IP-Adresse) verwendet werden, und in
   ``/etc/mysql/mariadb.conf.d/50-server.cnf`` die Zeile ``bind-address`` entsprechend angepasst
   bzw. entfernt werden.

Das Plugin greift über das Python-Modul ``pymysql`` auf MySQL/MariaDB zu. Dieses Modul ist nicht
Teil der Grundinstallation und muss im für SmartHomeNG verwendeten virtuellen Python Environment
(siehe :doc:`/referenz/python/virtual_environments`) nachinstalliert werden:

.. code-block:: bash

   pip3 install pymysql

Die eigentliche Plugin-Konfiguration (``driver: mariadb``, Verbindungsdaten) ist unter
:doc:`/plugins_doc/config/database` beschrieben.
