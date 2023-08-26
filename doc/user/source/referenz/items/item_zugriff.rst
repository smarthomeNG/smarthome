
Zugriff auf die Werte fon Items
===============================

Das Lesen eines Itemwertes und das Zuweisen/Schreiben eines Item Wertes werden im folgenden beschrieben.

|

Lesen einer Item Wertes
-----------------------

Der Syntax um den Wert eines Items in Logiken oder in eval-Ausdrücken zu lesen, ist folgender:

.. code-block:: python

    sh.<Pfad des Items>()

**Pfad des Items** beschreibt den vollständigen Pfad eines Items. Wenn ein Item vom Typ String folgendermaßen
konfiguriert ist:

.. code-block:: yaml

    Opa:
        Papa:
            Kind:
                type: str

ist für das Item ``Kind`` der Pfad ``Opa.Papa.Kind``. Auf den Wert kann folglich über ``sh.Opa.Papa.Kind()``
zugegriffen werden.

|

Wenn ein Item einen komplexen Datentyp (``type: list`` oder ``type: dict``) hat, ist außer dem Zugriff auf den gesamten
Item Wert (also die komplette Liste oder das komplette dict) auch der Zugriff auf einzelne Elemente dieser Item Werte
möglich.

|

Zugriff auf ein Listen-Element
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wenn ein Item als Liste konfiguriert ist, kann auf die einzelnen Elemente der Liste über ihre Position zugegriffen
werden, wobei 0 die erste Position kennzeichnet. Um z.B. auf das dritte Element einer Liste zuzugreifen, ist der
Syntax folgender:

.. code-block:: python

    sh.Opa.Papa.Kind(index=2)

Es ist auch möglich, auf die Liste vom Ende her zu zugreifen, wobei -1 das letze Element der Liste bezeichnet, -2
das vorletzte Element usw.

|

Zugriff auf ein Dict-Element
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

...

|

Schreiben eines Item Wertes
---------------------------

Der Syntax um den Wert eines Items in Logiken oder in eval-Ausdrücken zu setzen, ist folgender:

.. code-block:: python

    sh.<Pfad des Items>(<value>)

**Pfad des Items** beschreibt den vollständigen Pfad eines Items. Wenn ein Item vom Typ String folgendermaßen
konfiguriert ist:

.. code-block:: yaml

    Opa:
        Papa:
            Kind:
                type: str

ist für das Item ``Kind`` der Pfad ``Opa.Papa.Kind``. Auf den Wert kann folglich über ``sh.Opa.Papa.Kind(<value>)``
zugegriffen werden.

|

Wenn ein Item einen komplexen Datentyp (``type: list`` oder ``type: dict``) hat, ist außer dem Setzen des gesamten
Item Wertes (also die komplette Liste oder das komplette dict) auch das Setzen einzelner Elemente dieser Item Werte
möglich.

|

Zugriff auf ein Listen-Element
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wenn ein Item als Liste konfiguriert ist, kann auf die einzelnen Elemente der Liste über ihre Position zugegriffen
werden, wobei 0 die erste Position kennzeichnet. Um z.B. auf das dritte Element einer Liste zuzugreifen, ist
der Syntax folgender:

.. code-block:: python

    sh.Opa.Papa.Kind(<value>, index=2)

Es ist auch möglich, auf die Liste vom Ende her zu zugreifen, wobei -1 das letze Element der Liste bezeichnet, -2
das vorletzte Element usw.

|

Weitere Parameter Item Zugriff
------------------------------

Außer den oben beschriebenen Parametern (``value``, ``index`` und ``key``), gibt es noch weitere Parameter.

Der ineressanteste unter ihnen ist der Parameter ``caller``. Mit ihm wird beeinflusst, was bei einer Zuweisung zu
einem Item als **Update durch** und **Änderung durch** zum Beispiel in der Admin GUI zu einem Item angezeigt wird.

.. code-block:: python

    sh.Opa.Papa.Kind(<value>, caller='Meine eigene Logik')

Damit wird der standardmäßige Eintrag von **Update durch** und **Änderung durch** durch den gewählten Eintrag
ersetzt.

|

