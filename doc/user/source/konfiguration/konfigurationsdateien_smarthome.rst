
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

.. code-block:: yaml
   :caption: smarthome.yaml

   # /usr/local/smarthome/etc/smarthome.yaml
   lat: 51.1633                 # latitude
   lon: 10.4476                 # longitude
   elev: 500                    # elevation
   tz: Europe/Berlin            # timezone, the example will be fine for most parts of central Europe
   default_language: de         # default language for use with the backend plugin and multi-language entries in metadata
   assign_compatibility: latest # Assign Kompatibilität für timer und autotimer (compat_1.2 oder latest)



Die Koordinaten können mit Hilfe von GPS eines Mobiltelefons oder über eine entsprechende
(z.B. http://www.mapcoordinates.net/) bestimmt werden.


.. note::

    Die Konfigurationsparameter die in dieser Datei konfiguriert werden, können auch über das graphische Administrations-
    Interface geändert werden.

