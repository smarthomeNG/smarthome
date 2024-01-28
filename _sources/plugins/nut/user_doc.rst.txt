.. index:: Plugins; nut
.. index:: nut

===
nut
===

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left


Anforderungen
=============

NUT - Network UPS Tools zur Anbindung von Unterbrechungsfreien Stromversorgunen (USV), englisch Uninterruptible Power Supply (UPS). 
Die Anbindung wird über einen NUT Daemon realisiert.



Notwendige Software
-------------------

keine

Unterstützte Geräte
-------------------

z.B. jede USV hinter einer Synology. Die Synology DiskStation übernimmt in diesem Fall den NUT Server 


Konfiguration
=============

plugin.yaml
-----------

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


items.yaml
----------

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


logic.yaml
----------

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Funktionen
----------

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Beispiele
=========

Anwendungsbeispiel einer USV in Verbindung mit einem Synology NUT Deamon:

.. code:: yaml

    ups:  
        status:
            name: Status
            type: str
            nut_var: ups.status
            online:
                type: bool
                eval_trigger: ups.status
                eval: 1 if 'OL' in sh.ups.status() else 0
                cache: True
            on_battery:
                type: bool
                eval_trigger: ups.status
                eval: 1 if 'OB' in sh.ups.status() else 0
                cache: True
            low_battery:
                type: bool
                eval_trigger: ups.status
                eval: 1 if 'LB' in sh.ups.status() else 0
                cache: True
            charging:
                type: bool
                eval_trigger: ups.status
                eval: 1 if 'CHRG' in sh.ups.status() else 0

        battery:
            percent:
                type: num
                nut_var: battery.charge


Synology Beispiel
=================

Dieses Plugin kann direkt mit einer Synology Diskstation genutzt werden, die in diesem Fall als NUT Server fungiert. Die USV ist dabei per USB mit der Synology verbunden.
Die Synology Diskstation stellt jetzt den USV Status als NUT Server bereit. Um den NUT Server auf der Synology zu aktivieren

1) Aktiviere die NUT Option unter "Hardware and Energy"-> UPS-> "active network UPS server"
2) Klick auf "Authenticated Diskstation devices" und trage dort die IP des SmarthomeNG Rechners ein. Hierbei handelt es sich um eine White List, d.h. eine Liste aller 
   vertrauenswürdigen IPs, die der NUT Server bedient.
3) Aktiviere das NUT Plugin auf smarthomeNG Seite


Web Interface
=============

nicht vorhanden.


Versionshistorie
================

