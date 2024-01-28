.. index:: Plugins; sonos
.. index:: sonos

=====
sonos
=====

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left


Anforderungen
=============


Notwendige Software
-------------------

Folgende Python Pakete werden vom Plugin benötigt und automatisch bei der ersten Verwendung installiert:
 * xmltodict>=0.11.0
 * tinytag>=0.18.0
 * gtts

Weiterhin braucht das Basisframework SoCo diese python Pakete. Diese werden auch bei der ersten Verwendung installiert:
 * ifaddr
 * appdirs
 * lxml

Unterstützte Geräte
-------------------

Es werden alle Sonos Lautsprecher mit Sonos Softwareversion > 10.1 unterstützt.

`Offizielle Sonos Seite <https://www.sonos.com/>`_

Das Plugin basiert auf dem Sonos `SoCo Github Projekt <https://github.com/SoCo/SoCo>`_

Konfiguration
=============

Erste Schritte
--------------

Die Zuordnung der Items zu den Speakern erfolgt über eine eindeutige Speaker ID, auch UID genannt.
Diese können für Speaker im lokalen Netzwerk mittels des Python Skriptes ``search_uids.py`` ausgelesen werden. Dazu wird
das Skript in der Konsole folgendermaßen ausgeführt:

.. code-block:: python

    python3 search_uids.py

Die Aussgabe sieht dann so aus:

.. code-block:: bash

    ---------------------------------------------------------
    rincon_000f448c3392a01411
        ip           : 192.168.1.100
        speaker name : Wohnzimmer
        speaker model: Sonos PLAY:1

    ---------------------------------------------------------
    rincon_c7e91735d19711411
        ip           : 192.168.1.99
        speaker name : Kinderzimmer
        speaker model: Sonos PLAY:3
    ---------------------------------------------------------

Die erste Zeile jedes Eintrags gibt die UID an (rincon_xxxxxxxxxxxxxx).

Alternativ können die Speaker/Zones auch dem WebIF entnommen werden. Dazu muss das Plugin aktiviert sein, Items müssen
allerdings zu diesem Zeitpunkt noch nicht definiert sein.


plugin.yaml
-----------

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.

1) Sonos Speaker automatisch im Netzwerk suchen:
Standardmäßig können Sonos Speaker im lokalen Netzwerk automatisch detektiert und verwendet werden.


2) Sonos Speaker manuell konfigurieren:

In manchen Situation sollten die verfügbaren Sonos Speaker statisch über Ihre IP Adressen konfiguriert werden. Dies
ist zum Beispiel erforderlich, wenn das lokale Netzwerk Multicast und/oder UDP nicht unterstützt, was für die automatische Detektion
unter 1) benötigt wird.

Folgendermaßen werden Speaker statisch in der plugin.yaml konfiguriert:

.. code-block:: yaml

    Sonos:
        class_name: Sonos
        class_path: plugins.sonos
        speaker_ips:
          - 192.168.1.10
          - 192.168.1.77
          - 192.168.1.78

.. important::

    Die zyklische Discover Funktionalität prüft, ob neue Speaker hinzugekommen sind oder ob
    bekannte Speaker inzwischen offline sind. Die Funktionalität sollte aus Performancegründen nicht
    unnötig strapaziert werden.
    In der ``plugin.yaml`` kann hierzu im Parameter ``discover_cycle`` (in Sekunden) definiert werden, wie oft die
    Detektion ausgeführt werden soll.

    Es wird nicht empfohlen, den Wert kleiner als 60 Sekunden zu wählen.


items.yaml
----------

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


logic.yaml
----------

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Funktionen
----------

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Unterstütze Eigenschaften/Funktionen
====================================

Folgende Sonos Funktionen bzw. Eigenschaften werden unterstützt und können mit einem smarthomeNG Item verknüpft werden.
Es müssen nicht alle Items für die Funktionen angelegt werden. Die Items markiert mit ``visu`` sollten bei der Verwendung
des smartVisu Sonos Widgets mindestens angelegt werden.
Die Markierungen ``read`` bzw. ``write`` geben an, ob es sich um eine schreibende Funktion (für Befehle an Sonos)
und/oder lesende Funktion (Status von Sonos lesen) handelt.

