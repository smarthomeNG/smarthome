.. index:: Plugins; executor
.. index:: executor

executor
########

Einführung
==========

Das executor plugin kann genutzt werden, um **eval Ausdrücke** und **Python Code** (z.B. für **Logiken**) zu testen.

.. important::

  Seien Sie sich bewusst, dass die Aktivierung dieses Plugins ein Sicherheitsrisiko darstellen könnte. Wenn andere Personen Zugriff auf die Web-Schnittstelle erhalten,
  kann man das ganze SmartHomeNG-Biest kontrollieren. Seien Sie also vorsichtig!!!


Konfiguration
=============

Das Aktivieren des Plugins ist ausreichend.

Beispiele für Eval
==================

.. code-block:: python

    12 if 23 % 3 == 5 else None

Würde im Ergebnis **None** resultieren.

.. code-block:: python

    sh..child() + 4

Da sich im Evalausdruck ein relatives Item befindet, ist es notwendig im Feld "Itempfad" das Item anzugeben, dem das im Code angegebene Unteritem zugewiesen ist.

Beispiel Python Code
====================

Sowohl``logger`` als auch ``print`` funktionieren für die Ausgabe von Ergebnissen. Die Idee ist, dass Logiken mehr oder weniger 1:1 kopiert und getestet werden können.

Loggertest

.. code-block:: python

    logger.warning("Eine Warnung")
    logger.info("Eine Info")
    logger.debug("Eine Debugmeldung")
    logger.error("Eine Debugmeldung")


Datenserien für ein Item ausgeben

Abfragen von Daten aus dem database plugin für ein spezifisches Item:

.. code-block:: python

    import json

    def myconverter(o):
        import datetime
        if isinstance(o, datetime.datetime):
          return o.__str__()
    data = sh.<your item here>.series('max','1d','now')
    pretty = json.dumps(data, default = myconverter, indent = 2, separators=(',', ': '))
    print(pretty)


würde in folgendem Ergebnis münden.

.. code-block:: json

    {
      "sid": "ArbeitszimmerOG.Raumtemperatur|max|1d|now|100",
      "cmd": "series",
      "update": "2019-11-09 17:54:22.205668+01:00",
      "params": {
        "sid": "ArbeitszimmerOG.Raumtemperatur|max|1d|now|100",
        "update": true,
        "start": 1573317598203,
        "end": "now",
        "func": "max",
        "item": "ArbeitszimmerOG.Raumtemperatur",
        "step": 864000
      },
      "series": [
        [
          1573231198203,
          21.0
        ],
        [
          1573232535421,
          21.2
        ]
      ]
    }
