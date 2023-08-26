
Zugriff auf die Werte fon Items
===============================

...

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

ist für das Item `Kind` der Pfad `Opa.Papa.Kind`. Auf den Wert kann folglich über `sh.Opa.Papa.Kind()` zugegriffen
werden.

|

Wenn ein Item einen komplexen Datentyp (`type: list` oder `type: dict`) hat, ist außer dem Zugriff auf den gesamten
Item Wert (also die komplette Liste oder das komplette dict) auch der Zugriff auf einzelne Elemente dieser Item Werte
möglich.

Zugriff auf ein Listen-Element
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wenn ein Item als Liste konfiguriert ist:

.. code-block:: yaml

    Opa:
        Papa:
            Kind:
                type: list

kann auf die einzelnen Elemente der Liste über ihre Position zugegriffen werden, wobei 0 die erste Position
kennzeichnet. Um z.B. auf das dritte Element einer Liste zuzugreifen, ist der Syntax folgender:

.. code-block:: python

    sh.Opa.Papa.Kind(index=2)

Es ist auch möglich, auf die Liste vom Ende her zu zugreifen, wobei -1 das letze Element der Liste bezeichnet, -2
das vorlezte Element usw.

|

Zugriff auf ein Dict-Element
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

...

|

Schreiben eines Item Wertes
---------------------------

...

|
Der Syntax um den Wert eines Items in Logiken oder in eval-Ausdrücken zu setzen, ist folgender:

.. code-block:: python

    sh.<Pfad des Items>(<Wert>)

**Pfad des Items** beschreibt den vollständigen Pfad eines Items. Wenn ein Item vom Typ String folgendermaßen
konfiguriert ist:

.. code-block:: yaml

    Opa:
        Papa:
            Kind:
                type: str

ist für das Item `Kind` der Pfad `Opa.Papa.Kind`. Auf den Wert kann folglich über `sh.Opa.Papa.Kind(<Wert>)` zugegriffen
werden.

|

Wenn ein Item einen komplexen Datentyp (`type: list` oder `type: dict`) hat, ist außer dem Zugriff auf den gesamten
Item Wert (also die komplette Liste oder das komplette dict) auch der Zugriff auf einzelne Elemente dieser Item Werte
möglich.

Zugriff auf ein Listen-Element
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wenn ein Item als Liste konfiguriert ist:

.. code-block:: yaml

    Opa:
        Papa:
            Kind:
                type: list

kann auf die einzelnen Elemente der Liste über ihre Position zugegriffen werden, wobei 0 die erste Position
kennzeichnet. Um z.B. auf das dritte Element einer Liste zuzugreifen, ist der Syntax folgender:

.. code-block:: python

    sh.Opa.Papa.Kind(<Wert>, index=2)

Es ist auch möglich, auf die Liste vom Ende her zu zugreifen, wobei -1 das letze Element der Liste bezeichnet, -2
das vorlezte Element usw.

|

Weitere Parameter beim Zugriff auf Item Werte
---------------------------------------------

...

|

