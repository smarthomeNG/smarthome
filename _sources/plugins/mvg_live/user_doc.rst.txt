.. index:: Plugins; mvg_live
.. index:: mvg_live

========
mvg_live
========

Das Plugin fragt Abfahrtszeiten von Haltestellen der Münchner Verkehrsbetriebe (MVG) über die
Python-Bibliothek ``mvg`` ab. Häufige Abfragen sollten vermieden werden, z.B. durch eine manuell
ausgelöste Aktualisierung statt eines festen Abfrage-Zyklus.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/mvg_live` beschrieben.


Beispiele
=========

Das Plugin liefert keine vordefinierten Items. Für eine Abfrage per Logik werden z.B. folgende
Items benötigt::

    travel_info:

        mvg_station:

            search:
                type: str
                cache: 'yes'
                visu_acl: rw

                result:
                    type: str
                    cache: 'yes'
                    visu_acl: ro

                refresh:
                    type: bool
                    visu_acl: rw
                    enforce_updates: 'true'

Eine Logik kann auf Änderungen von **search** und **search.refresh** reagieren und die Abfahrten
über **get_station_departures()** (siehe :doc:`/plugins_doc/config/mvg_live`) abrufen und z.B. als
HTML-Tabelle in **search.result** ablegen::

    MVGWatch:
        filename: mvg.py
        watch_item:
          - travel_info.mvg_station.search
          - travel_info.mvg_station.search.refresh
