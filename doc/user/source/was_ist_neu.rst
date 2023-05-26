:tocdepth: 1

Neuerungen im Release v1.10
===========================

Hier ist eine Kurzübersicht über größere Neuerungen im aktuellen Release. Eine vollständige Übersicht der Änderungen in
diesem und den vorangegangenen Releases ist den :doc:`Release Notes </release/release>` zu finden.

  - **Structs**: Es ist jetzt eine beliebige Verschachtelung von structs möglich. stucts können auch auf Unterebenen
    einer stuct eingebunden werden.
  - **Items**: Es gibt neue Attribute, die es ermöglichen ein Item als Hysterese-Glied mit optionalem Zeitlied
    zu konfigurieren.
  - **Items**: In den Attributen **autotimer** und **cycle** können nun eval Ausdrücke in der Konfiguration genutzt
    werden. Bisher waren nur konstante Werte und alternativ Item Referenzen möglich

Details zu den genannten Punkten sind in den Abschnitten :doc:`Konfiguration </konfiguration/konfiguration>`
bzw. :doc:`Referenz </referenz/referenz>` zu finden.

Die vollständigen Änderungen dieses Releases können in den :doc:`Release Notes v1.10  </release/1_10>` nachgelesen
werden.


Neuerungen bei Plugins
~~~~~~~~~~~~~~~~~~~~~~

Bei den Plugins sind folgende Änderungen zu beachten:

  - **Plugin smartvisu**: Der Default Wert des Parameters **generate_pages** wurde auf **False** geändert. Zum
    generieren von Seiten muss dieser Parameter nun aktive konfiguriert werden.
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

