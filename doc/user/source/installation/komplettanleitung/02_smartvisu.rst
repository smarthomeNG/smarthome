
.. index:: smartVISU; Installation

.. role:: bluesup
.. role:: redsup

======================
smartVISU installieren
======================

Die SmartVISU ist eine Sammlung von HTML-Dateien und PHP Skripten die es ermöglicht Items vom SmartHomeNG
anzuzeigen. Im Wesentlichen wird dazu PHP und ein Webserver benötigt: Aktuell können unter anderem
Apache2 oder NGINX genutzt werden.
Variable Daten (z.B. Itemwerte, Plotdaten) tauschen SmartVisu und SmartHomeNG über eine Websocket-Verbindung aus.

.. contents:: Schritte der Installation
   :local:


Webserver und zusätzliche Pakete installieren
=============================================

Die folgende Anleitung funktioniert für eine Installation unter Debian Trixie (13) oder auch Debian Bookkworm (12).
Für andere Versionen kann es sein das weitere Pakete benötigt werden oder aber auch Pakete nicht gebraucht werden.
In dem Fall gibt es im Internet genügend andere Quellen die Hilfe versprechen.

.. tab-set::

    .. tab-item:: Apache2

        Auf einigen Debian Distributionen ist Apache2 bereits vorinstalliert, dennoch braucht es jedenfalls noch
        einige zusätzliche Pakete, insbesondere PHP.

        .. code-block:: bash

           sudo apt-get install apache2 libawl-php php-curl php-json php-xml php-mbstring php-zip libapache2-mod-php
           # nun zur Sicherheit den apache neu starten
           sudo systemctl restart apache2

    .. tab-item:: NGINX

        Wer auf die Visu auch über das Internet (ohne VPN) zugreifen möchte, sollte NGINX installieren und
        dann der Anleitung zum :doc:`Reverse Proxy </visualisierung/reverse_proxy>` folgen. Jedenfalls
        sind das Paket für den Webserver und PHP 8.x zu installieren.

        .. code-block:: bash

          sudo apt-get install nginx-full php-fpm
          sudo nano /etc/nginx/sites-available/default

        Bei der Standardkonfiguration von NGINX kann auf die entsprechenden Handbücher zum Paket zurückgegriffen
        werden. Wichtig ist jedenfalls das korrekte Handling von PHP Dateien, das wie folgt im ``server`` Abschnitt konfiguriert wird:

        .. code-block:: bash

          location ~ \.php$ {
              try_files $uri =404;
              fastcgi_split_path_info ^(.+\.php)(/.+)$;
              fastcgi_pass unix:/run/php/php-fpm.sock;
              fastcgi_index index.php;
              fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
              include fastcgi_params;

          }

        Schließlich müssen noch die Rechte richtig gesetzt werden.

        .. code-block:: bash

          sudo chown www-data:www-data /etc/nginx/sites-available/default


        Sollte es Probleme mit PHP geben, sind folgende Schritte durchzuführen:

        .. code-block:: bash

          sudo mkdir /etc/systemd/system/php-fpm.service.d/
          sudo nano /etc/systemd/system/php-fpm.service.d/service_php_fix.conf

        Hier ist folgender Inhalt einzutragen. Danach die Datei speichern und schließen.

        .. code-block:: bash

          [Service]
            RuntimeDirectory=php
            RuntimeDirectoryMode=755

        Schließlich sollte PHP und der Webserver neu gestartet werden.

        .. code-block:: bash

           sudo systemctl restart php-fpm.service
           sudo systemctl restart nginx


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

.. hint::

    Eine Besonderheit des Apache Webservers ist sein spezieller Umgang mit einem Ordner namens "icons" im Root-Verzeichnis.
    Da smartVISU einen solchen Ordner verwendet, sollte sie immer wie oben angegeben in einem Unterverzeichnis angelegt werden, damit keine Konflikte entstehen.
    Dies gilt auch für Docker-Umgebungen.

