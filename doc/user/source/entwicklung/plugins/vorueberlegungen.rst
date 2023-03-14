
===============
Vorüberlegungen
===============

Fragestellungen
===============

Bevor die Erstellung eines Plugins beginnt, muss man sich einige Fragen stellen und beantworten:

- Welchen Typ soll das Plugin haben, welches erstellt werden soll?
- Soll das Plugin über MQTT mit dem/den anzusteuernden Device(s) kommunizieren?
- Soll das externe System direkt angesteuert werden oder soll auf existierende Python Packages zurück gegriffen werden?
- Unter welcher Python Version soll das Plugin laufen?

|

Typ des Plugins
===============

In SmartHomeNG gibt es folgende Plugin Typen:

System Plugin
-------------

System Plugins steuern keine externen Devices an, sondern erweitern die Funktionalität von SmartHomeNG.

Beispiele für System Plugins sind: **cli**, **database** oder **stateengine**


Interface Plugin
----------------

Ein Interface Plugin verbindet SmartHomeNG mit genau einem externen Device. Beispiele sind Plugins, die über eine
serielle Schnittstelle kommunizieren.

Es können aber auch Devices sein, die das Netzwer oder ein Bus System kommunizieren, wenn das Plugin nur genau **ein**
Device ansteuern kann. Ein Interface Plugin kann als Multi-Instance Plugin ausgelegt werden. Dann kann je Instanz ein
Device angeseteuert werden.

Beispiele für Interface Plugins sind: **avdevice** oder **viessmann**


Gateway Plugin
--------------

Ein Gateway Plugin verbindet SmartHomeNG mit mit einer Reihe von externen Devices, die über die selbe Art kommunizieren.
Diese Plugins sprechen ein Gateway an, welches dann über ein Bussystem die eigentlichen Devices anspricht (z.B. KNX,
Philips Hue oder Homematic).

Bei Gateway Plugins wird über ein Item Attribut gesteuert, welches Device angesprochen werden soll.

Beispiele für Gateway Plugins sind: **knx**, **hue2**, **onewire** oder **tasmota**


Protokoll Plugin
----------------

Protokoll Plugins steuern keine Devices direkt an, sondern ermöglichen die Kommunikation über ein Protokoll.

Beispiele für Protokoll Plugins sind: **mqtt**, **network**, **snmp** oder **wol**


Web/Cloud Plugin
----------------

Web/Cloud Plugins kommunizieren mit Web- bzw. Cloud Diensten, um Informationen in SmartHomeNG einzulesen bzw.
Informationen aus SmartHomeNG auszugeben.

Beispiele für Web/Cloud Plugins sind: **alexa4p3**, **ical**, **jsonread** oder **piratewthr**

|

Plugin Vorlagen
===============

Um ein neues Plugin zu erstellen, ist es am besten die Vorlage zu verwenden, die unter /dev/sample_plugin zu finden ist.
Falls das Plugin über MQTT kommunizieren soll, ist es besser, die Vorlage zu verwenden, die unter /dev/sample_mqttplugin
zu finden ist.

Falls über MQTT kommuniziert werden soll, wäre es für einfache Aufgabenstellungen auch zu überlegen, kein eigenes Plugin
zu schreiben, sondern das generische mqtt Plugin zu nutzen.

|

Nutzung von Python Packages
===========================

Die Frage, ob fertige 3rd Party Packages eingesetzt werden sollen, ist gut abzuwägen. Als Vorteil ist anzuführen,
dass man sich evtl. erhebliche Programmierung spart. Allerdings kommt es immer wieder vor, dass Python Packages im
Zuge ihrer Weiterentwicklung Breaking Changes einführen und bei Einsatz dieser neuen Package Version (z.B. bei
einer Neuinstallation von SmartHomeNG), das Plugin plötzlich und unerwartet nicht mehr funktioniert.

Die Angabe einer bestimmten Version eines eingesetzten Packages ist jedoch auch keine Lösung, da Requirements aus
anderen Plugins oder auch Requirements in anderen eingesetzten Packages evtl. dazu führen, dass es keine geeignete
Package Version mehr gibt, die installiert werden könnte.


Python Version
==============

Je nachdem unter welcher Python Version SmartHomeNG läuft, stehen Python Features zur Verfügung, oder eben auch nicht.
Es sollten nach Möglichkeit nur Python Features genutzt werden, die bereits in der ältesten von SmartHomeNG
unterstützten Python Version (siehe :ref:`Hard- u. Software Anforderungen <python_versionen>`) zur Verfügung stehen.
Dadurch ist das Plugin am felxibelsten einsetzbar.

Sollte auf ein Python Features zurück gegriffen werden (müssen), welches erst in neueren Python Versionen zur
Verfügung steht, ist es wichtig, die minimale Python Version unter der das Plugin lauffähig ist, in den Metadaten
in der Datei plugin.yaml des Plugins anzugeben.

Sollte auf ein Python Features zurück gegriffen werden (müssen), welches in neueren Python nicht mehr zur Verfügung
steht, ist es wichtig, die maximale Python Version unter der das Plugin lauffähig ist, in den Metadaten
in der Datei plugin.yaml des Plugins anzugeben.

