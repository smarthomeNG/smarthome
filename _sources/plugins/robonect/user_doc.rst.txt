.. index:: Plugins; robonect
.. index:: robonect

========
robonect
========

Das Plugin liest Daten von Mährobotern mit Robonect Hx-Modul (Husqvarna, Gardena, Flymo,
McCulloch) aus und kann den Mäher darüber hinaus auch steuern, soweit die Robonect-API dies
unterstützt.

Voraussetzungen
================

Für den Betrieb wird ein Mähroboter mit installiertem Robonect Hx-Modul benötigt, siehe
`robonect.de <https://robonect.de/>`_ bzw. das zugehörige `Forum <https://forum.robonect.de/>`_.
Andere Module desselben Herstellers funktionieren unter Umständen ebenfalls.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/robonect`
beschrieben.

Item-Attribute
--------------

**robonect_data_type** ordnet ein Item einem bestimmten Wert des Robonect-Moduls zu; die
unterstützten Werte lassen sich am einfachsten über die mitgelieferten Item-Structs nutzen, siehe
:doc:`/plugins_doc/config/robonect`.

**robonect_battery_index** und **robonect_remote_index** werden nur für Items benötigt, deren
**robonect_data_type** sich auf eine bestimmte Batterie (``battery_*``) bzw. einen bestimmten
Fernstart-Punkt (``remotestart_*``) bezieht; sie geben an, welche Batterie (beginnend bei 0) bzw.
welcher Fernstart-Punkt (1 oder 2) gemeint ist.

Die Items **control** und **control/mode** aus dem mitgelieferten Item-Struct lassen sich
beschreiben, um den Mäher direkt zu steuern (**control**: start/stop, **control/mode**:
home/eod/man/auto). Das funktioniert allerdings nur, wenn das Plugin im MQTT-Modus
(**mode: mqtt**) läuft. Im API-Modus stehen dafür stattdessen die Plugin-Funktionen zur Verfügung,
siehe Webinterface, Tab **Plugin-API**.

Web Interface
=============

Das Webinterface zeigt oben allgemeine Statusinformationen (Erreichbarkeit, Status, Modus) sowie
Schaltflächen, mit denen der Betriebsmodus (**AUTO**, **HOME**, **EOD**, **MANUAL**) direkt
umgeschaltet werden kann.

Im ersten Tab werden alle vom Plugin genutzten Items mit ihren aktuellen Werten angezeigt.

Der Tab **Fehlercodes** zeigt die vom Mäher gemeldete Fehlerhistorie.

Der Tab **Plugin-API** listet die vom Plugin bereitgestellten, aus Logiken aufrufbaren Funktionen
mit Beschreibung und Parametern auf.
