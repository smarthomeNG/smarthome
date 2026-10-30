
.. _`smarthome.yaml`:

smarthome.yaml
==============

Um Werte wie *sunrise*, *sunset*, *azimuth* und *elevation* der Sonne oder des Mondes für den
Ort der SmartHomeNG Installation berechnen zu können, sind die geographischen Koordinaten
der SmartHomeNG Installation notwendig. Diese werden zusammen mit einigen globalen SmartHomeNG
Konfigurationen in smarthome.yaml konfiguriert.

Erzeuge eine neue Datei ``smarthome.yaml`` im Verzeichnis *``etc``* oder kopiere die vorhandene
Datei ``smarthome.yaml.default`` zu ``smarthome.yaml`` und passe sie nach Deinen Erfordernissen
an.

.. hint::

    Falls beim Start von SmartHomeNG keine Datei ``smarthome.yaml`` existiert, wird die Datei
    ``smarthome.yaml.default`` aus dem ``templates``-Ordner automatisch kopiert.

Die Datei sollte folgendermaßen aussehen:

.. literalinclude:: ../../../../../templates/smarthome.yaml.default
   :caption: smarthome.yaml
   :language: yaml



Die Koordinaten können mit Hilfe von GPS eines Mobiltelefons oder über eine entsprechende
(z.B. http://www.mapcoordinates.net/) bestimmt werden.

Parameter
---------

Die folgenden Parameter können in der ``etc/smarthome.yaml`` angegeben werden. Die Feiertags-Einstellungen, die
die Admin GUI auf der gleichen Seite anzeigt, werden in der :doc:`holidays.yaml <holidays>` gespeichert.

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Standard
     - Beschreibung
   * - ``lat``
     - ``53.5989481``
     - Breitengrad der SmartHomeNG Installation
   * - ``lon``
     - ``10.0459898``
     - Längengrad der SmartHomeNG Installation
   * - ``elev``
     - ``20``
     - Höhe der SmartHomeNG Installation über Normal-Null
   * - ``tz``
     - ``Europe/Berlin``
     - Zeitzone der SmartHomeNG Installation
   * - ``default_language``
     - ``de``
     - Standard-Sprache der SmartHomeNG Installation
   * - ``fallback_language_order``
     - ``en,de``
     - Reihenfolge der Sprachen, in der Texte gesucht werden, wenn ein Text in der Standard-Sprache nicht vorhanden ist
   * - ``assign_compatibility``
     - ``latest``
     - Wenn 'latest' gewählt wird, werden Werte bei der Zuweisung zu Items in den Datentyp des Items gewandelt, sonst werden sie als string zugewiesen
   * - ``use_conditional_triggers``
     - ``false``
     - Die experimentellen Item-Attribute ``trigger`` und ``trigger_condition`` zulassen (siehe :doc:`trigger_condition </referenz/items/standard_attribute/trigger_condition>`)
   * - ``deprecated_warnings``
     - ``false``
     - Warnungen loggen, wenn Funktionen/Methoden aufgerufen werden, die als veraltet gekennzeichnet sind
   * - ``backup_name_stem``
     - 
     - Namens-Stamm, der dem Namen der Sicherungsdatei vorangestellt wird (hilfreich, wenn mehrere Instanzen von SmartHomeNG gesichert werden)
   * - ``allow_system_power``
     - ``false``
     - Erlaubt der AdminUI, den Rechner (Host) auszuschalten oder neu zu starten. Der Befehl wird mit den Rechten des SmartHomeNG-Benutzers ausgeführt, das Betriebssystem entscheidet über die Berechtigung.
   * - ``config_etc``
     - ``true``
     - Konfigurationsverzeichnisse (items, logics, structs, scenes, functions) unterhalb von etc/ suchen. Vorhandene Verzeichnisse im Hauptverzeichnis werden beim Start automatisch dorthin verschoben. False verwendet die bis 1.12 übliche Struktur.
   * - ``legacy_instances``
     - ``false``
     - True: Instanznamen aus dem 'instance'-Parameter in plugin.yaml verwenden (Verhalten bis 1.12). False: der Name des Abschnitts in plugin.yaml ist der Instanzname
   * - ``pip_command``
     - 
     - PIP-Befehl, falls pip3 nicht automatisch gefunden wird (z.B. 'python3 -m pip')
   * - ``db_query_timeout``
     - ``60``
     - Timeout in Sekunden für Datenbankabfragen (z.B. MySQL). Verhindert dauerhaftes Blockieren bei einem nicht erreichbaren Datenbankserver. Gilt auch als Lock-Timeout beim Schließen der Verbindung.
   * - ``runtime_warn``
     - ``120``
     - Laufzeit in Sekunden, ab der für einen Scheduler-Task (Logik, Item-Zyklus/Crontab, Plugin-Scheduler) eine Warnung mit Stacktrace geloggt wird, erneut bei jeder Verdopplung. 0 = aus. Logiken können den Wert mit ihrem eigenen Parameter runtime_warn überschreiben.
   * - ``orb_backend``
     - ``ephem``
     - Bibliothek für die Berechnung von Sonne und Mond (``ephem``, ``skyfield``, ``skyfield-cached``, siehe :doc:`lib.orb </lib/orb>`). Ist sie nicht installiert, wird mit einer Warnung ein installiertes Backend verwendet.
   * - ``sun_neverup_delta``
     - ``0.00001``
     - Korrektur in Grad, um Sonnenauf- und -untergänge nahe der Polartage und -nächte berechnen zu können
   * - ``default_logtext``
     - 
     - Standard-Text für Logeinträge des Item-Attributs ``log_change``, wenn das Item kein ``log_text`` hat (Platzhalter siehe :doc:`log_change </referenz/items/standard_attribute/log_change>`)
   * - ``created_items_file``
     - ``created``
     - Name der Datei in etc/items (ohne .yaml), in die zur Laufzeit erzeugte Items geschrieben werden, wenn kein Dateiname angegeben ist
   * - ``ignore_item_collision``
     - ``false``
     - Items, deren Name mit einem Attribut des übergeordneten Objekts kollidiert, mit einer Warnung trotzdem anlegen, statt sie zu verwerfen
   * - ``restart_on_num_workers``
     - ``30``
     - SmartHomeNG wird neu gestartet, wenn der Scheduler so viele Worker-Threads benötigt
   * - ``shpypi_crontab``
     - ``7 3 * *``
     - Crontab-Eintrag für die Abfrage der Paket-Versionen auf PyPI
   * - ``module_paths``
     - 
     - Zusätzliche Verzeichnisse für Python-Module (werden sys.path hinzugefügt, normalerweise nicht nötig)
   * - ``threadinfo_export``
     - ``false``
     - Alle 120 Sekunden Informationen zu den Threads für das Tool tools/cpuusage.py exportieren


.. note::

    Die Konfigurationsparameter die in dieser Datei konfiguriert werden, können auch über das graphische Administrations-
    Interface geändert werden.

