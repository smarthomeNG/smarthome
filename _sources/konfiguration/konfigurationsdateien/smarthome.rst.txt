
.. _`smarthome.yaml`:

smarthome.yaml
==============

Um Werte wie *sunrise*, *sunset*, *azimuth* und *elevation* der Sonne oder des Mondes für den
Ort der SmartHomeNG Installation berechnen zu können, sind die geographischen Koordinaten
der SmartHomeNG Installation notwendig. Diese werden zusammen mit einigen globalen SmartHomeNG
Konfigurationen in smarthome.yaml konfiguriert.

Erzeuge eine neue Datei **smarthome.yaml** im Verzeichnis ***../etc*** oder kopiere die vorhandene
Datei **smarthome.yaml.default** zu **smarthome.yaml** und passe sie nach Deinen Erfordernissen
an.

.. hint::

    Falls beim Start von SmartHomeNG keine Datei **smarthome.yaml** existiert, wird die Datei
    **smarthome.yaml.default** automatisch kopiert.

Die Datei sollte folgendermaßen aussehen:

.. literalinclude:: ../../../../../etc/smarthome.yaml.default
   :caption: smarthome.yaml
   :language: yaml



Die Koordinaten können mit Hilfe von GPS eines Mobiltelefons oder über eine entsprechende
(z.B. http://www.mapcoordinates.net/) bestimmt werden.


.. note::

    Die Konfigurationsparameter die in dieser Datei konfiguriert werden, können auch über das graphische Administrations-
    Interface geändert werden.

