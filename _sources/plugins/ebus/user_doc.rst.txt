.. index:: Plugins; ebus
.. index:: ebus


====
ebus
====

Dieses Plugin verbindet sich zu einem ebus daemon und kann über diesen mit Geräten mit eBus Schnittstellen kommunizieren.

Anforderungen
=============

Eine ebus Schnittstelle

Notwendige Software
-------------------

Ein konfigurierter und funktionierender ebus Daemon der im Netzwerk erreichbar ist.

Unterstützte Geräte
-------------------

Beispielsweise Geräte von Vaillant, Wolf, Kromschroeder und andere die über eine ebus Schnittstelle kommunizieren können.


Konfiguration
=============

Die Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/ebus` beschrieben.


plugin.yaml
-----------

Zu den Informationen, welche Parameter in der ../etc/plugin.yaml konfiguriert werden können bzw. müssen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/ebus>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

items.yaml
----------

Zu den Informationen, welche Attribute in der Item Konfiguration verwendet werden können bzw. müssen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/ebus>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

logic.yaml
----------

Zu den Informationen, welche Konfigurationsmöglichkeiten für Logiken bestehen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/ebus>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

Funktionen
----------

Zu den Informationen, welche Funktionen das Plugin bereitstellt (z.B. zur Nutzung in Logiken), bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/ebus>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

Beispiele
=========

.. code:: yaml

   ebus_geraet:

       hk_pumpe_perc:
           type: num
           knx_dpt: 5
           knx_send: 8/6/110
           knx_reply: 8/6/110
           ebus_cmd: cir2 heat_pump_curr
           ebus_type: get
           # akt. PWM-Wert Heizkreizpumpe

       ernergie_summe:
           type: num
           knx_dpt: 12
           knx_send: 8/6/22
           knx_reply: 8/6/22
           ebus_cmd: mv yield_sum
           ebus_type: get
           # Energieertrag

       speicherladung:
           type: bool
           knx_dpt: 1
           knx_listen: 8/7/1
           ebus_cmd: short hw_load
           ebus_type: set
           # Quick - WW Speicherladung


Web Interface
=============

Das Plugin hat derzeit kein Web Interface