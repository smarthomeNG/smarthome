:tocdepth: 5

.. index:: SmartHomeNG Methoden; Logiken
.. index:: Logiken; SmartHomeNG Methoden


====================
SmartHomeNG Methoden
====================

.. include:: /referenz/smarthomeng/feiertage_datum_zeit.rst


.. include:: /referenz/smarthomeng/methoden_sonne_mond.rst



Hilfsfunktionen
===============

Das frühere ``sh.tools`` Objekt gibt es nicht mehr. Seine Funktionen stehen in den Bibliotheken ``lib.utils``,
``lib.network`` und im ``sh.shtime`` Objekt zur Verfügung:

Ping
----

Sendet ein Ping an einen Computer und liefert das Ergebnis. Beispiel:

.. code:: python

   from lib.network import Network

   sh.office.laptop(Network.ping('hostname'))

setzt das Item ``office.laptop`` entsprechend der Rückmeldung ob ein Ping erfolgreich war oder nicht.

Taupunkt und Feuchtigkeit
-------------------------

``Utils.dewpoint(temp, hum)`` berechnet den Taupunkt für eine gegebene Temperatur und relative Feuchtigkeit.
``Utils.rel2abs(temp, hum)`` wandelt einen relativen Feuchtigkeitswert in einen absoluten Feuchtigkeitswert um,
``Utils.abs2rel(temp, abs_hum)`` wandelt zurück. Beispiel:

.. code:: python

   from lib.utils import Utils

   sh.office.dew(Utils.dewpoint(sh.office.temp(), sh.office.hum()))

setzt das Item ``office.dew`` auf das Ergebnis der Taupunktberechnung der Itemwerte von ``office.temp`` und ``office.hum``

Inhalt einer Webseite abrufen
-----------------------------

``Http.get_binary()`` liefert den Inhalt einer Webseite als Bytes oder ``None``, wenn ein Fehler auftritt.
Mit ``require_ok=True`` wird auch bei einem anderen Status als 200 ``None`` geliefert.

.. code:: python

   from lib.network import Http

   content = Http().get_binary('https://www.regular.com', require_ok=True)

Zur Authentifizierung kann ``auth=('username', 'password')`` angegeben werden, eine Zeitüberschreitung wird mit
``timeout=4`` (Sekunden) bestimmt. Mit ``Http().get_text()`` erhält man den Inhalt als String.

Zeitstempel
-----------

Ein datetime Objekt ``dt`` wird mit ``dt.timestamp()`` in einen Unix Zeitstempel umgewandelt, mit
``dt.timestamp() * 1000`` in einen Zeitstempel für JavaScript (json).

Laufzeit
--------

``sh.shtime.runtime()`` liefert die Laufzeit von SmartHomeNG zurück.
