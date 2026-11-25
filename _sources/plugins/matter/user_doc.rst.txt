.. index:: Plugins; matter
.. index:: matter

======
matter
======

Matter-Plugin für SmartHomeNG mit zwei unabhängigen Rollen: **server** (kommissioniert und steuert
echte Matter-Geräte direkt - ohne separaten Hub/Bridge/App) und **bridge** (macht shng-Items als
eigene "Geräte" für andere Matter-Ökosysteme sichtbar - Apple Home, Google Home, ...).
Beide Rollen laufen in derselben Plugin-Instanz und werden über ``server_enabled``/``bridge_enabled``
einzeln aktiviert. Sie laufen unabhängig voneinander: fällt eine Rolle aus (z.B. fehlende
Sidecar-Datei), läuft die andere weiter; ein Absturz startet nur die betroffene Rolle neu. Items mit
Attributen einer deaktivierten Rolle werden ignoriert, beim Start erscheint dazu eine Warnung.

Wird shng hart beendet, können die Node.js-Prozesse weiterlaufen. Ihre PID liegt jeweils im
Storage-Verzeichnis der Rolle; ein solcher übrig gebliebener Prozess wird beim nächsten Start
beendet, bevor ein neuer gestartet wird.

Voraussetzungen
===============

Dieses Plugin hat eine Laufzeitabhängigkeit außerhalb von Python (Node.js) und startet zwei
separate Node.js-Prozesse, einen pro Rolle - beide benötigen eine unterstützte Node.js-Version
(``>=20.19.0 <22.0.0 || >=22.13.0``). Mit ``nvm``::

    nvm install lts/jod
    nvm use lts/jod

Beide Rollen teilen sich ein gemeinsames Node.js-Dependency-Verzeichnis, es genügt eine
einzige Installation::

    cd plugins/matter/sidecar
    npm install

Das installiert sowohl den matter-server-Sidecar als auch die von ``bridge.js`` benötigten Pakete.

Matter-over-Thread-Geräte anbinden
===================================

Türkontakte, Hygrometer und ähnliche batteriebetriebene Sensoren nutzen meist Thread statt Wifi
und benötigen dafür zusätzliche, physische Infrastruktur (einen Thread Border Router, einen
Bluetooth-Adapter) sowie einen einmaligen Einrichtungsschritt im Webinterface.

Grund für den Unterschied: Wifi-Geräte hängen direkt im bestehenden LAN/WLAN, das matter-server
ohnehin schon erreicht - keine weitere Einrichtung nötig. Thread-Geräte bilden dagegen ihr
eigenes, vom LAN getrenntes Funk-Mesh; ohne eine Brücke dorthin (Thread Border Router) bleiben
sie für matter-server unerreichbar, unabhängig von allem anderen in diesem Plugin. Details:

.. toctree::
   :maxdepth: 1
   :titlesonly:

   user_doc/thread

Konfiguration
=============

Siehe plugin.yaml für die vollständige Parameterliste. 

Item-Attribute
--------------

``matter_node``, ``matter_endpoint``, ``matter_cluster`` adressieren eine bestimmte Gerätefunktion. 
Diese drei müssen nur einmal am Hauptitem eines Geräts gesetzt werden und werden an alle Kind-Items
vererbt.

Für einen Schalter (matter-intern bool-Item im On/Off-Schema, z.B. OnOff) wird ``matter_switch: true``
verwendet. Für alles andere werden die Low-Level-Attribute direkt verwendet: ``matter_attribute``
macht das Item zu einem Read-/Subscribe-Spiegel dieses Attributs. ``matter_command`` (optional mit
``matter_command_params``) lässt eine Änderung des Itemwerts den entsprechenden Befehl auslösen; der
Platzhalter ``"$value"`` in einem Parameterwert wird durch durch den geschriebenen Item-Wert
ersetzet (z.B. für den ``level``-Parameter von ``MoveToLevel``). ``matter_attribute`` und
``matter_command`` können am selben Item gesetzt werden (spiegelt den Status per Subscription, steuert
ihn per Befehl beim Schreiben).

Ein reines Befehls-Item ohne passendes Status-Attribut (z.B. ``toggle``) schreibt immer nur True oder 1
und benötigt daher ``enforce_updates: true`` und ggf. einen ``autotimer``, der ihn wieder auf False oder
0 zurücksetzt.

