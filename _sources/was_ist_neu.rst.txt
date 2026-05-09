:tocdepth: 2

Neuerungen im Release v1.12
===========================

Hier ist eine Kurzübersicht über größere Neuerungen im aktuellen Release. Eine vollständige Übersicht der Änderungen in
diesem und den vorangegangenen Releases ist den :doc:`Release Notes </release/release>` zu finden.

  - **Core**:

    - **Itemtypen**: Für Items gibt es jetzt die beiden Typen **datetime** und **timestamp**. Der Typ `datetime`
      entspricht dem `datetime.datetime`-Objekt, der Typ `timestamp` entspricht einem POSIX-timestamp als `float`.
      Beide Typen haben zusätzliche Methoden, um die Ausgabe im `datetime`-, `timestamp`- oder Textformat auszugeben.

    - **Backup der Konfiguration**: Das Sichern und Wiederherstellen der Konfiguration wurde erweitert.
      Beim sichern der Konfiguration werden nun, falls vorhanden, die privaten Plugins (Plugins, deren
      Name mit ``priv_`` beginnt) und die privaten Tools (das Verzeichnis priv_tools) mit gesichert und
      beim Wiederherstellen aus der Zip Datei zurück kopiert.

      Dadurch steht jetzt eine einfache Möglichkeit der Sicherung dieser Dateien, die nicht in git
      gesichert werden, zur Verfügung.

    - **Konfiguration unterhalb von etc mit Migration**: Wenn SmartHomeNG mit der Kommandozeilenoption **-e** gestartet
      wird, sucht es die Konfigurationsverzeichnisse ``items``, ``structs``, ``logics``, ``uf`` und ``scenes``
      nicht mehr im Stammverzeichnis, sondern unterhalb von ``etc``. Dies ist auch durch die Option
      **config_etc: true** in der ``etc/smarthome.yaml`` möglich.

      Gleichzeitig wird versucht, vorhandene Konfigurationsdateien nach ``etc/<Verzeichnis>`` zu verschieben und -
      beim Aufruf mit **-e** - den Eintrag **config_etc: true** in der ``etc/smarthome.yaml`` einzutragen, da nach
      der Migration der Konfigurationsdateien der bisherige Aufruf nicht mehr funktionieren würde.

      Die Konfiguration unterhalb von ``etc`` soll in zukünftigen Releases Standard werden.

    - **Anpassung der Plugin-Instanzbenennung**: Bisher wurde der Instanzname eines Plugins aus der Angabe
      **instance: <name>** in der ``etc/plugin.yaml`` ermittelt. Im - derzeit optional verfügbaren - neuen
      System wird stattdessen der Name des entsprechenden Abschnitts in der ``etc/plugin.yaml`` verwendet.
      Damit erhält standardmäßig jedes Plugin, das mehrfach eingebunden wird, einen Instanzbezeichner. Wenn
      das für einzelne Instanzen nicht gewollt ist, kann mit **default_instance: true** für einzelne Plugins
      weiterhin der leere Instanzname verwendet werden.

      Um dieses System jetzt schon zu aktivieren, muss in der ``etc/smarthome.yaml`` die Option
      **legacy_instances: false** gesetzt werden.

      Diese Methode der Instanzbenennung soll in zukünftigen Releases Standard werden.

    - **Vererbbare Item-Attribute**: Bei der Einbindung von Item-Template-Strukturen können Item-Attribute
      definiert werden, die an alle Items der Struktur vererbt werden. Häufige Beispiele können z.B. 
      die Attribute `database`, `cache` oder `enforce_updates` sein.

  - **Plugins**:

    - **smartvisu**: Im smartvisu Plugin wurde die Generierung erweitert.
      Nun können in generierten Seiten Buttons als Top Navigation eingerichtet werden. Damit ist es möglich
      Seiten zu generieren, die sich unterhalb der Top Navigation mit unterschiedlichen Inhalten füllen
      lassen.
      (Siehe auch :doc:`Generierung der Visu Seiten/Top Navigation </visualisierung/top_navigation>`)

    - **alexa**, **influxdata**, **memlog**, **operationlog**, **raumfeld**, **sml**, **sqlite_visu2_8**, **wunderground**:
      Diese Plugins waren als `deprecated` markiert und wurden entfernt. Sie sind
      bei Bedarf im Repo `smarthomeNG/plugins-archive` verfügbar.

  - **Dokumentation**:

    - **Ordner/Dateien**: Vor dem Hintergrund, dass die Konfiguration zukünftig vollständig unterhalb von
      ``etc`` abgelegt werden soll (Option **-e**/**--config-etc**), werden alle Datei- und Pfadnamen von
      Konfigurationsdateien unterhalb von ``etc`` angegeben. In Ausnahmefällen können z.B. in Beispielen
      nur lokale Dateinamen angegeben werden.

    - **Verweise auf ältere SmartHomeNG-Versionen**: In der Beschreibung von Konfiguration oder Syntax wird
      nur noch der aktuell gültige Stand angegeben. Beschreibungen, wie etwas in früheren Versionen
      angegeben werden musste, oder seit welcher Version ein bestimmtes Feature implementiert ist, entfallen.
      Nach Möglichkeit werden Dokumentationen von früheren Versionen von SmartHomeNG parallel als Archiv
      bereitgestellt.

|

.. comment

    Neuerungen im Release v1.12.x
    -----------------------------

    *Hier kommen die Neuerungen des Releases v1.12.1 hin.*

    ...

    Ab dem Release v1.9.4 misst SmartHomeNG beim ersten Start die Geschwindigkeit der CPU, um je nach Geschwindigkeit
    interne Konfigurationen vorzunehmen. Die Messung wird nur wiederholt, wenn sich die Hardware geändert hat.

    Die Messung nimmt, je nach CPU, einige Zeit in Anspruch. Auf einem Raspberry Pi 2 zum Beispiel, verlängert sich dadurch
    die Start Zeit beim ersten Start von SmartHomeNG um ca. 3 Minuten.

    Es sind auch :ref:`sechs neue Plugins <release194_neue_plugins>` hinzugekommen.


    Die vollständigen Änderungen können in den :doc:`Release Notes </release/1_9_4>` nachgelesen werden.

  - **Neues Layout der Konfiguration**:

    - SmartHomeNG ermöglicht wahlweise, ein Layout der Konfiguration zu nutzen,
      dass sich näher an der klassischen Dateistruktur von Unix/Linux anpasst.

      Dabei befinden sich alle Verzeichniss mit nutzergenerierter Konfiguration
      unterhalb von `etc/`, also `items/`, `logics/`, `structs/`, `scenes/` und
      `functions/`.

    - Das neue Layout wird durch den Kommandozeilenschalter `-e` oder
      `--config_etc` aktiviert. Dies muss bei jedem Start angegeben werden.