bass
----
``read`` ``write``

Dieses Attribut steuert die Basslautstärke eines Speakers. Der Wert muss ein ganzzahliger Wert zwischen -10 und 10 sein.
Diese Eigenschaft ist **kein** Gruppenbefehl. Wird ein untergeordnetes Item mit Attribut ``group_command: True`` gesetzt,
wird die Basslautstärke trotzdem für alle Speaker einer Gruppe gesetzt.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

coordinator
-----------
``read``

Gibt die UID des Speakers zurück, der aktuell der Koordinator der Gruppe ist. Die UID ist ein String. Ist ein Speaker nicht
Teil einer Gruppe, ist er per Definition immer selber Koordinator. Das Item gibt in diesem Fall die eigene UID zurück.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

cross_fade
----------
``read`` ``write``

Setzt bzw. liest den Cross-Fade Modus eines Speakers. Das Item ist vom Typ Boolean. `True` bedeutet Cross-Fade
eingeschaltet, `False` ausgeschaltet.
Das Setzen ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

current_track
-------------
``read``

Gibt die Indexposition des aktuell gespielten Tracks innerhalb der Playliste zurück. Das Item ist vom Typ Integer.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

current_track_duration
----------------------
``read``

Gibt die aktuelle Spiellänge des Tracks im Format HH:mm:ss an.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

current_transport_actions
-------------------------
``read`` ``visu``

Gibt die möglichen Transport Actions für den aktuellen Track wieder.
Mögliche Werte sind: Set, Stop, Pause, Play, X_DLNA_SeekTime, Next, Previous, X_DLNA_SeekTrackNr.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

current_valid_play_modes
------------------------
``read``

Gibt alle validen Abspielmodi für den aktuellen Zustand zurück. Die Modi werden als String (mit Kommata getrennt) ausgegeben.
Einer der Modi kann dem ``play_mode`` Befehl übergeben werden.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

dialog_mode
-----------
``read`` ``write``

Nur unterstützt von Sonos Playbars.
Setzt bzw. liest den Dialog Modus einer Playbar. `True` bedeutet Dialog Modus ein, `False` Modus aus.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an (zu bestätigen).

household_id
------------
``read``

Gibt die Household ID des Speakers zurück.

is_coordinator
--------------
``read``

Gibt den Status zurück, ob ein Speaker Koordinator eine Gruppe ist, oder nicht. Das Item ist vom Typ Boolean.
Rückgabe von `True`, falls der Speaker der Koordinator ist, `False`, falls der Koordinator ein anderer Speaker ist.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

is_initialized
--------------
``read``

Gibt den Status zurück, ob ein Speaker initialisiert und erreichbar ist. Das Item ist vom Typ Boolean.
`True` bedeutet, dass der Speaker initialisiert und erreichbar ist. Bei `False` ist der Speaker entweder offline oder nicht vollständig initialisiert.
Nutze dieses Item in Logiken oder Szenen, bevor weitere Kommendos an den Speaker gesendet werden, siehe Beispiel 3).

join
----
``write``

Verbindet einen Speaker mit einem anderen Speaker oder Gruppe per Übergabe der UID eines Geräts,
welches sich schon in der Gruppe befindet. Zusätzlich sollte für das Item das smarthomeNG item Attribut ``enforce_update: True``
gesetzt werden.

load_sonos_playlist
-------------------
``write``

Lädt eine Sonos playlist über ihren Namen. Die Funktion ``sonos_playlists`` zeigt alle verfügbaren Playlisten an.
Dies ist ein Gruppenbefehl, der auf jeden Speaker einer Gruppe angewandt werden kann.

