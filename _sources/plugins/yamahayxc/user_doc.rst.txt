yamahayxc
#########

Ein Plugin zur Steuerung von Yamaha MusicCast-kompatiblen Geräten (Receiver, Streaminglautsprecher u.ä.).

Die Grundlage für das Plugin wurde schamlos bei Raoul Thill geklaut, dem Autor des yamaha-Plugins für ältere Yamaha-Receiver in SmartHomeNG.


Anforderungen
=============

- SmartHomeNG 2.0 und das Python-Modul ``requests`` (wird normalerweise automatisch installiert).
- Ein Yamaha-Gerät mit MusicCast, das im Netzwerk unter einer festen IP-Adresse oder einem festen Hostnamen
  erreichbar ist.
- Netzwerk: Das Plugin schickt seine Anfragen per HTTP (Port 80) an das Gerät. Das Gerät schickt Statusmeldungen per
  UDP an den Port **41100** von SmartHomeNG zurück. Dieser Port darf nicht durch eine Firewall oder ein Docker-Netz
  blockiert werden.
- Optional, für Servernavigation und Titelsuche: ein UPnP/DLNA-Medienserver im selben Netz (siehe
  `UPnP und Medienserver`_).
- Optional: smartVISU für die mitgelieferten Widgets.

Wer das Plugin schon aus früheren Versionen kennt, findet die Änderungen unter `Anpassungen von früheren Versionen`_.


Grundlagen
==========

Yamaha MusicCast und YXC
------------------------

MusicCast ist das Netzwerk-Audiosystem von Yamaha. Die Geräte lassen sich über eine Schnittstelle namens *Yamaha
Extended Control* (YXC) steuern - dieselbe, die auch die MusicCast-App benutzt. Für das Plugin ist wichtig:

- Das Plugin schickt Befehle und Abfragen an das Gerät und bekommt die Antwort sofort zurück.
- Änderungen am Gerät (jemand dreht an der Lautstärke, die MusicCast-App startet einen Titel) meldet das Gerät von sich
  aus - aber nur, solange das Plugin in den letzten 10 Minuten mit ihm kommuniziert hat. Deshalb fragt das Plugin
  regelmäßig den Status ab (Parameter ``cycle``). So erkennt es auch, wenn ein Gerät nicht mehr erreichbar ist
  (Item ``reachable``).
- Jedes Gerät hat mindestens eine **Zone** (``main``) und kann weitere **Zonen** (``zone2``, ``zone3``, ...) haben, z.B.
  ein Receiver, der mehrere Räume versorgt. Lautstärke, Klangeinstellungen und die Wahl der Tonquelle gelten je Zone.
- Manche Funktionen gibt es dagegen nur **einmal je Gerät**: den Netzwerk-Player (im Plugin: ``netusb``; er spielt alles, was
  aus dem Netzwerk oder von USB kommt: Medienserver, Netradio, Bluetooth, Streamingdienste), den Tuner und die
  Multiroom-Funktion (Link). Jede Zone kann den Netzwerk-Player oder den Tuner als Tonquelle wählen. Wählen mehrere
  Zonen den Netzwerk-Player, teilen sie ihn sich: Was dort läuft (Titel, Wiedergabe, Warteschlange), ist für alle
  dasselbe. Deshalb gehören diese Funktionen im Plugin zum Gerät und nicht zu einer Zone.
- Jedes Gerät hat andere Funktionen. Beim Start fragt das Plugin die Funktionen des Geräts ab und richtet sich danach:
  Nicht unterstützte Befehle werden abgelehnt (mit Hinweis im Log), die Lautstärke wird auf den Bereich des Geräts
  begrenzt, und die gültigen Werte des Geräts (z.B. die Liste der Tonquellen) stehen als Items bereit. Antwortet das
  Gerät beim Start nicht, holt das Plugin die Abfrage bei der nächsten Erreichbarkeitsprüfung nach.

UPnP und Medienserver
---------------------

Musik aus dem Heimnetz liegt meist auf einem **Medienserver**. Das ist ein Programm auf einem PC, NAS oder Router,
z.B. der Medienserver eines Synology- oder QNAP-NAS oder einer FRITZ!Box, Twonky, MinimServer, Plex oder Jellyfin. Das
Verfahren dahinter heißt UPnP (oder DLNA).

- Der Server hat einen **Namen**. Das Yamaha-Gerät zeigt ihn in der Tonquelle *Server* an (in der MusicCast-App unter
  *Server*), und darunter die Bibliothek des Servers als Menü: Server → Ordner (z.B. Musik → Album) → Titel.
- Server und Geräte finden sich im Netz über ein Verfahren namens **SSDP**: Ein Gerät fragt im Netz nach vorhandenen
  Medienservern, und diese antworten mit Name und Adresse. Das funktioniert nur im selben Netz (Subnetz), nicht über
  VLAN- oder Docker-Grenzen hinweg.
- Die Musik wird direkt vom Server zum Yamaha-Gerät übertragen, nicht über SmartHomeNG. Das Plugin gibt dem Gerät nur
  Befehle.

Das Plugin nutzt Medienserver auf zwei Arten:

- **Servernavigation:** Es kann wie die MusicCast-App durch das Menü des Servers navigieren. Dafür ist nichts
  einzurichten, das Gerät kennt seine Server selbst.
- **Titel- und Albumsuche:** Es kann nach Titeln und Alben **im** Medienserver suchen und sie abspielen. Nur dafür
  muss das Plugin selbst den Server kennen (Parameter ``media_server``, siehe
  `Titel- und Albumsuche im Medienserver`_).


