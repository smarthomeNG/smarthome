.. index:: Plugins; wettercom
.. index:: wettercom

=========
wettercom
=========

Das Plugin ruft Wettervorhersagedaten für einen registrierten Standort über die wetter.com API ab
und stellt sie über eine Logik in Items zur Verfügung.

Voraussetzungen
================

Für die Nutzung wird ein wetter.com-Account mit einem eigenen Projekt benötigt. Empfohlen wird ein
Projekt mit einer Vorlaufzeit von 3 Tagen und allen verfügbaren Datenfeldern.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/wettercom` beschrieben.

Item-Structs
------------

Das Plugin liefert das Item-Struct **wetter** mit der vollständigen Vorhersagestruktur (**heute**,
**morgen**, **uebermorgen**, jeweils unterteilt in **frueh**, **mittag**, **spaet** und **nacht**)
mit. Es wird wie folgt in die eigene Item-Konfiguration eingebunden::

    wetter:
        struct: wettercom.wetter

Die vollständige Struktur ist auf der :doc:`Konfigurationsseite </plugins_doc/config/wettercom>`
aufgelistet.

Verwendung
==========

Das Plugin stellt zwei Funktionen bereit, die aus einer Logik heraus aufgerufen werden:

**search(location)**
    Sucht auf wetter.com nach dem City-Code eines Orts. Gibt ein leeres Dictionary zurück, wenn
    kein Treffer gefunden wurde, andernfalls eine Liste von City-Codes (bester Treffer zuerst).

**forecast(city_code)**
    Ruft die Vorhersagedaten für einen City-Code ab (ermittelbar über **search()** oder die
    wetter.com-Webseite). Das Ergebnis ist ein Dictionary, das für jeden Vorhersagezeitpunkt
    (üblicherweise drei Tage zu je vier Zeitpunkten) eine Liste mit acht Werten enthält: minimale
    Temperatur, maximale Temperatur, Wettertext, Niederschlagswahrscheinlichkeit,
    Windgeschwindigkeit, Windrichtung in Grad, Windrichtung als Text und Wettercode.

Da wetter.com die Anzahl der Abfragen auf 10000 pro Monat begrenzt, sollte **forecast()** zyklisch
aus einer Logik heraus aufgerufen werden, z.B. alle 900 Sekunden::

    wettercom:
        filename: wettercom.py
        crontab: init
        cycle: 900

Die Logik kann die zurückgegebenen Werte anschließend den Feldern des **wetter**-Structs zuweisen,
hier am Beispiel des heutigen Vormittags (**frueh**)::

    forecast = sh.wettercom.forecast('CITYCODE')
    werte = forecast[zeitpunkt]

    frame = sh.wetter.vorhersage.heute.frueh
    frame.temperatur.min(werte[0])
    frame.temperatur.max(werte[1])
    frame.text(werte[2])
    frame.niederschlag(werte[3])
    frame.wind.geschwindigkeit(werte[4])
    frame.wind.richtung(werte[5])
    frame.wind.richtung.text(werte[6])
    frame.code(werte[7])