Unteritem  ``start_after``:
Wird ein untergeordnetes item vom Typ Boolean mit dem Attribut ``sonos_attrib: start_after`` angelegt, kann das Verhalten
nach Laden der Playliste bestimmt werden. Wird das Item auf `True` gesetzt, startet der Speaker direkt die Wiedergabe.
Wird das Item auf `False` gesetzt, wird nur die Playliste geladen und es erfolgt keine direkte Wiedergabe.
Wird dieses Item weggelassen, ist das Standardverhalten `False`.

Unteritem ``clear_queue``:
Wird ein untergeordnetes item vom Typ Boolean mit dem Attribut ``sonos_attrib: clear_queue`` angelegt, wird bei Wert
`True` die bestehende Sonos Playlist gelöscht bevor die neue Playlist geladen wird. Bei Wert `False` bleibt die bestehende Liste
erhalten und die Songs der neu zu ladenden Playliste werden angehängt.
Wird dieses Item weggelassen, ist das Standardverhalten `False`.

Unteritem  ``start_track``:
Wird ein untergeordnetes item vom Typ Number mit dem Attribut ``sonos_attrib: start_track`` angelegt, kann die Indexposition
innerhalb der geladen Playliste definiert werden, von wo die Wiedergabe startet. Der erste Song in der Playliste entspricht der
Indexposition `0`.
Wird dieses Item weggelassen, ist das Standardverhalten ein Start bei Indexposition `0`.

loudness
--------
``read`` ``write``

Setzt oder liest den Modus Lautstärkeabsenkung eines Speakers. Das Item ist vom Typ Boolean. Bei Wert `True`
wird die Lautstärke und Bass abgesenkt, bei `False` nicht.
Diese Eigenschaft ist kein Gruppenbefehl. Nichtsdestotrotz kann über ein untergeordnetes Item mit dem Attribut
``group_command: True`` ein Gruppenbefehl erzwungen werden, d.h. die Lautstärkeabsenkung wird für alle Speaker innerhalb der Gruppe gesetzt.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

streamtype
----------
``read`` ``visu``