Für den ordnungsgemäßen Betrieb der SmartVISU in Verbindung mit mit SmartHomeNG müssen noch das Plugin **smartvisu** und das **Websocket-Modul** konfiguriert werden.
Beide sind in der **plugin.yaml.default** und **module.yaml.default** bereits vorkonfiguriert
und werden beim ersten Start nach einer frischen Installation in die Einstellungen
übernommen.


Zugriff auf die SmartVISU testen
================================

Mit einem Browser kann nun erstmals auf die SmartVISU zugegriffen werden: Hierbei ist ``<ip-des-servers>`` natürlich
mit der IP oder dem Hostnamen deines SmartVISU Servers ersetzen: ``http://<ip-des-servers>/smartvisu``.
Bei **Checking your configuration** sollte alles mit einem Haken versehen sein. Falls nicht, sind die
entsprechenden Änderungen vorzunehmen **bevor man weiter macht**.

Über den Knopf **Config** kommt man ins smartVISU Interface direkt auf die Config Seite. Diese ist anfangs in Englischer
Sprache. Unter **User Interface > Language** kann man die Sprache auf Deutsch einstellen und mit **Save Settings** speichern.
Danach sind alle Menüpunkte und Hilfetexte in Deutscher Sprache (wird im Folgenden vorausgesetzt).

Bei Smarthome/IoT-Datenquelle ist **SmartHomeNG** auszuwählen. Bei der Adresse (Host / IP) muss die IP Adresse des
Servers eingeben werden, auf dem SmartHomeNG installiert ist. Alternativ kann der Hostname des Serves 
angegeben werden. Bei Port ist standardmäßig ``2424`` einzugeben und TLS-Port ``2425``.

**ACHTUNG**: Hier **NICHT** ``localhost`` oder ``127.0.0.1`` eingeben, denn die Adresse wird vom Client Browser benötigt,
um aktuelle Daten über einen Websocket direkt von SmartHomeNG abzufragen. 

Soll die Visu über einen Hostnamen anstatt der IP-Adresse aufgerufen werden, muss der Hostnamne im Untermenü 
**smartVISU Hostname / Proxy Server** als Hostname bekannt gemacht werden, damit der Treiber dies von einer externen URL 
unterscheiden kann.

Im Tab **Benutzeroberfläche** müssen noch die anzuzeigenden Visu-Seiten eingestellt
werden. Bevor man eigene Seiten erstellt, kann man dort verschiedene Demoseiten ausprobieren,
die dann als Basis für die eigene Visu dienen können.

Um die Einstellungen zu sichern bitte **Einstellungen speichern** auswählen.


Eigene Visu Seiten anlegen
==========================

Um mit der SmartVISU eine eigene Visu anzulegen, muss innerhalb des Ordners ``pages`` der SmartVISU ein neues
Verzeichnis angelegt werden, in dem dann die eigenen Seiten z.B. für Räume oder Funktionsbereiche abgelegt werden.
Es existiert im Ordner ``pages`` bereits ein Unterordner ``_template``. Dieser wird als Basis der neuen Visu einfach
kopiert ``cp _template <meineneuevisu>``. Für ``<meineneuevisu>`` sollte **nicht smarthome** gewählt werden
wenn später die Visu vom SmartHomeNG Plugin **smartvisu** erstellt werden soll. Die manuell erstellten Seiten
könnten sonst einfach von SmartHomeNG überschrieben werden.

Die Dateien für die SmartVISU sind einfache HTML Dateien, die auf eigene Bedürfnisse beliebig angepasst werden
können. Die einzelnen Bedienelemente wie Buttons, Flips und Werteanzeigen (sogenannte Widgets) sind Makros, 
die mit der Makrosprache **TWIG** definiert sind und mit vielen Optionen für die jeweilige Aufgabe parametriert 
werden können. Als Hilfestellung für die Parametrierung bringt smartVISU eine integrierte interaktive Dokumentation
in Englisch mit, die über die Systemseite (Zahnradsymbbol in der Kopfzeile) aufgerufen wird. Sie enthält viele
Widget-Beispiele, deren Funktionen live, aber offline getestet werden können. 

