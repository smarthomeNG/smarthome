# SmartHomeNG — Plugin-Entwicklung: Einführung und Leitfaden

Dieses Dokument richtet sich an Entwicklerinnen und Entwickler, die ein eigenes Plugin für SmartHomeNG schreiben möchten.
Es sind keine vertieften Python-Kenntnisse erforderlich — wer grundlegende Konzepte wie Klassen, Methoden und `if`/`for` kennt, kann loslegen.

Hinweise für erfahrenere Entwickler sind gesondert markiert:

> **💡 Hinweis für erfahrene Python-Entwickler**  
> Diese Kästen enthalten Hintergrundinformationen, die für Einsteiger zunächst nicht relevant sind.

> **📐 Hintergrund:** Die Designentscheidungen, die diesem Leitfaden zugrunde liegen, sind in
> [`DESIGNPHILOSOPHIE.md`](DESIGNPHILOSOPHIE.md) (was SmartHomeNG architektonisch ausmacht) und
> [`ENTWICKLUNGSRICHTLINIEN.md`](ENTWICKLUNGSRICHTLINIEN.md) (verbindliche Leitplanken für Kern- und
> Plugin-Entwicklung, insb. zu optionalen Lifecycle-Hooks) festgehalten.

---

## Inhaltsverzeichnis