Funktionsübersicht
==================

Die Funktionen sind in Gruppen sortiert. Jede Gruppe ist ein Item-Struct (siehe `Konfiguration`_), die Structs lassen
sich frei kombinieren. Die einzelnen Items einer Gruppe sind im jeweiligen Struct in der ``plugin.yaml`` beschrieben
und im Webinterface des Plugins aufgelistet.

Funktionsgruppen
----------------

.. tab-set::

   .. tab-item:: Grundfunktionen

      Struct ``amp`` (Zone ``main``) bzw. ``zone2``/``zone3``/``zone4``. Je Zone:

      - Ein/Aus (``power``), Stummschaltung (``mute``), Ausschalt-Timer (``sleep``)
      - Lautstärke in Prozent (``volume``, in Gerätewerten unter ``volume.raw``)
      - Tonquelle (``input``), dazu die Liste der Tonquellen des Geräts (``input.values``)
      - Erreichbarkeit des Geräts (``reachable``, ``last_seen``)
      - ``update`` liest den kompletten Status neu, ``passthru`` schickt einen beliebigen Befehl an das Gerät

   .. tab-item:: Wiedergabe

      Struct ``netusb``, einmal je Gerät:

      - Wiedergabe steuern (``netusb.playback``: play, pause, stop, vorheriger/nächster Titel)
      - Titel, Interpret, Spielzeit, Länge und Coverbild des laufenden Titels
      - Wiederholen und Zufallswiedergabe (``repeat``, ``shuffle``)

   .. tab-item:: Tonquellen

      - Tonquelle wählen (``input``, Struct ``amp``)
      - Netzwerk-Tonquellen wie Medienserver, USB, Netradio oder Streamingdienste: Struct ``netusb``, siehe
        `netusb im Überblick`_
      - Tuner AM/FM, bei Geräten mit DAB auch DAB (Struct ``tuner``): Band, Frequenz, Sendersuchlauf, Presets

   .. tab-item:: Klang (DSP)

      Struct ``dsp``, je Zone. Welche Funktionen es gibt, hängt vom Gerät ab: Sound Program, 3D-Surround,
      Direct/Pure Direct, Enhancer, Bass/Höhen/Balance, Equalizer. ``dsp.available`` zeigt, ob das Gerät überhaupt
      Klangfunktionen hat.

   .. tab-item:: Multiroom (Link)

      Struct ``link``, einmal je Gerät. Geräte zu Gruppen zusammenfassen: Gruppe aufbauen, einer Gruppe beitreten, sie
      verlassen, Teilnehmer hinzufügen oder entfernen. ``link.linked`` und ``link.role`` zeigen den Zustand.

   .. tab-item:: Weiteres

      - Wecker (Struct ``alarm``, nur bei Geräten mit Weckerfunktion)
      - Diagnose-Items (Struct ``debug``) für die Fehlersuche
      - Befehle, für die das Plugin kein eigenes Item hat, lassen sich über ``passthru`` an das Gerät senden.

|

netusb im Überblick
-------------------

``netusb`` fasst alles zusammen, was das Gerät aus dem Netzwerk oder von USB abspielt. Die Einzelheiten stehen in der
`Referenz netusb`_.

.. tab-set::

   .. tab-item:: Wiedergabe und Status

      Wiedergabe steuern, Angaben zum laufenden Titel lesen, Wiederholen und Zufallswiedergabe, Favoriten (``preset``).

   .. tab-item:: Servernavigation

      Das Gerät zeigt die Bibliothek eines Medienservers (oder eines USB-Sticks) als Menü. Mit ``browse`` lässt sich
      darin navigieren wie in der MusicCast-App: Liste lesen, Ordner öffnen, zurückgehen, abspielen. Das Gerät merkt
      sich nur **eine** Position im Menü. MusicCast-App, Visu und Plugin teilen sich diese Position.

   .. tab-item:: Warteschlange

      Die Warteschlange enthält den laufenden und die als Nächstes folgenden Titel. Sie lässt sich anzeigen, ein Titel
      daraus kann angewählt werden, Einträge können gelöscht und die ganze Warteschlange geleert werden (``queue``).

   .. tab-item:: Playlisten

      Das Gerät speichert bis zu 5 benannte MusicCast-Playlisten (auf dem Gerät, nicht auf dem Server). Titel aus der
      Servernavigation lassen sich einer Playliste hinzufügen, die Warteschlange lässt sich als Playliste sichern, und
      ``mc_playlist`` spielt eine Playliste ab.

   .. tab-item:: Titel- und Albumsuche

      Ein Suchtext wird in das Item ``search`` geschrieben. Das Plugin sucht im Medienserver und spielt den besten
      Treffer ab, siehe `Titel- und Albumsuche im Medienserver`_.

|


Konfiguration
=============

plugin.yaml
-----------

.. code-block:: yaml

    yamahayxc:
        plugin_name: yamahayxc
        # cycle: 60
        # media_server: Musikserver

Für den normalen Betrieb sind keine Parameter nötig.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Parameter
     - Bedeutung
   * - ``cycle``
     - Sekunden zwischen den Erreichbarkeitsprüfungen der Geräte (Standard 60)
   * - ``media_server``
     - **Nur für die Titel- und Albumsuche nötig**, nicht für Wiedergabe oder Servernavigation. Name des Medienservers
       (z.B. ``Musikserver``) oder die Adresse seiner Gerätebeschreibung. Leer (Standard) schaltet die Suche ab.
       Siehe `Titel- und Albumsuche im Medienserver`_.