Gibt den aktuellen Streamtyp zurück. Das Item ist vom Typ String. Mögliche Werte sind
`music` (Standard, z.B. beim Spielen eines Songs aus dem Netzwerk), `radio`, `tv` (falls der Audio Output einer Playbar
auf `TV` gesetzt ist, oder `line-in` (z.B. beim Sonos Play5).
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

mute
----
``read`` ``write`` ``visu``

Stellt einen Speaker auf lautlos. Das Item ist vom Typ Boolean. Der Wert `True` bedeutet lautlos (mute),
`False` bedeutet laut (un-mute).
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

next
----
``write`` ``visu``

Wechselt zum nächsten Song der aktuellen Playliste. Das Item ist vom Typ Boolean. Der Wert `True`
bedeutet Sprung zum nächsten Track. Ein Setzen auf `False` hat keinen Effekt. Zusätzlich muss
für das Item das smarthomeNG item Attribut ``enforce_update: True`` gesetzt werden.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.

night_mode
----------
``read`` ``write``

Nur von der Sonos Playbar unterstützt.
Setzt oder liest den Nachtmodus einer Sonos Playbar. Das Item ist vom Typ Boolean. Wert `True` zeigt Nachtmodus aktiv an,
Wert `False` bedeutet Nachtmodus aus.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an (bisher ungetestet).

number_of_tracks
----------------
``read``

Gibt die komplette Anzahl an Tracks in der aktuellen Playliste zurück.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

pause
-----
``read`` ``write`` ``visu``

Pausiert die Wiedergabe. Das Item ist vom Typ Boolean. Wert `True` bedeutet pausieren, `False` führt die Wiedergabe fort.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

play
----
``read`` ``write`` ``visu``

Startet die Wiedergabe.  Das Item ist vom Typ Boolean. Der Wert `True` bedeutet Wiedergabe, `False` bedeutet pausieren.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

player_name
-----------
``read``

Gibt den Namen des Speakers zurück. Das Item ist vom Typ String.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

play_mode
---------
``read`` ``write``

Setzt oder liest den Abspielmodus für einen Speaker. Das Item ist vom Typ String.
Erlaubte Werte sind `NORMAL`, `REPEAT_ALL`, `SHUFFLE`, `SHUFFLE_NOREPEAT`, `SHUFFLE_REPEAT_ONE`, `REPEAT_ONE`.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

play_snippet
-------------
``write``

Spielt ein Audio Snippet über einen Audiodateinamen ab (z.B. `alarm.mp3`). Das Item ist vom Typ String.
Voraussetzung ist, dass in der ``plugin.yaml`` die Attribute ``tts`` und der ``local_webservice_path`` gesetzt sind.
Die Audiodatei muss in dem unter ``local_webservice_path`` oder ``local_webservice_path_snippet`` angegebenen Pfaden liegen.
Folgende Dateiformate werden unterstützt: `mp3`, `mp4`, `ogg`, `wav`, `aac` (tested only with `mp3`).
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.

Unteritem  ``snippet_volume``:
Wird ein untergeordnetes Item vom Typ Number mit Attribut ``sonos_attrib: snippet_volume`` definiert,
kann die Laustärke explizit für das Abspielen von Snippets gesetzt werden. Diese Snippet Lautstärke beeinflusst nicht
die Lautstärke der normalen Wiedergabe, auf die nach Abspielen des Snippets zurück gewechselt wird.
Wird ein Snippet in einer Gruppe abgespielt, wird für jeden einzelnen Speaker die ursprüngliche Lautstärke wiederhergestellt.

Unteritem  ``snippet_fade_in``:
Wird ein untergeordnetes Item vom Typ Boolean mit Attribut ``sonos_attrib: snippet_fade_in`` definiert, wird die Lautstärke
nach dem Abspielen des Snippets von `0` auf das gewünschte Level schrittweise angehoben und eingeblendet.

play_tts
--------
``write``

Spielt eine definierte Nachricht ab (Text-to-Speech). Das Item ist vom Typ String. Aus der Nachricht im String wird von dem Google TTS API eine
Audiodatei erzeugt, die lokal gespeichert und abgespielt wird.
Für die Nutzung dieses Features müssen mindestens zwei Parameter in der ``plugin.yaml`` gesetzt sein:
``tts`` und ``local_webservice_path``.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.

Unteritem ``tts_language``:
Wird ein untergeordnetes Item vom Typ String mit Attribut ``sonos_attrib: tts_language`` angelegt, kann die
Spracheinstellung der Google TTS API definiert werden.
Gültige Werte sind `en`, `de`, `es`, `fr`, `it`. Ist das Item nicht vorhanden, wird die Standardeinstellung `de` verwendet.

Unteritem ``tts_volume``:
Wird ein untergeordnetes Item vom Typ Number mit Attribut ``sonos_attrib: tts_volume`` angelegt, kann die Lautstärke
für das Abspielen von Text-to-Speech separat definiert werden. Die reguläre Lautstärke wird damit nicht beeinflusst.
Nach der Ansage wird die Lautstärke jedes Speakers individuell in der Gruppe wieder hergestellt.

Unteritem ``tts_fade_in``:
Wird ein untergeordnetes Item vom Typ Boolean mit Attribut ``sonos_attrib: tts_fade_in`` definiert, wird die Lautstärke
nach dem Abspielen der Nachricht von 0 auf das gewünschte Level schrittweise angehoben und eingeblendet.

play_sonos_radio / play_tunein
------------------------------
``write``

Spielt einen Radiosender anhand eines Namens. Das Item ist vom Typ String. Sonos sucht dazu in einer Datenbank
nach potentiellen Radiostationen, die dem Namen entsprechen.
Wird mehr als ein zum Suchbegriff passender Radiosender gefunden, wird der erste Treffer verwendet.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet. Empfohlen wird die Nutzung der Funktion play_sonos_radio.
Die alte Funktion play_tunein existiert noch, sollte aber nicht mehr verwendet werden.

Unteritem ``start_after``:
Wird ein untergeordnetes Item vom Typ Boolean mit Attribut ``sonos_attrib: start_after`` definiert, wird das
Verhalten nach dem Laden der Radiostation definiert. Der Wert `True`, startet die Wiedergabe automatisch.
Existiert das Unteritem nicht, ist die Standardeinstellung `True`.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.

play_url
--------
``write``

Spielt eine gegebene URL. Das Item ist vom Typ String, in dem die URL übergeben wird.

Unteritem ``start_after``:
Wird ein untergeordnetes Item vom Typ Boolean mit Attribut ``sonos_attrib: start_after`` definiert, wird das
Verhalten nach dem Laden der URL definiert. Wurde der obige ``group_command`` auf `True` gesetzt,
startet die Wiedergabe automatisch. Existiert das Unteritem nicht, ist die Standardeinstellung `True`.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.

play_sharelink
--------------
``write``

Spielt einen gegebenen Sharelink, z.B. einen Spotify Sharelink. In diesem Fall wird ein Premium Spotify Account benötigt, da der
kostenlose Account Sharelinks nicht unterstützt.

Unteritem  ``start_after``:
Wird ein untergeordnetes Item vom Typ Boolean mit Attribut ``sonos_attrib: start_after`` definiert, wird das
Verhalten nach dem Laden des Sharelinks definiert. Wurde der obige ``group_command`` auf `True` gesetzt,
startet die Wiedergabe automatisch. Existiert das Unteritem nicht, ist die Standardeinstellung `True`.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.

previous
--------
``write`` ``visu``

Setzt den aktuellen Track auf den Vorherigen zurück. Das Item ist vom Typ Boolean. Der Wert `True` triggert das Schalten
auf den vorherigen Track, der Wert `False` hat keinen Effekt.
Zusätzlich muss für das Item das smarthomeNG Item Attribut ``enforce_update: True`` gesetzt werden.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.

radio_station
-------------
``read`` ``visu``

Gibt den Namen des aktuellen Radiosenders zurück.
Das Item ist vom Typ String. Falls kein Radio gespielt wird, siehe ``streamtype``, ist das Item leer.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

radio_show
----------
``read`` ``visu``

Falls verfügbar (hängt von dem Radiosender ab), gibt dieses Item den Namen des aktuellen Programms zurück.
Das Item ist vom Typ String. Falls kein Radio gespielt wird, siehe ``streamtype``, ist das Item leer.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

snooze
------
``read`` ``write``

Setzt bzw. liest den Snooze Timer. Das Item ist vom Typ Number mit ganzzahligen Werten zwischen 0 - 86399 (in Sekunden).
Der Wert `0` bedeutet, dass der Snooze Timer ausgeschaltet ist.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.
Der Wert wird **nicht** in Echtzeit aktualisiert, sondern in jedem Speaker Discovery Zyklus aktualisiert.

sonos_playlists
---------------
``read`` ``visu``


Gibt eine Liste der erstellten Sonos Playlists zurück. Das Item ist vom Typ String. Die Playlists können über
``load_sonos_playlist`` geladen werden.

status_light
------------
``read`` ``write``

Setzt bzw. liest den Status der LED im Speaker. Das Item ist vom Typ Boolean. Der Wert `True` bedeutet LED eingeschaltet,
`False` bedeutet deaktiviert. Der Wert wird **nicht** in Echtzeit aktualisiert, sondern in jedem Speaker Discovery Zyklus aktualisiert.

buttons_enabled
---------------
``read`` ``write``

Setzt bzw. liest den Status des Tasters/Touchbedienung am Speaker. Das Item ist vom Typ Boolean. Der Wert `True` bedeutet
Taster/Touchbedienung eingeschaltet, `False` bedeutet deaktiviert. Der Wert wird **nicht** in Echtzeit aktualisiert,
sondern in jedem Speaker Discovery Zyklus aktualisiert.

stop
----
``read`` ``write`` ``visu``

Stoppt die Wiedergabe. Das Item ist vom Typ Boolean. Der Wert `True` steht für Stop, `False` für Wiedergabe starten.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

stream_content
--------------
``read`` ``visu``

Gibt den Inhalt wieder, der aktuell für einen Radiosender bereitgestellt wird, z.B.
aktuell gespielter Titel und Interpret. Das Item ist vom Typ String. Falls kein Radio gespielt wird, siehe ``streamtype``,
ist das Item leer.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

switch_line_in
--------------
``write``

Schaltet den Audioeingang eines Sonos Play5 (oder anderen Sonos Speaker mit Line-in Eingang) auf den Line-in Eingang.
Das Item ist vom Typ Boolean. Wert `True` triggert das Schalten auf Line-in,
`False` hat keinen Effekt.

switch_tv
---------
``write``

Nur von der Sonos Playbar unterstützt. Schaltet den Playbar auf TV Eingang. Das Item ist vom Typ Boolean. Wert `True`
bedeutet auf den TV Eingang schalten, `False` hat keine Effekt.

track_album
-----------
``read`` ``visu``

Gibt den Albumtitel des aktuellen Tracks zurück. Das Item ist vom Typ String.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

track_album_art
---------------
``read`` ``visu``

Gibt die URL des Albumcovers für den aktuellen Track zurück. Das Item ist vom Typ String.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

track_artist
------------
``read`` ``visu``

Gibt den Artisten des aktuellen Track zurück. Das Item ist vom Typ String.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

track_title
-----------
``read`` ``visu``

Gibt den Titel des aktuellen Tracks zurück. Das Item ist vom Typ String.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

track_uri
---------
``read`` ``visu``

Gibt die URI (Link) auf den aktuell wiedergegebenen Track zurück. Das Item ist vom Typ String.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

treble
------
``read`` ``write``

Setzt bzw. liest das Höhen Level eines Speakers. Das Item ist vom Typ Number und muss ein ganzzahligen Wert zwischen -10 and 10 enthalten.
Diese Eigenschaft ist **kein** Gruppenbefehl. Nichtsdestotrotz kann ein untergeordnetes Item ``group_command: True`` definiert werden,
um die Höheneinstellung für alle Speaker innerhalb der Gruppe zu übernehmen.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

uid
---
``read``

Gibt die eindeutige Speaker ID als String zurück.

unjoin
------
``write``

Entkoppelt einen Speaker aus einer Gruppe.

Unteritem ``start_after``:
Wird ein untergeordnetes Item vom Typ Boolean mit Attribut ``sonos_attrib: start_after`` definiert, wird dadurch das Verhalten
nach Entkopplung festgelegt.
Ein Wert `True` bedeutet, der entkoppelte Speaker startet seine individuelle Wiedergabe, `False` startet keine Wiedergabe.
Dieses Unteritem ist optional und kann weggelassen werden. In dem Fall greift das Standardverhalten als keine Wiedergabe.

volume
------
``read`` ``write`` ``visu``

Setzt bzw. liest den Lautstärkepegel eines Speakers. Das Item ist vom Typ Number und muss ein ganzzahliger Wert zwischen 0-100 sein.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.
Es wird empfohlen, zusätzlich das Item Attribut ``enforce_updates: true`` zu setzen.

Unteritem ``group_command``:
Wird ein untergeordnetes Item vom Typ Boolean mit Attribut ``sonos_attrib: group_command`` definiert, wird die Lautstärke
auf alle Speaker innerhalb der Gruppe angewendet.

Unteritem ``max_volume``:
Wird ein untergeordnetes Item vom Typ Number mit Attribut ``sonos_attrib: max_volume`` definiert, wird der Wert der
maximal möglichen Lautstärke auf den Wert begrenzt. Wertebereich ist 0-100. Dies betrifft nicht das Setzen der Lautstärke via Sonos APP.
Wurde der obige ``group_command`` auf `True` gesetzt, betrifft die Begrenzung alle Speaker innerhalb der Gruppe.

Unteritem  ``volume_dpt3``:
Um die Lautstärke inkrementell via KNX dpt3 ohne externe Logik zu verstellen, kann optional dieses untergeordnete Item definiert werden.
Hierzu wird ein untergeordnetes Item mit ``volume_dpt3`` angelegt, siehe Beispiel 4).

