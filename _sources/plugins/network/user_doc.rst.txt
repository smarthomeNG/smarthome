
.. index:: Plugins; network

=======
network
=======

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left


Konfiguration
-------------

Im folgenden ist die alte Dokumentation zu lesen. Die aktuelle Dokumentation zur Konfiguration ist
unter :doc:`/plugins_doc/config/influxdb2` nachzulesen.


.. _pluginyaml:

plugin.yaml
~~~~~~~~~~~

.. code:: yaml

   nw:
       class_name: Network
       class_path: plugins.network
       # ip: 0.0.0.0
       # port: 2727
       tcp: yes
       tcp_acl:
         - 127.0.0.1
         - 192.168.0.34
       # udp: no
       # udp_acl: '*'
       http: 12345

Attribute
~~~~~~~~~

-  ``ip``: gibt eine hörende IP Addresse an. Standardmäßig werden Daten von allen IP Adressen akzeptiert.

-  ``port``: gibt den hörenden Port für generisch eintreffende TCP und
   UDP Verbindungen an. Der Standard ist Port 2727.

:Note: Es ist zu beachten, dass Portangaben unter Linux größer als 1024 sein müssen, damit sie ohne root-Zugriff genutzt werden können. Ports unter 1025 sind *reservierte Ports* und damit dem System vorbehalten.

-  ``tcp``: Das Plugin akzeptiert grundsätzlich keine TCP Verbindungen.
   Erst wenn dieses Attribut auf 'yes' gesetzt wird, werden TCP Verbindungen akzeptiert.

-  ``tcp_acl``: Wenn das Attribut ``tcp`` gesetzt ist, werden grundsätzlich alle Verbindungenanfragen
   mit TCP Protokoll akzeptiert. Dieses Attribut kann genutzt werden um durch Angabe
   einer oder mehrerer IP Adressen den Zugriff einzuschränken.

-  ``udp``: Das Plugin akzeptiert grundsätzlich keine UDP Verbindungen.
   Erst wenn dieses Attribut auf 'yes' gesetzt wird, werden UDP Verbindungen akzeptiert.

-  ``udp_acl``: Wenn das Attribut ``udp`` gesetzt ist, werden grundsätzlich alle Verbindungenanfragen
   mit UDP Protokoll akzeptiert. Dieses Attribut kann genutzt werden um durch Angabe
   einer oder mehrerer IP Adressen den Zugriff einzuschränken.

-  ``http``: Port auf dem Anfragen für HTTP GET akzeptiert werden

-  ``http_acl``: Das Plugin akzeptiert grundsätzlich alle HTTP GET Verbindungen.
   Dieses Attribut kann genutzt werden um durch Angabe
   einer oder mehrerer IP Adressen den Zugriff einzuschränken.

.. _itemsyaml:

items.yaml
~~~~~~~~~~

nw
^^

Wenn dieses Attribut auf 'yes' gesetzt ist, kann dieses Item mit Datenpaketen via
TCP und/oder UDP gesetzt werden.

.. code:: yaml

   test:

       item1:
           type: str
           nw: 'yes'

nw_acl
^^^^^^

Genau wie die Attribute tcp_acl/udp_acl kann mit diesem Attribut
eine oder mehrere IP festgelegt werden, die Verbindungen akzeptieren.
Das Atribut gilt sowohl für UDP als auch für TCP Verbindungen.
Ein vorhandenes ``tcp_acl`` oder ``udp_acl`` Attribut wird in der Wirkung übersteuert.

nw_udp_listen/nw_tcp_listen/nw_http_listen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mit den Atributen ``nw_udp_listen``, ``nw_tcp_listen`` und ``nw_http_listen``
für ein Item kann eine spezielle Verbindungskombination festgelegt werden.
Ein http listener quittiert wie ein herkoemmlicher HTTP Server eingehende POST und GET Anfragen.
Das Argument kann ein Port sein oder die Kombination von IP und Port.

