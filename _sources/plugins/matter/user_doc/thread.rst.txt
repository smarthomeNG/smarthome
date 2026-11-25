
.. index:: matter; Thread-Geräte anbinden
.. index:: matter; Thread Border Router
.. index:: matter; Bluetooth

===================
Thread-Geräte
===================

Matter-over-Thread-Geräte (Türkontakte, Hygrometer, viele batteriebetriebene Sensoren) brauchen
zusätzliche, physische Infrastruktur, die Matter-over-Wifi-Geräte (z.B. smarte Steckdosen) nicht
benötigen. Diese Seite beschreibt, was zusätzlich nötig ist und wie es eingerichtet wird.

Matter, Thread und Border Router: Begriffsklärung
====================================================

**Matter** ist der Anwendungs-Layer-Standard, den dieses Plugin implementiert - Gerätetypen,
Cluster, Befehle, Kommissionierung. Matter läuft immer über IP, benötigt aber einen
Transportweg darunter: WLAN, Ethernet oder Thread.

**Thread** ist einer dieser Transportwege - ein stromsparendes 802.15.4-Funk-Mesh-Netz mit
eigenem IPv6-Adressraum, für batteriebetriebene Geräte gedacht, für die WLAN zu stromhungrig
wäre. Thread-Geräte bilden untereinander ein eigenes Mesh, das nicht Teil des normalen LANs/WLANs
ist.

Ein **Thread Border Router (TBR)** verbindet dieses Thread-Mesh mit dem normalen IP-Netz
(Routing zwischen Thread und LAN, mDNS-Weiterleitung). Ohne TBR bleibt das Thread-Mesh vom Rest
des Netzes isoliert.

matter-server (der Sidecar dieses Plugins) ist ein Matter-**Controller** - er kommissioniert
Geräte und spricht die Matter-Anwendungsschicht, spannt aber selbst kein Netz auf. Bei
WLAN-Geräten verlässt er sich auf ein bereits bestehendes WLAN; bei Thread-Geräten entsprechend
auf einen bereits bestehenden, separat eingerichteten TBR. Der Rest dieser Seite beschreibt genau
diese zusätzliche, für Thread nötige Infrastruktur.

Übersicht: was zusätzlich benötigt wird
========================================

- Ein **Thread Border Router (TBR)**, bereits im lokalen Netz aktiv, bevor überhaupt ein
  Kopplungsversuch gestartet wird. matter-server (der Sidecar dieses Plugins) ist ein
  Matter-**Controller**, kein Border Router - er kann kein Thread-Netz selbst aufspannen.
- Ein **Bluetooth-Adapter** auf dem Host, auf dem dieses Plugin (server-Rolle) läuft - für die
  Erstkopplung neuer, noch nicht vernetzter Geräte (siehe unten, warum).
- **IPv6** im lokalen Netz, zumindest auf dem Segment, in dem der Border Router und der
  matter-server-Host stehen.

Ohne TBR schlägt jeder Kopplungsversuch eines Thread-Geräts fehl - unabhängig davon, ob Bluetooth
korrekt eingerichtet ist oder nicht.

Thread Border Router
=====================

.. index:: matter; OpenThread Border Router
.. index:: matter; OTBR

Zwei Wege:

- Ein **fertiges TBR-Gerät** (z.B. ein Zigbee/Thread-Hub eines Herstellers, oder ein
  Smart-Home-Hub mit eingebautem TBR). Keine weitere Einrichtung für dieses Plugin nötig - das
  TBR-Gerät kümmert sich selbst um das Thread-Netz, matter-server findet es über mDNS.
- **OpenThread Border Router (OTBR) selbst betreiben** - quelloffen, herstellerunabhängig, läuft
  als Docker-Container auf jedem Linux-Host (auch ohne Home Assistant). Der Rest dieses Abschnitts
  beschreibt diesen Weg.

Benötigte Hardware für einen selbst betriebenen OTBR
------------------------------------------------------

