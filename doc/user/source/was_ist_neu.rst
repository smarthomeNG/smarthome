:tocdepth: 1

Neuerungen im Release v1.10
===========================

Hier ist eine Kurzübersicht über größere Neuerungen im aktuellen Release. Eine vollständige Übersicht der Änderungen in
diesem und den vorangegangenen Releases ist den :doc:`Release Notes </release/release>` zu finden.

  - **Python Environment**: SmartHomeNG sollte/muss in einem virtuellen Python Environment laufen. Ab

    - **postinstall Skript**: Debian 12/Python 3.11 können in die systemseitige Installation nicht mehr beliebig
      Python Packages installiert werden. Es gibt jetzt ein neues Skript ``tools/postinstall`` welches ein Standard
      Environment anlegt, in dem SmartHomeNG später läuft/laufen soll.
      (Siehe auch :doc:`Komplettanleitung </installation/komplettanleitung/02_smarthomeng>`)

    - **virtuelle Environments**: Skripte zum Anlegen und Aktivieren von virtuellen Python Environments
  - **Structs**:

    - **Verschachtelung**: Es ist jetzt eine beliebige Verschachtelung von structs möglich. stucts können auch
      auf Unterebenen einer stuct eingebunden werden.
    - **relative Referenzen**: Bei der Einbindung von Sub-Structs aus der selben Datei können jetzt relative
      Angaben gemacht werden.
    - **structs Verzeichnis**: Dateien mit struct Definitionen werden jetzt im Verzeichnis ../structs abgelegt.
      Bestehende Definitionsdateien werden automatisch aus dem ../etc Verzeichnis in das ../structs Verzeichnis
      migriert.
  - **Items**:

    - **Hysterese**: Es gibt neue Attribute, die es ermöglichen ein Item als Hysterese-Glied mit optionalem Zeitlied
      zu konfigurieren.
    - **Attribute**: In den Attributen **autotimer** und **cycle** können nun eval Ausdrücke
      in der Konfiguration genutzt werden. Bisher waren nur konstante Werte und alternativ Item Referenzen
      möglich
    - **Platzhalter in Attributen**: Es ist jetzt möglich innerhalb von Attributwerten über Platzhalter die
      Inhalte anderer Attribute zu verwenden.
      Details sind in der :ref:`Dokumentation <Platzhalter_in_Attributwerten>` zu finden.
  - **Neue Bibliothek lib.env**:

    - lib.env enthält eine Reihe von Funktionen zur Maßeinheitenumrechnung für Environment Daten, sowie weitere
      Funktionen welche den Umgang mit Environment Informationen unterstützen.
      Details sind in der :doc:`Dokumentation </lib/env>` zu finden.
    - Die Funktionen können in Logiken und eval Statements in Item Attributen einfach mit ``env.<Funktion>``
      aufgerufen werden.
  - **Admin GUI**:

    - **Logiken**:
      - Die Liste der Logiken kann nun gruppiert angezeigt werden. Logiken können einer oder mehreren
      Gruppen zugeordnet werden.
      - Zu den Gruppen können eine Titelzeile und eine Beschreibung gepflegt werden.
    - **Systemeigenschaften**: Die Resource Graphen der Systemdaten funktionieren jetzt auch, ohne dass das smartvisu
      Plugin konfiguriert sein muss.
    - **Items**: Es ist jetzt möglich die Veränderung des Werte von mehreren Items in einer Tabelle live zu
      überwachen.

Details zu den genannten Punkten sind in den Abschnitten :doc:`Konfiguration </konfiguration/konfiguration>`
bzw. :doc:`Referenz </referenz/referenz>` zu finden.

Die vollständigen Änderungen dieses Releases können in den :doc:`Release Notes v1.10  </release/1_10>` nachgelesen
werden.


Neuerungen bei Plugins
~~~~~~~~~~~~~~~~~~~~~~

Bei den Plugins sind folgende Änderungen zu beachten:

  - **Plugin smartvisu**: Der Default Wert des Parameters **generate_pages** wurde auf **False** geändert. Zum
    generieren von Seiten muss dieser Parameter nun aktiv konfiguriert werden.
  - Es sind auch einige :ref:`neue Plugins <releasenotes_1_10_neue_plugins>` hinzugekommen.
  - Außerdem hat es eine Reihe von :ref:`Updates zu bestehenden Plugins <releasenotes_1_10_updates_plugins>` gegeben.
  - Es sind einige veraltete Plugins :ref:`retired <releasenotes_1_10_retired_plugins>` worden.


Neuerungen für Plugin Entwickler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Für Entwickler von Plugins gibt es folgende Neuerungen:

  - **SmartPlugin**: Die Klasse SmartPlugin ist in der Funktionalität erweitert worden
  - **SmartDevicePlugin**: Das SmartDevicePlugin (sdp) ist aus der Notwendigkeit geboren, für jedes neue Plugin und
    jedes neue Gerät aufs Neue das ganze Kern-Plugin neu zu erfinden - Item-Handling, Zuordnung von Items zu Befehlen
    (commands) und Kommunikation mit Netzwerk- oder seriellen Treibern oder Libraries.
  - **lib.env**: Neue Bibliothek zum Umgang mit Environment Daten.
    Details sind in der :doc:`Dokumentation </lib/env>` zu finden


Details zu den genannten Punkten sind in den Abschnitten :doc:`Entwicklung </entwicklung/entwicklung>`
bzw. :doc:`Referenz </referenz/referenz>` zu finden.

|


.. comment

    Neuerungen im Release v1.10.1
    -----------------------------

    Ab dem Release v1.9.4 misst SmartHomeNG beim ersten Start die Geschwindigkeit der CPU, um je nach Geschwindigkeit
    interne Konfigurationen vorzunehmen. Die Messung wird nur wiederholt, wenn sich die Hardware geändert hat.

    Die Messung nimmt, je nach CPU, einige Zeit in Anspruch. Auf einem Raspberry Pi 2 zum Beispiel, verlängert sich dadurch
    die Start Zeit beim ersten Start von SmartHomeNG um ca. 3 Minuten.

    Es sind auch :ref:`sechs neue Plugins <release194_neue_plugins>` hinzugekommen.


    Die vollständigen Änderungen können in den :doc:`Release Notes </release/1_9_4>` nachgelesen werden.

