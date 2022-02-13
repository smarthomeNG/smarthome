
.. index:: Logging; Logging in Logiken
.. index:: Logiken; Logging in Logiken

.. role:: bluesup
.. role:: redsup


==================
Logging in Logiken
==================

Logger Konfiguration
====================

Damit aus Logiken heraus geloggt werden kann, muss dafür in der Logging-Konfigurationsdatei ``etc/logging.yaml``
ein entsprechender Logger konfiguriert sein.

Es sollte auf jeden Fall ein Standardlogger für alle Logiken konfiguriert sein, damit Warnungen und Fehler geloggt
werden können. Dazu ist in der Standardkonfiguration von SmartHomeNG der notwendige Logger bereits folgendermaßen
konfiguriert:

.. code-block:: yaml
   :caption:  etc/logging.yaml

   logger:

       ...

       logics:
           handlers: [shng_details_file]
           level: WARNING

Wenn aus allen Logiken heraus auch INFOs und DEBUG Informationen geloggt werden sollen, kann hier der ``level``
entsprechend angepasst werden.

Ein besserer Weg ist es jedoch, für die jeweilige Logik aus der heraus weitere Informationen geloggt werden sollen,
einen eigenen Logger anzulegen. Dadurch kann das Logging für jede Logik unabhängig von den anderen Logiken festgelegt
werden. Dazu muss ein weiterer Logger angelegt werden, der den Namen der Logik enthält ``logics.<Logikname>``.
Dabei ist der Logikname **nicht** der Name der Python Skript Datei, sondern der Name des Abschnitts in der
Konfigurationsdatei ``etc/logics.yaml``.

Für eine Logik mit dem Namen ``example``, sieht das beispielsweise folgendermaßen aus:

.. code-block:: yaml
   :caption:  etc/logging.yaml

   logger:

       ...

       logics:
           handlers: [shng_details_file]
           level: WARNING

       logics.example:
           level: INFO

Als Handler wird dabei der bereits im Logger ``logics`` definierte Handler verwendet. Es können bei Bedarf im
Logger der einzelnen Logik zusätzliche handler angegeben werden. Dabei muss darauf geachtet werden, dass der im
Logger ``logics`` definierte Handler nicht erneut angegeben wird, sa sonst die Logausgaben doppelt erfolgen.



Logging im Code
===============

Nachdem das Logging für die Logik/Logiken wie oben beschrieben konfiguriert wurde, können aus dem Code der Logik
heraus folgendermaßen Logeinträge erstellt werden:

.. code-block:: python

    logger.error("Logtext der mit dem Level ERROR geloggt wird")

    logger.warning("Logtext der mit dem Level WARNING geloggt wird")

    logger.info("Logtext der mit dem Level INFO geloggt wird")

    logger.debug("Logtext der mit dem Level DEBUG geloggt wird")


Zusätzlich zu den Logeinträgen die in der Logik explizit erzeugt werden, wird vor Aufruf der Logik ein Logeintrag
erzeugt, der anzeigt, was die Ausführung der Logik getriggert hat. Dieser Logeintrag wird im Level DEBUG geschrieben.
Er erscheint in den Logdateien also nur, wenn der Loglevel für die entsprechende Logik auf DEBUG gesetzt ist.

