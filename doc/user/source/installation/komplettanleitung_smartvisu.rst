smartVISU installieren
======================

-  Schritte der Installation:

   -  `zusätzliche Pakete
      installieren <#zusätzliche-pakete-installieren>`__
   -  `SmartVISU Quellcode laden <#smartvisu-quellcode-laden>`__

Die SmartVISU ist eine Sammlung von HTML-Dateien und PHP Skripten die es
ermöglicht Items vom SmartHomeNG anzuzeigen. Im Wesentlichen wird dazu
ein Webserver benötigt, hier der Apache2 und für die variablen Daten des
SmartHomeNG braucht die SmartVisu noch eine Websocket-Verbindung zum
SmartHomeNG.

zusätzliche Pakete installieren
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Der Apache2 braucht noch ein paar Pakete wie PHP um die Webseiten der
SmartVISU liefern zu können:

.. code-block:: bash

   sudo apt-get install libawl-php php-curl php php-json php-xml php7.0-mbstring
   sudo service apache2 restart


SmartVISU Quellcode laden
~~~~~~~~~~~~~~~~~~~~~~~~~

Stand April 2019 wird die letzte verfügbare Master-Version 2.8 der
SmartVISU geladen. Seit Dezember 2017 steht die Version 2.9 in den
Startlöchern. Diese Dokumentation ist nicht tagesaktuell, daher bitte
vor dem Installieren `auf der Projektseite <http://www.smartvisu.de/>`__
prüfen, welches der aktuelle Master ist.

Eine alternative Installation der SmartVISU 2.9 ist möglich und auch empfohlen.
Dazu muß der Branch von **master** auf **develop** gewechselt werden
Die Dateien der SmartVISU werden in einem Unterverzeichnis abgelegt,
das für den Apache2 zugänglich ist:

.. code-block:: bash

    cd /var/www/html
    sudo rm index.html
    sudo mkdir smartVISU
    sudo chown smarthome:www-data smartVISU
    # guid setzen
    chmod g+rws smartVISU/
    cd smartVISU
    git clone git://github.com/Martin-Gleiss/smartvisu.git .
    # Apache2 Zugriff erlauben
    sudo find . -type d -exec chmod g+rwsx {} +
    sudo find . -type f -exec chmod g+r {} +

Umschalten auf die SmartVISU 2.9 develop Version geht über eine
Shell im Verzeichnis der smartVISU mit

.. code-block:: bash

   cd /var/www/html/smartVISU
   git checkout develop

umschalten auf den masterbranch ginge entsprechend mit

.. code-block:: bash

   cd /var/www/html/smartVISU
   git checkout master

Für den ordnungsgemäßen Betrieb braucht die SmartVISU noch das SmartHomeNG Plugin
**visu_websocket**. Dieses ist in der **plugin.yaml.default** bereits vorkonfiguriert
und es ist zumeist nicht nötig die Vorgabewerte zu ändern.

Zugriff auf die SmartVISU testen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mit einem Browser kann nun erstmals auf die SmartVISU zugegriffen
werden: Hierbei ist ``<ip-des-servers>`` natürlich mit der IP oder dem
Hostnamen deines SmartVISU Servers ersetzen:
``http://<ip-des-servers>/smartVISU`` Bei **Checking your
configuration** sollte alles mit einem grünen Häckchen versehen sein.
Über den Knopf **Config** kommt man ins SmartVISU Interface direkt auf
die Config Seite.

Bei I/O Connection **SmartHomeNG** auswählen. Bei Adresse (URL / IP) die IP Adresse des
Servers oder den DNS Namen eingeben auf dem SmartHomeNG installiert ist.
Bei Port ist standardmäßig ``2424`` einzugeben.

**ACHTUNG**: Hier **NICHT** ***localhost*** oder ***127.0.0.1***
eingeben, denn diese Adresse wird vom Client Browser benutzt
(Javascripts) um aktuelle Daten über einen Websocket direkt von
SmartHomeNG abzufragen.

Im Tab **Interfaces** muß noch die anzuzeigende Visu Seite eingestellt
werden. Dort kann unter anderem gewählt werden zwischen verschiedenen
Demoseiten.

Um die Einstellungen zu sichern bitte **Save** auswählen.

Eigene Visu Seiten anlegen
^^^^^^^^^^^^^^^^^^^^^^^^^^

Um mit der SmartVISU eine eigene Visu anzulegen, muß innerhalb des
Ordners ``pages`` der SmartVISU ein neues Verzeichnis angelegt werden,
in dem dann die eigenen Seiten z.B. für Räume oder Funktionsbereich
abgelegt werden. Es existiert im Ordner ``pages`` bereits ein
Unterordner ``_template``. Dieser wird als Basis der neuen Visu einfach
kopiert ``cp _template <meineneuevisu>``. Für sollte ***nicht
smarthome*** gewählt werden wenn später die Visu vom SmartHomeNG Plugin
**visu\_smartvisu** erstellt werden soll. Die manuell erstellten Seiten
könnten sonst einfach von SmartHomeNG überschrieben werden. Die Dateien
für die SmartVISU sind einfache HTML Dateien. Die einzelnen Schalter,
Buttons, Anzeigen (sogenannte Widgets) sind Makros die mit der
Makrosprache TWIG definiert sind. Die HTML können auf eigene Bedürfnisse
beliebig angepasst werden. Im einzelnen ist das `auf der
Projektseite <http://www.smartvisu.de/>`__ nachzulesen.

SmartHomeNG Plugin **visu\_smartvisu**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mit dem Plugin ***visu\_smartvisu*** können aus der Definition der Items
in SmartHomeNG automatisch Visuseiten erstellt werden. Diese Visu Seiten
werden im Verzeichnis ``smarthome`` erstellt. Dazu bitte beim
entsprechenden Plugin die Doku lesen.
