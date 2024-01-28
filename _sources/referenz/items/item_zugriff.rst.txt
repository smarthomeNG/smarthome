
.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup

.. _Zugriff_auf_Attributwerte:

Zugriff auf die Werte von Items
===============================

Das Lesen eines Itemwertes und das Zuweisen/Schreiben eines Item Wertes werden im folgenden beschrieben.

|

.. index:: Items; Wert lesen

Lesen einer Item Wertes
-----------------------

Der Syntax um den Wert eines Items in Logiken oder in eval-Ausdrücken zu lesen, ist folgender:

.. code-block:: python

    myvar = sh.<Pfad des Items>()

**Pfad des Items** beschreibt den vollständigen Pfad eines Items. Wenn ein Item vom Typ String folgendermaßen
konfiguriert ist:

.. code-block:: yaml

    Oma:
        Papa:
            Kind:
                type: str

ist für das Item ``Kind`` der Pfad ``Oma.Papa.Kind``. Auf den Wert kann folglich über ``sh.Oma.Papa.Kind()``
zugegriffen werden.

Wenn ein Item einen komplexen Datentyp (``type: list`` oder ``type: dict``) hat, ist außer dem Zugriff auf den gesamten
Item Wert (also die komplette Liste oder das komplette dict) auch der Zugriff auf einzelne Elemente dieser Item Werte
möglich.

|

Zugriff auf ein Listen-Element :redsup:`neu`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wenn ein Item als Liste konfiguriert ist, kann auf die einzelnen Elemente der Liste über ihre Position zugegriffen
werden, wobei 0 die erste Position kennzeichnet. Um z.B. auf das dritte Element einer Liste zuzugreifen, ist der
Syntax folgender:

.. code-block:: python

    myvar = sh.Oma.Papa.Kind(index=2)

Es ist auch möglich, auf die Liste vom Ende her zu zugreifen, wobei -1 das letze Element der Liste bezeichnet, -2
das vorletzte Element usw.

|

Zugriff auf ein Dict-Element :redsup:`neu`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wenn ein Item als Dict konfiguriert ist, kann auf die einzelnen Elemente des Dicts über ihren Key zugegriffen
werden. Um z.B. auf das Element mit dem Key **meinWert** eines Dicts zuzugreifen, ist der Syntax folgender:

.. code-block:: python

    myvar = sh.Oma.Papa.Kind(key='myKey')


|


.. index:: Items; Wert schreiben

Schreiben eines Item Wertes
---------------------------

Der Syntax um den Wert (value) eines Items in Logiken oder in eval-Ausdrücken zu setzen, ist folgender:

.. code-block:: python

    sh.<Pfad des Items>(<value>)

**Pfad des Items** beschreibt den vollständigen Pfad eines Items. Wenn ein Item vom Typ String folgendermaßen
konfiguriert ist:

.. code-block:: yaml

    Oma:
        Papa:
            Kind:
                type: str

ist für das Item ``Kind`` der Pfad ``Oma.Papa.Kind``. Den Wert kann folglich über ``sh.Oma.Papa.Kind(<value>)``
gesetzt werden.

|

Wenn ein Item einen komplexen Datentyp (``type: list`` oder ``type: dict``) hat, ist außer dem Setzen des gesamten
Item Wertes (also die komplette Liste oder das komplette dict) auch das Setzen einzelner Elemente dieser Item Werte
durch Angabe eines weiteren Parameters möglich. Wichtig ist, dass der zu setzende Wert der erste Parameter ist.
Alle weiteren (namentlich benannten) Parameter dürfen erst danach folgen.

|

Schreiben eines Listen-Elements :redsup:`neu`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wenn ein Item als Liste konfiguriert ist, kann auf die einzelnen Elemente der Liste über ihre Position zugegriffen
werden, wobei 0 die erste Position kennzeichnet. Um z.B. das dritte Element einer Liste zu setzen, ist
der Syntax folgender:

.. code-block:: python

    sh.Oma.Papa.Kind(<value>, index=2)

Es ist auch möglich, auf die Liste vom Ende her zu zugreifen, wobei -1 das letze Element der Liste bezeichnet, -2
das vorletzte Element usw.

Wenn eine Liste vergrößert werden soll, so gibt es die Möglichkeit das neue Item am Anfang oder am Ende der Liste
anzufügen.

Um einen Wert am Ende der Liste anzufügen, ist als **index** der String 'append' anzugeben.

.. code-block:: python

    sh.Oma.Papa.Kind(<value>, index='append')


Um einen Wert am Anfang der Liste einzufügen, ist als **index** der String 'prepend' anzugeben.

.. code-block:: python

    sh.Oma.Papa.Kind(<value>, index='prepend')


|

Schreiben eines Dict-Elements :redsup:`neu`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wenn ein Item als Dict konfiguriert ist, kann auf die einzelnen Elemente des Dicts über ihren Key zugegriffen
werden. Um z.B. auf das Element mit dem Key **myKey** eines Dicts zu setzen, ist der Syntax folgender:

.. code-block:: python

    sh.Oma.Papa.Kind(<value>, key='myKey')


Falls der Key im dict noch nicht existiert, wird ein neuer Eintrag hinzugefügt.

|

Weitere Parameter Item Zugriff
------------------------------

Außer den oben beschriebenen Parametern (``value``, ``index`` und ``key``), gibt es noch weitere Parameter.

Der ineressanteste unter ihnen ist der Parameter ``caller``. Mit ihm wird beeinflusst, was bei einer Zuweisung zu
einem Item als **Update durch** und **Änderung durch** zum Beispiel in der Admin GUI zu einem Item angezeigt wird.

.. code-block:: python

    sh.Oma.Papa.Kind(<value>, caller='Meine eigene Logik')

Damit wird der standardmäßige Eintrag von **Update durch** und **Änderung durch** durch den gewählten Eintrag
ersetzt.

Ein weiterer Parameter ist ``source``. Dieser wird im allgemeinen in Gateway Plugins genutzt, um zu kennzeichnen
von welchem externen Device ein Itemwert verändert wurde.

Plugins setzen einen Item Wert normalerweise so:

.. code-block:: python

    sh.Oma.Papa.Kind(<value>, caller=<Plugin Name>)

Damit wird der Plugin Name in der Admin GUI in den Feldern **Update durch** und **Änderung durch** angezeigt.

Bei einem Gateway Plugin, bei dem das Plugin mehrere externe Geräte unterstützt, wird der Wert des Items folgendermaßen
gesetzt:

.. code-block:: python

    sh.Oma.Papa.Kind(<value>, caller=<Plugin Name>, source=<Device ID>)

Dadurch wird in der Admin GUI in den Feldern **Update durch** und **Änderung durch** <Plugin Name>:<Device ID>
angezeigt.

|

