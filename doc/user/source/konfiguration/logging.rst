:tocdepth: 2

.. index:: Logging

#######
Logging
#######

Ein `Log <https://de.wikipedia.org/wiki/Log>`_ zeichnet Ergebnisse von Vorgängen oder Berechnungen auf
und dient der Dokumentation. Anhand eines Logs kann man Programmfehlern auf die Spur kommen oder bestimmte
Situationen können im Nachhinein untersucht werden. Je detaillierter ein Log geführt wird, desto einfacher
ist die Untersuchung bestimmter Sachverhalte.
Je nachdem, was man untersuchen möchte, kann man mit einem **Logging Level** im Programm vorgeben wie ernst
oder wie wichtig ein bestimmter Logeintrag ist.
Innerhalb des Kerns von SmartHomeNG finden sich zum Beispiel Einträge im Programm mit dem Log Level **NOTICE**
die in einer Logdatei dann im Ergebnis so aufgezeichnet werden:

``2021-04-16  21:56:31 NOTICE   lib.smarthome     --------------------   Init SmartHomeNG 1.8.2c.4e0938c2.develop   --------------------``

Das ist als Information zu sehen um bei Problemen Hilfe zu erhalten. Es deutet hier nichts auf Fehler oder Probleme hin.
Ein anderer Logging Befehl im Core mit dem Log Level **WARNING** erzeugt hingehen folgendes:

``2021-04-16  21:56:32 WARNING  lib.module        Not loading module Mqtt from section 'mqtt': Module is disabled``

Das ist als Warnung gedacht um darauf hinzuweisen, das ein Module nicht geladen wird und in dieser Folge eventuell
weitere Fehler oder Probleme auftauchen könnten. Steigerungen von Warnungen sind Log Level **ERROR** oder **CRITICAL**.
Während ein **ERROR** also ein Fehler durchaus bedeuten kann das SmartHomeNG weiterarbeiten kann, bedeutet ein **CRITICAL**
also ein kritischer Fehler das das Programm beendet werden muss.
Fehlt ein für den Kern von SmartHomeNG benötigtes Modul, so stell das einen kritischen Fehler dar.

Die Log Level in der Übersicht, absteigend in der Bedeutung für den Programmablauf:

.. list-table:: Log Level
   :header-rows: 1

   * - Level
     - Numerischer Wert
     - Anmerkung
   * - 50
     - CRITICAL
     - kritisch, führt zumeist zum Programmabbruch
   * - 40
     - ERROR
     - Fehler im Programmablauf, Programm kann zumeist weiterlaufen, Funktionalität möglicherweise eingeschränkt
   * - 31
     - NOTICE
     - Ein Hinweis der zur grundlegenden Information dient und nicht als Warnung verstanden werden soll.
       Dieser Log Level ist spezifisch für SmartHomeNG und ist im Standard Logging von Python nicht vordefiniert.
   * - 30
     - WARNING
     - Warnung das etwas unerwartetes passiert ist aber trotzdem weitergearbeitet werden kann
   * - 20
     - INFO
     - Eine Ablaufinformation die nicht unbedingt wichtig ist
   * - DEBUG
     - 10
     - Informationen für die Fehlersuche die normalerweise nicht benötigt werden
   * - NOTSET
     - 0
     - Es wird kein Logeintrag erzeugt

Es können prinzipiell auch weitere eigene Log Level definiert werden die dann für besondere Situationen benutzt werden können.
Ein Beispiel wäre ein Log Level **VERBOSE** mit dem Wert **8** der für die Fehlersuche in einem bestimmten Bereich eines Plugins
Verwendung finden könnte.
Für SmartHomeNG ist derzeit nur **NOTICE** vordefiniert um informelle Logging Einträge zu erzeugen, die nicht als Warnung
verstanden werden sollen.

Konfiguration des Loggings
==========================

Auf der Seite `Python Logging <https://docs.python.org/3.6/library/logging.html#module-logging>`_
sind die Konfigurationsmöglichkeiten detailliert beschrieben.