``matter_available`` (bool, read-only) gibt an, ob das Gerät für den matter-server erreichbar ist.

Geräte dauerhaft benennen: matter_alias
---------------------------------------

``node_id`` wird von matter-server zum Kommissionierungszeitpunkt vergeben und ist über einen
Dekommissionierungs-/Rekommissionierungszyklus hinweg nicht garantiert stabil (Werksreset eines
Geräts, Wechsel von und wieder auf shngs Fabric, ...). Jedes über ein fest eingetragenes
``matter_node`` adressierte Item zeigt danach still auf das falsche Gerät, bis es von Hand
aktualisiert wird.

``matter_alias`` kann statt ``matter_node`` verwendet werden, um einen lesbaren Namen zu benutzen.

Die Zuordnung zu der jeweiligen ``matter_node`` erfolgt im Web-Interface und wird **durch das Plugin**
in Items unterhalb von ``server_alias_base_item`` gesichert. Jedes direkte Kind-Item davon gilt als
eine Alias-Definition. Die ``node_id`` eines Items wird dann bei jedem Zugriff über diese Tabelle 
aufgelöst, statt fest codiert zu sein. Das Basis-Item selbst muss bereits existieren, das Plugin 
legt es nicht selbst an. Das Umleiten eines Alias im Webinterface wirkt sofort, ohne Neustart.
Schreibzugriffe auf Items, deren Alias nicht (mehr) existiert, werden mit einer Fehlermeldung
verworfen.

Kopplung
--------

Eine Kopplung über den Pairing-Code läuft im Hintergrund und kann einige Minuten dauern
(``server_commission_timeout``). Das Webinterface zeigt ihren Status laufend an und meldet das
Ergebnis, sobald es vorliegt.

bridge-Rolle: shng-Items für andere Matter-Ökosysteme sichtbar machen
=====================================================================

Die bridge-Rolle stellt shng-Items als gebrückte Gerätefunktionen für andere Matter-Controller wie 
Apple Home bereit.

``matter_expose_type`` an einem Item definiert seine matter-Funktion. Der Item-Typ muss dazu passen,
sonst wird das Item mit einer Fehlermeldung ignoriert:

- ``switch`` (Item-Typ ``bool``) - ein schreibbarer bool-Aktor (``OnOffPlugInUnit``). Vom anderen Controller aus
  beschreibbar; ein Schreiben dort löst über den üblichen Item-Update-Mechanismus zurück ins Item
  aus, und eine Item-Wertänderung wird genauso an den anderen Controller weitergegeben.
- ``contact`` (Item-Typ ``bool``) - ein reiner bool-Sensor (``ContactSensor``, z.B. ein Türkontakt), der Werte wird nur 
  von SmartHomeNG aus weitergegeben, es ist keine Änderung über Matter möglich.
- ``temperature_sensor`` (Item-Typ ``num``) - ein reiner Sensor (``TemperatureSensor``), analog zu ``contact``. 
  Der Item-Wert wird als Grad Celsius interpretiert.

``matter_expose_name`` (optional) legt den Namen fest, der dem anderen Controller angezeigt wird.
Ohne ihn wird der vollständige Item-Pfad verwendet.

Das Koppeln der bridge mit dem Fabric eines anderen Controllers (Apple Home, Google Home, ...) 
benötigt den Code oder QR-Code des Bridge-Webinterfaces. Da die bridge nur ein Entwicklungs-/Test-
Attestierungszertifikat (nicht CSA-zertifiziert) hat, zeigen die meisten Controller während der
Kopplung eine Warnung "nicht zertifiziertes Zubehör" an.

Änderungen an ``matter_expose_*``-Attributen werden üblicherweise innerhalb weniger Sekunden über
matter an gekoppelte Controller verteilt. 

Item-Structs
============

``item_structs`` in ``plugin.yaml`` enthält generische Vorlagen pro Cluster (``switch``,
``electrical_power_measurement``, ``contact``, ``temperature_sensor``, ``humidity_sensor``,
``battery``) und darauf aufbauende Vorlagen für getestete Geräte. Am anwendenden Item werden
``matter_node`` und ggf. ``matter_endpoint`` gesetzt. Gerätevorlagen bisher:

- ``matter.shelly_plug_m_3gen_simple`` (OnOff-Schalter/Toggle + Verfügbarkeit)
- ``matter.shelly_plug_m_3gen`` (zusätzlich mit Messung von Leistung/Spannung/Strom)

