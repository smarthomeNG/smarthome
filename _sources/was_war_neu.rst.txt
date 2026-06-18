
===============================
Neuerungen der letzten Releases
===============================

Hier sind die wichtigsten Neuerungen aus den Letzten Releases:

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

Neuerungen im Release v1.11
===========================

Hier ist eine Kurzübersicht über größere Neuerungen im aktuellen Release. Eine vollständige Übersicht der Änderungen in
diesem und den vorangegangenen Releases ist den :doc:`Release Notes </release/release>` zu finden.

  - **Plugins**:

    - **Asyncio**: Die SmartPlugin Klasse unterstützt nun asyncio.
      Python Packages zur Ansteuerung von Peripherie werden zunehmend unter Verwendung von asyncio erstellt.
      Um diese Packages in Plugins nutzen zu können, muss das jeweilige Plugin asyncio unterstützen.
      Mit der Unterstützung von asyncio in der SmartPlugin Klasse wird es erheblich einfacher Plugins zu erstellen, die
      asyncio-basierte Packages nutzen.
      (Siehe auch :doc:`Plugins/Asyncio Support </referenz/plugins/asyncio_support>`)

  - **Tools**:

    - **ESPHome**: Im Release sind Tools zur Installation und Verwaltung von ESPHome enthalten.
      Wenn ESPHome Devices durch Plugins angesteuert werden sollen kann es hilfreich sein, das ESPHome Dashboard
      zur Verwaltung der ESPHome Devices zu nutzen.
      (Siehe auch :doc:`ESPHome Dashboard </installation/komplettanleitung/10_esphome>`)

|

Neuerungen im Release v1.10
===========================

Hier ist eine Kurzübersicht über größere Neuerungen im aktuellen Release. Eine vollständige Übersicht der Änderungen in
diesem und den vorangegangenen Releases ist den :doc:`Release Notes </release/release>` zu finden.

  - **Python Environment**: SmartHomeNG sollte/muss in einem virtuellen Python Environment laufen.

    - **postinstall Skript**: Ab Debian 12/Python 3.11 können in die systemseitige Installation nicht mehr beliebig
      Python Packages installiert werden. Es gibt jetzt ein neues Skript ``tools/postinstall`` welches ein Standard
      Environment anlegt, in dem SmartHomeNG später läuft/laufen soll.
      (Siehe auch :doc:`Komplettanleitung </installation/komplettanleitung/03_smarthomeng>`)

    - **virtuelle Environments**: Skripte zum Anlegen und Aktivieren von virtuellen Python Environments
  - **Items**:

    - **Hysterese**: Es gibt neue Attribute, die es ermöglichen ein Item als Hysterese-Glied mit optionalem Zeitlied
      zu konfigurieren.
    - **Attribute**: In den Attributen **autotimer** und **cycle** können nun eval Ausdrücke
      in der Konfiguration genutzt werden. Bisher waren nur konstante Werte und alternativ Item Referenzen
      möglich
    - **Platzhalter in Attributen**: Es ist jetzt möglich innerhalb von Attributwerten über Platzhalter die
      Inhalte anderer Attribute zu verwenden.
      Details sind in der :ref:`Dokumentation <Platzhalter_in_Attributwerten>` zu finden.
    - **Zugriff auf Elemente komplexer Items**: Bei Items vom Typ **list** oder **dict** ist es möglich auf einzelne
      Elemente zuzugreifen.
      Details sind in der :ref:`Dokumentation <Zugriff_auf_Attributwerte>` zu finden.
  - **Structs**:

    - **Verschachtelung**: Es ist jetzt eine beliebige Verschachtelung von structs möglich. stucts können auch
      auf Unterebenen einer stuct eingebunden werden.
    - **relative Referenzen**: Bei der Einbindung von Sub-Structs aus der selben Datei können jetzt relative
      Angaben gemacht werden.
    - **structs Verzeichnis**: Dateien mit struct Definitionen werden jetzt im Verzeichnis ``etc/structs`` abgelegt.
      Bestehende Definitionsdateien werden automatisch aus dem ``etc`` Verzeichnis in das ``etc/structs`` Verzeichnis
      migriert.
  - **Plugins**:

    - **Installation**: Falls eine neuere Version eines Plugins aus dem develop Branch auf GitHub installiert werden
      soll, ohne deshalb die eigene Installation vollständig auf die (nicht notwendigerweise stabile) develop Version
      von SmartHomeNG umzustellen, wurde ein Skript erstellt. Dieses Skript installiert ein gewähltes Plugin aus dem
      develop branch zusätzlich in die aktuelle Installation von SmartHomeNG.
      Details sind in der Dokumentation unter :ref:`Tipps & Tricks <Plugin_aus_develop>` zu finden.

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
      - Zu Logiken kann nun eine Beschreibung erfasst werden. Diese wird in der Liste der Logiken, sowie zu den
        verbundenen Logiken in den Item-Details angezeigt.
      - Zu den Gruppen können eine Titelzeile und eine Beschreibung gepflegt werden.
    - **Systemeigenschaften**: Die Resource Graphen der Systemdaten funktionieren jetzt auch, ohne dass das smartvisu
      Plugin konfiguriert sein muss.
    - **Items**: Es ist jetzt möglich die Veränderung des Werte von mehreren Items in einer Tabelle live zu
      überwachen.

Details zu den genannten Punkten sind in den Abschnitten :doc:`Konfiguration </konfiguration/konfiguration>`
bzw. :doc:`Referenz </referenz/referenz>` zu finden.

Die vollständigen Änderungen am Core können in den :ref:`Release Notes v1.10  <Änderungen_am_core>` nachgelesen
werden.

|

Neuerungen bei Plugins
----------------------

Bei den Plugins sind folgende Änderungen zu beachten:

  - **Plugin shelly**: Es werden jetzt Shelly Devices mit dem (neuen) Gen2 API untersützt.
  - **Plugin smartvisu**: Der Default Wert des Parameters **generate_pages** wurde auf **False** geändert. Zum
    generieren von Seiten muss dieser Parameter nun aktiv konfiguriert werden.

Die vollständigen Änderungen bei Plugins können in den Release Notes in den Abschnitten

  - :ref:`neue Plugins <releasenotes_1_10_neue_plugins>`
  - :ref:`Updates zu bestehenden Plugins <releasenotes_1_10_updates_plugins>`
  - :ref:`veraltete/retired Plugins <releasenotes_1_10_retired_plugins>`

nachgelesen werden.

|

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

Tipps & Tricks
--------------

Folgende Tipps sind in der Doku hinzugekommen:

  - :ref:`Ein Plugin aus develop installieren <Plugin_aus_develop>`
  - :ref:`SmartHomeNG umziehen <shng_umziehen>`

|
