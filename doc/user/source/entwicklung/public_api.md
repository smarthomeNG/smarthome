# SmartHomeNG: Öffentliche API und Versionierung

SmartHomeNG folgt ab Version **2.0.0** dem [Semantic Versioning 2.0.0](https://semver.org/lang/de/).
Dieses Dokument legt fest, was zur öffentlichen API gehört, wie Versionsnummern zu lesen sind und
welche Änderungen welche Versionserhöhung nach sich ziehen. Es richtet sich an Entwickler von
Plugins, Modulen, Logiken und Visualisierungen sowie an alle, die auf SmartHomeNG aufbauen.

## Was zur öffentlichen API gehört

Nur die hier aufgeführten Bereiche sind durch die Versionsnummer abgedeckt. Alles andere kann sich
in jeder Version ändern.

### 1. Python-API für Plugin-, Modul- und Logik-Autoren

Öffentliche Klassen, Methoden, Funktionen und `GROSS_GESCHRIEBENE` Konstanten der folgenden Dateien
im Verzeichnis `lib/`. Bei Klassen zählen auch die Signaturen von `__init__` und `__call__`.

| Bereich | Dateien |
|---|---|
| Plugin-Basisklassen | `lib/model/*.py` (u. a. `SmartPlugin`, `MqttPlugin`), `lib/model/sdp/*.py` (`SmartDevicePlugin`, SDP) |
| Items | `lib/item/*.py` (`Item`, `Items`) |
| Kern und Infrastruktur | `lib/smarthome.py`, `lib/plugin.py`, `lib/module.py`, `lib/logic.py`, `lib/scheduler.py`, `lib/config.py`, `lib/metadata.py`, `lib/constants.py` |
| Hilfsklassen | `lib/utils.py`, `lib/shtime.py`, `lib/network.py`, `lib/db.py`, `lib/shyaml.py`, `lib/log.py`, `lib/translation.py`, `lib/orb.py`, `lib/triggertimes.py` |

### 2. Konfiguration für Anwender

- **Modul-Parameter**: die in `modules/*/module.yaml` deklarierten Parameter, also die Schlüssel,
  die Anwender in `etc/*.yaml` eintragen.
- **Kommandozeilen-Optionen** von `bin/smarthome.py`.
- **Item-Attribute**, wie sie in `modules/core/items.yaml` katalogisiert sind (Name, Typ, zulässige
  Werte).
- **Struct-Syntax** und der **Namensraum von Logik-Skripten**.

### 3. smartVISU-Websocket-Protokoll

Die Kommandos, die `modules/websocket/smartvisu.py` entgegennimmt und sendet. Visualisierungen von
Drittanbietern verlassen sich darauf.

## Nicht öffentliche API

Dies darf sich jederzeit ändern, auch in Patch-Versionen:

- Namen, die mit einem Unterstrich beginnen, sowie Module, deren Dateiname mit einem Unterstrich
  beginnt (z. B. `lib/item/_internal/`).
- Die REST-API und das Websocket-Protokoll des Admin-Moduls. Einziger Client ist die
  mitgelieferte Admin-Oberfläche (shngadmin).
- Dateien der Weboberflächen (Assets, Templates), `tools/`, `tests/` sowie die Texte von
  Log-Meldungen.
- Versionsangaben von Drittbibliotheken in `requirements.txt`.
- Die unterstützten Python-Versionen (das ist eine Support-Zusage, keine API).

## Versionsnummern

| Komponente | Schema |
|---|---|
| Core | `X.Y.Z`; während der Entwicklung trägt `develop` eine Vorabversion `X.Y.Z-dev.N` |
| Plugins, Module | `X.Y.Z` in `plugin.yaml` bzw. `module.yaml`, identisch mit `PLUGIN_VERSION` im Code |
| SmartDevicePlugin | `SDP_VERSION`; Plugins fordern eine Mindestversion über `sdp_minversion` in `plugin.yaml` |

Anforderungsfelder (`sh_minversion`, `sh_maxversion`, `sdp_minversion`, `py_minversion`,
`py_maxversion`) dürfen aus historischen Gründen eine vierte Ziffer enthalten (`1.12.2.2`). Sie ordnet
sich zwischen `1.12.2` und `1.12.3` ein. Die Version einer Komponente selbst hat immer genau drei
Ziffern.

Build-Metadaten nach einem `+` (Commit, Branch) sind informativ und werden beim Vergleich von
Versionen ignoriert.

Veröffentlichungen vor 2.0.0 werden nicht nachträglich eingeordnet.

## Welche Änderung erhöht welche Versionsstelle

| Änderung | Erhöhung |
|---|---|
| Entfernter oder umbenannter öffentlicher Name; geänderte Signatur, die bestehende Aufrufer bricht; geänderter Parametertyp; neuer Pflichtparameter; eingeschränkte zulässige Werte (`valid_*`); entfernte Kommandozeilen-Option oder entferntes Websocket-Kommando | **Major** |
| Erhöhte `sh_minversion` eines Plugins oder Moduls | **Major** |
| Geänderter Standardwert eines in einer `module.yaml` deklarierten Konfigurationsparameters (einschließlich der Kernparameter der `smarthome.yaml`) | **Major** |
| Erhöhte `py_minversion` (Python-Versionen werden gemäß dem Python-EOL-Zeitplan aufgegeben und in den Release Notes angekündigt) | **Minor** |
| Neuer öffentlicher Name, neuer optionaler Parameter, neue Kommandozeilen-Option, neues Websocket-Kommando oder erweiterte zulässige Werte (`valid_*`) | **Minor** |
| Fehlerbehebung, interne Änderung, Dokumentation | **Patch** |

Solange eine Komponente unter 1.0.0 liegt, erzwingt kein Änderungstyp eine Major-Erhöhung.

### Abkündigungen

Öffentliche API wird nicht ohne Vorwarnung entfernt: Eine Abkündigung erfolgt in einem
Minor-Release (Warnung im Log, Eintrag in den Release Notes), die Entfernung frühestens im folgenden
Major-Release.

## Hinweise für Entwickler

- Wer ein Plugin oder Modul ändert, erhöht dessen Version entsprechend der obigen Tabelle, bevor die
  Änderung eingereicht wird. Im Zweifel gilt die höhere Stufe.
- `PLUGIN_VERSION` im Code und `version` in `plugin.yaml` bzw. `module.yaml` müssen übereinstimmen.
- `sh_minversion` darf nicht höher sein als die Version des Cores, in dem das Plugin ausgeliefert
  wird.
- Eine Änderung, die nur Tests, Dokumentation (`*.rst`, `*.md`) oder superseded Plugin-Versionen
  (`_pv_*`) betrifft, benötigt keine neue Version.
- Verwende nur öffentliche Namen aus Abschnitt 1. Wer auf unterstrichene Namen oder nicht
  aufgeführte Module zugreift, muss damit rechnen, dass dies in jeder Version bricht.
