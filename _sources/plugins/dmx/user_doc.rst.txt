DMX
===

Vorbedingungen
--------------

Dieses Plugin benötigt eine der folgenden unterstützten DMX-Schnittstellen:

- `NanoDMX`_
- `DMXking`_ sollte auch mit anderen Enttec Pro-kompatiblen Geräten funktionieren.

Die Kommunikation mit der Schnittstelle erfolgt über die serielle Schnittstelle.
Daher ist auch ein serieller Python-Treiber erforderlich. Eine requirements Datei ist
bereitgestellt, um die Installation zu erleichtern.

Konfiguration
-------------

plugin.yaml
~~~~~~~~~~~

.. code :: yaml

   dmx:
       class_name: DMX
       class_path: plugins.dmx
       serialport: /dev/usbtty...
       # interface = nanodmx

Bei `` interface`` kann zwischen `` nanodmx`` und `` enttec`` gewählt werden.
Standardmäßig wird nanodmx verwendet.

Die serielle Schnittstelle muss mit der tatsächlichen Schnittstelle übereinstimmen. Unter Linux könnte es sein
notwendig, um eine udev-Regel zu erstellen. Für ein NanoDMX-Gerät bereitgestellt über
`` / dev / usbtty-1-2.4`` könnte die folgende udev-Regel passen:

.. code :: bash

   # /etc/udev/rules.d/80-smarthome.rules
   SUBSYSTEMS=="usb",KERNEL=="ttyACM*",ATTRS{product}=="NanoDMX Interface",SYMLINK+="usbtty-%b"

In der Online-Hilfe für Linux kann die Erstellung von udev Regeln nachgelesen werden.

items.yaml
~~~~~~~~~~

dmx_ch
^^^^^^

Mit diesem Attribut können ein oder mehrere DMX-Kanäle als Integer angegeben werden
angegeben

Beispiel
~~~~~~~~

.. code:: yaml

   living_room:

       dimlight:
           type: num
           dmx_ch:
             - 10
             - 11

       dimlight_reading:
           type: num
           dmx_ch: 23

In einer Logik führt ein Ausdruck wie ``sh.living_room.dimlight(80)`` dazu das
``80`` zu den Kanälen ``10`` und ``11`` gesendet wird, um das Wohnzimmerlicht zu dimmen.
Entsprechend sendet der Ausdruck ``sh.living_room.dimlightreading(50)`` eine `50`` an den Kanal
``23``, um das Leselicht im Wohnzimmer zu dimmen.

Methoden
--------

send(Kanal, Wert)
~~~~~~~~~~~~~~~~~

Sendet den Wert an den angegebenen DMX-Kanal. Der Wert kann im Bereich von ``0`` bis ``255`` liegen.

Beispiel:
``sh.dmx.send(12, 255)`` sendet den Wert ``255`` an den Kanal ``12``

.. _NanoDMX: http://www.dmx4all.de/
.. _DMXking: http://www.dmxking.com
