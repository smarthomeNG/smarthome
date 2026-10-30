:tocdepth: 2

Neuerungen im Release v2.0
==========================

Hier ist eine Kurzübersicht über größere Neuerungen im aktuellen Release. Eine vollständige Übersicht der Änderungen in
diesem und den vorangegangenen Releases ist den :doc:`Release Notes </release/release>` zu finden.

SmartHomeNG 2.0 ist ein Major-Release: Funktionen, die seit längerem als veraltet gekennzeichnet waren, wurden
entfernt. Vor dem Update bitte die :ref:`Hinweise zum Update <releasenotes_2_0_0_update>` in den Release Notes lesen
und das Tool :doc:`upgrade_check.py </tools/tools_upgrade_check>` ausführen, das die nötigen Änderungen der
Konfiguration findet und die meisten davon selbst durchführt.

  - **Core**:

    - **Versionierung**: Die Versionsnummer folgt jetzt dem Semantic Versioning (``Major.Minor.Patch``). Eine neue
      Major-Version kennzeichnet Änderungen, an die Konfigurationen, Logiken oder Plugins angepasst werden müssen.

    - **Python**: Die minimale Python-Version ist **Python 3.11**.

    - **Neue Standards**: Die Konfiguration liegt standardmäßig vollständig unterhalb von ``etc``
      (``config_etc: true``), der Name eines Abschnitts in der ``etc/plugin.yaml`` ist der Instanzname eines Plugins
      (``legacy_instances: false``). Das ``.conf`` Format, klassische (Nicht-Smart-)Plugins, ``sh.tools`` und die
      veralteten Methoden des ``sh`` Objekts (z.B. ``sh.return_item()``, ``sh.now()``) wurden entfernt.

    - **Items bearbeiten**: Items und ganze Item-Bäume können in der Admin GUI angelegt, bearbeitet, umbenannt,
      verschoben, kopiert und gelöscht werden. Kommentare in den YAML Dateien bleiben dabei erhalten, Referenzen in
      anderen Items werden angepasst bzw. vor dem Löschen angezeigt.
      (Siehe auch :doc:`Admin GUI/Items </admin/items>`)

    - **Laufende Tasks**: Der Scheduler erfasst die Laufzeit von Logiken, Item-Zyklen und Plugin-Schedulern. Läuft
      ein Task zu lange, wird eine Warnung mit Stacktrace geloggt (``runtime_warn``). Logiken können in der Admin GUI
      oder automatisch (``runtime_cancel``) abgebrochen werden.
      (Siehe auch :doc:`Admin GUI/Threads </admin/threads>`)

    - **Datenbank**: Die Datenbank-Schicht unterstützt PostgreSQL mit TimescaleDB, ist robuster gegen
      Verbindungsprobleme und bietet Transaktionen. Mit :doc:`db_migrate.py </tools/tools_db_migrate>` kann die
      Datenbank des database Plugins zwischen SQLite3, MySQL/MariaDB und PostgreSQL+TimescaleDB umgezogen werden.

    - **Admin GUI**: Die neue Seite :doc:`Übersicht </admin/dashboard>` zeigt den Zustand der Installation auf einen
      Blick. Auf der Seite :doc:`Dienste </admin/dienste>` können Core und Plugins aus Git aktualisiert, der Core
      gestoppt und - wenn erlaubt (``allow_system_power``) - der Rechner ausgeschaltet oder neu gestartet werden.
      Die Kommunikation mit dem Core läuft vollständig über die REST API.

    - **Sicherheit**: Passwörter von http Modul und Admin GUI werden als gesalzene PBKDF2 Hashes gespeichert,
      CORS-Header werden nur noch für konfigurierte Origins gesendet.

    - **var Verzeichnis**: Mit der Kommandozeilenoption ``-u`` / ``--var_dir`` kann ein separates Verzeichnis für
      Cache, Logs, Datenbanken und andere Laufzeitdaten verwendet werden.

  - **Plugins**:

    - **SmartDevicePlugin 2.0**: Die Basisklasse für Geräte-Plugins wurde überarbeitet. Verbindung und Protokoll
      werden über deklarierte Regeln gewählt, die Verbindungs-Konfiguration ist typisiert.
    - **MQTT**: Mit dem Parameter ``select`` von ``add_subscription()`` können Plugins einem Item einen Teil eines
      JSON-Payloads übergeben (JMESPath).
    - ...

  - **Dokumentation**:

    - Alle Parameter der ``etc/smarthome.yaml`` sind beschrieben, ebenso die in eval Ausdrücken verfügbaren Namen.
    - Für Entwickler beschreibt ``doc/dev`` den Aufbau von lib.item, der Datenbank-Schicht, von SDP 2.0, der Admin GUI
      und der Workflows.

|
