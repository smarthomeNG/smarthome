
.. index:: Referenz; Logging Formatter
.. Index:: Logging Formatter; Referenz

.. role:: bluesup
.. role:: redsup


=================
Logging Formatter
=================

Mit **Logging Formattern** wird festgelegt, wie die Informationen aufbereitet werden sollen, wenn sie in ein
Log geschrieben werden.

Der standardmäßig in SmartHomeNG verwendete Logger ist **shng_simple** und in der Konfigurationsdatei
``../etc/logging.yaml`` definiert. Dieser Logger sollte für das Warnings-Log (und möglichst auch für die weitern
Logs) verwendet werden. Er bietet einen guten Kompromiss zwischen Übersichtlichkeit/Lesbarkeit und Detailreichtum.
Die Ausgaben mit diesem Formatter helfen besonders bei Supportanfragen.

Der **shng_simple** Formatter gibt außer der Log Message die folgenden Attribute aus: Den Zeitpunkt, den Loglevel
und den Namen des Loggers. Er ist folgendermaßen definiert:

.. code-block:: yaml

    formatters:

        shng_simple:
            format: '%(asctime)s %(levelname)-8s %(name)-19s %(message)s'
            datefmt: '%Y-%m-%d  %H:%M:%S'

Wenn zusätzlich die Ausgabe der Zeitzone benötigt/gewünscht wird, kann das Datumsformat entsprechend angepasst
werden:

.. code-block:: yaml

    formatters:

        shng_simple:
            format: '%(asctime)s %(levelname)-8s %(name)-19s %(message)s'
            datefmt: '%Y-%m-%d  %H:%M:%S %Z'


Eine vollständige Liste der Attribute eines Log-Records kann in der Python Dokumentation unter
`logging - Logging facility for Python <https://docs.python.org/3/library/logging.html>`_ nachgelesen werden.

|