Ist mein Gerät dabei?
---------------------

Für diese Modelle gibt es fertige Geräte-Structs, die die passenden Funktionsgruppen kombinieren:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Modell
     - Struct
     - enthält
   * - WX-010
     - ``yamahayxc.wx-010``
     - Grundfunktionen, Link, netusb
   * - ISX-18D
     - ``yamahayxc.isx-18d``
     - Grundfunktionen, Link, netusb, Tuner (mit DAB), Wecker
   * - RX-V483
     - ``yamahayxc.rx-v483``
     - Grundfunktionen, Link, netusb, Tuner, DSP, Zone 2
   * - RX-S602D
     - ``yamahayxc.rx-s602d``
     - wie RX-V483

Das Plugin funktioniert auch mit Modellen, die nicht in der Liste stehen:

- **Ähnliches Modell ausprobieren:** Das Struct eines verwandten Geräts passt oft. Die Lautsprecher WX-021
  (MusicCast 20), WX-030 und WX-051 (MusicCast 50) z.B. sind leistungsfähiger als der WX-010 und haben mehr
  Funktionen, sollten sich aber grundsätzlich mit ``yamahayxc.wx-010`` bedienen lassen. Andere AV-Receiver sollten
  mit einem der beiden Receiver-Structs funktionieren (die beiden sind ohnehin gleich aufgebaut). Items für
  Funktionen, die das Gerät nicht hat, bleiben dann ohne Wirkung.
- **Empfehlung abfragen:** Das Webinterface des Plugins (Reiter *Gerät abfragen*) fragt das Gerät ab und empfiehlt die
  passenden Structs samt fertigem Konfigurationsblock, siehe `Webinterface`_.
