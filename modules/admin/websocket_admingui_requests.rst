

Requests von der Admin GUI an SmartHomeNG
-----------------------------------------

item
~~~~

Mit dem ``item`` Befehl kann ein Client die Änderung eines Item Wertes anfordern.

Das Beispiel fordert an, das Item mit der id with the id ``wohnung.buero.schreibtischleuchte.onoff`` auf den
Wert 0 (für Off) zu ändern:

.. comment .. code-block:: JSON
.. code::

  {
  "cmd":"item",
  "id":"wohnung.buero.schreibtischleuchte.onoff",
  "val":"0"
  }

Das Plugin sendert keine Antwort zu dem ``item`` Befehl.


monitor
~~~~~~~

Mit dem ``monitor`` Befehl kann ein Client die aktuellen Werte einer Liste von Items anfordern.
Die Liste der Items für die Werte angefordert werden, muss durch Kommata getrennt sein, wie es das
folgende Beispiel zeigt:

.. comment .. code-block:: JSON
.. code::

  {
    "cmd":"monitor",
    "items":[
      "wohnung.hauswirtschaft.deckenlicht",
      "wohnung.hauswirtschaft.waschmaschine",
      "wohnung.hauswirtschaft.waschmaschine.status",
      "wohnung.hauswirtschaft.waschmaschine.ma",
      "wohnung.hauswirtschaft.trockner",
      "wohnung.hauswirtschaft.trockner.status",
      "wohnung.hauswirtschaft.trockner.ma",
      ]
  }

Das Plugin antwortet mit einer Liste von Wertepaaren, wobei jedes Wertepaar aus der Item-Id und dem zugehörigen
Wert besteht.

Nach der Liste folgt noch die Angabe der Befehls-Typs, der die Antwort ausgelöst hat-
Eine Antwort zu dem oben beschriebenen Request kann folgendermaßen aussehen:

.. comment .. code-block:: JSON
.. code::

  {
    "items": [
      ["wohnung.hauswirtschaft.deckenlicht", false],
      ["wohnung.hauswirtschaft.waschmaschine", true],
      ["wohnung.hauswirtschaft.waschmaschine.status", 1],
      ["wohnung.hauswirtschaft.waschmaschine.ma", 37],
      ["wohnung.hauswirtschaft.trockner", true],
      ["wohnung.hauswirtschaft.trockner.status", 1],
      ["wohnung.hauswirtschaft.trockner.ma", 0]
    ],
    "cmd": "item"
  }

Zusätzlich initialisiert das Plugin eine Update Routine, welche bei Änderungen von Item Werten in SmartHomeNG
automatisch eine Information an den Client sendet.
Zum Beispiel:

.. comment .. code-block:: JSON
.. code::

  {
    "items": [
      ["wohnung.hauswirtschaft.waschmaschine.ma", 36]
    ],
    "cmd": "item"
  }


ping
~~~~

Mit dem ``ping`` Befehl kann ein Client prüfen, ob die Verbindung zum Plugin besteht.

.. comment .. code-block:: JSON
.. code::

  {"cmd":"ping"}

Das Plugin antwortet mit:

.. comment .. code-block:: JSON
.. code::

  {"cmd":"pong"}


series
~~~~~~

Mit dem ``series`` Befehl kann ein Client eine Serie von Werten zu einem Item anfordern. Die angeforderten Werte
werden dazu aus einer Datenbank gelesen, in der das **database** Plugin sie abgelegt hat. Daher kann der ``series``
Befehl nur Werte für Items liefern, die so konfiguriert sind, dass sie Daten im **database** Plugin speichern.

Der ``series`` Befehl wird von der Admin GUI genutzt, um Daten für das plot-Widget zu erhalten. Das folgende
Beispiel fordert eine Serie von Mittelwerten der letzten 48 Stunden an. Die Serie soll 100 Werte umfassen:

.. comment .. code-block:: JSON
.. code::

  {
   "cmd":"series",
   "item":"wohnung.verteilung.zaehler.wirkleistung",
   "series":"avg",
   "start":"48h",
   "end":"now",
   "count":100
  }

Das Attribut ``series`` im Befehl definiert, welche Funktion genutzt wird, um die Werte für die Serie zu ermitteln.
Mögliche Functionen sind **min**, **max**, **avg** und **sum**. Diese Funktionen sind im **database** Plugin
implementiert. Falls das ``end`` Attribut weggelassen wird, wird ``"end":"now"`` durch das Plugin angenommen.
Falls das ``count`` Attribut weggelassen wird, wird ``"count":100`` durch das Plugin angenommen.

Die Antwort zu dem oben beschriebenen Request kann folgendermaßen aussehen:

.. comment .. code-block:: JSON
.. code::

  {
    "series": [
        [1460636598495, 1831.97],
        [1460637648422, 1458.14],
        [1460639298307, 757.22],
        [1460641098243, 577.38],
        "... 102 values in total",
        [1460802051217, 740.61],
        [1460803884973, 637.61],
        [1460805521319, 744.41],
        [1460807229532, 718.03],
        [1460808823757, 681.25],
        [1460809294663, 681.25]
    ],
    "cmd": "series",
    "params": {
      "end": "now",
      "start": 1460809294663,
      "update": true,
      "item": "wohnung.verteilung.zaehler.wirkleistung",
      "step": 1728000.01,
      "func": "avg",
      "sid": "wohnung.verteilung.zaehler.wirkleistung|avg|48h|now"
    },
    "update": "2016-04-16T21:14:50.20.8227+02:00",
    "sid": "wohnung.verteilung.zaehler.wirkleistung|avg|48h|now"
  }

