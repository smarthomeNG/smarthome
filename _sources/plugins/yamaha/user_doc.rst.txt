Yamaha
======

Plugin zur Steuerung von Yamaha RX-V- und RX-S-Receivern, z. B.: Power On/Off,
Auswahl des Eingangs, Lautstärke einstellen und stumm schalten.

Dieses Plugin befindet sich noch in der Entwicklung, ist jedoch für den Autor im täglichen Gebrauch.
Dort wird das Plugin zum Einschalten des Yamaha RX-S600 und RX-V475 verwendet
den Eingangskanal auszuwählen. 
Je nach Eingang wird die Lautstärke auch angepasst, was für den Autor gut funktioniert.
Stummschaltung wird aktuell nicht verwendet.

Das Plugin verwendet das Yamaha Network Control (YNC) Protokoll. 
Das Protokoll arbeitet intern mit Datenaustausch im XML Format.
Ereignisbenachrichtigungen werden über UDP multicast empfangen (SSDP), wenn das Gerät sie sendet.
Um die Benachrichtigungen zu erhalten, muss das Yamaha-Gerät das selbe Subnetz 
wie der SmartHomeNG-Host verwenden.

Derzeit wird nur die Hauptzone unterstützt.

Anforderungen
-------------

Notwendige Software
~~~~~~~~~~~~~~~~~~~

Es ist keine zusätzliche Software erforderlich

Unterstützte Geräte
~~~~~~~~~~~~~~~~~~~

Alle Serien 

* RX-V4xx
* RX-V5xx
* RX-V6xx
* RX-V7xx 
* RX-Sxxx 

haben das selbe API, also sollten sie mit diesem Plugin funktionieren.

Der RXS-602D ist ebenfalls getestet und funktioniert im Grunde genommen mit Ausnahme des
Benachrichtigungen, die überhaupt nicht gesendet werden. Da dieses Gerät auch
unterstützt MusicCast, alternativ kann das Yamahaxyc-Plugin verwendet werden.

Nach der Installation des Plugins kann es sein, dass keine Ereignisbenachrichtigungen 
über multicast empfangen werden.
Um Ereignisbenachrichtigungen zu aktivieren muss das Gerät mindestens einmal 
einmal mit SmartHomeNG eingeschaltet werden.

Konfiguration
-------------

plugin.yaml
~~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


items.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.

Beispiel für Items:

.. code-block:: yaml

   livingroom:

       yamaha:
           yamaha_host: 192.168.178.186

           power:
               type: bool
               yamaha_cmd: power
               enforce_updates: 'True'

           volume:
               type: num
               yamaha_cmd: volume
               enforce_updates: 'True'

           mute:
               type: bool
               yamaha_cmd: mute
               enforce_updates: 'True'

           input:
               type: str
               yamaha_cmd: input
               enforce_updates: 'True'

**Achtung:**
    Der oberste Item Name kann mit Plugin Namen kollidieren

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

SmartHomeNG liefert eine Reihe Komponenten von Drittherstellern mit, die für die Gestaltung des Webinterfaces genutzt werden können. Erweiterungen dieser Komponenten usw. finden sich im Ordner ``/modules/http/webif/gstatic``.

Wenn das Plugin darüber hinaus noch Komponenten benötigt, werden diese im Ordner ``webif/static`` des Plugins abgelegt.
 