:tocdepth: 2

Neuerungen im Release v1.12
===========================

Hier ist eine Kurzübersicht über größere Neuerungen im aktuellen Release. Eine vollständige Übersicht der Änderungen in
diesem und den vorangegangenen Releases ist den :doc:`Release Notes </release/release>` zu finden.

  - **Plugins**:

    - **smartvisu**: Im smartvisu Plugin wurde die Generierung erweitert.
      Nun können in generierten Seiten Buttons als Top Navigation eingerichtet werden. Damit ist es möglich
      Seiten zu generieren, die sich unterhalb der Top Navigation mit unterschiedlichen Inhalten füllen
      lassen.
      (Siehe auch :doc:`Generierung der Visu Seiten/Top Navigation </visualisierung/top_navigation>`)

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


