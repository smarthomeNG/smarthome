
.. index:: smartVISU; Installation

.. role:: bluesup
.. role:: redsup

======================
smartVISU installieren
======================

Die SmartVISU ist eine Sammlung von HTML-Dateien und PHP Skripten die es ermöglicht Items vom SmartHomeNG
anzuzeigen. Im Wesentlichen wird dazu ein Webserver benötigt, Apache2 oder NGINX und für die variablen Daten
des SmartHomeNG braucht die SmartVisu noch eine Websocket-Verbindung zum SmartHomeNG.

.. contents:: Schritte der Installation
   :local:


Webserver und zusätzliche Pakete installieren
=============================================

.. tabs::

    .. tab:: Apache2

        Auf einigen Debian Distributionen ist Apache2 bereits vorinstalliert, dennoch braucht es jedenfalls noch
        einige zusätzliche Pakete, insbesondere PHP.

        .. code-block:: bash

           sudo apt-get install apache2 libawl-php php-curl php8.2-fpm php-json php-xml php-mbstring
           sudo systemctl restart apache2

    .. tab:: NGINX

        Wer auf die Visu auch über das Internet (ohne VPN) zugreifen möchte, sollte NGINX installieren und
        dann der Anleitung zum :doc:`Reverse Proxy </visualisierung/reverse_proxy>` folgen. Jedenfalls
        sind das Paket für den Webserver und PHP 8.2 zu installieren.

        .. code-block:: bash

          sudo apt-get install nginx-full php8.2-fpm
          sudo nano /etc/nginx/sites-available/default

        Bei der Standardkonfiguration von NGINX kann auf die entsprechenden Handbücher zum Paket zurückgegriffen
        werden. Wichtig ist jedenfalls das korrekte Handling von PHP Dateien, das wie folgt im ``server`` Abschnitt konfiguriert wird:

        .. code-block:: bash

          location ~ \.php$ {
              try_files $uri =404;
              fastcgi_split_path_info ^(.+\.php)(/.+)$;
              fastcgi_pass unix:/run/php/php8.2-fpm.sock;
              fastcgi_index index.php;
              fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
              include fastcgi_params;

          }

        Schließlich müssen noch die Rechte richtig gesetzt werden.

        .. code-block:: bash

          sudo chown www-data:www-data /etc/nginx/sites-available/default


Sollte es Probleme mit PHP geben, sind folgende Schritte durchzuführen:

.. code-block:: bash

  sudo mkdir /etc/systemd/system/php8.2-fpm.service.d/
  sudo nano /etc/systemd/system/php8.2-fpm.service.d/service_php_fix.conf

Hier ist folgender Inhalt einzutragen. Danach die Datei speichern und schließen.

.. code-block:: bash

  [Service]
    RuntimeDirectory=php
    RuntimeDirectoryMode=755

Schließlich sollte PHP und der Webserver neu gestartet werden.

.. code-block:: bash

   sudo systemctl restart php8.2-fpm.service
   sudo systemctl restart nginx ODER sudo systemctl restart apache2


SmartVISU Quellcode laden
=========================

Die Dateien der SmartVISU werden in einem Unterverzeichnis abgelegt,
das für den Webserver zugänglich ist:

.. code-block:: bash

    cd /var/www/html
    sudo rm index.html
    sudo mkdir smartvisu
    sudo chown smarthome:www-data smartvisu
    # guid setzen
    chmod g+rws smartvisu/
    cd smartvisu
    git clone https://github.com/Martin-Gleiss/smartvisu.git .
    # Schreibrechte für Cache und Konfigurationsdateien setzen
    bash setpermissions

Bitte auf den **Punkt** am Ende des **git clone** Kommandos achten!

Eine Besonderheit des Apache Webservers ist sein spezieller Umgang mit einem Ordner namens "icons" im Root-Verzeichnis. Da smartVISU einen solchen Ordner verwendet, sollte sie immer wie oben angegeben in einem Unterverzeichnis angelegt werden, damit keine Konflikte entstehen. Dies gilt auch für Docker-Umgebungen.

Für den ordnungsgemäßen Betrieb braucht die SmartVISU noch das SmartHomeNG Plugin **smartvisu** und das **Websocket-Modul** (oder
"visu_websocket", das aber seit v1.8 deprecated ist). Beide sind in der **plugin.yaml.default** und **module.yaml.default** bereits vorkonfiguriert
und werden beim ersten Start nach einer frischen Installation in die Einstellungen
übernommen.


Zugriff auf die SmartVISU testen
================================

Mit einem Browser kann nun erstmals auf die SmartVISU zugegriffen werden: Hierbei ist ``<ip-des-servers>`` natürlich
mit der IP oder dem Hostnamen deines SmartVISU Servers ersetzen: ``http://<ip-des-servers>/smartvisu``.
Bei **Checking your configuration** sollte alles mit einem Haken versehen sein. Falls nicht, sind die
entsprechenden Änderungen vorzunehmen **bevor man weiter macht**.

