:tocdepth: 5

.. index:: Logging; Logging in Logiken
.. index:: Logiken; Logging in Logiken


==================
Logging in Logiken
==================

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
