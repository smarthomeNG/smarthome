.. index:: Plugins; ksemmodbus
.. index:: ksemmodbus

==========
ksemmodbus
==========

Das Plugin liest die Messwerte eines Kostal Smart Energy Meter über Modbus TCP aus und stellt sie
als Items in SmartHomeNG zur Verfügung.


Voraussetzungen
================

Es wird ein Kostal Smart Energy Meter benötigt, der über das Netzwerk per Modbus TCP erreichbar ist.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/ksemmodbus` beschrieben.

Als Vorlage für die Item-Konfiguration liefert das Plugin die Datei
``ksemmodbus/files/kostal_item_template.yaml`` mit, die nach ``items`` kopiert und angepasst werden kann.


Item-Attribute
---------------

Jedes Item-Attribut entspricht einer Modbus-Registeradresse des Smart Energy Meter:

========  ================  ======  =======
Attribut  Bedeutung         Format  Einheit
========  ================  ======  =======
ksem_0    Wirkleistung +    U32     W
ksem_2    Wirkleistung -    U32     W
ksem_4    Blindleistung +   U32     var
ksem_6    Blindleistung -   U32     var
ksem_16   Scheinleistung +  U32     VA
ksem_18   Scheinleistung -  U32     VA
ksem_24   Leistungsfaktor   Float   -
ksem_512  Wirkarbeit +      U64     Wh
ksem_516  Wirkarbeit -      U64     Wh
ksem_520  Blindarbeit +     U64     varh
ksem_524  Blindarbeit -     U64     varh
ksem_544  Scheinarbeit +    U64     VAh
ksem_548  Scheinarbeit -    U64     VAh
========  ================  ======  =======
