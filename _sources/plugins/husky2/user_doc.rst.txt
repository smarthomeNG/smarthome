husky2
======

Ein Plugin um diverse Husqvarna Automower (R) mit SmartHomeNG ansteuern zu können, sowie deren Informationen abzufragen.

Anforderungen
-------------
Zur Verwendung des Plugins wird zusätzlich zu einem gültigen Benutzerkonto, welches für die Automower Connect App
verwendet wird, auch ein API-Key und dessen Api-Secret benötigt. Diese müssen in der Plugin-Konfiguration hinterlegt
werden. Dazu auf https://developer.husqvarnagroup.cloud/applications mit dem bereits aus der App vorhandenen
Benutzernamen und Passwort anmelden und eine neue Applikation erstellen. Als redirect URL kann dabei z.B.
"http://localhost:8080" eingetragen werden. Abschließend der Applikation noch die "Authentication API" und die
"Automower Connect API" zu zuweisen.

Notwendige Software
~~~~~~~~~~~~~~~~~~~

Für die Kommunikation wird die Python-Bibliothek aioautomower benötigt. Diese wird bei der ersten Verwundung des Plugins
automatisch zu SmarthomeNG hinzugefügt.

Unterstützte Geräte
~~~~~~~~~~~~~~~~~~~

Alle bekannten Automower Modelle können mit dem Plugin angesteuert werden.

Konfiguration
-------------

plugin.yaml
~~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.

.. code-block:: yaml

    am315x:
        plugin_name: husky2
        apikey: mykey
        apisecret: mysecret

Items
~~~~~

Die husky_state Attribute können die Werte wie in der Dokumentation von Husqvarna
( https://developer.husqvarnagroup.cloud/apis/automower-connect-api#status%20description%20and%20error%20codes )
beschrieben annehmen. Zu beachten ist jedoch, dass diese ebenfalls in die Sprachen, die in der locale.yaml definiert
sind, übersetzt werden. Somit ist bei einer Überprüfung auf einen bestimmten Zustand, der Status in der jeweiligen
Sprache zu verwenden. Z.B. die Aktivität "GOING_HOME" entspricht in deutsch "Unterwegs zur Ladestation". Genauso
werden auch Fehlermeldungen gehandhabt. Für die vollständige Auflistung bitte in der locale.yaml nachlesen.


Funktionen
~~~~~~~~~~

Zur Zeit stehen keine Funktionen für dieses Plugin zur Verfügung.


Beispiele
---------

Beispielhafte Nutzung des Plugins mit SmartVisu:

.. image:: assets/control_sv.png
   :class: screenshot

.. image:: assets/state_sv.png
   :class: screenshot

SV Widget
---------

Für die Anzeige der aktuellen Position sowie den Pfad zwischen den letzten Positionen des Mähers, steht das widget
map zur Verfügung. Dieses ist auf basis von https://www.smarthomeng.de/google-maps-widget-fuer-smartvisu-2-9 mit
google maps erstellt worden. Das widget benötigt generell einen google maps api key, für Testzwecke
kann es jedoch auch ohne diesen verwendet werden.

Nachfolgend sind die Parameter für das Widget aufgelistet.

.. code-block:: html

    {{ husky2.map(id, name, latitude, longitude, gpspoints, mapskey, zoomlevel, pathcolor) }}

Eine Beispielhafte Verwendung könnte dabei so aussehen:

.. code-block:: html

    {{ husky2.map('', 'mower.info.device', 'mower.state.latitude', 'mower.state.longitude', 'mower.state.gpspoints', '4ADdsf665dSF53fdg5DGdasfg43SDF51', 19, '#3afd02') }}

Web Interface
-------------

Das Webinterface gibt einen Überblick über den aktuellen und vergangenen Status des Automowers, sowie die Möglichkeit
Ihn mit Start, Stop und Parken grundlegend zu steuern. Weiters sind alle Items gelistet die im Zusammenhang mit dem
Husky2 Plugin und somit dem Automower definiert wurden.

.. image:: assets/webif.png
   :class: screenshot

Credits
-------

* SmartHome NG Team
* Thomas Peter Protzner ([@Thomas55555](https://github.com/Thomas55555) and his [aioautomower](https://github.com/Thomas55555/aioautomower) project)
