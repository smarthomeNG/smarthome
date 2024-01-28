.. index:: Plugins; executor
.. index:: executor

========
executor
========


.. image:: webif/static/img/plugin_logo.svg
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Einführung
~~~~~~~~~~

Das executor Plugin kann genutzt werden, um **Python Code** (z.B. für **Logiken**) zu testen.

.. important::

  Seien Sie sich bewusst, dass die Aktivierung dieses Plugins ein Sicherheitsrisiko darstellen könnte.
  Wenn andere Personen Zugriff auf die Web-Schnittstelle erhalten,
  kann man das ganze SmartHomeNG-Biest kontrollieren. Seien Sie also vorsichtig!!!


Konfiguration
=============

Das Aktivieren des Plugins ist ausreichend. Optional kann noch ein Verzeichnis für Skripte konfiguriert werden
über das Attribut ``executor_scripts`` in der ``plugin.yaml``.
Damit wird dem Plugin eine relative Pfadangabe unterhalb *var* angegeben wo Skripte für das Executor Plugin abgelegt werden.

Webinterface
============

Im Webinterface findet sich eine Listbox mit den auf dem Rechner gespeicherten Skripten.
Um das Skript in den Editor zu laden, entweder ein Skript in der Liste einfach anklicken und auf *aus Datei laden* klicken oder
direkt in der Liste einen Doppelklick auf die gewünschte Datei ausführen.

Der Dateiname wird entsprechend der gewählten Datei gesetzt. Mit Klick auf *aktuellen Code speichern* wird der Code im konfigurierten
Skript Verzeichnis unter dem aktuell in der Eingabebox vorgegebenem Dateinamen abgespeichert.

Mit einem Klick auf *Code ausführen!* oder der Kombination Ctrl+Return wird der Code an SmartHomeNG gesendet und ausgeführt.
Das kann gerade bei Datenbank Abfragen recht lange dauern. Es kann keine Rückmeldung von SmartHomeNG abgefragt werden wie weit der Code derzeit ist.
Das Ergebnis wird unten angezeigt. Solange kein Ergebnis vorliegt, steht im Ergebniskasten **... processing ...**

Mit einem Klick auf *Datei löschen* wird versucht, die unter Dateiname angezeigte Datei ohne Rückfrage zu löschen.
Anschliessend wird die Liste der Skripte aktualisiert.

Beispiel Python Code
====================

Sowohl ``logger`` als auch ``print`` funktionieren für die Ausgabe von Ergebnissen.
Die Idee ist, dass Logiken mehr oder weniger 1:1 kopiert und getestet werden können.


Loggertest
----------

.. code-block:: python

    logger.warning("Eine Warnung")
    logger.info("Eine Info")
    logger.debug("Eine Debugmeldung")
    logger.error("Eine Debugmeldung")


Datenserien für ein Item ausgeben
---------------------------------

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


würde in folgendem Ergebnis münden:

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


Zählen der Datensätze in der Datenbank
--------------------------------------

Das folgende Snippet zeigt alle Datenbank-Items an und zählt die Einträge in der Datenbank. Vorsicht: Dies kann sehr lange dauern, wenn Sie eine große Anzahl von Einträgen mit Datenbankattributen haben.

.. code-block:: python

    from lib.item import Items
    items = Items.get_instance()
    myfiller = "                                                            "
    allItems = items.return_items()
    for myItem in allItems:
        if not hasattr(myItem,'db'):
            continue
        mycount = myItem.db('countall', 0)
        print (myItem.property.name + myfiller[0:len(myfiller)-len(myItem.property.name)]+ ' - Anzahl Datensätze :'+str(mycount))