zone_group_members
------------------
``read``

Gibt eine Liste aller UIDs aus, die sich in der Gruppe des Speakers befinden. Die Liste enthält auch den aktuellen Speaker.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

sonos_favorites
---------------
``read``

Liest die Liste der gespeicherten Sonos Favoriten. Das Item ist vom Typ List.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

favorite_radio_stations
-----------------------
``read``

Liest die Liste der gespeicherten Tunein Favoriten. Das Item ist vom Typ List.
Das Item wird über Sonos Events aktualisiert und zeigt daher immer den aktuellen Status an.

play_favorite_title
-------------------
``write``

Spielt einen gespeicherten Sonos Favoriten anhand eines Namens. Das Item ist vom Typ String.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.
Die Liste der gespeicherten Favoriten kann mit dem Attribut ``sonos_favorites`` einem Item zugewiesen werden.

play_favorite_number
--------------------
``write``

Spielt einen gespeicherten Sonos Favoriten anhand der Nummer des Listeneintrages. Das Item ist vom Typ Number
und muss zwischen 1 und Länge der Favoritenliste liegen. Letztere kann mit dem Attribut ``sonos_favorites`` einem Item zugewiesen werden.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.

play_favorite_radio_title
-------------------------
``write``

Spielt einen gespeicherten Tunein Radio Favoriten anhand eines Namens. Das Item ist vom Typ String.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.
Die Liste der gespeicherten Favoriten kann mit dem Attribut ``favorite_radio_stations`` einem Item zugewiesen werden.

