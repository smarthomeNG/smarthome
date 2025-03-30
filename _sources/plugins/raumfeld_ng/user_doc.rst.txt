.. index:: Plugins; raumfeld_ng
.. index:: raumfeld_ng


===========
raumfeld_ng
===========


Das Plugin verbindet den raumfeld node-raumserver mit SmartHomeNG
Es ist möglich damit eine raumfeld/teufel Multiraum System zu steuern.

Anforderungen
=============

...

Notwendige Software
-------------------

-  https://github.com/ChriD/node-raumserver

Unterstützte Geräte
-------------------

-  Raumfeld / Teufel Multiraum Lautsprecher System

Konfiguration
=============

Die Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/raumfeld_ng` beschrieben.


plugin.yaml
-----------

Zu den Informationen, welche Parameter in der ../etc/plugin.yaml konfiguriert werden können bzw. müssen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/raumfeld_ng>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

.. code:: yaml

   raumfeld_ng:
       plugin_name: raumfeld_ng
       rf_HostIP: '127.0.0.1'
       rf_HostPort: '8080'

Ein Hostname oder eine Host IP sowie ein Port werden benötigt.


items.yaml
----------

Zu den Informationen, welche Attribute in der Item Konfiguration verwendet werden können bzw. müssen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/raumfeld_ng>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).


Es gibt zwei Gruppen von Item Attributen: Eine für Geräte (speaker) und eine für Zonen (group of speaker)
Die Konfiguration der Zonen kann mit dem Plugin nicht geändert werden.

Geräte Attribute
^^^^^^^^^^^^^^^^

Beispiel:

.. code:: yaml

    kueche:
        # read / write the powerstate of the device 
        rf_power_state_kueche:
            type: bool 
            rf_renderer_name: "Kueche"
            rf_attr: power_state 
            rf_scope: room 
            initial_value: False
            enforce_updates: ‘yes’

        # read / write the volume of the device
        rf_volume_kueche:
            type: num
            rf_renderer_name: "Kueche"
            rf_attr: set_volume
            rf_scope: room
            mode: absolute
            initial_value: 30
            enforce_updates: 'yes'

        # write only - mute / unMute / toggleMute
        rf_set_mute_kueche:
            type: str
            rf_renderer_name: "Kueche"
            rf_attr: set_mute
            rf_scope: room
            enforce_updates: 'yes'

Zonen Attribute
^^^^^^^^^^^^^^^

.. code:: yaml

    zone_kueche:
        # read / write the play state of the zone
        rf_play_state_kueche:
            type: str
            rf_renderer_name: "Kueche"
            rf_attr: play_state
            rf_scope: zone
            enforce_updates: 'yes'

        # write only list ["playlist", tracknum], without tracknum start first track (zone)
        rf_load_playlist_kueche:
            type: list
            rf_renderer_name: "Kueche"
            rf_attr: load_playlist
            rf_scope: zone
            enforce_updates: 'yes'

        # write only the track to play
        rf_load_track_kueche:
            type: num
            rf_renderer_name: "Kueche"
            rf_attr: load_track
            rf_scope: zone
            enforce_updates: 'yes'

        # read only the zone mediainfo
        rf_mediainfo_kueche:
            type: list
            rf_renderer_name: "Kueche"
            rf_attr: get_mediainfo
            rf_scope: zone
            enforce_updates: 'yes'

logic.yaml
----------

Zu den Informationen, welche Konfigurationsmöglichkeiten für Logiken bestehen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/raumfeld_ng>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

Funktionen
----------

Zu den Informationen, welche Funktionen das Plugin bereitstellt (z.B. zur Nutzung in Logiken), bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/raumfeld_ng>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).


Beispiele
=========

# diese beiden Funktionen sehe ich pro speaker, Media geht ja nicht, da man das nur in der Zone spielen kann.
# es sollte tatsächlich gehen, dass die beiden Items jeweils auseinandergehalten werden. Das sollte dann einmal
# - speaker1.rfpower_state
# und einmal
# - speaker2.rfpower_state
# sein.

.. code:: yaml

        speaker1:
            rf_power_state:
                type: bool
                rf_zone_name: Bad-Kueche
                rf_room_name: Bad
                rf_scoop: room        
                rf_attr: power_state
                initial_value: False

            rf_volume_level:
                type: num
                rf_zone_name: Bad
                rf_scoop: room        
                rf_attr: volume_level
                initial_value: 25


        speaker2:
            rf_power_state:
                type: bool
                rf_zone_name: Bad-Kueche
                rf_room_name: Kueche
                rf_scoop: room        
                rf_attr: power_state
                initial_value: False

            rf_volume_level:
                type: num
                rf_zone_name: Bad
                rf_scoop: room        
                rf_attr: volume_level
                initial_value: 25

        zone_bad_kueche:
            rf_volume_level:
                type: num
                rf_zone_name: Bad-Kueche
                rf_scoop: zone
                rf_attr: volume_level
                initial_value: 25

            rf_media_uri:
                type: str
                rf_zone_name: Bad-Kueche
                rf_scoop: zone
                rf_attr: loaduri

            rf_media_playlist:
                type: str
                rf_zone_name: Bad-Kueche
                rf_scoop: zone
                rf_attr: loadplaylist

Web Interface
=============

Es ist aktuell kein Webinterface vorhanden.