SmartHomeNG lädt beim Start die Konfiguration des Logging aus der Datei **etc/logging.yaml**. Ist diese Datei nicht vorhanden,
so versucht SmartHomeNG die Datei **etc/logging.yaml.default** zu kopieren nach **etc/logging.yaml** und dann daraus
die Konfiguration des Loggings zu laden.

Wenn bei der Konfiguration des Loggings etwas schief geht, kann also jederzeit die Datei **etc/logging.yaml** gelöscht oder
besser umbenannt werden und wird dann beim nächsten Neustart durch den Inhalt der **etc/logging.yaml.default** frisch bereitgestellt.

Ein Beispiel für **etc/logging.yaml.default** im Folgenden:

.. literalinclude:: ../../../../etc/logging.yaml.default
   :caption: ../etc/logging.yaml
   :language: yaml


Kurzdoku der Einträge in der Konfigurationsdatei
------------------------------------------------

Die einzelnen Konfigurationseinträge haben die folgende Bedeutung:

+-----------------+----------------------------------------------------------------------------------------------------+
| **Abschnitte**  | **Bedeutung**                                                                                      |
+=================+====================================================================================================+
| **formatters:** | Definiert das Ausgabeformat der einzelnen Loggingeinträge. Mehrere unterschiedliche                |
|                 | **formatter** können dazu verwendet werden um unterschiedlich aussehende Logdateien                |
|                 | zu erzeugen. In der Konfigurationsdatei **etc/logging.yaml** sind die Formatter                    |
|                 | **`simple`** und **`detail`** vorkonfiguriert. Weitere Formatter können bei Bedarf                 |
|                 | hinzugefügt werden.                                                                                |
+-----------------+----------------------------------------------------------------------------------------------------+
| **handlers:**   | Handler definieren die Log-Behandlungsroutinen/Ausgabekanäle die verwendet werden.                 |
|                 | In Python gibt es bereits mehrere vorimplementierte und mächtige Handler-Typen die in der          |
|                 | `Python Doku <https://docs.python.org/3.4/library/logging.handlers.html#module-logging.handlers>`_ |
|                 | beschrieben sind. Als eigentliche Handler sind in der Konfigurationsdatei **etc/logging.yaml**     |
|                 | die Handler **`console`** und **`file`** vordefiniert. Wenn Log-Einträge z.B. in eine andere       |
|                 | Datei geschrieben werden sollen, muss ein weiterer Handler definiert werden.                       |
|                 | Sollen Filter angewendet werden, so sind diese im entsprechenden Handler durch                     |
|                 | filters: [`filtername1`, `filtername2`] anzugeben (siehe filters)                                  |
+-----------------+----------------------------------------------------------------------------------------------------+
| **filters:**    | Filter bestimmen durch Angabe des Loggernamen, -moduls und -eintrags, welche Zeilen aus dem Log    |
|                 | angezeigt bzw. versteckt werden sollen. Der Eintrag (z.B. loggerfilter) kann bei den Handlers      |
|                 | mittels **`filters: [<filtername>]`** referenziert werden. Wichtig ist, den Filternamen in eckige  |
|                 | Klammern zu setzen, auch wenn nur ein Filter zum Einsatz kommen soll.                              |
|                 | Jeder Filter kann durch bis zu drei Parameter definiert werden, wobei diese nach AND Logik         |
|                 | evaluiert werden:                                                                                  |
|                 | - name: Loggername (z.B. lib.item)                                                                 |
|                 | - module: Loggermodul, va. bei Plugins u.U. relevant (z.B. item)                                   |
|                 | - timestamp: Uhrzeit/Datum (z.B. "23:00")                                                          |
|                 | - msg: Der tatsächliche Logeintrag als RegEx, z.B. "Result = (.\*) \(for attribute 'eval'\)"       |
|                 | Durch die Angabe von invert: True werden NUR die passenden Messages geloggt und sonst nichts.      |
|                 | Ein Beispiel ist unter :doc:`Logging - Best Practices <logging_best_practices>` zu finden.         |
+-----------------+----------------------------------------------------------------------------------------------------+
| **loggers:**    | Hier werden die einzelnen Logger definiert und was mit diesen Einträgen passiert,                  |
|                 | welche Handler und formatter verwendet werden. Das Level konfiguriert dabei die                    |
|                 | Logtiefe für die einzelne Komponente. Bei den loggern ist es nun möglich einzelne                  |
|                 | Plugins oder Libs im Debug protokollieren zu lassen. Dazu sind in der Konfiguration                |
|                 | bereits einige Beispiele.                                                                          |
+-----------------+----------------------------------------------------------------------------------------------------+
| **root:**       | Hier ist die Konfiguration des root Loggers der für die ganze Anwendung gilt. Dieser               |
|                 | root Logger wird für alle Komponenten verwendet, auch die die nicht unter loggers: konfiguriert    |
|                 | sind. Da der root Logger ALLE Logeinträge empfängt sollte der level: unbedingt auf WARNING stehen. |
+-----------------+----------------------------------------------------------------------------------------------------+

