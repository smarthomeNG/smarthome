Installation über Docker
========================

Einführung
----------

Docker erlaubt das Verpacken von Applikationen inklusive aller
Abhängigkeiten (z.B. Python) in einem Container.
Vergleichbar vielleicht zu einer APK-Datei auf Android.
Viele NAS Hersteller verwenden Docker genau für diesen Zweck,
so dass SmartHomeNG auf einem NAS sozusagen aus
dem App-Store geladen werden kann.

Dabei ist jeder Container für sich abgeschlossen und vom Host-System
(das System auf dem Docker läuft) isoliert. Benötigt z.B. eine
Applikation zwingend Python 3.5.1 und die andere Python 3.4.1, so ist
dies in unterschiedlichen Containern ohne weiteres möglich. Dies ähnelt
auf dem ersten Blick vielleicht einer Virtualisierung, doch ist ein
wesentlicher Unterschied, dass die Applikation direkt auf der Hardware
des Host-Systems läuft - nur isoliert.

Darüber hinaus, bzw. dadurch ist die Installation einer Anwendung
ähnlich einfach, wie auf dem Handy. Für SmartHomeNG reicht z.B. ein

.. code-block:: bash

  docker pull henfri/smarthome-ng

oder für den knxd

.. code-block:: bash

  docker pull henfri/knxd

Danach muss die jeweilige Applikation natürlich noch gestartet werden.
Hierbei ist zu beachten, dass die jeweilige Applikation zunächst
vollkommen abgeschottet ist. Nur wenn Ports (Netzwerk) oder
Verzeichnisse (Massenspeicher) in den Container abgebildet werden, sind
diese Ports vom Host-System im Container sichtbar.

Dies geschieht über die Parameter ``-p`` und ``-v``

.. code-block:: bash

  docker run henfri/smarthome-ng -p 123:456

Würde den Container starten und den Port ``123`` vom Host auf den Port ``456``
im Container mappen. Über den Parameter ``-p`` können auch Geräte (``/dev/*``)
übergeben werden.

Docker-Compose
--------------

Für unsere Belange werden mehrere Container verwendet:

* smarthome-ng
* knxd
* owfs
* smartvisu

Damit diese in der richtigen Reihenfolge gestartet werden, gibt es
Docker-Compose. In der ``docker-compose.yml``. Hier werden dann auch alle
Mappings (Ports und Verzeichnisse) angegeben.

Anleitung
---------

Eine Anleitung für die Installation gibt es
`hier <https://github.com/henfri/docker/tree/master/knx>`__ (Englisch)
und
`hier <https://knx-user-forum.de/forum/supportforen/smarthome-py/974370-smarthome-ng-sv-installation-ratzfatz>`__
(Deutsch)