Das Plugin antwortet mit einer List von Werte-Paaren. Jedes Werte-Paar besteht aus einem timestamp und dem
zugehörigen Item Wert. Der Liste folgt der Befehls-Typ, der die Serie angefordert hat und die Parameter, die zur
Erzeugung der Serie genutzt wurden.

Die letzten beiden Attribute definieren einen Identifier für die Serie sowie eine Zeitangabe, wann das Update
durch das Plugin gesendet wurde.

Zusätzlich initialisiert das Plugin eine Update Routine, welche nach einer definierten Zeit ein Update für die
Werte der Serie sendet. Zum Beispiel:

.. comment .. code-block:: JSON
.. code::

    {
      "series": [
        [1460810141323, 711.25],
        [1460811024119, 711.25]
        ],
      "cmd": "series",
      "sid": "wohnung.verteilung.zaehler.wirkleistung|avg|48h|now"
    }


series_cancel
~~~~~~~~~~~~~

Mit dem ``series_cancel`` Befehl kann ein Client die Updates einer Serie, die er vorher aboniert hat, beenden.

.. comment .. code-block:: JSON
.. code::

  {
   "cmd":"series_cancel",
   "item":"wohnung.verteilung.zaehler.wirkleistung",
   "series":"avg",
   "start":"48h",
   "end":"now",
   "count":100
  }

Das Plugin antwortet mit:

.. comment .. code-block:: JSON
.. code::

  {
   "cmd":"series_cancel",
   "result": "..."
  }

oder

.. comment .. code-block:: JSON
.. code::

  {
   "cmd":"series_cancel",
   "error": "..."
  }


log
~~~

Mit dem ``log`` Befehl kann ein Client die letzten Einträge eines Logs anfordern. Das folgende Beispiel fordert
die letzten 5 Einträge des env.core Logs an:


.. comment .. code-block:: JSON
.. code::

  {"cmd":"log","name":"env.core.log","max":"5"}

Das Plugin antwortet mit einer einer Liste von Messages, die folgendermaßen aussehen kann:

.. comment .. code-block:: JSON
.. code::

  {
   "init":"y",
   "cmd":"log",
   "name":"env.core.log",
   "log":[
      {"message":"VISU: WebSocketHandler uses protocol version 4","level":"WARNING","thread":"Main","time":"2016-04-16T15:53:21.354815+02:00"},
      {"message":"Using sonos section [sonos_bo], sonos_uid = RINCON_B8E93792D35401400","level":"WARNING","thread":"myradio","time":"2016-04-16T15:52:28.980100+02:00"},
      {"message":"Mondaufgang um 15:26:50 bei Azimuth 76.9 und Monduntergang um 04:39:55 bei Azimuth 285.5","level":"WARNING","thread":"mysunmoon","time":"2016-04-16T15:52:27.678330+02:00"},
      {"message":"No broker url given, assuming current ip and default broker port: http://10.0.0.182:12900","level":"WARNING","thread":"Main","time":"2016-04-16T15:52:14.006478+02:00"},
      {"message":"mlgw: Serial number of ML Gateway is 22804066","level":"WARNING","thread":"Main","time":"2016-04-16T15:52:13.869275+02:00"}
   ]
  }


log_cancel
~~~~~~~~~~~~~

Mit dem ``log_cancel`` Befehl kann ein Client die Updates eines Logs, welches er vorher aboniert hat, beenden.
Dieser Befehl ist ab Protokoll Version 4.1 verfügbar.

.. comment .. code-block:: JSON
.. code::

  {
   "cmd":"log_cancel",
   "item":"env.core.log",
  }

Das Plugin antwortet mit:

.. comment .. code-block:: JSON
.. code::

  {
   "cmd":"log_cancel",
   "result": "..."
  }

oder

.. comment .. code-block:: JSON
.. code::

  {
   "cmd":"log_cancel",
   "error": "..."
  }


proto
~~~~~

Mit dem ``proto`` Befehl kann ein Client die Version des Websocket-Nutzdaten Protokolls angeben, mit der der CLient
kommunizieren möchte:

.. comment .. code-block:: JSON
.. code::

  {"cmd":"proto","ver":4}

Das Plugin antwortet mit der Protokoll Version, die es unterstützt. Zusätzlich sendet es die aktuelle Zeit
(mit Zeitzone) des SmartHomeNG Systems:

.. comment .. code-block:: JSON
.. code::

  {
   "cmd": "proto",
   "ver": 1.0,
   "time":"2023-04-14T21:23:20.248227+02:00"
  }

identity
~~~~~~~~

Mit dem ``identity`` Befehl kann ein Client Informationen über sich selbst an das Plugin senden. Der Befehl sollte
direkt nach dem Öffnen der Verbindung gesendet werden.

Das folgende Beispiel zeigt, was ein Admin GUI v0.8.1 Client, welcher in einem Chrome Browser läuft, senden würde:

.. code:: code-block:: JSON

  {
   "cmd": "identity",
   "sw": "shngAdmin",
   "ver": "v0.8.1",
   "browser": "Chrome",
   "bver": "113"
  }

Das Websocket Modul sendet keine Antwort zu dem ``identity`` Befehl.