Wenn man **Logger** definiert, welche die Log-Einträge über zusätzliche **Handler** ausgeben, ist
zu beachten, dass die Ausgabe zusätzlich IMMER durch den Standardhandler (**file:**) erfolgt. Dies
führt dazu, dass die Einträge sowohl in der Standard Log-Datei von SmartHomeNG, als auch in der
zusätzlich definierten Log Datei erscheinen, falls der Level des Log Eintrages INFO oder höher ist.

Wenn man möchte, dass im Standard Log nur WARNINGS und ERRORS erscheinen, muss ein zusätzlicher
Eintrag im Handler **file:** erfolgen. Der Eintrag `level: WARNING` führt dazu, dass über den
Handler **file:** nur Ausgaben für Fehler und Warnungen erfolgen. INFO und DEBUG Ausgaben erfolgen
dann nur noch über den zusätzlichen Handler.

|

Logging Handler und Filter
==========================

Zusätzlich zu den Logging Handlern, die im Standard Logging Modul von Python definiert, bringt
SmartHomeNG weitere Handler und Filter mit, die bei der Konfiguration in ../etc/logging.yaml verwendet werden
können.

Die Beschreibung dieser Handler und Filter ist im Referenz Abschnitt unter Logging zu finden:

.. toctree::

.. toctree::
   :maxdepth: 4
   :titlesonly:

   /referenz/logging/logging_handler
   /referenz/logging/logging_filter


Plugin und Logik Entwicklung
============================

Für die Entwickler von Plugins:

Früher musste in Plugins ein Logger in der Form

.. code-block:: python

   import logging
   self.logger = logging.getLogger(__name__)


in der `__init__` Methode instanziert werden. Das ist inzwischen nicht mehr notwendig. Die SmartPlugin
Klasse erzeugt den Logger inzwischen selbst. Ein **import logging** ist nicht mehr notwendig und die
Initialisierung des Loggers in der `__init__` Methode sollte auch weggelassen werden.

Für die Entwickler von Logiken:
Verwendet man zur Instanziierung einen eigenen Namen (nicht empfohlen), wie z.B.

.. code-block:: python

   self.logger = logging.getLogger('DWD')


muss in der config auch dieser Name verwendet werden. Ohne `plugin.` oder `logics.`


.. code-block:: yaml
   :caption: ../etc/logging.yaml

   loggers:
       DWD:
           level: DEBUG



Logging der Veränderung von Items
---------------------------------

Die Veränderung von Item Werten kann am einfachsten geloggt werden, indem bei dem Item das Attribut **log_change** gesetzt
wird und auf einen entsprechenden Item Logger verweist. Der Item Logger muss in der etc/logging.yaml mit Level INFO oder
DEBUG definiert sein.

.. code-block:: yaml
   :caption: items/items.yaml

    test:
        item:
            log_change: <Logger-Name>


und

.. code-block:: yaml
   :caption: etc/logging.yaml

    ...-

    logger:
        items_<Logger-Name>:
            level: INFO
            handlers: [shng_details_file]

    ...


Best Practices
==============

Wer eine brauchbare leicht konfigurierbare Logging Konfiguration oder Beispiele zum Nutzen
von RegEx Ausdrücken sucht, der wird hier :doc:`Logging - Best Practices <logging_best_practices>` fündig.


.. toctree::
   :maxdepth: 4
   :titlesonly:

   logging_best_practices.rst