Über den Knopf **Config** kommt man ins SmartVISU Interface direkt auf die Config Seite.

Bei I/O Connection **SmartHomeNG** auswählen. Bei Adresse (URL / IP) die IP Adresse des
Servers oder den DNS Namen eingeben auf dem SmartHomeNG installiert ist.
Bei Port ist standardmäßig ``2424`` einzugeben.

**ACHTUNG**: Hier **NICHT** ``localhost`` oder ``127.0.0.1``
eingeben, denn diese Adresse wird vom Client Browser benutzt
(Javascripts) um aktuelle Daten über einen Websocket direkt von
SmartHomeNG abzufragen.

Im Tab **Interfaces** muss noch die anzuzeigende Visu Seite eingestellt
werden. Dort kann unter anderem gewählt werden zwischen verschiedenen
Demoseiten.

Um die Einstellungen zu sichern bitte **Save** auswählen.


Eigene Visu Seiten anlegen
==========================

Um mit der SmartVISU eine eigene Visu anzulegen, muss innerhalb des Ordners ``pages`` der SmartVISU ein neues
Verzeichnis angelegt werden, in dem dann die eigenen Seiten z.B. für Räume oder Funktionsbereiche abgelegt werden.
Es existiert im Ordner ``pages`` bereits ein Unterordner ``_template``. Dieser wird als Basis der neuen Visu einfach
kopiert ``cp _template <meineneuevisu>``. Für ``<meineneuevisu>`` sollte **nicht smarthome** gewählt werden
wenn später die Visu vom SmartHomeNG Plugin **smartvisu** erstellt werden soll. Die manuell erstellten Seiten
könnten sonst einfach von SmartHomeNG überschrieben werden.

Die Dateien für die SmartVISU sind einfache HTML Dateien. Die einzelnen Bedienelemente wie Buttons, Flips,
Werteanzeigen (sogenannte Widgets) sind Makros die mit der Makrosprache **TWIG** definiert sind.
Die HTML können auf eigene Bedürfnisse beliebig angepasst werden.
Im einzelnen ist das zwar auf der  `Projektseite smartVISU <http://www.smartvisu.de/>`__ nachzulesen,
es wird aber empfohlen die entsprechende Dokumentation aus GitGub nachzuinstallieren, wo immer die aktuellste Version gepflegt ist (siehe unten).
Die durch die SmartVISU generierten HTML Seiten sind zwar responsiv aber durchweg statisch.
Die Kommunikation zwischen SmartHomeNG und der SmartVISU erfolgt über ein Websocket Plugin
für SmartHomeNG und JavaScript Code der in der HTML Seite eingebunden wird. Der Javascript Code manipuliert dann
aufgrund der via Websocket übermittelten Daten von Items in SmartHomeNG dynamisch den Inhalt der Webseite (DOM).


Nachinstallation der Kurzanleitung
==================================

Um die aktuelle Version 2.0 der Kurzanleitung nachzuinstallieren, sind folgende Kommandos auszuführen:

.. code-block:: bash

    cd /var/www/html/smartvisu/pages
    mkdir kurzanleitung
    cd kurzanleitung
    git clone https://github.com/smartVISU-newstuff/kurzanleitung .

(Bitte wie immer auf den Punkt am Ende des letzten Befehls achten)


Der Aufruf der Kurzanleitung kann anschließend im Browser mit dem
Befehl ``http://<ip-des-servers>/smartvisu/index.php?pages=kurzanleitung`` erfolgen.


SmartHomeNG Plugin **visu\_smartvisu**
======================================

.. hint::

    Bevor man sich an der automatischen Generierung von Visualisierungs-Seiten durch SmartHomeNG heran macht,
    sollte man sich zuerst mit der Dokumentation der smartVISU vertraut machen. Wenn man mit einem Browser
    die Seite einer noch nicht konfigurierten smartVISU aufruft, kommt man zu einer Inline Dokumentation der
    smartVISU. Eine umfassende aktuelle Kurzanleitung kann nachinstalliert werden. Wie das geht, ist weiter
    oben beschrieben.
    Zudem gibt es seit smartVISU v3.0 den Widget Assistenten, mit dem die benötigten Widgets parametriert,
    getestet und in die Zwischenablage kopiert werden können. Der Widget Assistent ist über das
    Systemmenü zu erreichen.

Mit dem Plugin **smartvisu** können aus der Definition der Items in SmartHomeNG automatisch Visuseiten
erstellt werden. Diese Visu Seiten werden im Verzeichnis ``smarthome`` des ``pages`` Verzeichnisses der
smartVISU erstellt. Das Plugin unterstützt smartVISU Versionen von v2.8 bis zur aktuellen Version.


Mischung von generierten und manuell erstellten Seiten
------------------------------------------------------

Es ist möglich automatisch generierte und manuell erstellte Seiten zu mischen. Das Vorgehen hierzu ist
in unter :doc:`Visualisierung </visualisierung/visualisierung>` und in der
:doc:`Dokumentation des Plugins </plugins/visu_smartvisu/user_doc>` beschrieben.
