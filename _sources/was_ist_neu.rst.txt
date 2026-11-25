:tocdepth: 2

Neuerungen im Release v2.0
==========================

Hier ist eine Kurzübersicht über größere Neuerungen im aktuellen Release. Eine vollständige Übersicht der Änderungen in
diesem und den vorangegangenen Releases ist in den :doc:`Release-Notes </release/release>` zu finden.

SmartHomeNG 2.0 ist ein Major-Release: Funktionen, die seit längerem als veraltet gekennzeichnet waren, sind
entfernt. Vor dem Update bitte die :ref:`Hinweise zum Update <releasenotes_2_0_0_update>` in den Release-Notes lesen
und das Tool :doc:`upgrade_check.py </tools/tools_upgrade_check>` ausführen, das die nötigen Änderungen der
Konfiguration findet und die meisten davon selbst durchführt.

  - **Core**:

    - **Python**: Die minimale Python-Version ist **Python 3.11**.

    - **Neue Standards**: Die Konfiguration liegt standardmäßig vollständig unterhalb von ``etc``
      (``config_etc: true``), der Name eines Abschnitts in der ``etc/plugin.yaml`` ist der Instanzname eines Plugins
      (``legacy_instances: false``). Das ``.conf``-Format, klassische (Nicht-Smart-)Plugins, ``sh.tools`` und die
      veralteten Methoden des ``sh``-Objekts (z.B. ``sh.return_item()``, ``sh.now()``) sind entfernt.

    - **Item-Attribut instance**: ``instance:`` wird an untergeordnete Items vererbt und bindet deren
      Plugin-Attribute ohne ``@<instanz>`` an die genannte Plugin-Instanz. Items, die ``instance:`` zusammen mit
      Attributen der Standard-Instanz eines Plugins verwenden, müssen angepasst werden.
      (Siehe auch :doc:`Plugins </konfiguration/plugins>`)

    - **Mehrzeilige Werte** in Item- und Struct-Dateien (außer Blöcken mit ``|``) werden, wie YAML es vorsieht,
      mit einem Leerzeichen verbunden; bisher wurden die Zeilen ohne Leerzeichen aneinandergehängt.

    - **Umstellung mit upgrade_check.py**: Das neue Tool :doc:`upgrade_check.py </tools/tools_upgrade_check>` prüft
      die Konfiguration einer bestehenden Installation (``etc/plugin.yaml``, Items, Structs, Logiken, Userfunctions,
      Szenen) auf die Änderungen von 2.0: Instanznamen und das Item-Attribut ``instance``, entfernte Methoden des
      ``sh``-Objekts und ``sh.tools``, Dateien im ``.conf``-Format, entfallene Modul-Parameter, ungesalzene
      Passwort-Hashes, mehrzeilige Werte und Dateien mit ``%YAML 1.1``. Ohne Optionen berichtet es nur; mit
      ``--fix`` führt es die meisten Änderungen selbst durch und sichert jede geänderte Datei vorher nach
      ``etc/upgrade_check_backup/``. Es sollte vor dem ersten Start von SmartHomeNG 2.0 ausgeführt werden.

    - **Versionierung**: Die Versionsnummer folgt jetzt dem Semantic Versioning (``Major.Minor.Patch``). Eine neue
      Major-Version kennzeichnet Änderungen, an die Konfigurationen, Logiken oder Plugins angepasst werden müssen.

    - **Items bearbeiten**: Items und ganze Item-Bäume können in der Admin-GUI angelegt, bearbeitet, umbenannt,
      verschoben, kopiert und gelöscht werden. Diese Änderungen können in den YAML-Dateien gespeichert oder nur bis
      zum nächsten Neustart übernommen werden. Kommentare in den YAML-Dateien bleiben dabei erhalten, Referenzen in
      anderen Items werden angepasst bzw. vor dem Löschen angezeigt.
      (Siehe auch :doc:`Admin-GUI/Items </admin/items>`)

    - **Laufende Tasks**: Der Scheduler erfasst die Laufzeit von Logiken, Item-Zyklen und Plugin-Schedulern. Läuft
      ein Task zu lange, wird eine Warnung geloggt (``runtime_warn``), der Stacktrace auf DEBUG. Logiken können in
      der Admin-GUI oder automatisch (``runtime_cancel``) abgebrochen werden.
      (Siehe auch :doc:`Admin-GUI/Threads </admin/threads>`)

    - **Datenbank**: Die Datenbank-Schicht unterstützt PostgreSQL mit TimescaleDB, ist robuster gegen
      Verbindungsprobleme und bietet Transaktionen. Mit :doc:`db_migrate.py </tools/tools_db_migrate>` kann die
      Datenbank des database-Plugins zwischen SQLite3, MySQL/MariaDB und PostgreSQL+TimescaleDB umgezogen werden.

    - **Admin-GUI**: Die neue Seite :doc:`Übersicht </admin/dashboard>` zeigt den Zustand der Installation auf einen
      Blick. Auf der Seite :doc:`Dienste </admin/dienste>` können Core und Plugins aus Git aktualisiert, der Core
      gestoppt und - wenn erlaubt (``allow_system_power``) - der Rechner ausgeschaltet oder neu gestartet werden.
      Die Kommunikation mit dem Core läuft vollständig über die REST-API.

    - **Sicherheit**: Passwörter von http-Modul und Admin-GUI werden als gesalzene PBKDF2-Hashes gespeichert,
      CORS-Header werden nur noch für konfigurierte Origins gesendet.

    - **var-Verzeichnis**: Mit der Kommandozeilenoption ``-u`` / ``--var_dir`` kann ein separates Verzeichnis für
      Cache, Logs, Datenbanken und andere Laufzeitdaten verwendet werden.

    - **YAML 1.2**: Empfohlen wird YAML 1.2, die mitgelieferten Vorlagen enthalten keine Zeile ``%YAML 1.1`` mehr.
      Dateien älterer Installationen können mit ``tools/upgrade_check.py --only yaml-1.1`` umgestellt werden.
      (Siehe auch :ref:`YAML 1.1 und YAML 1.2 <yaml_versionen>`)

  - **Plugins**:

    - **Neue Plugins**: **matter** bindet Matter-Geräte an (auch über Thread) und macht SmartHomeNG-Items als
      Matter-Bridge für andere Ökosysteme wie Apple Home sichtbar. **deebot** steuert Deebot-Saugroboter von Ecovacs
      und ersetzt das Plugin deebot_ozmo.

    - **database**: Das Plugin unterstützt PostgreSQL mit TimescaleDB und den WAL-Modus von SQLite, kann alte Daten
      automatisch aggregieren und Werte als ungültig markieren statt sie zu löschen (z.B. wenn ein Gerät offline
      ist, auch durch shelly, tasmota, zigbee2mqtt und matter). Das Webinterface ist stark erweitert.
      Mit PostgreSQL+TimescaleDB ist das database Plugin die empfohlene Wahl für Zeitreihen-Daten, auch als Ersatz
      für die Plugins influxdb und influxdb2.

    - **SmartDevicePlugin 2.0**: Die Basisklasse für Geräte-Plugins ist überarbeitet. Verbindung und Protokoll
      werden über deklarierte Regeln gewählt, die Verbindungs-Konfiguration ist typisiert. Die Plugins denon, epson,
      kodi, lms, oppo, pioneer und viessmann sind umgestellt; der Parameter ``conn_type`` entfällt.

    - **MQTT**: Mit dem Parameter ``select`` von ``add_subscription()`` können Plugins einem Item einen Teil eines
      JSON-Payloads übergeben (JMESPath); das mqtt-Plugin bietet dafür das Attribut ``mqtt_select_in``.

    - **Webinterfaces**: Werte werden als Text eingefügt, HTML-Markup nur noch ausdrücklich
      (``shngInsertText(..., as_html)``). Webinterfaces eigener Plugins müssen ggf. angepasst werden.

    - **Nicht mehr lauffähige Plugins**: darksky, deebot_ozmo, harmony, roomba_980 und zwave sind als ``defunct``
      gekennzeichnet. Sie werden beim Laden mit einer Warnung gemeldet und mit Release 2.1 entfernt.

  - **Dokumentation**:

    - Alle Parameter der ``etc/smarthome.yaml`` sind beschrieben, ebenso die in eval-Ausdrücken verfügbaren Namen.
    - Die Unterschiede zwischen YAML 1.1 und YAML 1.2 und die Regeln für Quotes sind beschrieben.
    - Für Entwickler beschreibt ``doc/dev`` den Aufbau von lib.item, der Datenbank-Schicht, von SDP 2.0, der Admin-GUI
      und der Workflows.

|