.. code:: yaml

   test:

       item1:
           type: str
           # bind to 0.0.0.0:7777 (jede IP Addresse)
           nw_tcp_listen: 7777

       item2:
           type: str
           # bind to 0.0.0.0:7777 and 127.0.0.1:8888
           nw_udp_listen: 127.0.0.1:8888

       item3:
           type: str
           # bind to 192.168.1.1:7778
           nw_http_listen: 192.168.1.1:7778


Wenn ein TCP/UDP Paket an den Port gesendet wird, wird das Item auf den Wert des
entsprechenden Datenpaketinhalts gesetzt.
``$ echo teststring | nc -u 127.0.0.1 8888``
würde den Wert von ``item2`` auf ``teststring`` setzen.

nw_udp_send
^^^^^^^^^^^

Dieses Attribut erlaubt es einen Port und eine IP Adresse festzulegen, an die ein
Datenpaket mit dem Wert des Items per UDP geschickt wird.
Wird zusätzlich zu Port und IP noch ein ``=Benutzerdatenstring`` angehängt,
so wird anstelle des Itemwertes hier **Benutzerdatenstring** gesendet.
Wenn in diesem zusätzlichen ``=Benutzerdatenstring`` das Wort itemvalue vorkommt,
so wird für das Wort itemvalue der Wert des Items ersetzt.

.. code:: yaml

   test:

       item1:
           type: str
           # sendet per UDP Paket ein Datenpaket mit dem Wert des Items
           nw_udp_send: 11.11.11.11:7777

       item2:
           type: str
           ## sendet per UDP ein Datenpaket mit 'Benutzerdatenstring' als Inhalt
           nw_udp_send: "11.11.11.11:7777=Benutzerdatenstring"

       item3:
           type: str
           ## sendet per UDP ein Datenpaket mit 'Kommando: <hier der Wert von sh.test.item3>' als Inhalt
           nw_udp_send: "11.11.11.11:7777=Kommando: itemvalue"

.. _logicyaml:

logic.yaml
~~~~~~~~~~

Die gleichen Attribute für die Items finden auch Anwendung um Logiken zu triggern

Im Kontext einer Logik hat das dictionary *trigger* folgenden Einträge:

-  trigger['by'] Protokoll (tcp, udp, http)

-  trigger['source'] IP Adresse des Absenders

-  trigger['value'] Datenpaket


Benutzung
---------

Es wird folgendes generisches Paketformat erwartet: ``key|id|value``
Aktuell werden drei Schlüsselworte unterstützt:

-  ``item|item.path|value``
-  ``logic|logic_name|value``
-  ``log|loglevel|message`` # loglevel kann ``info``, ``warning`` oder ``error`` sein

.. code:: bash

   # sendet ein Datenpaket per UDP um das Item 'network.incoming' auf '123' zu setzen
   $ echo "item|network.incoming|123" | nc -uw 1 XX.XX.XX.XX 2727`

   # sendet ein Datenpaket per TCP um die Logik 'sage' mit 'Hallo Welt!' zu triggern
   $ echo "logic|sage|Hallo Welt!" | nc -w 1 XX.XX.XX.XX 2727`

   # sendet ein Datenpaket per UDP um einen Loggingeintrag mit dem Loglevel 'warning'
   # und der Meldung 'Internet Verbindung verloren' zu erstellen
   $ echo "log|warning|Internet Verbindung verloren" | nc -uw 1 XX.XX.XX.XX 2727`

   # http Anfrage um das Item  'network.incoming' auf '123' zu setzen
   $ wget "http://XX.XX.XX.XX:8090/item|network.incoming|123"

Funktionen
----------

udp(host, port, data)
~~~~~~~~~~~~~~~~~~~~~

Um per UDP Protokoll ein Datenpaket mit dem Inhalt ``Einschalten!``
an die IP ``192.168.0.5`` und Port ``9999`` zu senden, kann man folgende Anweisung nutzen:

``sh.nw.udp('192.168.0.5', 9999, 'Einschalten!')``
