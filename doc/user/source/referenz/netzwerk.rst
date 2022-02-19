
.. index:: Referenz; Netzwerk
.. Index:: Netzwerk; Referenz

.. role:: bluesup
.. role:: greensup
.. role:: redsup


======================
Netzwerk :redsup:`Neu`
======================

Hier sind einige Informationen über die Netzwerk Nutzung durch SmartHomeNG zusammengestellt.

SmartHomeNG nutzt bisher IP v4. Es ist noch nicht durchgängig IP v6 fähig.


Ports
=====

Folgende Ports werden durch SmartHomeNG auf dem System geöffnet. Aufgelistst sind die Standard Ports. Alle Ports
können frei konfiguriert werden.

.. csv-table:: Port Nutzung durch SmartHomeNG
  :header: "Port", "Prozess", "Modul/Plugin", "Config Parameter", "Verwendung"
  :widths: 13, 22, 31, 25, 60

  "2424",  "SmartHomeNG",     "websocket Modul",     "port",         "ws:// für die smartVISU"
  "2425",  "SmartHomeNG",     "websocket Modul",     "tls_port",     "wss:// für die smartVISU (falls aktiviert)"
  "2727",  "SmartHomeNG",     "network Plugin",      "port",          "Eingehende TCP oder UDP Kommunikation"
  "8383",  "SmartHomeNG",     "http Modul",          "port",         "http:// für die Admin GUI und Webinterfaces"
  "8384",  "SmartHomeNG",     "http Modul",          "servicesport", "Webservices"
  "8385",  "SmartHomeNG",     "http Modul",          "tls_port",     "https:// für die Admin GUI und Webinterfaces (falls aktiviert)"


Die folgenden Dienste können auf dem System auf dem SmartHomeNG läuft installiert sein oder auf anderen Rechnern.
Falls diese Dienste auch auf dem SmartHomeNG System installiert/gestartet sind, sind zusätzlich folgende Ports
geöffenet:

.. csv-table:: Port Nutzung durch weitere Dienste
  :header: "Port", "Prozess", "Software", "Verwendung"
  :widths: 13, 22, 32, 85

  "1883",  "Mosquitto",  "MQTT Broker",                "Broker zur Nutzung des MQTT Protokolls über TCP"
  "4304",  "owserver",   "1-wire control Daemon",      "Ansteuerung des 1-Wire Bus Systems"
  "6600",  "mpd",        "Music Player Daemon",        "Wiedergabe von Musik über Audio Peripherie eines Linux Systems"
  "6720",  "knxd",       "KNX Daemon",                 "Kommunikation zu KNX Interface oder KNX Router"
  "8883",  "Mosquitto",  "MQTT Broker",                "Secure MQTT über TCP (falls konfiguriert)"