Im Test stellte sich heraus, dass die Spannungswerte über Matter nicht immer live übertagen wurden,
obwohl diese im Gerät vorliegen und z.B. über MQTT sehr wohl übertragen werden. Dies sollte im
Zweifelsfall selbst geprüft werden.

Mehrere Instanzen
=================

Jede Instanz ist eine eigene Matter-Fabric und eine eigene bridge. Ports, Storage-Verzeichnisse,
``server_alias_base_item`` und ``server_generated_items_base`` müssen sich zwischen Instanzen
unterscheiden (siehe plugin.yaml). Item-Attribute einer Instanz tragen deren Namen
(``matter_node@<instanz>``); Structs werden mit ``@<instanz>`` referenziert, ihre Attribute erhalten
den Instanz-Namen dann automatisch::

    kueche_steckdose:
        struct: matter.shelly_plug_m_3gen@zweite
        matter_node@zweite: 3

Die über "Item erstellen" erzeugten Items verwenden diese Form automatisch. Die bridge einer
benannten Instanz meldet sich mit der Kennung ``shng-bridge-<instanz>`` (bei sehr langen
Instanz-Namen gekürzt und um einen kurzen Hash ergänzt); die Standard-Instanz behält ihre bisherige
Kennung.

Ein Gerät mit Apple Home / Google Home usw. teilen
==================================================

Matter-Geräte unterstützen die gleichzeitige Verbindung zu mehreren Controllern - ein mit shng
gekoppeltes Gerät kann auch einem anderen Ökosystem auf dessen separaten Fabric beitreten, ohne
dass shng seine eigene Kopplung verliert. Der **Teilen**-Button im Devices-Tab öffnet auf diesem
Gerät ein neues 15-minütiges Kopplungsfenster und zeigt sowohl einen scanbaren QR-Code als auch 
den manuellen Pairing-Code (und den rohen QR-Inhalts-String) zur Eingabe in der anderen App.

Der **Fabrics**-Button listet jede aktuell auf einem Gerät vorhandene Fabric (Vendor, Label,
fabric_id) mit einer Entfernen-Option je Fabric. Für das Entfernen aus dem shng-Fabric sollte
der **Entfernen**-Button verwendet werden.

Aktueller Umfang
================

**server-Rolle**:

- Sidecar-Prozessüberwachung (automatischer Neustart mit Backoff)
- WebSocket-Client zu matter-server (Kommissionierung, Attribut-Lesen/Schreiben, Befehle,
  Subscriptions)
- Item-Mapping: generische ``matter_attribute``/``matter_command``-Attribute sowie die
  ``matter_switch``-Kurzform für bool-On/Off-Cluster
- ``matter_alias``: node_id-Indirektion für eine über Rekommissionierung hinweg stabile
  Item-Zuordnung
- Endpoint-/Cluster-Discovery-Browser (Discovery-Tab)
- Item-Vorschlag pro Gerät: Copy-Paste-YAML oder direktes Anlegen als echte Items
  ("Item erstellen"-Button) unter ``server_generated_items_base``
- ``item_structs`` mit generischen Cluster-Vorlagen (``switch``, ``electrical_power_measurement``,
  ``contact``, ``temperature_sensor``, ``humidity_sensor``, ``battery``) sowie fertigen
  Geräte-Vorlagen (``shelly_plug_m_3gen``/``_simple``)
- Matter-over-Thread: Bluetooth-basierte Erstkopplung, Verwaltung der Thread
  Netzwerk-Zugangsdaten im Webinterface (manuell oder automatisch von der Border-Router-REST-API
  abgerufen)
- Gerät mit einem weiteren Controller teilen (neues Kopplungsfenster, QR-Code), Fabric-Liste mit
  Entfernen-Option je Fabric
- Gezielt erzwungenes Neu-Interview eines Geräts, Anzeige der aktuell verbundenen IP-Adresse(n)

**bridge-Rolle**:

- Expose-Typen ``switch``, ``contact``, ``temperature_sensor``
- Live-Hinzufügen/-Entfernen von Accessories ohne bridge-Neustart
- Webif-Kopplung mit anderen Matter-Controllern (QR-Code/Code), Fabric-Liste mit
  Entfernen-Option je Fabric