Ein **RCP-fähiger Funk-Stick** (Radio Co-Processor, mit ``ot-rcp``-Firmware, IEEE 802.15.4). Ein
bekannt funktionierendes Gerät: **ConBee III**.

.. warning::

   Nicht jeder "Zigbee/Thread-Stick" ist als eigenständiger TBR nutzbar - manche Hersteller-FAQs
   grenzen explizit ein, ob "nicht mit dem Hersteller-Hub nutzbar" bedeutet "gar nicht standalone
   möglich" oder nur "kein fertiges Komplettpaket ohne Zusatz-Software". Vor dem Kauf die genaue
   Formulierung der Hersteller-FAQ prüfen, nicht nur den Produktnamen.

Die **Baudrate** des Sticks muss zur ``OT_RCP_DEVICE``-Umgebungsvariable passen - sie ist nicht
für jeden Stick gleich. ConBee III läuft mit 115200, nicht mit der neueren OTBR-Standard-Baudrate
460800.

Docker-Setup
------------

.. code-block:: bash

   sudo mkdir -p /var/lib/otbr
   docker run --name=otbr --detach --network=host --cap-add=NET_ADMIN \
     --device=/dev/thread --device=/dev/net/tun \
     --volume=/var/lib/otbr:/data --env-file=otbr-env.list \
     --restart=always openthread/border-router

``/dev/thread`` durch den tatsächlichen Geräte-Pfad des RCP-Sticks ersetzen (z.B. per Udev-Regel
auf einen stabilen Namen fixieren, nicht auf ``/dev/ttyUSB0`` verlassen, das sich nach einem
Neustart ändern kann).

``otbr-env.list`` (Beispiel):

.. code-block:: text

   OT_RCP_DEVICE=spinel+hdlc+uart:///dev/thread?uart-baudrate=115200
   OT_INFRA_IF=eth0
   OT_THREAD_IF=wpan0
   OT_WEB_LISTEN_PORT=9090

``OT_INFRA_IF`` ist das Netzwerk-Interface, über das der Border Router das Thread-Netz mit dem
normalen LAN verbindet - i.d.R. das reguläre Ethernet/WLAN-Interface des Hosts.

.. note::

   ``OT_WEB_LISTEN_PORT`` ist optional und nur nötig, falls Port 8080 (OTBRs Standard für sein
   eigenes Web-Dashboard) bereits belegt ist. Betrifft nur das Dashboard, nicht die
   Kern-Funktionalität (Port 8081, REST-API) - ein Konflikt dort zeigt sich in den Logs als
   Absturz von ``otbr-web``, während ``otbr-agent`` normal weiterläuft.

.. important::

   Nur die Silicon-Labs-eigenen Images (``siliconlabsinc/openthread-border-router``) sind
   32-Bit-ARMv7-only. Auf einem 64-Bit-Host (arm64/x86_64) das generische
   ``openthread/border-router``-Image verwenden, nicht das Silicon-Labs-Image.

IPv6 auf dem Infra-Interface
------------------------------

.. index:: matter; IPv6 Thread

Der Border Router benötigt IPv6 auf ``OT_INFRA_IF`` - Thread selbst basiert auf IPv6.

.. warning::

   Zwei unterschiedliche, unabhängig voneinander wirkende sysctls können IPv6 auf einem
   Interface verhindern - ``disable_ipv6`` allein zu prüfen reicht nicht:

   - ``net.ipv6.conf.<interface>.disable_ipv6`` - der bekannte Ein/Aus-Schalter.
   - ``net.ipv6.conf.<interface>.addr_gen_mode`` - steuert, *wie* Adressen generiert werden. Wert
     ``1`` bedeutet "keine" - es werden **überhaupt keine** IPv6-Adressen erzeugt, nicht einmal
     eine Link-Local-Adresse, obwohl ``disable_ipv6`` auf ``0`` steht. ``ip -6 addr show
     <interface>`` zeigt dann eine komplett leere Liste.

   Bei fehlender IPv6-Adresse trotz ``disable_ipv6=0`` als nächstes ``addr_gen_mode`` prüfen:

   .. code-block:: bash

      sysctl net.ipv6.conf.<interface>.addr_gen_mode
      # 0 = EUI64 (normal), 1 = keine Adressen, 2 = stable-privacy, 3 = random
      sysctl -w net.ipv6.conf.<interface>.addr_gen_mode=0

