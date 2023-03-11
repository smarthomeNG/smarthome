:tocdepth: 1

Neuerungen im Release v1.9
==========================

Hier ist eine Kurzübersicht über größere Neuerungen im aktuellen Release.
Eine vollständige Übersicht der Änderungen ist den den :doc:`Release Notes </release/release>` zu finden.

  - **Structs**: Es sind mehrere struct Definitionsdateien möglich
  - **Item Logging**: Funktionalität stark erweitert (kann das operationslog Plugin ersetzen)
  - **Logging**: Es gibt einen Handler, der beim rotieren der Log Dateien die File-Extension erhält
  - **Logging**: Es gibt einen Handler, der beim Logging den Zugriff auf die memory Logs von SmartHomeNG erlaubt
  - **Userfunctions**: Es können Python Funktionen definiert werden, die in eval Statements und Logiken verwendet
    werden können. Userfunctions können zur Laufzeit neu geladen werden.
  - **Szenen**: Die Szenen Definitionsdateien können neu geladen werden, ohne SmartHomeNG neu starten zu müssen

Details zu den genannten Punkten sind in den Abschnitten :doc:`Konfiguration </konfiguration/konfiguration>`
bzw. :doc:`Referenz </referenz/referenz>` zu finden.

|

Auch bei den Plugins hat es größere Änderungen gegeben:

  - **diverse Plugins**: Umstellung der Plugins die bisher lib.connection nutzten auf lib.network

|

Neuerungen im Release v1.9.4
----------------------------

Ab dem Release v1.9.4 misst SmartHomeNG beim ersten Start die Geschwindigkeit der CPU, um je nach Geschwindigkeit
interne Konfigurationen vorzunehmen. Die Messung wird nur wiederholt, wenn sich die Hardware geändert hat.

Die Messung nimmt, je nach CPU, einige Zeit in Anspruch. Auf einem Raspberry Pi 2 zum Beispiel, verlängert sich dadurch
die Start Zeit beim ersten Start von SmartHomeNG um ca. 3 Minuten.

Die vollständigen Änderungen können in den :doc:`Release Notes </release/1_9_4>` nachgelesen werden.

