
.. role:: redsup
.. role:: bluesup

===========================
*log_change* und *log_text*
===========================


.. index:: Standard-Attribute; log_change
.. index:: log_change

Attribut *log_change*
=====================

Ab SmartHomeNG v1.5 ermöglicht das Attribut **log_change** das Loggen jeder Veränderung des Item-Wertes. **log_change**
muss dazu den Namen des zu verwendeten Loggers enthalten. In **../etc/logging.yaml** muss der Logger als
**items.<Name>** konfiguriert sein. Wertänderungen des Items werden dann mit dem Level **INFO** geloggt.

Ab **SmartHomeNG v1.9** kann das Item Logging über die Attribute **log_level** und **log_text** an die eigenen
Bedürfnisse angepasst werden.


Attribut *log_level*
====================

Das Attribut **log_level** ermöglicht es einen anderen Loglevel für den durch **log_change** ausgelösten Log-Eintrag
festzulegen. Der angegebene Loglevel kann jeder in SmartHomeNG unterstützte Python Loglevel sein (DEBUG, INFO, WARNING,
ERROR, CRITICAL). Die Angabe kann durch den Namen oder den Integer Wert des Loglevels erfolgen.

**Beispiel:** ``log_level: WARNING``

eval-Ausduck in log_level
--------------------------

Ab **SmarthomeNG v1.10.1** ist es möglich, das Loglevel variabel mittels Eval-Ausdruck festzulegen. Es wird dadurch
vor dem Schreiben eines jeden Logging-Eintrags neu evaluiert.

**Beispiel:** ``log_level: '{10 if value == 5 else "WARNING" if value == 1 else "INFO"}'``


Attribut *log_text*
===================

Das Attribut **log_text** ermöglicht es, einen eigenen Text für den Logeintrag festzulegen.
Wird das Attribut nicht angegeben, wird versucht, das im smarthome.yaml hinterlegte Attribut ``default_logtext``
heranzuziehen. Dieses kann die unten angegebenen Variablen enthalten. Ist auch dieses
Attribut nicht angegeben, wird folgende Muster herangezogen:
``Item Change: {id} = {value}  -  caller: {caller}{source}{destination}``

Wird **log_text** angegeben, kann dabei eine Reihe von Variablen und eval-Ausdrücken genutzt werden.


