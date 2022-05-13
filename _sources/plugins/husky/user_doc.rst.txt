husky
=====

Ein Plugin um Husqvarna Automower (R) mit SmartHomeNG ansteuern zu können.

Anforderungen
-------------

Es wird ein gültiges Konto bei Husqvarna benötigt.
Um dieses Konto anzulegen wird die Husqvarna AMC App auf einem Smartphone verwendet.
Die funktionierende App und das Konto mit Benutzer-ID und Password werden für das Plugin benötigt.


Notwendige Software
~~~~~~~~~~~~~~~~~~~

Keine

Unterstützte Geräte
~~~~~~~~~~~~~~~~~~~

Alle bekannten Automower Modelle sollten mit dem Plugin unterstützt werden.

Konfiguration
-------------

plugin.yaml
~~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.

.. code-block:: yaml

    am315x:
        plugin_name: husky
        userid: email@domain.de 
        password: mysecret 



items.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


logic.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Funktionen
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Beispiele
---------

Hier können ausführlichere Beispiele und Anwendungsfälle beschrieben werden.


Web Interface
-------------

SmartHomeNG liefert eine Reihe Komponenten von Drittherstellern mit, die für die Gestaltung des Webinterfaces genutzt werden können.
Erweiterungen dieser Komponenten usw. finden sich im Ordner ``/modules/http/webif/gstatic``.

Wenn das Plugin darüber hinaus noch Komponenten benötigt, werden diese im Ordner ``webif/static`` des Plugins abgelegt.

Credits
-------

* SmartHome NG Team
* Christophe Carré ([@crisz](https://github.com/chrisz) and his [pyhusmow](https://github.com/chrisz/pyhusmow) project)
* David Karlsson ([@dinmammas](https://github.com/dinmammas) and his [homebridge-robonect](https://github.com/dinmammas/homebridge-robonect) project)
* Jake Forrester ([@rannmann](https://github.com/rannmann) and his [node-husqvarna-automower](https://github.com/rannmann/node-husqvarna-automower) project)
* NextDom Team ([@NextDom](https://github.com/NextDom) and his [plugin-husqvarna](https://github.com/NextDom/plugin-husqvarna) project)