play_favorite_radio_number
--------------------------
``write``

Spielt einen gespeicherten Tunein Radio Favoriten anhand der Nummer des Listeneintrages. Das Item ist vom Typ Number
und muss zwischen 1 und Länge der Radiofavoritenliste liegen. Letztere kann mit dem Attribut ``favorite_radio_stations`` einem Item zugewiesen werden.
Der Befehl ist ein Gruppenbefehl und wird für alle Speaker einer Gruppe angewendet.


Nicht echtzeitfähige Eigenschaften
----------------------------------

Einige Eigenschaften sind nicht Event basiert. Das bedeutet, dass sie nicht direkt nach
Änderung über ein Event aktualisiert werden, sondern die Änderung erst bei der nächsten
zyklischen Abfrage bei smarthomeNG ankommt.

Folgende Eigenschaften sind **nicht** Event basiert:

- snooze
- status_light


Gruppenbefehle
--------------
Einige Items werden immer als Gruppenbefehl, d.h. auf alle Speaker innerhalb einer Gruppe ausgeführt.
Folgende Methoden sind Gruppenbefehle:

* play
* pause
* stop
* mute
* cross_fade
* snooze
* play_mode
* next
* previous
* play_tunein
* play_url
* load_sonos_playlist

Für diese Items ist es egal, für welchen Speaker einer Gruppe diese Kommandos gesendet werden. Sie werden automatisch für alle
Speaker einer Gruppe angewendet.