.. attention::

    **Achtung:** log_text darf keine Single-Quotes (``'``) enthalten!

    Falls es aufgrund des YAML Syntaxes notwendig kann der gesamte String für log_text in Single-Quotes (')
    eingeschlossen werden.

    **Beispiel:** ``log_text: 'Alter={age}'``



Variablen in log_text
---------------------

Um den Log Text dynamisch gestalten zu können, können variable Werte in den Text String eingeschlossen werden.

Die Variablen müssen in geschweifte Klammern eingeschlossen werden.

**Beispiel:** ``log_text: Das Alter des Item-Wertes ist {age} Sekunden``

Unterstützt werden folgende Variablen/Platzhalter:

+-----------------+------------------------------------------------------------------------------+
| **Variable**    | **Beschreibung**                                                             |
+=================+==============================================================================+
|  {value}        |  Aktueller Wert des Items                                                    |
+-----------------+------------------------------------------------------------------------------+
|  {caller}       |  Aufrufendes Objekt, welches das Item verändert                              |
+-----------------+------------------------------------------------------------------------------+
|  {source}       |  Quelle des Item Werts (oder None)                                           |
+-----------------+------------------------------------------------------------------------------+
|  {dest}         |  Ziel des Wertes (oder None)                                                 |
+-----------------+------------------------------------------------------------------------------+
|  {name}         |  Name des Items                                                              |
+-----------------+------------------------------------------------------------------------------+
|  {age}          |  Alter des aktuellen Item-Wertes                                             |
+-----------------+------------------------------------------------------------------------------+
|  {mvalue}       |  Über ``log_mapping`` zugewiesener Wert für den eigentlichen Item Wert       |
+-----------------+------------------------------------------------------------------------------+
|  {lvalue}       |  Letzter Wert des Items                                                      |
+-----------------+------------------------------------------------------------------------------+
|  {mlvalue}      |  Über ``log_mapping`` zugewiesener Wert für den letzten Item Wert            |
+-----------------+------------------------------------------------------------------------------+
|  {pname}        |  Name des Parent-Items                                                       |
+-----------------+------------------------------------------------------------------------------+
|  {id}           |  ID (Pfad) des Items                                                         |
+-----------------+------------------------------------------------------------------------------+
|  {pid}          |  ID (Pfad) des Parent-Items                                                  |
+-----------------+------------------------------------------------------------------------------+
|  {lowlimit}     |  unterer Grenzwert für Logeinträge aus dem ``log_rules`` Attribut            |
+-----------------+------------------------------------------------------------------------------+
|  {highlimit}    |  oberer Grenzwert für Logeinträge aus dem ``log_rules`` Attribut             |
+-----------------+------------------------------------------------------------------------------+
|  {stamp}        |  aktueller UNIX Zeitstempel                                                  |
+-----------------+------------------------------------------------------------------------------+
|  {time}         |  aktuelle Uhrzeit im Format HH:MM:SS                                         |
+-----------------+------------------------------------------------------------------------------+
|  {date}         |  aktuelles Datum im Format DD.MM.YYYY                                        |
+-----------------+------------------------------------------------------------------------------+
|  {now}          |  aktuelle Zeit im Format von sh.now (YYYY-MM-DD HH:MM:SS.ss+TZ)              |
+-----------------+------------------------------------------------------------------------------+
|  {itemvalue}    |  der Wert eines Items (z.B, ein Text) aus dem ``log_rules`` Attribut         |
+-----------------+------------------------------------------------------------------------------+
|  {filter}       |  der aktuell aktive (positive) Filter                                        |
+-----------------+------------------------------------------------------------------------------+
|  {exclude}      |  der aktuell aktive negative Filter                                          |
+-----------------+------------------------------------------------------------------------------+

eval-Ausdrücke in log_text
--------------------------

Zusätzlich zu den Variaben, können in den Log Text auch eval Ausdrücke eingeschlossen werden. Diese sind in
geschwungene Klammern zu setzen.

Es können auch mehrere eval-Ausdrücke in einen Log Text eingebunden und mit Variablen konfiguriert werden.

**Beispiel:** ``log_text: Ergebnis={1+value} für item {id}``
**Beispiel:** ``log_text: Ergebnis={"Eins" if value == 1 else "Zwei" if value == 2 else 1+value} für item {id}``


Attribut *log_mapping*
======================

Über das **log_mapping** Attribut kann festgelegt werden, auf welche Werte/Strings der Wert eines Items für das
Logging gemappt werden soll. Das Attribut **log_mapping** enthält dazu in einem String die Beschreibung eines
dicts. Wobei der Key den zu übersetzenden/mappenden Wert angibt und der dazu gehörige Value des dicts den String
angibt, der über die Variable ``{mvalue}`` ausgegeben wird.

**Beispiel:**

.. code-block:: yaml

    log_mapping: "{
        '1': 'Eins',
        '2': 'Zwei',
        '3': 'Drei'
        }"


Attribut *log_rules*
====================

Über das **log_rules** Attribut kann festgelegt werden, welche zusätzliche Regeln für das Erzeugen des Log-Eintrages
anzuwenden sind. Das Attribut **log_rules** enthält dazu in einem String die Beschreibung eines dicts.

**Beispiel:**

.. code-block:: yaml

    item:
        type: num
        log_rules: "{
            'lowlimit' : -1.0,
            'highlimit': 10.0,
            'filter': [1, 2, 5],
            'exclude': '.exclude_values',
            'itemvalue': '.text'
            }"

        exclude_values:
            type: list
            initial_value: [2, 10]
            cache: True

        text:
            type: str
            initial_value: 'This is the log message'
            cache: True

Die Filter Liste hat dabei Vorrang. Es wird also nur bei den Werten 1, 2 und 5 geloggt, obwohl lowlimit und
highlimit weitere Werte zulassen würden bzw. exclude einen der Werte ausschließen würde.

.. hint::

    Sämtliche Werte in den log_rules können ab SmartHomeNG 1.10 auch in Items hinterlegt werden.
    Der Verweis auf das jeweilige Item erfolgt dabei durch den absoluten oder relativen Itempfad als String (ohne sh.).

lowlimit
--------

Ein Wert, der angibt, unterhalb welchen Wertes des Items **kein** Logeintrag geschrieben werden soll.
Werte werden geschrieben, Wenn **lowlimit** <= **value** ist.

**low_limit** kann nur auf Items vom Typ **num** angewendet werden.


highlimit
---------

Ein Wert, der angibt, oberhalb welchen Wertes des Items **kein** Logeintrag geschrieben werden soll.
Werte werden geschrieben, Wenn **value** < **highlimit** ist.

**highlimit** kann nur auf Items vom Typ **num** angewendet werden.


filter
------

Eine Werteliste, die angibt, bei welchen Werten des Items ein Logeintrag geschrieben werden soll.

Wenn das Item vom Typ **num** ist, muss die Liste auch numerische Werte (int oder float) enthalten
(``'filter': [1, 2, 5, 2.1]``). Falls das Item von einem anderen Datentyp ist, muss die Liste Strings
enthalten (``'filter': ['1', '2', '5']``).


exclude
-------

Eine Werteliste, die angibt, bei welchen Werten des Items ein Logeintrag nicht geschrieben werden soll.

Wenn das Item vom Typ **num** ist, muss die Liste auch numerische Werte (int oder float) enthalten
(``'exclude': [1, 2, 5, 2.1]``). Falls das Item von einem anderen Datentyp ist, muss die Liste Strings
enthalten (``'exclude': ['1', '2', '5']``).


itemvalue
---------

Der absolute oder relative Pfad zu einem Item, dessen Wert ausgelesen werden soll.
Dies kann beispielsweise dazu genutzt werden, die Lognachricht zur Laufzeit anzupassen.
