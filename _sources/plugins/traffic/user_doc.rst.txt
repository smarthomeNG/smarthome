.. index:: Plugins; traffic
.. index:: traffic

=======
traffic
=======

Das Plugin fragt Reisezeiten und Streckeninformationen über die kostenlose
`Google Directions API <https://developers.google.com/maps/documentation/directions/intro?hl=de#traffic-model>`_
ab. Die Zuordnung der Ergebnisse zu Items erfolgt über eigene Logiken.


Voraussetzungen
================

Für den Zugriff auf die Google Directions API wird ein persönlicher API-Key benötigt (siehe oben
verlinkte Google-Dokumentation). Das kostenlose Kontingent ist auf 2500 Anfragen pro Tag begrenzt.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/traffic` beschrieben.


Beispiele
=========

Das Plugin liefert keine vordefinierten Items, die Ergebnisse einer Routenabfrage werden über eine
eigene Logik in selbst angelegte Items geschrieben. Ein möglicher Item-Aufbau::

    travel_info:

        travel_time:
            type: num

            in_traffic:
                type: num

        travel_distance:
            type: num

        travel_summary:
            type: str

        start_address:
            type: str

        end_address:
            type: str


Verwendung
==========

Routeninformationen werden aus Logiken heraus über die Funktion **get_route_info()** abgefragt
(Instanzname entsprechend der eigenen Konfiguration, Parameter siehe
:doc:`/plugins_doc/config/traffic`). Zurückgegeben wird ein dict (bei ``alternatives=True`` eine
Liste von dicts) mit Routeninformationen, u.a. **distance** (in Metern), **duration** (in Sekunden)
und **summary**::

    route = sh.traffic.get_route_info(sh._lat + ',' + sh._lon, 'Berlin', False, 'now', 'driving')
    sh.travel_info.travel_time(route['duration'])
    sh.travel_info.travel_time.in_traffic(route['duration_in_traffic'])
    sh.travel_info.travel_distance(route['distance'])
    sh.travel_info.travel_summary(route['summary'])
    sh.travel_info.start_address(route['start_address'])
    sh.travel_info.end_address(route['end_address'])