- **Modell-Struct ergänzen lassen:** Die Antwort des Geräts auf ``getFeatures`` (im Browser unter
  ``http://<Adresse des Geräts>/YamahaExtendedControl/v1/system/getFeatures`` abrufbar) im
  `Support-Forum <https://knx-user-forum.de/forum/supportforen/smarthome-py/1174064-plugin-yamaha-musiccast-geräte-neuere-generation>`_
  posten, dann wird ein Struct für das Modell ergänzt.

items.yaml
----------

Das Item für das Gerät bekommt das Attribut ``yamahayxc_host`` (Hostname oder IP-Adresse) und, bei Geräten mit mehreren
Zonen, ``yamahayxc_zone``. Beide Attribute gelten auch für alle untergeordneten Items, die Items können also beliebig
tief verschachtelt werden.

.. tab-set::

   .. tab-item:: Modell-Struct

      .. code-block:: yaml

          media:
              wohnzimmer:
                  yamahayxc_host: 192.168.2.212
                  struct: yamahayxc.rx-v483

      Die Items heißen dann z.B. ``media.wohnzimmer.power``, ``media.wohnzimmer.volume``,
      ``media.wohnzimmer.netusb.playback`` und ``media.wohnzimmer.zone2.power``.

   .. tab-item:: Funktionsgruppen kombinieren

      .. code-block:: yaml

          media:
              wx010:
                  yamahayxc_host: 192.168.2.211
                  yamahayxc_zone: main
                  struct: [yamahayxc.amp, yamahayxc.netusb, yamahayxc.link]

      Verfügbare Structs: ``amp``, ``zone2``/``zone3``/``zone4``, ``netusb``, ``tuner``, ``dsp``, ``link``, ``alarm``,
      ``debug``.

   .. tab-item:: Mehrere Zonen

      .. code-block:: yaml

          media:
              avr:
                  yamahayxc_host: 192.168.2.212
                  struct: [yamahayxc.amp, yamahayxc.netusb]

                  zone2:
                      struct: yamahayxc.zone2

      ``netusb``, ``tuner`` und ``link`` gibt es nur einmal je Gerät. Sie gehören deshalb nur **einmal** in die
      Konfiguration und nicht in jede Zone. ``zone2.available`` zeigt, ob das Gerät die Zone tatsächlich hat (so kann
      eine Visu Zonen ein- oder ausblenden).

   .. tab-item:: Mehrere Geräte

      .. code-block:: yaml

          media:
              wohnzimmer:
                  yamahayxc_host: 192.168.2.212
                  struct: yamahayxc.rx-v483

              bad:
                  yamahayxc_host: 192.168.2.211
                  struct: yamahayxc.wx-010

   .. tab-item:: Ohne Structs

      Ein einzelnes Item wird über das Attribut ``yamahayxc_cmd`` mit einer Funktion des Plugins verbunden:

      .. code-block:: yaml

          media:
              wx010:
                  yamahayxc_host: 192.168.2.211
                  yamahayxc_zone: main

                  power:
                      type: bool
                      yamahayxc_cmd: power
                      enforce_updates: true

                  track:
                      type: str
                      yamahayxc_cmd: track

      Die möglichen Werte für ``yamahayxc_cmd`` stehen in den Structs der ``plugin.yaml``. Das Webinterface zeigt sie
      im Reiter *Items* für jedes vorhandene Item.

|

Tonquellen kürzen und benennen
------------------------------

``input.values`` enthält standardmäßig alle Tonquellen des Geräts. Mit dem Attribut ``yamahayxc_inputs`` lässt sich
die Liste kürzen, und die Tonquellen können eigene Anzeigenamen bekommen:

.. code-block:: yaml

    yamahayxc_inputs:
      - tuner
      - hdmi1: Fire TV
      - 'hdmi2=Kodi'

- Das Attribut gilt wie ``yamahayxc_zone`` für alle untergeordneten Items und kann an einem Zonen-Item überschrieben
  werden.
- Es kürzt nur die Liste in ``input.values``. ``input`` kann weiterhin auf jede Tonquelle des Geräts gesetzt werden.
- Ein Anzeigename wird als ``id=Name`` oder als ``id: Name`` im Listeneintrag angegeben. Die Schreibweise
  ``yamahayxc_inputs: {hdmi1: Fire TV}`` (ohne Liste) geht in einer Item-Datei nicht, weil SmartHomeNG daraus ein
  Unter-Item machen würde.
- Tonquellen, die das Gerät nicht kennt (Tippfehler), werden ignoriert und im Log (Level INFO) genannt. Bleibt keine
  einzige Tonquelle übrig, enthält die Liste wieder alle.
- ``input.names`` enthält die Anzeigenamen in derselben Reihenfolge wie ``input.values``: den Namen aus
  ``yamahayxc_inputs``, sonst den am Gerät eingestellten Namen (z.B. "Blu-Ray" für ``hdmi1``), sonst die Tonquelle mit
  großem Anfangsbuchstaben. Die Werte in ``input.values`` bleiben klein geschrieben, damit Vergleiche wie
  ``input() == "hdmi3"`` funktionieren.

Webinterface
------------

Das Plugin hat ein Webinterface (Admin-UI) mit drei Reitern:

- *Items*: alle Items des Plugins mit Kommando, Host, Zone und aktuellem Wert
- *Geräte*: je Gerät die vom Gerät gemeldeten Informationen und eine daraus abgeleitete Struct-Empfehlung samt
  fertigem Konfigurationsblock
- *Gerät abfragen*: fragt ein noch nicht konfiguriertes Gerät per Hostname oder IP-Adresse ab und liefert dieselbe
  Empfehlung. Die Abfrage liest nur, am Gerät wird nichts verändert.

smartVISU-Widgets
-----------------

Das Plugin bringt Widgets für smartVISU mit (Ordner ``sv_widgets``): ein Geräte-Widget, einen Player und einen
Playlist-Button. Sie arbeiten mit den Items der Structs.

Bedienung per CLI
-----------------

.. code-block::

    > up media.wx010.power=True
    > up media.wx010.input=net_radio
    > up media.wx010.volume=15
    > up media.wx010.mute=True
    > up media.wx010.netusb.playback=play
    > up media.wx010.netusb.search='Sunday'
    > up media.avr.tuner.band=fm
    > up media.avr.tuner.freq=87500
    > up media.avr.tuner.preset=5
    > up media.avr.dsp.sound_program=munich
    > up media.avr.dsp.tone.bass=3
    > up media.avr.dsp.tone.balance=-5
    > up media.avr.link.client.join=192.168.2.212
    > up media.wx010.passthru='v1/main/setPower?power=standby'


Referenz netusb
===============

Die Items stehen unter ``netusb``, z.B. ``media.wx010.netusb.playback``. Items, die als *Auslöser* bezeichnet sind,
führen ihre Aktion aus, wenn ``True`` geschrieben wird, und setzen sich danach selbst auf ``False`` zurück.

.. tab-set::

   .. tab-item:: Wiedergabe

      - ``playback``: Wiedergabestatus und Steuerung (play, pause, stop, previous, next)
      - ``track``, ``artist``, ``curtime``, ``totaltime`` (Sekunden), ``albumart`` (Adresse des Coverbilds),
        ``albumarturl`` (fertiger HTML-Baustein mit dem Coverbild), ``playing`` (bool)
      - ``repeat`` (off/one/all) und ``shuffle`` (off/on/songs/albums, je nach Gerät). Die gültigen Werte stehen in
        ``repeat_available`` und ``shuffle_available``. Das Plugin prüft den geschriebenen Wert nicht selbst; einen
        ungültigen Wert lehnt das Gerät ab (Warnung im Log).
      - ``preset``: Favoriten und Netradio-Presets des Geräts anwählen. Welche Nummern belegt sind, lässt sich nicht
        abfragen.
      - ``queue_type``: Art der aktuellen Warteschlange
      - ``update``: liest die Werte und die Playlisten-Namen neu (Auslöser)

   .. tab-item:: Servernavigation

      Das Gerät liefert immer nur einen Ausschnitt des Menüs. Items unter ``browse``:

      - ``list``: die aktuelle Seite (bis zu 8 Einträge). Je Eintrag gibt ``attribute`` an, ob er ein Ordner ist (lässt
        sich öffnen) und/oder abspielbar.
      - ``menu_name``, ``menu_layer``, ``max_line``, ``index``, ``playing_index``: Name und Ebene des aktuellen Menüs,
        Anzahl seiner Einträge, Beginn der aktuellen Seite und der gerade spielende Eintrag
      - ``page``: eine bestimmte Seite anfordern (der Wert wird auf ein Vielfaches von 8 abgerundet)
      - ``select``, ``play``: einen Eintrag öffnen bzw. abspielen. Der Wert ist die Position des Eintrags im ganzen
        Menü, ab 0 gezählt (``index`` + Position in ``list``). ``play`` spielt immer in der Zone ``main``.
      - ``return``: eine Ebene zurück (Auslöser)
      - ``busy``: ``True``, solange das Gerät eine Liste lädt

      Zu beachten:

      - Das Gerät merkt sich nur **eine** Position im Menü. Wer gleichzeitig mit der MusicCast-App oder einer zweiten
        Visu navigiert, verstellt sie für alle.
      - Das Laden einer Liste kann laut Yamaha bis zu 30 Sekunden dauern. In dieser Zeit nimmt das Gerät keine anderen
        Anfragen an.

      Die Aktionen aus dem "..."-Menü der MusicCast-App gibt es ebenfalls. Der Wert ist jeweils wieder die Position des
      Eintrags:

      - ``play_now``: sofort abspielen (auch ganze Alben und Ordner)
      - ``play_next``: als Nächstes abspielen
      - ``queue_add``: hinten an die Warteschlange anhängen
      - ``playlist_add``: einer Playliste hinzufügen (siehe den Reiter *Playlisten*)

      Diese vier Aktionen sind von Yamaha nicht dokumentiert; sie wurden aus dem Verhalten der MusicCast-App
      abgeleitet. Ob sie bei allen Tonquellen und Firmware-Ständen gleich funktionieren, ist nicht bestätigt.

   .. tab-item:: Warteschlange

      Items unter ``queue``:

      - ``list``, ``max_line``, ``playing_index``: die Warteschlange, die Anzahl ihrer Einträge und der gerade
        spielende Eintrag
      - ``play``, ``delete``: einen Eintrag anwählen bzw. löschen. Der Wert ist die Position **in der Warteschlange**,
        nicht die Position im Menü der Servernavigation.
      - ``save_playlist``: sichert die ganze Warteschlange als Playliste (Auslöser). Welche Playliste, legt
        ``browse.playlist_bank`` fest.
      - ``clear``: leert die Warteschlange (Auslöser)
      - ``update``: liest die Warteschlange neu (Auslöser)

      Auch die Warteschlange ist von Yamaha nicht dokumentiert. Das Plugin liest sie mit einer einzigen Abfrage; wie
      sich sehr lange Warteschlangen verhalten, ist nicht bestätigt.

   .. tab-item:: Playlisten

      - ``browse.playlist_bank`` (1-5): wählt die Playliste, auf die sich die folgenden Aktionen beziehen. Muss vor
        dem ersten ``playlist_add`` gesetzt werden.
      - ``browse.playlist_add``: fügt einen Eintrag aus der Servernavigation der gewählten Playliste hinzu (Wert:
        Position des Eintrags)
      - ``queue.save_playlist``: sichert die ganze Warteschlange in der gewählten Playliste (Auslöser)
      - ``browse.playlist_names``: die Namen aller Playlisten
      - ``browse.playlist_rename``: benennt die gewählte Playliste um (Wert: neuer Name)
      - ``browse.playlist_clear``: leert die gewählte Playliste, der Name bleibt (Auslöser)
      - ``mc_playlist`` (1-5): spielt eine gespeicherte Playliste ab dem ersten Eintrag ab. ``preset`` ist etwas
        anderes: Es lädt Favoriten und Netradio-Presets.

      Die Namen der Playlisten werden nicht laufend abgefragt. ``netusb.update`` liest sie neu.

|


Titel- und Albumsuche im Medienserver
=====================================

Mit dem Item ``search`` wird ein Titel oder Album per Suchtext im Medienserver gefunden und auf dem Gerät abgespielt,
ohne in der MusicCast-App durch Menüs zu navigieren. Beispiel (CLI-Plugin):

.. code-block::

    > up media.wx010.netusb.search='Sunday'

Das Plugin fragt den Medienserver nach dem Suchtext und wählt den besten Treffer. Dann schaltet es die Zone ``main``
des Geräts ein, wählt die Tonquelle ``server`` und navigiert im Menü des Geräts bis zum Treffer, so wie man es in der
MusicCast-App von Hand tun würde. Ein Album wird komplett abgespielt, ein Titel innerhalb seines Albums (das Album
läuft danach weiter). Die Suche läuft im Hintergrund. Eine neue Suche für dasselbe Gerät ersetzt eine noch laufende.

Getestet ist die Suche bisher nur mit Twonky 8.5.1 und einem Yamaha RX-V483. Andere Medienserver können sich anders
verhalten, siehe den Reiter *Fehlersuche*.

.. tab-set::

   .. tab-item:: Einrichtung

      Voraussetzung: Das Gerät zeigt den Medienserver in der Tonquelle *Server* an.

      **1. Medienserver in der plugin.yaml eintragen**

      .. code-block:: yaml

          yamahayxc:
              plugin_name: yamahayxc
              media_server: Musikserver

      Einzutragen ist der **Name des Medienservers**, z.B. ``Musikserver`` oder ``Medien NAS (Keller)``.
      Groß-/Kleinschreibung ist egal. Der Name steht

      - in der MusicCast-App in der Liste unter *Server*,
      - in der obersten Ebene der Servernavigation, z.B. im smartVISU-Widget, wenn als Tonquelle *Server* gewählt ist.

      Das Plugin sucht den Server mit diesem Namen selbst im Netz (per SSDP, siehe `UPnP und Medienserver`_).

      Findet es ihn nicht (z.B. weil SmartHomeNG in einem anderen Netz läuft als der Server), kann statt des Namens
      die Adresse der **Gerätebeschreibung** des Servers eingetragen werden. Das ist eine Datei, die jeder Medienserver
      unter einer eigenen Adresse bereitstellt:

      .. code-block:: yaml

          yamahayxc:
              plugin_name: yamahayxc
              media_server: http://192.168.1.10:9000/dev0/desc.xml

      Die Adresse ist bei jedem Medienserver anders (Port und Pfad). Das Beispiel gilt für Twonky. Die Adresse steht in
      der Dokumentation oder Weboberfläche des Servers; auch UPnP-Browser-Programme zeigen sie an. Ein Port-Scan des
      Server-Rechners hilft meist nicht weiter, weil daraus der Pfad der Datei nicht hervorgeht.

      Bleibt ``media_server`` leer (Standard), ist die Suche abgeschaltet und ``search.status`` zeigt ``disabled``.

      **2. Das Item einbinden**

      Das Item ``search`` gehört zum Struct ``yamahayxc.netusb`` und ist damit auch in allen Modell-Structs enthalten:

      .. code-block:: yaml

          media:
              wx010:
                  yamahayxc_host: 192.168.2.211
                  struct: [yamahayxc.amp, yamahayxc.netusb]

      Die Items heißen dann ``media.wx010.netusb.search`` (hier wird der Suchtext geschrieben),
      ``media.wx010.netusb.search.status`` und ``media.wx010.netusb.search.result``.

      **3. Ausprobieren**

      .. code-block::

          > up media.wx010.netusb.search='Sunday'

      Danach zeigt ``media.wx010.netusb.search.status`` das Ergebnis (bei Erfolg ``ok``). Bei der ersten Suche schreibt
      das Plugin eine Zeile wie diese ins Log, sobald es den Server gefunden hat:

      .. code-block::

          media search: using media server Musikserver at http://192.168.1.10:9000/dev0/srv1/control

      Die genannte Adresse dient nur der Steuerung des Servers durch Programme. Im Browser geöffnet zeigt sie
      ``404 Not Found`` oder Ähnliches. Das ist normal und kein Fehler.

   .. tab-item:: Suchtext

      Groß-/Kleinschreibung spielt keine Rolle.

      .. list-table::
         :header-rows: 1
         :widths: 28 72

         * - Eingabe
           - Bedeutung
         * - ``sunday``
           - Titel oder Album, dessen Name ``sunday`` enthält
         * - ``come together``
           - der Name muss **alle** Wörter enthalten, in beliebiger Reihenfolge, auch mit anderem Text dazwischen
         * - ``"let it be"``
           - in Anführungszeichen: die Wortfolge muss **zusammenhängend** im Namen vorkommen
         * - ``album: abbey road``
           - nur Alben suchen (``album:`` klein geschrieben und als erstes Wort)
         * - ``title: yesterday``
           - nur Titel suchen (``title:`` klein geschrieben und als erstes Wort)

      Passen mehrere Treffer, gilt diese Rangfolge: zuerst der Treffer, dessen Name genau dem Suchtext entspricht,
      dann Alben vor Titeln, dann die Reihenfolge des Servers.

   .. tab-item:: Status und Ergebnis

      .. list-table::
         :header-rows: 1
         :widths: 22 78

         * - ``search.status``
           - Bedeutung
         * - ``idle``
           - keine Suche aktiv (Zustand nach dem Start)
         * - ``busy``
           - die Suche läuft
         * - ``ok``
           - ein Treffer wurde gefunden und zum Abspielen an das Gerät geschickt
         * - ``no_match``
           - der Server hat zum Suchtext nichts gefunden
         * - ``path_failed``
           - ein Treffer wurde gefunden, ließ sich aber im Menü des Geräts nicht erreichen (Einzelheiten im Log)
         * - ``error``
           - der Medienserver oder das Gerät war nicht erreichbar oder hat eine Anfrage abgelehnt
         * - ``disabled``
           - ``media_server`` ist nicht gesetzt

      ``search.result`` enthält bei ``ok`` den abgespielten Treffer, sonst ein leeres Dict:

      .. code-block::

          {'type': 'track', 'title': 'Sunday', 'album': 'Greatest Hits', 'path': ['Musikserver', 'Music', 'Album', 'Greatest Hits', 'Sunday']}

      ``path`` ist der Weg durch das Menü des Geräts, dem das Plugin gefolgt ist.

   .. tab-item:: Aus Logiken

      Die Suche lässt sich auch aus einer Logik starten. Der Aufruf gibt ``False`` zurück, wenn die Suche nicht
      gestartet wurde (Suche abgeschaltet, unbekanntes Gerät). Das Ergebnis steht wie oben in den Items.

      .. code-block:: python

          plugin = sh.plugins.return_plugin('yamahayxc')
          plugin.search_play('192.168.2.211', 'album: abbey road')

      Der erste Wert ist das Gerät, angegeben wie in ``yamahayxc_host``.

   .. tab-item:: Fehlersuche

      Das Plugin schreibt zu jeder Suche eine Zeile mit dem Ergebnis ins Log (Log-Level INFO). Bei ``no_match`` und
      ``path_failed`` nennen weitere Zeilen den Grund. Beispiele:

      .. code-block::

          media search 'Sunday' on 192.168.2.211: ok (track 'Sunday')
          media search: nothing found for 'zzzz'
          media search: no album container 'X' lists track 'Y'
          media search: device has no entry 'Album' in layer 2

      - ``no_match``: Der Server hat zum Suchtext nichts gefunden. Weniger Wörter oder ``title:`` bzw. ``album:``
        können helfen.
      - ``error`` nach dem Eintragen von ``media_server``: Das Log nennt die Ursache. Entweder wurde der Server nicht
        gefunden (Name falsch geschrieben, oder SmartHomeNG und Server liegen nicht im selben Netz - dann die Adresse
        der Gerätebeschreibung eintragen), oder er antwortet nicht.
      - ``path_failed``: Der Server hat etwas gefunden, aber das Plugin konnte den Treffer im Menü des Geräts nicht
        erreichen. Das Plugin erwartet, dass ein Titel in einem Album liegt, das der Server unter dem Albumnamen
        auflistet, und dass das Gerät dieselben Einträge in seinem Menü zeigt. Medienserver, die ihre Bibliothek
        anders aufbauen, können daran scheitern. In diesem Fall bitte die Log-Zeilen zur Suche (Log-Level INFO) und den
        Namen des Medienservers im Support-Forum melden.
      - ``ok``, aber es wird nichts abgespielt: Das Gerät hat den Befehl angenommen, kann die Dateien aber nicht
        wiedergeben. Das lässt sich in der MusicCast-App gegenprüfen.

      Zum Abspielen wird immer die Zone ``main`` verwendet. Während eine Suche das Menü des Geräts benutzt, warten
      Schreibzugriffe auf die ``browse``-Items, bis sie fertig ist.

|


Referenz weitere Funktionen
===========================

.. tab-set::

   .. tab-item:: Tuner und DAB

      Struct ``tuner``, einmal je Gerät.

      - ``band``: am oder fm, bei Geräten mit DAB auch dab. Die gültigen Werte stehen in ``band.values``.
      - ``freq``: Frequenz in kHz, die Grenzen für das gewählte Band in ``freq.min`` und ``freq.max``
      - ``seek``: Sendersuchlauf
      - ``tuned``: ein Sender wird empfangen
      - ``station``: Sendername (bei FM der RDS-Name, bei DAB das Service Label)
      - ``preset``: Preset wählen. Gelesen liefert das Item die aktuelle Preset-Nummer (0 = kein Preset).
        ``preset.max`` nennt die Anzahl der Presets.
      - ``preset_store``, ``preset_clear``: den aktuellen Sender auf einer Preset-Nummer speichern bzw. ein Preset
        löschen. ``preset_switch``: zum nächsten oder vorherigen Preset wechseln.
      - ``stations``: die Presets des gewählten Bands (je Eintrag Speicherplatz, Band, Nummer, Name). Geräte ohne RDS
        liefern bei FM keine Namen.
      - ``auto_preset``: sucht FM-Sender und legt sie in den Presets ab (überschreibt die vorhandenen).
        ``auto_preset.available`` zeigt, ob das Gerät das kann.

      **DAB:**

      - ``ensemble`` und ``dls``: Senderpaket und Zusatztext des empfangenen Senders
      - ``dab_service`` (``next``/``previous``): den nächsten bzw. vorherigen Sender wählen
      - ``dab_scan``: ``True`` startet den Sendersuchlauf, ``False`` bricht ihn ab. ``dab_status``,
        ``dab_scan_progress`` und ``dab_station_count`` zeigen den Fortschritt. Ein Suchlauf löscht die DAB-Presets.
      - Das Gerät liefert keine DAB-Senderliste und wählt Sender nur schrittweise. ``dab_walk`` (``True`` startet,
        ``False`` bricht ab) erstellt die Liste deshalb, indem es alle Sender nacheinander anwählt. Das dauert etwa
        3 Sekunden je Sender, das Gerät ist währenddessen stumm geschaltet. Das Ergebnis steht in ``dab_services``
        (Index, ID, Name), Zustand und Fortschritt in ``dab_walk_state`` und ``dab_walk_progress``.
      - ``dab_tune``: stellt einen Sender der Liste ein (Wert: der Index aus ``dab_services``)
      - Die Senderliste wird nicht dauerhaft gespeichert. Nach einem Neustart des Plugins oder einem Sendersuchlauf
        muss sie neu erstellt werden.
      - Nicht unterstützt: Tune Aid und das Verschieben von Presets. Letzteres geht über ``passthru``.
      - Das Lesen der DAB-Werte ist an einem Gerät mit DAB geprüft. Senderliste, ``stations`` und ``auto_preset`` sind
        bisher nur gegen simulierte Geräte getestet.

   .. tab-item:: Klang (DSP)

      Struct ``dsp``, je Zone. Welche Funktionen es gibt, hängt vom Gerät ab.

      - ``sound_program``, ``surround_3d``, ``direct``, ``pure_direct``, ``enhancer``
      - Klangregelung: ``tone.bass``, ``tone.treble``, ``tone.balance``, dazu die Betriebsart ``tone_control_mode``
      - Equalizer: ``equalizer.low``, ``equalizer.mid``, ``equalizer.high``, dazu die Betriebsart ``equalizer_mode``
      - ``dsp.available``: ``True``, wenn die Zone mindestens eine Klangfunktion hat. Damit kann eine Visu die
        Klangeinstellungen nur dann anzeigen, wenn es etwas einzustellen gibt.
      - ``update``: liest die Werte neu (Auslöser)

      Die gültigen Bereiche und Werte stehen in Unteritems, siehe den Reiter *Wertebereiche und -listen*.

   .. tab-item:: Multiroom (Link)

      Struct ``link``, einmal je Gerät. In einer Link-Gruppe gibt ein Gerät die Musik vor (bei Yamaha heißt es
      **Server** der Gruppe, nicht zu verwechseln mit einem Medienserver), die anderen spielen als **Clients** mit.

      - ``linked`` (bool): Das Gerät ist in einer Gruppe.
      - ``role``: ``server``, ``client`` oder ``none``. Ist das Gerät in keiner Gruppe, zeigt ``role`` immer ``none``.
      - ``available_devices``: alle Geräte, die im Plugin konfiguriert sind (als Auswahlliste für eine Visu)
      - ``server.add_device``, ``server.remove_device``: ein Gerät in die eigene Gruppe aufnehmen bzw. daraus
        entfernen (Wert: Hostname oder IP-Adresse des anderen Geräts)
      - ``server.linked_devices``: die Teilnehmer der Gruppe (nur gefüllt, wenn das Gerät Server ist)
      - ``server.disband``: löst die Gruppe auf (Auslöser)
      - ``client.join``: der Gruppe eines anderen Geräts beitreten (Wert: Hostname oder IP-Adresse des Servers)
      - ``client.leave``: die Gruppe verlassen (Auslöser)
      - ``options``: selten benötigte Angaben (Kennung und Name der Gruppe u.ä.)
      - Die Einstellungen ``link_control``, ``link_audio_delay`` und ``link_audio_quality`` gelten je Zone und stehen
        deshalb in ``amp`` bzw. ``zone2``/``zone3``/``zone4``.

      Das Gerät braucht für diese Aktionen einen Moment. Das Plugin wartet nicht darauf; der neue Zustand erscheint
      mit der nächsten Statusmeldung des Geräts. Getestet ist Link bisher mit zwei Geräten (ein Server, ein Client).
      Rückmeldungen zu größeren Gruppen sind willkommen.

   .. tab-item:: Wertebereiche und -listen

      Das Plugin liest beim Start vom Gerät, welche Werte gültig sind, und stellt sie in Unteritems bereit. Diese
      Unteritems lassen sich nur lesen und ändern sich im Betrieb nicht.

      - Bereiche: ``volume.min``, ``volume.max``, ``volume.step`` (entsprechend bei ``tone.bass``, ``equalizer.low``
        usw.)
      - Listen: ``input.values``, ``sound_program.values``, ``tone_control_mode.values``, ``equalizer_mode.values``,
        ``link_control.values``, ``link_audio_delay.values``, ``link_audio_quality.values``. Meldet ein Gerät eine Liste
        nicht, bleibt das Item leer.
      - ``volume`` ist immer in Prozent (0 bis 100), unabhängig vom Bereich des Geräts. Die Lautstärke in Gerätewerten
        steht in ``volume.raw``.

   .. tab-item:: Erreichbarkeit

      ``reachable`` und ``last_seen`` (Struct ``amp``) gelten für das ganze Gerät.

      Das Plugin fragt alle ``cycle`` Sekunden (Standard 60) den Status ab. Nach zwei Fehlversuchen in Folge gilt das
      Gerät als nicht erreichbar (``reachable`` = ``False``, Warnung im Log). Sobald es wieder antwortet, gilt es als
      erreichbar, und das Plugin liest alle Werte neu. ``last_seen`` enthält den Zeitpunkt des letzten erfolgreichen
      Kontakts (Unix-Zeitstempel).

      Die übrigen Items behalten ihren letzten Wert, solange das Gerät nicht erreichbar ist. Eine Visu kann sie anhand
      von ``reachable`` und ``last_seen`` z.B. ausgrauen. Befehle schickt das Plugin trotzdem immer an das Gerät.

   .. tab-item:: Aktualisieren

      Nach jedem Schreiben eines Items liest das Plugin den betroffenen Bereich automatisch neu (nur die Zone, nur
      netusb usw.). Ein manuelles Aktualisieren ist deshalb selten nötig. Dafür gibt es diese Auslöser:

      - ``update`` (Struct ``amp``) liest alles neu: alle Zonen, netusb, Tuner, Link und Wecker.
      - ``netusb.update``, ``tuner.update``, ``link.update`` und ``dsp.update`` lesen nur ihren Bereich neu.

|


Anpassungen von früheren Versionen
==================================

Wer das Plugin schon vor der Aufteilung in Funktionsgruppen benutzt hat, kann die Konfiguration nach dieser Tabelle
umstellen. ``volume`` ist nicht betroffen, der Pfad ist unverändert.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Früher
     - Jetzt
   * - ``yamahayxc.basic`` (alles in einem Struct)
     - ``[yamahayxc.amp, yamahayxc.netusb]``. ``yamahayxc.basic`` gibt es übergangsweise weiter, mit den alten
       Item-Pfaden. Für das alte ``alarm`` gilt dasselbe mit ``yamahayxc.legacy_alarm``.
   * - ``yamahayxc.alarm`` (enthielt ``basic``)
     - ``yamahayxc.alarm`` enthält nur noch die drei Wecker-Items: ``[yamahayxc.amp, yamahayxc.alarm]``
   * - ``tone_bass``, ``tone_treble``, ``balance``, ``eq_low``, ``eq_mid``, ``eq_high`` direkt unter dem Geräte-Item
     - Struct ``yamahayxc.dsp``: ``dsp.tone.bass``, ``dsp.tone.treble``, ``dsp.tone.balance``, ``dsp.equalizer.low``
       usw. Verweise in Visu und Logiken müssen auf die neuen Pfade umgestellt werden.
   * - ``yamahayxc.link`` enthielt ``link_control``, ``link_audio_delay`` und ``link_audio_quality``
     - Diese drei Items kommen jetzt aus ``amp`` bzw. ``zone2``/``zone3``/``zone4``. Betroffen ist nur, wer ``link``
       ohne ``amp`` verwendet.
   * - ``yamahayxc.isx-18``
     - ``yamahayxc.isx-18d``. Der alte Name funktioniert noch, wird aber mit dem nächsten Major-Release entfernt.
