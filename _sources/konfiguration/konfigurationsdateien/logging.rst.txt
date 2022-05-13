
.. _`logging.yaml`:

logging.yaml
============

Der Core von SmartHomeNG und jedes Modul/Plugin ist in der Lage Logging Informationen auszugeben.
Das Logging kann so konfiguriert werden, das für Debugging viele Detailinformationen geloggt werden,
oder für den normalen Betrieb so, dass nur wichtige bzw. kritische Informationen geloggt werden.

Es existiert eine separate Seite, auf der erklärt wird wie das :doc:`Logging im einzelnen konfiguriert <../logging>`
werden kann. Zum Start reicht es die Einstellungen zu verwenden, wie si in der Datei ``logging.yaml.default``
vorgegeben sind. Einfach diese Datei zu ``logging.yaml`` kopieren und nach den eigenen Bedürfnissen
anpassen. Die Konfiguration sollte in etwa so aussehen:

.. literalinclude:: ../../../../../etc/logging.yaml.default
   :caption: logging.yaml
   :language: yaml

Weitere Details sind unter :doc:`logging <../logging>` zu finden.

