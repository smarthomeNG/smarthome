
.. role:: redsup
.. role:: bluesup

=========================================
*log_change* und *log_text* :redsup:`Neu`
=========================================


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


Attribut *log_text*
===================

Das Attribut **log_text** ermöglicht es einen eigenen Text für den Logeintrag festzulegen. **log_text** kann dabei
eine Reihe von Variablen und eval-Ausdrücken enthalten.


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
|  {lowlimit}     |  unterer Grenzwert für Logeinträge                                           |
+-----------------+------------------------------------------------------------------------------+
|  {highlimit}    |  oberer Grenzwert für Logeinträge                                            |
+-----------------+------------------------------------------------------------------------------+


eval-Ausdrücke in log_text
--------------------------

Zusätzlich zu den Variaben, können in den Log Text auch eval Ausdrücke eingeschlossen werden. Der Syntax dazu ist
folgender: ``{eval(<Ausdruck>)}``. Dabei muss sicher gestellt sein, dass der Ausdruck ein String ist. Wenn man
zum Beispiel nur Zahlen addiert ``3+5``, muss dieser Ausdruck in **doppelte** Anführungszeichen (``"``) gesetzt werden:
``{eval("3+5")}``.

Es können auch mehrere eval-Ausdrücke in einen Log Text eingebunden und mit Variablen konfiguriert werden.

**Beispiel:** ``log_text: Ergebnis={eval("1+4")} für item {id}``


Attribut *log_mapping*
======================

Über das **log_mapping** Attribut kann festgelegt werden, auf welche Werte/Strings der Wert eines Items für das
Logging gemappt werden soll. Das Attribut **log_mapping** enthält dazu in einem String die Beschreibung eines
dicts. Wobei der Key den zu übersetzenden/mappenden Wert angibt und der dazu gehörige Value des dicts den String
angeibt, der über die Variable ``{mvalue}`` ausgegeben wird.

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

    log_rules: "{
        'lowlimit' : -1.0,
        'highlimit': 10.0,
        'filter': [1, 2, 5]
        }"

Die Filter Liste hat dabei vorrang. Es wird also nur bei den Werten 1, 2 und 5 geloggt, obwohl lowlimit und
highlimit weitere Werte zulassen würden.


lowlimit
--------

``lowlimit`` ein Wert der angibt, unterhalb welchen Wertes des Items **kein** Logeintrag geschrieben werden soll.
Werte werden geschrieben, Wenn **lowlimit** <= **value** ist.

**low_limit** kann nur auf Items vom Typ **num** angewendet werden.


highlimit
---------

``highlimit`` ein Wert der angibt, oberhalb welchen Wertes des Items **kein** Logeintrag geschrieben werden soll.
Werte werden geschrieben, Wenn **value** < **highlimit** ist.

**highlimit** kann nur auf Items vom Typ **num** angewendet werden.


filter
------

``filter`` eine Werteliste die angibt, bei welchen Werten des Items ein Logeintrag geschrieben werden soll.

Wenn das Item vom Typ **num** ist, muss die Liste auch numerische Werte (int oder float) enthalten
(``'filter': [1, 2, 5, 2.1]``). Falls das Item von einem anderen Datentyp ist, muss die Liste Strings
enthalten (``'filter': ['1', '2', '5']``).