Thread-Netzwerk aktiv bilden
------------------------------

Ein laufender OTBR-Container bedeutet nicht automatisch ein bestehendes Thread-Netz - beides
muss getrennt eingerichtet werden:

.. code-block:: bash

   docker exec otbr ot-ctl dataset init new
   docker exec otbr ot-ctl dataset commit active
   docker exec otbr ot-ctl ifconfig up
   docker exec otbr ot-ctl thread start
   docker exec otbr ot-ctl state

``state`` sollte nach kurzer Zeit ``leader`` zeigen. ``detached`` direkt nach ``thread start`` ist
normal (kurzer Übergangszustand) - nur wenn es dauerhaft bei ``detached`` bleibt, liegt ein
Problem vor (RCP-Kommunikation prüfen, ``docker logs otbr``).

.. warning::

   mDNS ist link-lokales Multicast (Port 5353) und überschreitet keine VLAN-/Subnetz-Grenzen,
   auch wenn Routing zwischen den Netzen erlaubt ist. Border Router und der matter-server-Host
   (dieses Plugin) müssen im selben Layer-2-Segment stehen, sonst findet matter-server den
   Border Router nicht - andernfalls ist zusätzlich ein mDNS-Reflektor (z.B. Avahi im
   Reflector-Modus) nötig.

Bluetooth für die Erstkopplung
=================================

.. index:: matter; Bluetooth Adapter
.. index:: matter; BLE Kommissionierung

Ein fabrikneues, noch nie gekoppeltes Matter-over-Thread-Gerät hat noch keine
Netzwerk-Zugangsdaten und ist daher noch nicht über IP erreichbar. Die Übergabe dieser
Zugangsdaten beim allerersten Pairing läuft über **Bluetooth Low Energy (BLE)**, nicht über das
Thread-Netz selbst. Ohne einen funktionierenden Bluetooth-Adapter auf dem matter-server-Host
lässt sich daher kein neues Thread-Gerät kommissionieren, unabhängig davon, wie gut der Border
Router eingerichtet ist.

Ein einfacher USB-BLE-Stick genügt (getestet: TP-Link UB500).

Einrichtung
-----------

1. HCI-ID des Adapters ermitteln (i.d.R. ``0`` für den einzigen/ersten Adapter, ``hci0``):

   .. code-block:: bash

      bluetoothctl list

2. Im Plugin-Instanz-Parameter ``server_bluetooth_adapter`` die HCI-ID eintragen (als String,
   z.B. ``'0'`` - **nicht** die MAC-Adresse).

.. important::

   Ohne gesetzten ``server_bluetooth_adapter`` bleibt BLE deaktiviert und ein neues
   Thread-Gerät kann nicht kommissioniert werden, selbst mit korrekt funktionierender Hardware.

Bekannte Bluetooth-Stolperfallen unter Linux
-----------------------------------------------