Ebenfalls auf der Systemseite befindet sich der Widget-Assistent. Mit ihm können Widgets live parametriert und 
online am Backend (z.B. SmartHomeNG) getestet werden. Der eingegebene Code wird automatisch in die Zwischenablage
kopiert und kann direkt in die HTML-Seiten hineinkopiert werden. Um die volle Funktionalität nutzen zu können, 
muss SmartHomeNG fertig konfiguriert und gestartet sein und das smartvisu-Plugin muss die Datei "masteritem.json"
erstellt haben, die dem Assistenten die definierten Items und ihre Typen bekannt macht.

Wer noch tiefer in die Zusammenhänge einsteigen will, kann die sog. "Kurzanleitung"  in Deutscher Sprache verwenden
(siehe unten). Dort werden für viele Grundfunktionen die Parametrierung der Items in SmartHomeNG gemeinsam mit der 
zugehörigen Widget-Parametrierung in smartVISU erklärt.

Dokumentation und Kurzanleitung sind zwar auf der `Projektseite smartVISU <http://www.smartvisu.de/>`__ zu finden, 
es wird aber empfohlen die integrierte Dokumentation in der Visu zu verwenden, die immer zur installierten
Version passt und aktuell ist. 

Die für die SmartVISU generierten HTML Seiten sind zwar responsiv, aber durchweg statisch. Die Kommunikation zwischen 
SmartHomeNG und der SmartVISU erfolgt über das Websocketmodul für SmartHomeNG und JavaScript Code, der automatisch 
zu den Widgets in die HTML Seite eingebunden wird. Der Javascript Code steuert dann dynamisch das Verhalten der Seite 
in Abhängigkeit von den via Websocket übermittelten Daten von Items in SmartHomeNG. 


SmartVISU Kurzanleitung
=======================

Ab Version v3.7 bringt smartVISU die Kurzanleitung im Unterordner pages bereits mit. 
Für alle älteren SmartVISU Installationen <= v3.6 muß die Kurzanleitung manuell nachinstalliert werden.
Dazu sind folgende Kommandos auszuführen:

.. code-block:: bash

    cd /var/www/html/smartvisu/pages
    mkdir kurzanleitung
    cd kurzanleitung
    git clone https://github.com/smartVISU-newstuff/kurzanleitung .

(Bitte wie immer auf den Punkt am Ende des letzten Befehls achten)


Wenn die Kurzanleitung installiert ist, erscheint automatisch ein entsprechender Menüpunkt auf der
Systemseite. Alternativ kann die Kurzanleitung im Browser mit det URL 
``http://<ip-des-servers>/smartvisu/index.php?pages=kurzanleitung`` aufgerufen werden. 


SmartHomeNG Plugin **smartvisu**
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

Mit dem Plugin **smartvisu** können aus der Definition der Items in SmartHomeNG automatisch Visu-Seiten
erstellt werden. Hierzu müssen die benötigten Seitenformate und der benötigte Widget-Code direkt in die 
Item-Definitionen von SmartHomeNG geschrieben werden. Dies ist im
Abschnitt :doc:`Visualisierung </visualisierung/visualisierung>` genau beschrieben. Die so erstellten Visu-Seiten 
werden im Verzeichnis ``smarthome`` des ``pages`` Verzeichnisses der smartVISU abgelegt. In der Konfiguration
von smartVISU ist dafür ``Smarthome`` für die Seiten der Benutzeroberfläche einzustellen. 

Das Plugin unterstützt smartVISU Versionen von v2.8 bis zur aktuellen Version.


Mischung von generierten und manuell erstellten Seiten
------------------------------------------------------

Es ist möglich automatisch generierte und manuell erstellte Seiten zu mischen. Das Vorgehen hierzu ist
in unter :doc:`Visualisierung </visualisierung/visualisierung>` beschrieben.