Beispiele
=========

1) Radiosender abspielen
------------------------

Ein Radiosender wird über play_tunein ausgewählt.

.. code-block:: text

    sh.Sonos.Speaker.play_tunein('WDR2')
    sh.Sonos.Speaker.play(True)
    sh.Sonos.Speaker.mute(False)

2) Sonos Playlist abspielen
---------------------------

Eine Sonos Playliste wird über ``load_sonos_playlist`` ausgewählt.
Alle verfügbaren Playlists werden mit ``sonos_playlist`` angezeigt.

.. code-block:: text

    sh.Sonos.Speaker.load_sonos_playlist('NameDerPlaylist')

3) Nutzung der `is_initialized` Eigenschaft
-------------------------------------------

Nach Start dauert es etwas, bis alle Sonos Speaker im Netzwerk initialisiert sind. Es ist deshalb angeraten,
die Methode ``is_initialized`` in Logiken zu verwenden. Gibt die Eigenschaft `True` zurück, so ist der Speaker
erreichbar und funktional. `False` bedeutet, der Speaker ist noch nicht initialisiert oder offline.

Beispiel:

.. code-block:: python

    if sh.MySonosPlayer.is_initialized():
        do_something()

4a) Lautstärke inkrementell verstellen (via KNX dpt3)
-----------------------------------------------------

