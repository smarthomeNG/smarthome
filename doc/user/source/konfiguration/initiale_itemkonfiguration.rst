Initiale Item-Konfiguration
===========================

Beispiele für erstmaliges Setup
-------------------------------

Das Rückgrat von SmartHomeNG bilden die Items. Jedes Item kann (muss
aber nicht) bestimmte Eigenschaften haben. Eigenschaften (Attribute)
sind z.B. welchen Datentyp ein Item repräsentiert oder wie das Item gelesen oder
geschrieben werden kann. Wie welches Item gelesen und geschrieben werden
kann, hängt von den installierten Plugins ab.

Ein kleines Beispiel: Eine Lampe soll über KNX ein- und
ausgeschaltet werden. Dazu braucht es zwei Schritte:

1)  Das **KNX Plugin** muß installiert und aktiviert werden.
    Das geschieht in der Datei ``./etc/plugins.yaml``.
    Typischerweise sieht der entsprechende Eintrag dann so aus:

    .. code-block:: yaml

       knx:
          class_name: KNX
          class_path: plugins.knx
          host: 127.0.0.1

2)  Die Lampe muß nun als **Item** im SmartHomeNG angelegt werden.
    Dazu wird eine Datei mit beliebigem Namen im Verzeichnis ``./items``
    mit der Endung ``.yaml`` angelegt. z.B. die Datei ``./items/Lampen.yaml``.
    In dieser Datei wird das Item angelegt indem den Name des Items gefolgt von
    einem Doppelpunkt notiert wird. Der Inhalt der Datei wäre also:

    .. code-block:: yaml

       Lampe:

    Die Lampe soll an- und ausgeschaltet werden können und daher muß mit dem
    Schlüsselwort **type** der Datentyp **bool** zugewiesen werden.
    Zudem muß das Schlüsselwort um einige Zeichen eingerückt werden um dem
    yaml Parser von SmartHomeNG zu zeigen, das nun eine neue Ebene erfolgt.
    Somit ergibt sich:

    .. code-block:: yaml

       Lampe:
           type: bool

    Nun muß dem KNX Plugin über das Schlüsselwort **knx_listen** signalisiert
    werden das Änderungen vom Bus an das Item weitergeleitet werden sollen und
    weiterhin über das Schlüsselwort **knx_send** das alle Änderungen am Wert
    des Items die nicht vom KNX Plugin initiiert werden dann auf den Bus gesendet
    werden sollen. Zudem wird dem KNX Plugin noch der Datentyp vorgegeben,
    mit dem die Daten vom KNX Bus codiert bzw. decodiert werden sollen.
    Das Schlüsselwort hierzu ist **knx_dpt**

    .. code-block:: yaml

       Lampe:
           type: bool
           knx_dpt: 1
           knx_listen: 1/1/133
           knx_send: 1/1/130

    Sollte die fiktive Lampe auch über einen Dimmer angesteuert werden können,
    muß ein weiteres Item angelegt werden, da der Dimmwert ja nicht ein oder aus ist
    sondern einen Zahlenwert für die Dimmeinstellung vorsieht.
    Dazu benötigt man ein weiteres Item. Hierbei wird das Schlüsselwort **type** auf
    **num** gesetzt und der KNX Datentyp passend dazu **knx_dpt: 5**

    .. code-block:: yaml

       LampeDimmen:
           type: num
           knx_dpt: 5
           knx_listen: 1/1/134
           knx_send: 1/1/132

    Um sich viel Tipparbeit zu ersparen und die Struktur übersichtlich zu gestalten
    können Items hierarchisch angeordnet werden.
    Für das Beispiel mit der Lampe gibt es nun ein Hauptitem **Lampe** und darunter
    zwei Kinditems **schalten** und **dimmen** mit den oben eingeführten Schlüsselwörtern:

    .. code-block:: yaml

       Lampe:
           schalten:
               type: bool
               knx_dpt: 1
               knx_listen: 1/1/133
               knx_send: 1/1/130
           dimmen:
               type: num
               knx_dpt: 5
               knx_listen: 1/1/134
               knx_send: 1/1/132

Um den Überblick zu behalten empfiehlt sich folgendes Schema für die Erstellung
von Item Dateien:

.. code-block:: yaml

   Stockwerk:
       Raum:
           Gewerk:
               Ort:
                   Eigenschaft:

Beispiel:

.. code-block:: yaml

   EG:
       Bad:
           Licht:
               Decke:
                   schalten:
                       type: bool
                       knx_dpt: 1
                       knx_listen: 1/1/133
                       knx_send: 1/1/130
                   dimmen:
                       type: num
                       knx_dpt: 5
                       knx_listen: 1/1/134
                       knx_send: 1/1/132

Ein solches Schema hat den Vorteil, dass man mit
``*.*.Licht.*.schalten`` auf alle Lampen im Haus zugreifen kann,
beispielsweise um eine Logik auszulösen.

Möchte man nun das Beispiel erweitern um z.B. mit der SmartVISU die Lampe zu schalten,
muß man zunächst das Plugin **visu_websocket** in der ``./etc/plugin.yaml``
durch folgenden Eintrag aktivieren:

.. code-block:: yaml

   visu:
       class_name: WebSocket
       class_path: plugins.visu_websocket


Bei den Items ist das Schlüsselwort **visu_acl** zu ergänzen mit der Berechtigungsebene für den Websocket.
Im Falle der Lampe wäre das **rw** für einen Read/Write also Lese und Schreibzugriff auf
das Item durch das visu_websocket Plugin.

.. code-block:: yaml

   Lampe:
       schalten:
           type: bool
           knx_dpt: 1
           knx_listen: 1/1/133
           knx_send: 1/1/130
           visu_acl: rw
       dimmen:
           type: num
           knx_dpt: 5
           knx_listen: 1/1/134
           knx_send: 1/1/132
           visu_acl: rw


Um ein Item auf weitere Plugins reagieren zu lassen muß nun ebenfalls das gewünschte
Plugin aktiviert werden. Wie das funktioniert und welche Schlüsselworte das Plugin kennt
steht in der zugehörigen Readme Datei des Plugins.

Um also z.B. das Dash-Button Plugin zu nutzen muß dieses nur aktiviert werden und
das Item einfach noch um das Dash-Button Attribut erweitert werden:

.. code-block:: yaml

   Lampe:
       schalten:
           type: bool
           knx_dpt: 1
           knx_listen: 1/1/133
           knx_send: 1/1/130
           visu_acl: rw
           dashbutton_mac:  'AC:63:B0:02:CA:12'
           dashbutton_mode: 'flip'

D.h. man kann die Lampe nun via KNX, SmartVisu oder Dashbutton ein- und
ausschalten.

Wie man grundsätzlich die verschiedenen Plugins in der
``./etc/plugin.yaml`` konfiguriert, steht im Abschnitt **Konfiguration/Plugins**
der Doku. Auch wie die Attribute in den Items
gesetzt werden müssen, ist für jedes Plugin in der Doku der **Plugins**
zu finden.