- [Beispiel-Plugins](#beispiel-plugins)

1. [Voraussetzungen](#1-voraussetzungen)
2. [Verzeichnisstruktur eines Plugins](#2-verzeichnisstruktur-eines-plugins)
3. [SmartPlugin — das Grundgerüst](#3-smartplugin--das-grundgerüst)
4. [Die Pflichtmethoden im Detail](#4-die-pflichtmethoden-im-detail)
5. [Items verarbeiten: parse_item und update_item](#5-items-verarbeiten-parse_item-und-update_item)
6. [Weitere nützliche Methoden](#6-weitere-nützliche-methoden)
7. [Die plugin.yaml — Parameter und Item-Attribute](#7-die-pluginyaml--parameter-und-item-attribute)
8. [Tests schreiben](#8-tests-schreiben)
9. [MqttPlugin — Erweiterung für MQTT-Geräte](#9-mqttplugin--erweiterung-für-mqtt-geräte)
10. [SmartDevicePlugin — Erweiterung für Geräteprotokolle](#10-smartdeviceplugin--erweiterung-für-geräteprotokolle)
11. [Checkliste vor dem ersten Push](#11-checkliste-vor-dem-ersten-push)

---

## Beispiel-Plugins

Im Verzeichnis `dev/` liegen lauffähige Beispiel-Plugins, die als Startpunkt oder
Nachschlagewerk dienen:

| Verzeichnis | Beschreibung |
|---|---|
| `dev/sample_plugin/` | Einfaches SmartPlugin-Grundgerüst mit Webinterface und allen Pflichtmethoden |
| `dev/sample_mqttplugin/` | MqttPlugin mit Subscription-Beispiel und Webinterface |
| `dev/sample_smartdevice_plugin/` | SmartDevicePlugin mit vollständiger `commands.py`-Referenz |
| `dev/sample_smartdevice_standalone_plugin/` | SmartDevicePlugin mit Standalone-Modus (z.B. für Geräteabfragen ohne laufendes shNG) |

Jedes Beispiel-Plugin enthält ein `tests/test_contract.py`, das zeigt, wie
Contract-Tests für das jeweilige Plugin-Typ eingerichtet werden.

Beim Kopieren eines Beispiels nach `plugins/mein_plugin/`:
- Klassen- und Dateinamen anpassen
- `classname` in `plugin.yaml` entsprechend setzen
- `PLUGIN_VERSION` und `version` in `plugin.yaml` synchron halten
- Import in `tests/test_contract.py` von `dev.sample_*` auf `plugins.mein_plugin` umstellen

---

## 1. Voraussetzungen

- Python 3.10 oder höher
- Eine lauffähige SmartHomeNG-Installation (für manuelle Tests)
- Das Plugins-Repository als Unterverzeichnis `plugins/` im SmartHomeNG-Wurzelverzeichnis

Für die automatisierten Tests (empfohlen):

```bash
# Einmalig: virtuelle Umgebung anlegen und abhängige Pakete installieren
python3 -m venv venvs/shng
venvs/shng/bin/pip install -r requirements/test.txt

# Tests ausführen
venvs/shng/bin/pytest
```

> **💡 Hinweis für erfahrene Python-Entwickler**  
> SmartHomeNG verwendet `tox.ini` für die Testablaufkonfiguration. `testpaths` ist auf
> `tests plugins` gesetzt, `--ignore-glob=plugins/*/_pv_*` überspringt alte Plugin-Versionen.
> Code-Qualität wird mit `ruff` (Regeln E + F) geprüft — Konfiguration in `pyproject.toml`.
> Git-Hooks in `.githooks/` automatisieren ruff und pytest nach jedem Commit und blockieren
> Pushes bei Fehlern. Aktivierung: `tools/install-hooks.sh`.

---

## 2. Verzeichnisstruktur eines Plugins

Jedes Plugin lebt in einem eigenen Unterverzeichnis unter `plugins/`:

```
plugins/
└── mein_plugin/               ← Verzeichnisname = Kurzname des Plugins
    ├── __init__.py            ← Python-Paket-Marker (kann leer sein)
    ├── plugin.yaml            ← Metadaten, Parameter, Item-Attribute
    ├── plugin.py              ← (optional) Hauptklasse, wenn nicht in __init__.py
    └── tests/                 ← (empfohlen) Plugin-spezifische Tests
        └── test_mein_plugin.py
```

> **💡 Hinweis für erfahrene Python-Entwickler**  
> Der Plugin-Loader (`lib/plugin.py`) importiert das Plugin-Verzeichnis als Python-Paket.
> Die Hauptklasse kann in `__init__.py` oder in einer separaten `.py`-Datei liegen —
> `plugin.yaml` legt den Klassennamen via `classname:` fest.

---

## 3. SmartPlugin — das Grundgerüst

Jedes SmartPlugin-basierte Plugin erbt von `lib.model.smartplugin.SmartPlugin`.
Das folgende Gerüst ist der Ausgangspunkt für ein neues Plugin:

```python
#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab

from lib.model.smartplugin import SmartPlugin


class MeinPlugin(SmartPlugin):

    PLUGIN_VERSION = '1.0.0'       # Versionsnummer (muss mit plugin.yaml übereinstimmen)
    ALLOW_MULTIINSTANCE = False    # True: mehrere Instanzen erlaubt; False: nur eine

    def __init__(self, sh, mein_parameter='Standardwert', **kwargs):
        """
        Initialisierung des Plugins.
        Wird einmal beim Start von SmartHomeNG aufgerufen.
        """
        # Immer als erstes aufrufen — richtet interne SmartPlugin-Strukturen ein:
        super().__init__()

        # Eigene Initialisierung:
        self.mein_parameter = mein_parameter
        self.logger.info(f'Plugin initialisiert mit Parameter: {mein_parameter}')

    def run(self):
        """
        Startet das Plugin.
        Wird aufgerufen, nachdem alle Items geladen wurden.
        """
        self.alive = True           # WICHTIG: signalisiert SmartHomeNG, dass das Plugin läuft
        self.logger.info('Plugin gestartet')

    def stop(self):
        """
        Stoppt das Plugin (z. B. beim Herunterfahren von SmartHomeNG).
        """
        self.alive = False          # WICHTIG: signalisiert SmartHomeNG, dass das Plugin gestoppt ist
        self.logger.info('Plugin gestoppt')
```

**Was bedeutet `super().__init__()`?**  
`SmartPlugin` (die Elternklasse) hat eine eigene `__init__`-Methode, die interne Datenstrukturen anlegt (z. B. die Item-Liste). `super().__init__()` ruft diese Methode auf. Vergisst man diesen Aufruf, fehlen die internen Strukturen und das Plugin wird fehlerhaft laufen.

**Was ist `self`?**  
`self` ist der Verweis auf die aktuelle Plugin-Instanz. Über `self.irgendwas` werden Daten gespeichert und abgerufen, die dem Plugin gehören.

> **💡 Hinweis für erfahrene Python-Entwickler**  
> `PLUGIN_VERSION` und `ALLOW_MULTIINSTANCE` sind Klassen-Attribute, keine Instanz-Attribute.
> Sie werden vom Loader über `__new__` geprüft (PLUGIN_VERSION) und von `_set_multi_instance_capable()`
> ausgewertet. Als Klassen-Attribute sind sie Singletons pro Klasse — das ist beabsichtigt.  
> Der Loader setzt nach dem `__init__`-Aufruf folgende Instanz-Attribute per Setter:
> `_sh`, `_shortname`, `_classname`, `_configname`, `_plugin_dir`, `_parameters`.
> Innerhalb von `__init__` sind diese bereits über die Klassen-Attribute verfügbar
> (der Loader setzt sie kurz vor dem Aufruf als Klassen-Attribute).

---

## 4. Die Pflichtmethoden im Detail

### `__init__` — Initialisierung

```python
def __init__(self, sh, host='localhost', port=80, **kwargs):
    super().__init__()

    # Parameter lesen und prüfen
    self.host = self.get_parameter_value('host') or host
    self.port = int(self.get_parameter_value('port') or port)

    # Prüfen, ob alle notwendigen Parameter vorhanden sind
    if not self.host:
        self.logger.error('Parameter "host" fehlt — Plugin wird nicht gestartet')
        self._init_complete = False   # signalisiert dem Loader: nicht laden
        return

    self.logger.info(f'Verbinde mit {self.host}:{self.port}')
```

**Wichtige Regeln für `__init__`:**

- `super().__init__()` muss **als Erstes** aufgerufen werden.
- `self.alive` **nicht** auf `True` setzen — das passiert in `run()`.
- Wenn ein notwendiger Parameter fehlt oder ungültig ist: `self._init_complete = False` setzen und mit `return` abbrechen. Der Loader wird das Plugin dann nicht starten.
- Keine langen Wartezeiten oder Verbindungsversuche — `__init__` soll schnell durchlaufen.

### `run` — Plugin starten

```python
def run(self):
    self.alive = True

    # Verbindung zum Gerät aufbauen
    self._verbinden()

    # Periodische Abfrage registrieren (alle 30 Sekunden)
    self.scheduler_add('poll', self.poll_device, cycle=30)

    self.logger.info('Plugin läuft')
```

**Wichtig:** `self.alive = True` muss gesetzt werden, damit SmartHomeNG weiß, dass das Plugin aktiv ist.

### `stop` — Plugin stoppen

```python
def stop(self):
    self.alive = False

    # Scheduler aufräumen
    self.scheduler_remove('poll')

    # Verbindung trennen
    self._trennen()

    self.logger.info('Plugin gestoppt')
```

**Wichtig:** `self.alive = False` muss gesetzt werden. Alle in `run()` angelegten Scheduler sollten hier entfernt werden.

> **💡 Hinweis für erfahrene Python-Entwickler**  
> `SmartPlugin.deinit()` ruft automatisch `stop()` auf und entfernt danach alle registrierten
> Items. Eigene Aufräumarbeiten (Netzwerkverbindungen, Threads) müssen aber in `stop()`
> implementiert werden, da `deinit()` danach nicht mehr in die Plugin-Logik eingreift.
>
> **asyncio (optional):** Wenn die verwendete Gerätebibliothek asyncio-basiert ist, verwaltet
> SmartPlugin einen eigenen Event-Loop-Thread pro Plugin.  Das Grundmuster:
>
> - `run()` → `self.start_asyncio(self.plugin_coro())`
> - `stop()` → `self.stop_asyncio()`
> - `plugin_coro()` ist eine `async def`-Methode, die nach dem Setup `self.alive = True` setzt
>   und dann `await self.wait_for_asyncio_termination()` aufruft.  Erst wenn `stop_asyncio()`
>   ein `'STOP'`-Signal in die interne Queue schreibt, kehrt das `await` zurück und die
>   Coroutine räumt auf.
> - Aus synchronem Code (z. B. `update_item`) lässt sich die async-Seite über
>   `self.run_asyncio_coro(self._async_send(...))` aufrufen — die Methode blockiert den
>   aufrufenden Thread bis die Coroutine fertig ist.
>
> Ein vollständiges, kommentiertes Beispiel befindet sich am Ende von
> `dev/sample_plugin/__init__.py` (Abschnitt *OPTIONAL: asyncio support*).

---

## 5. Items verarbeiten: parse_item und update_item

Das Item-System ist das Herzstück von SmartHomeNG. Items sind benannte Datenpunkte
(z. B. `wohnzimmer.licht.an`), die einen Wert halten und bei Änderung Aktionen auslösen.

### `parse_item` — Items beim Start registrieren

`parse_item` wird für **jedes** Item im System aufgerufen, **bevor** `run()` startet.
Das Plugin entscheidet hier, ob es ein Item „übernimmt".

```python
def parse_item(self, item):
    # Prüfen, ob das Item das Plugin-Attribut "mein_plugin_befehl" hat
    if self.has_iattr(item.conf, 'mein_plugin_befehl'):
        befehl = self.get_iattr_value(item.conf, 'mein_plugin_befehl')
        self.add_item(item, config_data_dict={'befehl': befehl})
        self.logger.debug(f'Item {item.property.path} registriert mit Befehl {befehl}')

        # Rückgabe von self.update_item bedeutet:
        # "Wenn dieses Item im System geändert wird, ruf update_item auf"
        return self.update_item

    # Kein passendes Attribut → Item ignorieren
    return None
```

**Was ist `item.conf`?**  
Das ist das Konfigurations-Dictionary des Items. Darin stehen alle Attribute, die in der Item-YAML-Datei definiert wurden — also auch die Plugin-eigenen wie `mein_plugin_befehl`.

**Was macht `has_iattr` / `get_iattr_value`?**  
Diese Hilfsmethoden prüfen bzw. lesen Plugin-Attribute, auch wenn das Plugin in einer Multi-Instanz-Konfiguration läuft (dann heißt das Attribut z. B. `mein_plugin_befehl@instanz1`).

**Was bedeutet `return self.update_item`?**  
Das ist eine *Methodenreferenz* — keine Klammer, kein Aufruf. SmartHomeNG speichert diesen Verweis und ruft die Methode auf, wenn das Item seinen Wert ändert. Ohne dieses Return bekommt das Plugin keine Benachrichtigungen über Item-Änderungen.

> **💡 Hinweis für erfahrene Python-Entwickler**  
> `parse_item` ist nicht auf einen einmaligen Aufruf beim Start beschränkt — es kann auch aufgerufen
> werden, nachdem `run()` bereits läuft (z. B. wenn Items zur Laufzeit neu erzeugt werden). Wer eigene
> Geräte-/Item-Listen in `run()` einmalig aufbaut statt `self.add_item()`/`self.get_item_list()` zu
> nutzen, verpasst solche später hinzukommenden Items — das ist eine bekannte Einschränkung, kein Bug,
> aber bei neuen Plugins sollte `add_item()`/`get_item_list()` bevorzugt werden, um das zu vermeiden.

### `update_item` — Auf Item-Änderungen reagieren

```python
def update_item(self, item, caller=None, source=None, dest=None):
    # Immer zuerst den Basis-Handler aufrufen (behandelt das Pause-Item)
    if self.alive and caller != self.get_shortname():
        befehl = self.get_item_config(item).get('befehl')
        wert = item()   # aktueller Wert des Items
        self.logger.debug(f'Item {item.property.path} → {wert} (Befehl: {befehl})')
        self._sende_an_geraet(befehl, wert)
```

**Erklärung der Parameter:**
- `item` — das Item, das sich geändert hat
- `caller` — Name des Auslösers (z. B. Plugin-Name, `'KNX'`, `'Visu'`, ...)
- `source` — optionale Quelle der Änderung
- `dest` — optionales Ziel

**Warum `caller != self.get_shortname()`?**  
Wenn das Plugin selbst einen Item-Wert setzt (z. B. nach einer Geräte-Antwort), würde `update_item` sonst erneut aufgerufen — eine Endlosschleife. Durch diesen Check werden nur externe Änderungen verarbeitet.

> **💡 Hinweis für erfahrene Python-Entwickler**  
> `SmartPlugin.update_item()` enthält bereits eine Behandlung für das Pause-Item und
> einen Guard für `not self.alive`. Wer `update_item` überschreibt, sollte daher
> `super().update_item(item, caller, source, dest)` aufrufen **oder** diese Logik selbst
> implementieren. `self.get_item_config(item)` gibt das `config_data_dict` zurück, das
> in `parse_item` via `add_item(..., config_data_dict=...)` gespeichert wurde.

### `unparse_item` — Aufräumen bei Plugin-Entladen (optional)

`parse_item()` und `unparse_item()` sind ein symmetrisches Paar: was `parse_item()` beim Registrieren
eines Items an plugin-eigenen Daten anlegt, wird in `unparse_item()` wieder abgebaut.
`remove_item()`/`add_item()` sind dagegen die generischen, **vom Kern verwalteten** Methoden — sie
dürfen **nicht** überschrieben werden (`remove_item()` ruft `unparse_item()` intern bereits auf, siehe
unten).

`unparse_item(item)` muss nur überschrieben werden, wenn das Plugin **eigene** Datenstrukturen jenseits
von `add_item()`/`get_item_list()` für ein Item pflegt (z. B. eine eigene Mapping-Tabelle):

```python
def unparse_item(self, item):
    # Eigene Aufräumarbeiten zuerst
    self._meine_mapping_tabelle.pop(item.property.path, None)
    # Danach immer die Basisklasse aufrufen
    return super().unparse_item(item)
```

**Wichtig:** `super().unparse_item(item)` muss aufgerufen werden, sonst bleibt die in `parse_item()`
über `return self.update_item` registrierte Benachrichtigung für das Item bestehen.
`remove_item()` **nicht** überschreiben — diese Methode ist Teil des generischen Kern-Vertrags
(`add_item`/`remove_item`) und ruft `unparse_item()` bereits an der richtigen Stelle auf. Aktuell wird
das beim Entladen eines Plugins (`unload_plugin`) für jedes registrierte Item ausgelöst — perspektivisch
auch beim Löschen einzelner Items zur Laufzeit. Details zum dahinterliegenden additiven-Hook-Vertrag:
siehe [`ENTWICKLUNGSRICHTLINIEN.md`](ENTWICKLUNGSRICHTLINIEN.md).

---

## 6. Weitere nützliche Methoden

### Periodische Abfrage: `poll_device`

```python
def poll_device(self):
    """Wird zyklisch aufgerufen, wenn per scheduler_add registriert."""
    aktueller_wert = self._lese_vom_geraet()
    for item in self.get_item_list():
        item(aktueller_wert, self.get_shortname())
```

### Scheduler verwalten

```python
# In run(): Abfrage alle 60 Sekunden
self.scheduler_add('abfrage', self.poll_device, cycle=60)

# In stop():
self.scheduler_remove('abfrage')
```

### Item-Werte setzen

```python
# Item-Wert setzen (der zweite Parameter ist der "caller" — immer Plugin-Name angeben)
item(neuer_wert, self.get_shortname())
```

### Logging

SmartHomeNG stellt `self.logger` bereit — ein Standard-Python-Logger:

```python
self.logger.debug('Detailinfo')
self.logger.info('Normaler Betrieb')
self.logger.warning('Mögliches Problem')
self.logger.error('Fehler aufgetreten')
```

---

## 7. Die plugin.yaml — Parameter und Item-Attribute

Die `plugin.yaml` beschreibt das Plugin für SmartHomeNG: Metadaten, konfigurierbare Parameter und die Item-Attribute, die das Plugin versteht.

### Vollständiges Beispiel

```yaml
# plugin.yaml

plugin:
    type: interface                  # gateway | interface | protocol | system | web
    description:
        de: 'Mein Plugin — steuert Gerät XY'
        en: 'My Plugin — controls device XY'
    maintainer: IhrName
    state: develop                   # develop | ready | deprecated
    version: 1.0.0                   # muss mit PLUGIN_VERSION übereinstimmen
    sh_minversion: '1.9.0'
    multi_instance: False            # muss mit ALLOW_MULTIINSTANCE übereinstimmen
    classname: MeinPlugin            # muss mit dem Klassennamen übereinstimmen

parameters:
    host:
        type: str
        mandatory: True
        description:
            de: 'IP-Adresse oder Hostname des Geräts'
            en: 'IP address or hostname of the device'
    port:
        type: int
        default: 80
        description:
            de: 'TCP-Port des Geräts'
            en: 'TCP port of the device'
    passwort:
        type: password
        description:
            de: 'Passwort (wird in der Admin-Oberfläche verborgen)'
            en: 'Password (hidden in admin UI)'

item_attributes:
    mein_plugin_befehl:
        type: str
        description:
            de: 'Gerätebefehl, der mit diesem Item verknüpft wird'
            en: 'Device command linked to this item'
    mein_plugin_lesen:
        type: bool
        default: False
        description:
            de: 'True: Wert vom Gerät lesen, wenn sich das Item ändert'
            en: 'True: read value from device on item change'
```

### Gültige Parametertypen

| Typ | Python-Typ | Beispiel |
|-----|-----------|---------|
| `str` | `str` | `'localhost'` |
| `int` | `int` | `8080` |
| `num` / `float` | `float` | `21.5` |
| `bool` | `bool` | `True` / `False` |
| `list` | `list` | `['a', 'b']` |
| `list(str)` | `list` | Liste von Strings |
| `dict` | `dict` | `{key: value}` |
| `ip` / `ipv4` / `ipv6` | `str` | `'192.168.1.1'` |
| `mac` | `str` | `'AA:BB:CC:DD:EE:FF'` |
| `knx_ga` | `str` | `'1/2/3'` |
| `password` | `str` | Wie `str`, aber in der Admin-UI verborgen |
| `foo` | beliebig | Kein Typcheck |

**Wichtige Regeln:**
- `mandatory: True` und `default:` schließen sich aus — ein Parameter kann nicht gleichzeitig Pflicht und mit Default sein.
- `default:` muss zum deklarierten `type:` passen (ein `default: 'ja'` bei `type: int` ist ein Fehler).
- Fehlende Pflichtparameter verhindern das Laden des Plugins — die Prüfung erfolgt durch `lib.metadata`.

---

## 8. Tests schreiben

SmartHomeNG stellt ein wiederverwendbares Test-Framework für Plugins bereit. Es prüft automatisch die grundlegenden Vertragseigenschaften jedes Plugins.

### 8.1 Minimaler Test (SmartPlugin)

```python
# plugins/mein_plugin/tests/test_mein_plugin.py

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import tests.common as common
common.register_shng_log_levels()

from tests.plugin_contract.base      import BasePluginContractTest
from tests.plugin_contract.with_yaml import YamlPluginContractTest
from plugins.mein_plugin import MeinPlugin


class TestMeinPlugin(BasePluginContractTest, YamlPluginContractTest):
    """Automatische Vertragstests für MeinPlugin."""

    PLUGIN_CLASS       = MeinPlugin
    PLUGIN_INIT_PARAMS = {'host': '127.0.0.1', 'port': 80}

    # Wenn das Plugin zwei Attribute gleichzeitig braucht, um ein Item zu registrieren:
    ITEM_ATTR_SETS = [
        {'mein_plugin_befehl': 'Licht.An', 'mein_plugin_lesen': True},
    ]


if __name__ == '__main__':
    unittest.main()
```

Mit diesem einen Block erhält das Plugin automatisch:
- **~25 Vertragstests** aus `BasePluginContractTest` (Initialisierung, Item-Registry, Lifecycle ...)
- **~8 YAML-Tests** aus `YamlPluginContractTest` (Parametertypprüfung, Konsistenz mit Klassennamen ...)

### 8.2 Eigene Tests hinzufügen

Eigene Tests werden als zusätzliche Methoden in dieselbe Klasse geschrieben:

```python
class TestMeinPlugin(BasePluginContractTest, YamlPluginContractTest):
    PLUGIN_CLASS       = MeinPlugin
    PLUGIN_INIT_PARAMS = {'host': '127.0.0.1'}

    # --- Automatische Vertragstests (von den Mix-ins) ---
    # (keine Änderungen nötig)

    # --- Eigene Tests ---

    def test_verbindungsparameter_gespeichert(self):
        """host und port müssen nach __init__ gespeichert sein."""
        self.assertEqual(self.plugin.host, '127.0.0.1')

    def test_poll_device_setzt_item_wert(self):
        """poll_device() muss den Item-Wert aktualisieren."""
        # Item anlegen und registrieren
        from tests.plugin_contract._mockitem import MockItem
        item = MockItem('licht.an', conf={'mein_plugin_befehl': 'Licht.An'})
        self.plugin.parse_item(item)

        # poll_device aufrufen und Ergebnis prüfen
        self.plugin.poll_device()
        self.assertIsNotNone(item())   # Item sollte einen Wert haben
```

### 8.3 Was die Vertragstests prüfen (Übersicht)

| Tier | Klasse | Prüft |
|------|--------|-------|
| 1 | `BasePluginContractTest` | Pflichtattribute, Initialisierung, Item-Registry, Lifecycle |
| 2 | `YamlPluginContractTest` | plugin.yaml Konsistenz, Parametertypen, Item-Attribute |
| 3 | `MqttPluginContractTest` | MQTT-Subscriptions, Publish, Nachrichtenverarbeitung |
| 4 | `SdpPluginContractTest` | commands.py Struktur, Itemverdrahtung |

### 8.4 Hinweise zu `alive` und `_init_complete`

- `alive` ist nach `__init__` immer `False` — das ist korrekt.  
  Nach einem erfolgreichen `run()` *sollte* `alive` `True` sein, aber das ist nicht erzwungen, wenn das Plugin externe Ressourcen benötigt.
- `_init_complete = False` in `__init__` signalisiert dem Loader, dass das Plugin nicht gestartet werden soll.  
  In Tests führt das dazu, dass die Lifecycle-Tests das Plugin als nicht startbar behandeln.

> **💡 Hinweis für erfahrene Python-Entwickler**  
> Die Test-Mix-ins folgen dem *Test-Mixin-Pattern*: sie erben von `unittest.TestCase`,
> sind aber als Mix-ins konzipiert, die keine eigene `setUp`-Methode überschreiben, wenn
> das vom Untertyp bereits erledigt wird. Bei Mehrfachvererbung (z. B.
> `BasePluginContractTest, YamlPluginContractTest`) gilt MRO — beide `setUp`-Methoden
> werden in der richtigen Reihenfolge aufgerufen, weil `YamlPluginContractTest`
> keinen eigenen Plugin-Fixture anlegt, sondern diesen on-demand erzeugt.
> `make_plugin_instance()` aus `tests.plugin_contract.base` kann auch direkt in eigenen
> Fixtures verwendet werden.

---

## 9. MqttPlugin — Erweiterung für MQTT-Geräte

Plugins, die über MQTT kommunizieren, erben von `MqttPlugin` statt von `SmartPlugin`.
`MqttPlugin` übernimmt den Aufbau und die Verwaltung der MQTT-Verbindung; das Plugin
muss nur Topics abonnieren und veröffentlichen.

### Grundgerüst

```python
from lib.model.mqttplugin import MqttPlugin


class MeinMqttPlugin(MqttPlugin):

    PLUGIN_VERSION    = '1.0.0'
    ALLOW_MULTIINSTANCE = True

    def __init__(self, sh, **kwargs):
        super().__init__()
        # Nach super().__init__() steht self.mod_mqtt bereit
        if not self.mod_mqtt:
            return   # MQTT-Modul nicht geladen — __init_complete__ bereits False

    def run(self):
        # Topics für alle registrierten Items abonnieren
        self.start_subscriptions()
        self.alive = True

    def stop(self):
        self.alive = False
        # Alle Subscriptions beenden
        self.stop_subscriptions()

    def parse_item(self, item):
        if self.has_iattr(item.conf, 'mqtt_topic'):
            topic = self.get_iattr_value(item.conf, 'mqtt_topic')
            # Topic abonnieren; bei eingehender Nachricht: item(payload)
            self.add_subscription(topic, payload_type='str', item=item)
            self.add_item(item, config_data_dict={'topic': topic})
            return self.update_item

    def update_item(self, item, caller=None, source=None, dest=None):
        if self.alive and caller != self.get_shortname():
            topic = self.get_item_config(item).get('topic')
            # Item-Wert auf das MQTT-Topic veröffentlichen
            self.publish_topic(topic, item(), item=item)
```

### Wichtige MqttPlugin-Methoden

| Methode | Wann aufrufen | Beschreibung |
|---------|--------------|-------------|
| `start_subscriptions()` | In `run()` | Alle registrierten Topics abonnieren |
| `stop_subscriptions()` | In `stop()` | Alle Subscriptions beenden |
| `add_subscription(topic, payload_type, item, callback)` | In `parse_item()` | Topic registrieren |
| `publish_topic(topic, payload, item, qos, retain)` | In `update_item()` | Nachricht senden |

### Tests für MqttPlugin

```python
from tests.plugin_contract.base import BasePluginContractTest
from tests.plugin_contract.mqtt import MqttPluginContractTest
from plugins.mein_mqtt_plugin import MeinMqttPlugin

class TestMeinMqttPlugin(BasePluginContractTest, MqttPluginContractTest):
    PLUGIN_CLASS       = MeinMqttPlugin
    PLUGIN_INIT_PARAMS = {}
```

`MqttPluginContractTest` simuliert das MQTT-Modul automatisch — es wird kein echter Broker benötigt.

> **💡 Hinweis für erfahrene Python-Entwickler**  
> `MqttPlugin.__init__()` ruft `Modules.get_instance().get_module('mqtt')` auf.
> Der Test-Fixture patcht `lib.module.Modules.get_instance` so, dass ein `MockMqttModule`
> zurückgegeben wird, das `subscribe_topic`, `unsubscribe_topic` und `publish_topic` aufzeichnet.
> Eigene Callback-Funktionen (statt des Default-Handlers `_on_mqtt_message`) können in
> `add_subscription(..., callback=mein_callback)` übergeben werden. Der Default-Handler
> setzt den Item-Wert direkt: `item(payload, self.get_shortname())`.

---

## 10. SmartDevicePlugin — Erweiterung für Geräteprotokolle

`SmartDevicePlugin` (SDP) ist eine leistungsstarke Basisklasse für Plugins, die
netzwerk- oder seriell angebundene Geräte ansprechen. Die komplette Verbindungs- und
Protokollverwaltung ist eingebaut; das Plugin muss hauptsächlich nur die Befehlstabelle
in einer separaten `commands.py` definieren.

### Wann SmartDevicePlugin verwenden?

- Gerät kommuniziert über TCP (Anfrage/Antwort oder asynchron), UDP oder serielle Verbindung
- Gerät hat eine feste Befehlsstruktur (Opcodes, Antwortmuster)
- Werte müssen zwischen Gerät-Format und SmartHomeNG-Item-Typ konvertiert werden

### Verzeichnisstruktur eines SDP-Plugins

```
plugins/
└── mein_sdp_plugin/
    ├── __init__.py        ← Hauptklasse (erbt von SmartDevicePlugin)
    ├── commands.py        ← Befehlstabelle
    ├── datatypes.py       ← (optional) eigene Datentypkonverter
    └── plugin.yaml
```

### commands.py — Befehlstabelle

```python
# commands.py
commands = {
    'Licht': {
        'An': {
            'opcode':    '0x01',
            'read':      True,
            'write':     True,
            'item_type': 'bool',
            'dev_datatype': 'DT_Bool',
        },
        'Helligkeit': {
            'opcode':    '0x02',
            'read':      True,
            'write':     True,
            'item_type': 'num',
            'dev_datatype': 'DT_Byte',
        },
    },
}
```

### Minimale Plugin-Klasse

```python
from lib.model.smartdeviceplugin import SmartDevicePlugin

class MeinSdpPlugin(SmartDevicePlugin):

    PLUGIN_VERSION    = '1.0.0'
    ALLOW_MULTIINSTANCE = True

    def __init__(self, sh, **kwargs):
        super().__init__(sh, **kwargs)
        # Verbindungsparameter (host, port etc.) werden von SDP automatisch
        # aus plugin.yaml gelesen — kein eigenes Auslesen nötig

    def run(self):
        # SDP übernimmt den Verbindungsaufbau
        super().run()        # WICHTIG
        self.alive = True

    def stop(self):
        self.alive = False
        super().stop()       # WICHTIG
```

### Item-Attribute in plugin.yaml für SDP

SDP verwendet einen konfigurierbaren Attribut-Präfix (Standard: `ex`):

```yaml
item_attributes:
    ex_command:
        type: str
        description:
            de: 'Gerätebefehl (z. B. "Licht.An")'
    ex_read:
        type: bool
        description:
            de: 'True: Wert beim Start lesen'
    ex_write:
        type: bool
        description:
            de: 'True: Item-Änderungen an Gerät schicken'
```

### Tests für SmartDevicePlugin

```python
from tests.plugin_contract.base import BasePluginContractTest
from tests.plugin_contract.sdp  import SdpPluginContractTest
from plugins.mein_sdp_plugin import MeinSdpPlugin

class TestMeinSdpPlugin(BasePluginContractTest, SdpPluginContractTest):
    PLUGIN_CLASS       = MeinSdpPlugin
    PLUGIN_INIT_PARAMS = {'host': '127.0.0.1', 'port': 2101}
    SDP_ITEM_ATTR_SETS = [
        {'ex_command': 'Licht.An', 'ex_write': True},
        {'ex_command': 'Licht.Helligkeit', 'ex_read': True},
    ]
```

`SdpPluginContractTest` verwendet automatisch `conn_type: ''` (Null-Verbindung), damit kein echtes Gerät benötigt wird.

> **💡 Hinweis für erfahrene Python-Entwickler**  
> SDP trennt Verbindung, Protokoll und Befehlsverarbeitung in drei unabhängige Schichten:
> `SDPConnection` (Transport), `SDPProtocol` (Framing) und `SDPCommands`/`SDPCommand`
> (Datentransformation). Eigene Datentypkonverter erben von `SDPDataType` und werden
> in `commands.py` via `dev_datatype: 'DT_MeinTyp'` referenziert.
> `reply_pattern` in der Befehlsdefinition ist ein regulärer Ausdruck; Capture Groups
> werden als Gerätewert interpretiert. Lookup-Tabellen (`lookup`) übersetzen zwischen
> Gerätecodes und Item-Werten bidirektional.
> `CONN_NULL` (leerer String) erzeugt eine Stub-Verbindung ohne echten Transport —
> ideal für Unit-Tests von Konvertierungslogik.

---

## 11. Checkliste vor dem ersten Push

Vor dem ersten Commit ins Plugin-Repository alle Punkte abhaken:

### plugin.yaml
- [ ] `classname` stimmt mit dem Python-Klassennamen überein
- [ ] `version` stimmt mit `PLUGIN_VERSION` im Code überein
- [ ] `multi_instance` stimmt mit `ALLOW_MULTIINSTANCE` überein
- [ ] Alle `mandatory: True`-Parameter haben **kein** `default`
- [ ] Alle `default`-Werte passen zum deklarierten `type`
- [ ] Beschreibungen auf Deutsch und Englisch vorhanden

### Python-Code
- [ ] `super().__init__()` ist der **erste** Aufruf in `__init__`
- [ ] `run()` setzt `self.alive = True`
- [ ] `stop()` setzt `self.alive = False`
- [ ] Alle in `run()` angelegten Scheduler werden in `stop()` entfernt
- [ ] `update_item` enthält den `caller != self.get_shortname()`-Guard
- [ ] Falls das Plugin eigene Item-Datenstrukturen jenseits von `add_item()` pflegt: `unparse_item()`
  überschrieben, inkl. `super().unparse_item()`-Aufruf (nicht `remove_item()` überschreiben)

### Tests
- [ ] Datei `plugins/mein_plugin/tests/test_mein_plugin.py` existiert
- [ ] `BasePluginContractTest` ist eingebunden
- [ ] Falls plugin.yaml vorhanden: `YamlPluginContractTest` eingebunden
- [ ] `venvs/shng/bin/pytest` läuft ohne Fehler durch

### Code-Qualität
- [ ] `venvs/shng/bin/ruff check plugins/mein_plugin/` gibt keine Fehler
- [ ] Keine `print()`-Aufrufe — stattdessen `self.logger.*` verwenden

### Git-Hooks (einmalig pro Klon)
```bash
tools/install-hooks.sh
```
Das Skript fragt, ob die Hooks für **core**, **plugins** oder **beide** Repos eingerichtet werden sollen.
Details zu den einzelnen Checks und zur Bypass-Option: → Abschnitt 12.

---

## 12. Code-Qualitäts-Gates: Hooks und CI

SmartHomeNG setzt auf ein zweistufiges Sicherheitsnetz aus lokalen Git-Hooks und GitHub Actions CI.

| Zeitpunkt      | Hook / CI              | Was passiert                                                        |
|----------------|------------------------|---------------------------------------------------------------------|
| `git commit`   | pre-commit             | Staged `.py`-Dateien werden mit `ruff format` formatiert (auto) und mit `ruff check` geprüft (Hard Gate) |
| `git push`     | pre-push               | `pytest` läuft vollständig (Hard Gate)                              |
| Pull Request   | GitHub Actions         | ruff + pytest in CI — Ergebnis ist verpflichtend                    |

### Was die Hooks konkret tun

**pre-commit**

Nur **gestaged** Dateien (`.py`) werden verarbeitet. Ablauf:

1. `ruff format` formatiert die Dateien automatisch und legt die Änderungen nach.
   Kein manuelles `git add` nötig — das übernimmt der Hook.
2. `ruff check` prüft dieselben Dateien. Gibt es Lint-Fehler, wird der Commit abgebrochen
   und die betroffenen Stellen werden aufgelistet.

**pre-push** (shng core)

`pytest tests/` läuft vollständig. Ein fehlschlagender Test blockiert den Push.

**pre-push** (plugins, opt-in)

`pytest` läuft aus dem Plugin-Verzeichnis. Ein fehlschlagender Test blockiert den Push.

### Hooks installieren

```bash
tools/install-hooks.sh
```

Das Skript fragt interaktiv:

```
Install hooks for:
  c) shng core only
  p) plugins only
  b) both (default)
```

Für den **core** wird `git config core.hooksPath .githooks` gesetzt — die Hooks liegen
versioniert im Repo unter `.githooks/`.

Für **plugins** werden die Hooks direkt in `.git/hooks/` des Plugin-Repos geschrieben.
Das Plugin-Repo versioniert keine Hooks; sie sind vollständig **opt-in**.

### Bypass (nur im Notfall)

```bash
git commit --no-verify    # überspringt pre-commit (Format + Lint)
git push --no-verify      # überspringt pre-push (Tests)
```

**Achtung:** Die CI-Checks in GitHub Actions laufen immer — auch wenn die Hooks lokal
übersprungen wurden. Lint-Fehler oder fehlschlagende Tests blockieren den Merge des PR.

### Plugins: opt-in und CI

Im Plugins-Repo sind Hooks optional. Wer ohne Hooks arbeiten möchte, kann das tun —
die CI-Prüfung ist trotzdem verbindlich. Wer die Hooks installieren möchte:

```bash
# Im shng-Verzeichnis:
tools/install-hooks.sh
```

---

*Dieses Dokument ist Teil des SmartHomeNG-Projekts und wird bei Bedarf aktualisiert.*
