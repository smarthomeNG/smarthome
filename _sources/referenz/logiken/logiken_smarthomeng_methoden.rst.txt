:tocdepth: 5

.. index:: SmartHomeNG Methoden; Logiken
.. index:: Logiken; SmartHomeNG Methoden


====================
SmartHomeNG Methoden
====================

.. include:: /referenz/smarthomeng/feiertage_datum_zeit.rst


.. include:: /referenz/smarthomeng/methoden_sonne_mond.rst



sh.tools Objekt
===============

Das ``sh.tools`` Objekt stellt folgende nützliche Funktionen zur Verfügung:

sh.tools.ping()
---------------

Sendet ein Ping an einen Computer und liefert das Ergebnis. Beispiel:

``sh.office.laptop(sh.tools.ping('hostname'))``

setzt das Item ``office.laptop`` entsprechend der Rückmeldung ob ein Ping erfolgreich war oder nicht.

sh.tools.dewpoint()
-------------------

Berechnet den Taupunkt für eine gegebene Temperatur und Feuchtigkeit. Beispiel:

``sh.office.dew(sh.tools.dewpoint(sh.office.temp(), sh.office.hum())``

setzt das Item ``office.dew`` auf das Ergebnis der Taupunktberechnung der Itemwerte von ``office.temp`` und ``office.hum``

sh.tools.fetch_url()
--------------------

Liefert dem Inhalt einer Webseite als String oder ``False`` wenn ein Fehler auftritt.

``sh.tools.fetch_url('https://www.regular.com')``

Es ist möglich als Parameter den Benutzernamen und ein Password anzugeben um die Abfrage bei der zu authentifizieren.

``sh.tools.fetch_url('https://www.special.com', 'username', 'password')``

Weiterhin kann ein Parameter für eine Zeitüberschreitung bestimmt werden:

``sh.tools.fetch_url('https://www.regular.com', timeout=4)``

bricht nach 4 Sekunden ohne Ergebnis ab

sh.tools.dt2ts(dt)
------------------

Wandelt ein datetime Objekt in einen Unix Zeitstempel um.

sh.tools.dt2js(dt)
------------------

Wandelt ein datetime Objekt in einen json Zeitstempel um.


sh.tools.rel2abs(temp, hum)
---------------------------

Wandelt einen relativen Feuchtigkeitswert in einen absoluten Feuchtigkeitswert um.


sh.tools.runtime()
------------------

Liefert die Laufzeit von SmartHomeNG zurück.