.. warning::

   **Fehlende Adapter-Firmware.** Günstige USB-BLE-Sticks mit Realtek-Chipsatz (z.B. RTL8761B,
   u.a. im TP-Link UB500 verbaut) benötigen eine separate, proprietäre Firmware-Datei, die
   Debian/Devuan nicht standardmäßig installiert:

   .. code-block:: bash

      sudo apt-get install firmware-realtek

   Diese liegt in der ``non-free-firmware``-Repository-Komponente (Debian 12/"bookworm" und
   neuer; ältere Versionen nutzen ``non-free``) - ggf. erst in den apt-Quellen aktivieren. Ohne
   die Firmware zeigt ``dmesg`` einen Fehler wie ``firmware: failed to load rtl_bt/...`` - der
   Adapter wird als ``hci0`` erkannt, aber die Firmware-Initialisierung schlägt fehl. Nach der
   Installation den Stick einmal ab- und wieder anstecken (oder ohne physischen Zugriff per
   Treiber-Rebind: ``echo -n "<bus-id>:1.0" > /sys/bus/usb/drivers/btusb/unbind`` gefolgt von
   ``bind`` mit derselben ID).

   **Fehlende Root-Rechte für Raw-Sockets.** Ohne die Capability ``cap_net_raw`` auf dem
   tatsächlich verwendeten Node.js-Binary bleibt BLE-Scanning wirkungslos - **ohne jede
   Fehlermeldung**, das Scannen startet einfach nie:

   .. code-block:: bash

      sudo setcap cap_net_raw+eip <pfad-zum-node-binary>
      getcap <pfad-zum-node-binary>

   Den tatsächlich verwendeten Pfad über den laufenden Prozess ermitteln, nicht per ``which
   node`` raten - beides kann sich unterscheiden, je nachdem, welche Umgebung shng beim Start
   tatsächlich verwendet:

   .. code-block:: bash

      pgrep -f MatterServer.js
      readlink -f /proc/<pid>/exe

   **Adapter nicht eingeschaltet.** Der Raw-HCI-Modus (Linux-Standardverhalten von matter.js)
   schaltet einen ausgeschalteten Adapter nicht selbst ein:

   .. code-block:: bash

      sudo hciconfig hci0 up
      hciconfig hci0
      # Flags-Zeile muss "UP RUNNING" enthalten

Thread-Netzwerk-Zugangsdaten im Plugin registrieren
======================================================

.. index:: matter; Thread Netzwerk-Zugangsdaten

Selbst mit funktionierendem Bluetooth scheitert die Kommissionierung eines Thread-Geräts ohne
einen weiteren, einmaligen Schritt: matter-server muss wissen, welche Zugangsdaten es dem Gerät
für das Thread-Netz übergeben soll. Diese werden **nicht automatisch** vom Border Router
übernommen - sie müssen einmalig eingetragen werden.

Im Webinterface unter "Thread Netzwerk-Zugangsdaten" gibt es dafür zwei Wege:

- **Automatisch vom Border Router abrufen** (Button "Automatisch vom Border Router abrufen").
  Holt das aktive Dataset per ``GET /node/dataset/active`` direkt von OTBRs eigener REST-API und
  registriert es. Setzt voraus, dass der Plugin-Parameter ``server_otbr_rest_url`` auf eine vom
  shng-Host aus erreichbare OTBR-REST-API zeigt - der Default ``http://localhost:8081`` passt,
  wenn OTBR auf demselben Host wie shng läuft. Der Button erscheint nur, wenn dieser Parameter
  nicht leer ist.
- **Manuell eintragen**, falls OTBRs REST-API vom shng-Host aus nicht erreichbar ist (anderer
  Host, abweichender Port, Firewall):

  1. Aktives Dataset des Border Routers auslesen (Hex-Format):

     .. code-block:: bash

        docker exec otbr ot-ctl dataset active -x

  2. Den Hex-String in das Eingabefeld eintragen und absenden.

Die Zugangsdaten werden dauerhaft in matter-servers eigenem Speicher abgelegt (kein erneutes
Eintragen nach einem Neustart nötig) - eine einmalige Einrichtung pro Thread-Netz, kein Schritt
pro Gerät. Solange nichts gesetzt ist, zeigt der Devices-Tab ein Eingabefeld; danach zeigt der
Tabellenkopf oben auf der Seite stattdessen "Gesetzt" mit einer Löschen-Option (zum bewussten
Zurücksetzen, z.B. bei einem Netz-Wechsel).

