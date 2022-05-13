snmp
=========

Das SNMP-Plugin ermöglicht das Überwachen von Netzwerkgeräten mittels des SNMP Protokolls. Die Implementierung basiert auf den Python Package puresnmp.


Changelog
---------

1.1.0
~~~~~

-  Erweiterung der Datentypen
-  Erweiterung des WebIF

1.0.0
~~~~~

-  Erste Version

Anforderungen
-------------

Das Plugin benötigt die ``puresnmp``-Bibliothek.

Unterstützte Geräte
~~~~~~~~~~~~~~~~~~~

Jedes Netzwerkgerät, dass das SNMP Protokoll anbeitet, wird unterstützt.

Derzeit ist das Plugin mit folgenden Hardware gestestet:

Computer:

-  Raspberry Pi 3B


NAS:

-  QNAP NAS TS-251


Printer

-  Samsung ML-2070


Konfiguration
-------------

plugin.yaml
~~~~~~~~~~~

Die Konfiguration des Plugins bietet folgende Möglichkeiten:

snmp\_host
^^^^^^^^^^^^^^

IP-Adresse des Host, der per SNMP überwacht werden soll.


snmp\_commnity
^^^^^^^^^^^^^^

SNMP Community in der sich die Netzwerkgeräte befinden


Plugin-Konfiguration:
^^^^^^^^^^^^^^^^^^^^^

.. code:: yaml

    nas:
        plugin_name: snmp
        cycle: 300
        snmp_host: 192.168.2.9
        snmp_community: public
        instance: nas1


items.yaml
~~~~~~~~~~

Die Verknüpfung von SmartHomeNG-Items und SNMP OIDs ist vollständig flexibel und konfigurierbar. Mit den Item-Attributen kann das Verhalten des Plugins festgelegt werden.

Die folgenden Attribute werden unterstützt:

snmp\_oid
^^^^^^^^^^^^^^

Der Wert der angegebenen OID wird gelesen und dem Item zugewiesen.

.. code:: yaml

    item:
        snmp_oid@instance: '1.3.6.1.2.1.1.1.0'


snmp\_prop
^^^^^^^^^^^^^^

Der gelesene Rohwert wird gemäß dem angegebenen Parameterwert interpretiert.

.. code:: yaml

    item:        
        snmp_prop@instance: value

Zulässige Parameterwerte sind:

-  value: Der gelesene Rohwert wird in eine Zahl decodiert
-  string: Der gelesene Rohwert wird in einen Textstring decodiert.
-  hex-string: Der gelesene Rohwert in HEX wird in einen UTF-8 Textstring decodiert.
-  error-state: Der gelesene Rohwert (bytes) wird in einen Bitstring decodiert und die erste Postion eines "1"-bit ausgegeben.
-  mac-adress: Der gelesene Rohwert wird in eine MAC-Adresse decodiert.
-  ip-adress: Der gelesene Rohwert wird auf IP-Adressenformat geprüft und als String ausgegeben.


Beispiel
^^^^^^^^

Konfigurationsbeispiel:

.. code:: yaml

    nas:
        cpu_temp:
            name: CPU-Temperatur in °C
            type: num
            snmp_oid@nas1: '1.3.6.1.4.1.24681.1.2.5.0'
            snmp_prop@nas1: value

        cpu_usage:
            name: CPU-Auslastung [0-1]
            type: num
            snmp_oid@nas1: '1.3.6.1.4.1.24681.1.2.1.0'
            snmp_prop@nas1: value



Web-Interface
-------------

Im Web-Interface gibt es neben den allgemeinen Statusinformationen zum Plugin zwei Seiten.

Auf einer Seite werden die Items aufgelistet, die Plugin-Attributen konfiguriert haben. Damit kann eine schnelle Übersicht über die Konfiguration und die aktuellen Werte geboten werden.

Auf der zweiten Seite werden alle im aktuellen Befehlssatz enthaltenen Parameter aufgelistet.

