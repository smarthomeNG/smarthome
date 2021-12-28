
.. index:: smartVISU installieren

.. role:: bluesup
.. role:: redsup

======================
smartVISU installieren
======================

Die SmartVISU ist eine Sammlung von HTML-Dateien und PHP Skripten die es ermöglicht Items vom SmartHomeNG
anzuzeigen. Im Wesentlichen wird dazu ein Webserver benötigt, hier der Apache2 und für die variablen Daten
des SmartHomeNG braucht die SmartVisu noch eine Websocket-Verbindung zum SmartHomeNG.

.. contents:: Schritte der Installation
   :local:


zusätzliche Pakete installieren
===============================

Der Apache2 braucht noch ein paar Pakete wie PHP um die Webseiten der
SmartVISU liefern zu können:

.. code-block:: bash

   sudo apt-get install libawl-php php-curl php php-json php-xml php-mbstring
   sudo service apache2 restart


SmartVISU Quellcode laden
=========================

Die Dateien der SmartVISU werden in einem Unterverzeichnis abgelegt,
das für den **Apache2** Webserver zugänglich ist:

.. code-block:: bash

    cd /var/www/html
    sudo rm index.html
    sudo mkdir smartvisu
    sudo chown smarthome:www-data smartvisu
    # guid setzen
    chmod g+rws smartvisu/
    cd smartvisu
    git clone git://github.com/Martin-Gleiss/smartvisu.git .
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
Bei **Checking your configuration** sollte alles mit einem grünen Haken versehen sein. Falls nicht, sind die
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
    git clone git://github.com/smartVISU-newstuff/kurzanleitung .

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