Fehlerbilder bei fehlgeschlagener Kommissionierung
======================================================

Zwei deutlich unterschiedliche Fehler weisen auf unterschiedliche fehlende Voraussetzungen hin:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Fehlermeldung
     - Bedeutung
   * - ``No commissionable device was discovered``
     - Das Gerät wurde über keinen Kanal (weder Netzwerk noch Bluetooth) überhaupt gefunden.
       Meist: Gerät nicht (mehr) im Pairing-Modus, zu weit vom Bluetooth-Adapter entfernt,
       falscher Code eingegeben, oder Bluetooth ist nicht aktiv (siehe oben).
   * - ``No Wi-Fi/Thread network credentials are configured for commissioning...``
     - Bluetooth-Pairing war erfolgreich (Gerät ist bereits kryptografisch in shngs Fabric
       aufgenommen), aber es wurden keine Netzwerk-Zugangsdaten übergeben. Thread
       Netzwerk-Zugangsdaten (siehe oben) registrieren.

Bekannte Probleme
====================

node-gyp unter Debian/Devuan
------------------------------

.. index:: matter; node-gyp

Betrifft nicht nur dieses Plugin, sondern jeden nativen Node.js-Baustein, der während ``npm
install`` kompiliert werden muss (u.a. die BLE-Anbindung) - ein bekanntes
Debian/Devuan-Paketierungsproblem, kein Fehler dieses Plugins.

Debian/Devuan liefert ein eigenes, entkerntes ``node-gyp`` aus (``/usr/share/nodejs/node-gyp``),
das ein separates, nicht immer mitinstalliertes Python-Modul voraussetzt. Symptom:

.. code-block:: text

   ModuleNotFoundError: No module named 'gyp'

Da fehlgeschlagene optionale npm-Abhängigkeiten standardmäßig **stillschweigend** übersprungen
werden, erscheint ohne Weiteres gar keine Fehlermeldung - nur ein fehlendes Verzeichnis in
``node_modules``. Den eigentlichen Fehler sichtbar machen:

.. code-block:: bash

   npm install --foreground-scripts

.. warning::

   Ein global installiertes, aktuelles ``node-gyp`` (``npm install -g node-gyp``) behebt dies
   **nicht zuverlässig** - Debians eigenes npm ruft für automatisch getriggerte Builds
   weiterhin sein eigenes, systemweites ``node-gyp`` auf, unabhängig von ``$PATH``.

Stattdessen das fehlende Python-Modul in genau dem Python installieren, das node-gyp tatsächlich
verwendet - dessen eigene Log-Ausgabe zeigt den genauen Pfad (``gyp info find Python using ...
found at "..."``). Läuft eine virtuelle Umgebung (venv), reicht ein systemweites ``apt install
gyp`` **nicht** - venvs sind bewusst vom System-Python isoliert:

.. code-block:: bash

   <pfad-zum-python-des-venvs>/bin/pip install gyp-next

Multicast-Fehler (EHOSTUNREACH) auf macOS
---------------------------------------------

Falls matter-server auf macOS beim Senden von Multicast-Paketen mit ``EHOSTUNREACH`` fehlschlägt:
in einem konkreten Fall lag die Ursache nicht bei Little Snitch (auch mit einer expliziten
Erlauben-Regel für alle Prozesse im lokalen Netz), nicht an Parallels' virtuellen
Netzwerk-Interfaces (auch nach vollständigem Beenden von Parallels reproduzierbar) und nicht an
einer systemweiten Multicast-Sperre (funktionierender ``dns-sd``-Eigentest parallel dazu). Die
wahrscheinlichste verbleibende Ursache ist eine Eigenheit des jeweiligen Netzwerks selbst (z.B.
Client-Isolation in Gäste-/öffentlichen WLANs) - bei diesem Fehlerbild lohnt sich ein Test in
einem anderen Netz, bevor eine Software-Ursache vermutet wird.