Dieses Beispiel zeigt die Verstellung der Laustärke inkrementell via dpt3:

.. code-block:: yaml

    volume:
        ...
        ...
        volume_dpt3:
            type: list
            sonos_attrib: vol_dpt3
            sonos_dpt3_step: 2
            sonos_dpt3_time: 1

            helper:
                sonos_attrib: dpt3_helper
                type: num
                sonos_send: volume

Bitte sicherstellen, dass ein entsprechendes helper Item definiert wird. Über das Attribut ``sonos_dpt3_step``
werden die Laustärkeinkremente definiert und über ``sonos_dpt3_time`` die Zeit pro Inkrement. Beide Werte können
weggelassen werden. Dann werden die Standardwerte ``sonos_dpt3_step: 2`` und ``sonos_dpt3_step: 1`` verwendet.
Die Eigenschaften ``group_command`` und ``max_volume`` werden hierbei berücksichtigt.

4b) Erweitertes DPT3 Beispiel
-----------------------------

.. code-block:: yaml

    Kueche:
        sonos_uid: rincon_000e58cxxxxxxxxx

        volume:
          type: num
          sonos_recv: volume
          sonos_send: volume
          enforce_updates: true

          group_command:
            type: bool
            value: false
            sonos_attrib: group

          max_volume:
            type: num
            value: -1
            sonos_attrib: max_volume

          volume_dpt3:
            type: list
            sonos_attrib: vol_dpt3
            sonos_dpt3_step: 4
            sonos_dpt3_time: 1
            knx_dpt: 3
            knx_listen: 7/1/0

            helper:
              sonos_attrib: dpt3_helper
              type: num
              sonos_send: volume


5) Minimalbeispiel
------------------

Für ein Minimalbeispiel muss ein item mit dem Attribut ``sonos_uid`` und mindestens einem Unteritem definiert werden.
Beispiel:

.. code-block:: yaml

    MyRoom:
        MySonos:
            sonos_uid: rincon_xxxxxxxxxxxxxx

            play:
                type: bool
                sonos_recv: play
                sonos_send: play


Web Interface
=============

Das Plugin kann aus dem Admin Interface aufgerufen werden. Dazu auf der Seite Plugins in der entsprechenden
Zeile das Icon in der Spalte **Web Interface** anklicken.

Außerdem kann das Webinterface direkt über ``http://smarthome.local:8383/sonos`` aufgerufen werden.

Folgende Informationen können im Webinterface angezeigt werden:

 - Oben rechts werden allgemeine Parameter zum Plugin wie die verwendete SoCo Version angezeigt und die Anzahl der Speaker
   angezeigt, die aktuell online und verwendbar sind..
 - Tab Items: Mit dem Plugin verbundene Items
 - Tab Speakers/Zones: Details zu den Speakern/Zones im Netzwerk u.a. UID


SmartVisu Widget
================

Zur Nutzung des Sonos Widgets für SmartVisu die Dateien (html, css, js) unter
``plugins/sonos/sv_widget`` in den Ordner ``dropins/widgets`` der SmartVisu kopieren.

Sofern alle Sonos Items gemäß Beispiel Struct definiert worden sind, wird das Widget so integriert:

.. code-block:: html

    {% import "widget_sonos.html" as sonos %}
    {% block content %}

    <div class="block">
      <div class="set-2" data-role="collapsible-set" data-theme="c" data-content-theme="a" data-mini="true">
        <div data-role="collapsible" data-collapsed="false" >
          {{ sonos.player('sonos_kueche', 'Sonos.Kueche') }}
        </div>
      </div>
    </div>

    {% endblock %}
