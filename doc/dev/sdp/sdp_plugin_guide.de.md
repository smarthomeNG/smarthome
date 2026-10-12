# Ein Geräte-Plugin mit SmartDevicePlugin (SDP) 2.0 schreiben

*English version: [`sdp_plugin_guide.md`](sdp_plugin_guide.md)*

Zielgruppe: Plugin-Autoren. Du kennst den Aufbau eines SmartHomeNG-Plugins
(`plugin.yaml`, `__init__.py`, Items) und willst ein Gerät anbinden, das ein
Kommando/Antwort-Protokoll spricht. Wie SDP intern funktioniert, steht in
[`sdp_architecture.md`](sdp_architecture.md) (englisch); ein vollständiges
Beispiel in [`sdp_commands_tutorial.de.md`](sdp_commands_tutorial.de.md).

Inhalt

1. [Ist SDP die richtige Basis?](#1-ist-sdp-die-richtige-basis)
2. [Aufbau eines SDP-Plugins](#2-aufbau-eines-sdp-plugins)
3. [Die Plugin-Klasse: Deklarationen](#3-die-plugin-klasse-deklarationen)
4. [plugin.yaml](#4-pluginyaml)
5. [Referenz commands.py](#5-referenz-commandspy)
6. [Kommandoklassen](#6-kommandoklassen)
7. [Datentypen](#7-datentypen)
8. [Lookups](#8-lookups)
9. [Modelle](#9-modelle)
10. [Das Lese-/Schreibmodell](#10-das-lese-schreibmodell)
11. [Hooks: Gerätelogik ergänzen](#11-hooks-gerätelogik-ergänzen)
12. [Template-Werte zur Laufzeit](#12-template-werte-zur-laufzeit)
13. [Mehrere Geräte hinter einer Verbindung (Custom Tokens)](#13-mehrere-geräte-hinter-einer-verbindung-custom-tokens)
14. [Item-Structs erzeugen](#14-item-structs-erzeugen)
15. [Tests](#15-tests)
16. [Ein SDP-1.x-Plugin auf 2.0 migrieren](#16-ein-sdp-1x-plugin-auf-20-migrieren)
17. [Checkliste und Stolperfallen](#17-checkliste-und-stolperfallen)

---

## 1. Ist SDP die richtige Basis?

SDP passt, wenn:

- eine Plugin-Instanz über eine Verbindung spricht (TCP, HTTP, UDP, seriell),
- das Geräteprotokoll aus Kommandos besteht, die jeweils einen Wert lesen
  und/oder schreiben,
- Antworten (oder unaufgeforderte Meldungen) sich per regulärem Ausdruck,
  JSON-RPC-Id oder Anfrage/Antwort-Abfolge zuordnen lassen.

SDP passt nicht, oder nur mit viel eigenem Code, wenn eine Instanz viele
Geräte mit Discovery und Zustand pro Host verwaltet (z. B.
`plugins/yamahayxc`), wenn Werte als große Dokumente ankommen, die strukturell
verarbeitet werden müssen (Cloud-APIs, Browse-Bäume), oder wenn
Authentifizierungsabläufe dominieren.

## 2. Aufbau eines SDP-Plugins

```
plugins/<name>/
    __init__.py      Plugin-Klasse: Deklarationen, optional Hooks (oft < 20 Zeilen)
    commands.py      Kommandos, Lookups, optional Modelle / item_templates   (Pflicht)
    datatypes.py     eigene DT_*-Wertkonverter                                (optional)
    protocol.py      eigene SDPProtocol-Unterklasse                           (optional, selten)
    plugin.yaml      Metadaten, Parameter, Item-Attribute, erzeugte item_structs
    tests/           Characterization-, Contract-, Verhaltenstests
    webif/           optionales Web-Interface
```

Ein vollständiges echtes Plugin, `plugins/epson/__init__.py`, ohne
Lizenzkopf und Standalone-Boilerplate:

```python
from lib.model.sdp.command import SDPCommandParseStr
from lib.model.sdp.declarations import TransportRule
from lib.model.sdp.globals import CONN_SER_ASYNC
from lib.model.smartdeviceplugin import SmartDevicePlugin, Standalone


class epson(SmartDevicePlugin):
    """Device class for Epson projectors."""

    PLUGIN_VERSION = '1.0.0'

    TRANSPORTS = (TransportRule(CONN_SER_ASYNC, requires='serialport'),)
    COMMAND_CLASS = SDPCommandParseStr
    LINE_TERMINATED = True
```

Die Standalone-Boilerplate (Anfang von `__init__.py`, aus
`dev/sample_smartdevice_plugin/__init__.py` kopieren) setzt
`builtins.SDP_standalone` und erlaubt, die Datei direkt auszuführen, um Structs
zu erzeugen:

```python
import builtins
import os
import sys

if __name__ == '__main__':
    builtins.SDP_standalone = True

    class SmartPlugin:
        pass

    class SmartPluginWebIf:
        pass

    BASE = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-3])
    sys.path.insert(0, BASE)

elif not hasattr(builtins, 'SDP_standalone'):
    builtins.SDP_standalone = False

# ... Imports und Klasse ...

if __name__ == '__main__':
    s = Standalone(MyPlugin, sys.argv[0])
```

Die Bedingung `elif not hasattr(...)` ist wichtig: Beim Laden von
`commands.py` wird das Paket ein zweites Mal unter seinem Paketnamen
importiert; ein dort mit `False` überschriebenes `True` legt den
Standalone-Modus lahm.

## 3. Die Plugin-Klasse: Deklarationen

Gerätevorgaben sind Klassenattribute (`lib/model/smartdeviceplugin.py`):

| Attribut | Typ | Standard | Bedeutung |
|---|---|---|---|
| `TRANSPORTS` | `tuple[TransportRule, ...]` | `()` | Wahl des Transports; die erste passende Regel gewinnt |
| `PROTOCOL` | Typname oder Klasse | `None` | Protokoll, das den Transport umhüllt (`PROTO_JSONRPC`, `PROTO_RESEND` oder eigene Klasse) |
| `COMMAND_CLASS` | Klasse oder Klassenname in `lib.model.sdp.command` | `None` → `SDPCommand` | wie Kommandos Payloads bauen und Antworten auswerten |
| `LINE_TERMINATED` | bool | `False` | Parameter `terminator` an jede Payload anhängen und Antworten bis dahin lesen |
| `JSON_MOVE_KEYS` | `tuple[str, ...]` | `()` | nur JSON-RPC: Kwargs pro Sendung, die in die `params` der Anfrage verschoben werden |
| `CUSTOM_TOKEN` | `CustomTokenSpec` | `None` | mehrere Geräte hinter einer Verbindung, siehe Abschnitt 13 |

`TransportRule(use, requires=None)`: `use` ist ein Verbindungstyp
(`CONN_NET_TCP_CLI`, `CONN_NET_TCP_REQ`, `CONN_NET_UDP_SRV`, `CONN_SER_DIR`,
`CONN_SER_ASYNC`, `CONN_NULL`) oder eine Verbindungsklasse; `requires` nennt
den Plugin-Parameter, der gesetzt sein muss.

```python
TRANSPORTS = (
    TransportRule(CONN_NET_TCP_CLI, requires='host'),
    TransportRule(CONN_SER_ASYNC, requires='serialport'),
)
```

- `host` und `serialport` beide konfiguriert → die erste Regel gilt, Warnung.
- Keiner von beiden → Fehler „none of ['host', 'serialport'] is configured“,
  Plugin deaktiviert. `TransportRule(CONN_NULL)` nur dann als letzte Regel
  ergänzen, wenn das Plugin auch ohne Gerät laden soll (Beispiel-Plugin).
- Ein in `etc/plugin.yaml` gesetztes `conn_type` wird mit Warnung ignoriert.

Welcher Transport für welches Gerät:

| Gerät spricht | Transport | Antworten kommen |
|---|---|---|
| dauerhafter TCP-Socket, Zeilen- oder Bytestrom | `CONN_NET_TCP_CLI` | asynchron per Callback; verbindet sich selbst neu |
| HTTP-Anfrage/Antwort | `CONN_NET_TCP_REQ` | als Rückgabewert der Anfrage |
| HTTP + UDP-Push-Meldungen | `CONN_NET_UDP_SRV` | Rückgabewert der Anfrage + UDP-Callback |
| seriell, strikt Anfrage → Antwort | `CONN_SER_DIR` | als Rückgabewert, gelesen bis `limit_response` |
| seriell, Gerät sendet auch von sich aus | `CONN_SER_ASYNC` | asynchron über Lese-Thread |

Asynchrone Transporte bedeuten: Eine Antwort ist nicht mit ihrer Anfrage
verknüpft. SDP erkennt das Kommando am Antworttext über `reply_pattern`
(Abschnitt 5).

## 4. plugin.yaml

### Abschnitt plugin

```yaml
plugin:
    ...
    sdp_minversion: '2.0.0'     # in Anführungszeichen; bei älterem SDP wird das Plugin nicht geladen
    suspendable: true           # SDP implementiert Suspend/Resume
    classname: MyPlugin
```

### Parameter, die SDP liest

SDP sieht nur Parameter, die deine `plugin.yaml` deklariert (die Metadaten
verwerfen nicht deklarierte). Deklariere also, was dein Gerät braucht, mit
sinnvollen Standardwerten.

| Parameter | Standard, wenn nicht deklariert | Zweck |
|---|---|---|
| `host`, `port` | — / 0 | Netzwerkziel; `host` wählt Netzwerk-Regeln |
| `serialport`, `baudrate`, `bytesize`, `parity`, `stopbits` | — / 9600 / 8 / N / 1 | serielle Einstellungen |
| `terminator` | `''` | Zeilenende für `LINE_TERMINATED`; `"\r"` / `"\n"` in doppelten Anführungszeichen schreiben |
| `timeout` | 1.0 | Lese-Timeout des Transports (s) |
| `binary` | False | serielle Transporte liefern `bytes` statt `str` |
| `autoreconnect` | Transporte: True; vom Plugin geplanter Reconnect: aus | nach Verbindungsverlust neu verbinden — explizit deklarieren |
| `autoconnect` | Wert von `autoreconnect` (False, wenn dieser nicht deklariert ist) | beim Senden bei Bedarf verbinden |
| `connect_retries`, `connect_cycle` | 3, 5 | Versuche pro Runde, Sekunden dazwischen |
| `retry_cycle` | 30 | Sekunden zwischen Runden (TCP-Client) |
| `retry_suspend` | 0 | fehlgeschlagene Runden, bis das Plugin sich selbst suspendiert (TCP-Client; 0 = nie) |
| `send_retries`, `send_retries_cycle` | 0, 1 | unbeantwortete Kommandos erneut senden; `> 0` ohne `PROTOCOL` wählt das Resend-Protokoll |
| `send_timeout` | 5 | JSON-RPC: Sekunden, bis eine unbeantwortete Nachricht erneut gesendet wird |
| `model` | — | wählt ein Modell aus `commands.py` (Abschnitt 9) |
| `cycle` | — | pluginweiter Zyklus für Items mit `x_read_cyclic` |
| `delay_initial_read` | 0 | Sekunden nach dem Verbinden bis zum initialen Lesen (mindestens 1) |
| `resume_initial_read` | — | initiales Lesen nach jedem Reconnect/Resume wiederholen |
| `suspend_item` | — | Item-Pfad, der den Suspend-Modus schaltet |
| `recursive_custom` | — | Index (oder Liste) der Custom-Attribute, die Kind-Items erben |
| `loop_guard_count`, `loop_guard_window`, `loop_guard_source` | 0, 5, '' | unterdrückt einen Schreibvorgang, der `count`-mal innerhalb von `window` s wiederholt wird (nur Caller, die mit `source` beginnen, falls gesetzt) |

`conn_type`, `protocol` und `command_class` in neuen Plugins nicht
deklarieren; die Deklarationen ersetzen sie.

### Item-Attribute

SDP findet deine Item-Attribute am **Suffix**; das Präfix wählst du (`ex_`,
`denon_`, …). Deklariere die unterstützten Attribute unter `item_attributes`:

| Suffix | Typ | Wirkung |
|---|---|---|
| `_command` | str | bindet das Item an ein Kommando; das Item erhält die Werte dieses Kommandos |
| `_read` | bool | das Item fordert seinen Wert an (initial, zyklisch, Gruppenlesen) — Kommando muss lesbar sein |
| `_write` | bool | Item-Änderungen werden gesendet — Kommando muss schreibbar sein |
| `_read_group` | list(str) | Lesegruppen, zu denen das Kommando des Items gehört |
| `_read_cycle` | num | Intervall für zyklisches Lesen in Sekunden |
| `_read_cyclic` | bool | zyklisches Lesen mit dem pluginweiten `cycle` |
| `_read_initial` | bool | beim Verbinden lesen |
| `_readafterwrite` | num | das Kommando so viele Sekunden nach einem Schreibvorgang erneut lesen |
| `_read_group_trigger` | str | Setzen des Items liest die Gruppe; `0` liest alle lesbaren Kommandos |
| `_lookup` | str | Item enthält die Lookup-Tabelle `name[#fwd\|rev\|rci\|list]`; ein `fwd`-Item kann beschrieben werden, um die Tabelle zu ersetzen |
| `_valid_list` | str | Item enthält die valid_list des genannten Kommandos; Beschreiben ersetzt die Liste |
| `_custom1` … `_custom3` | str | freie Werte für dein Plugin; Custom Tokens (Abschnitt 13) |

Den vollständigen Block aus `dev/sample_smartdevice_plugin/plugin.yaml`
kopieren und anpassen.

## 5. Referenz commands.py

`commands.py` ist ein normales Python-Modul. SDP liest diese Namen auf
Modulebene:

| Name | Pflicht | Inhalt |
|---|---|---|
| `commands` | ja | der Kommandobaum |
| `lookups` | nein | Übersetzungstabellen (Abschnitt 8) |
| `models` | nein | Kommandolisten pro Modell (Abschnitt 9) |
| `item_templates` | nein | Attributsätze, die der Struct-Generator einfügen kann |

### Kommandobaum

Kommandos sind Dicts; beliebig verschachtelte Abschnitts-Dicts gruppieren sie.
Der Kommandoname ist der Pfad mit Punkten: `{'zone1': {'control': {'power':
{...}}}}` definiert `zone1.control.power`.

**`item_type` kennzeichnet ein Kommando.** Ein Dict mit `item_type` ist ein
Kommando; ein Dict ohne ist ein Abschnitt, dessen Dict-Werte SDP zu
`abschnitt.kind` abflacht. Fehlt `item_type` bei einem Kommando, werden seine
Dicts `cmd_settings`, `params` oder `item_attrs` zu unsinnigen Kommandos.
`item_type` immer setzen.

### Schlüssel eines Kommandos

| Schlüssel | Standard | Bedeutung |
|---|---|---|
| `read` | `True` | der Wert kann vom Gerät angefordert werden |
| `write` | `False` | Item-Werte können an das Gerät gesendet werden |
| `opcode` | `''` | Payload für Lesen und Schreiben, wenn `read_cmd` / `write_cmd` fehlen |
| `read_cmd` | — | Payload zum Lesen |
| `write_cmd` | — | Payload zum Schreiben |
| `item_type` | `'bool'` | shng-Itemtyp; kennzeichnet das Dict als Kommando; vom Struct-Generator genutzt |
| `dev_datatype` | `'raw'` | `DT_`-Klasse für die Wertumwandlung (`'int'` → `DT_int`); unbekannt → Fehlerlog, `DT_raw` |
| `reply_pattern` | — | Regex (oder Liste), die Antworten dieses Kommandos erkennt; Platzhalter siehe unten |
| `cmd_settings` | — | Wertprüfungen beim Schreiben (siehe unten) |
| `lookup` | — | Name der Lookup-Tabelle (Abschnitt 8); schaltet `cmd_settings`-Prüfungen ab |
| `params` | — | `SDPCommandJSON`: JSON-RPC-Params; `SDPCommandViessmann`: Kodierungsparameter |
| `custom_disabled` | `False` | Kommando von der Custom-Token-Behandlung ausnehmen |
| `send_retries` | — | Überschreibt `send_retries` für dieses Kommando (Resend-Protokoll) |
| `item_attrs` | — | Anweisungen für den Struct-Generator (Abschnitt 14); keine Wirkung zur Laufzeit |
| `param_values` | — | wird akzeptiert, von keiner Kommandoklasse verwendet |

`read` und `write` bei jedem Kommando explizit setzen; `read` ist
standardmäßig `True`.

### reply_pattern

Empfangene Daten ohne bekanntes Kommando (asynchrone Transporte,
Push-Meldungen) werden mit `re.search` gegen die `reply_pattern` **aller**
Kommandos geprüft. Jedes passende Kommando erhält die Daten. Daher:

- Muster verankern (`^…$`) und über alle Kommandos eindeutig halten;
- `'*'` steht für `read_cmd` (sonst `opcode`) des Kommandos, unverändert als
  Regex verwendet;
- mit `SDPCommandParseStr` extrahiert genau eine Capture-Gruppe den Wert; ohne
  Gruppe geht die ganze Antwort an den Datentyp; mehr als eine ist ein Fehler.
  `(?:…)` gruppiert ohne Capture.

Platzhalter, die beim Laden der Kommandos ersetzt werden (und erneut, wenn
sich ein Lookup oder eine valid_list ändert):

| Platzhalter | Ersetzt durch |
|---|---|
| `{LOOKUP}` | `(k1\|k2\|…)` — die escapten geräteseitigen Schlüssel der Lookup-Tabelle des Kommandos (eine Capture-Gruppe) |
| `{VALID_LIST}` | `(v1\|v2\|…)` aus `cmd_settings['valid_list']` |
| `{VALID_LIST_CI}` | dasselbe, ohne Beachtung der Groß-/Kleinschreibung |
| `{VALID_LIST_RE}` | `(re1\|re2\|…)` aus `valid_list_re` |
| `{CUSTOM_PATTERN1..3}` | `CUSTOM_TOKEN.reply_re` für diesen Index |
| `{PARAM:name}` | `template_vars['name']` beim Laden der Kommandos — vor `_post_init()`, also praktisch der Plugin-Parameter |

### cmd_settings (Prüfungen beim Schreiben)

Gilt für geschriebene Werte, wenn das Kommando kein `lookup` hat. Nur der erste
vorhandene Eintrag aus `valid_list_ci`, `valid_list`, `valid_list_re` oder der
Min/Max-Gruppe wird angewandt.

| Schlüssel | Wirkung |
|---|---|
| `valid_list` | Wert muss in der Liste stehen |
| `valid_list_ci` | dasselbe, ohne Beachtung der Groß-/Kleinschreibung |
| `valid_list_re` | Wert muss einen der Regexe per `fullmatch` erfüllen |
| `valid_min`, `valid_max` | außerhalb → Schreiben abgelehnt |
| `force_min`, `force_max` | außerhalb → auf die Grenze gesetzt |

Min/Max-Schlüssel werden in der Reihenfolge `valid_min`, `valid_max`,
`force_min`, `force_max` geprüft: Ein Wert außerhalb einer `valid_*`-Grenze
wird abgelehnt, bevor eine `force_*`-Grenze ihn begrenzen könnte. Pro Seite
entweder `valid_*` oder `force_*` verwenden (der Kommentar „precedence over
min“ in der Beispiel-`commands.py` stimmt nicht mit dem Code überein).

Ein abgelehnter Schreibvorgang setzt das Item auf seinen vorherigen Wert
zurück.

## 6. Kommandoklassen

| Klasse | Payload | Ersetzungen in `opcode` / `read_cmd` / `write_cmd` | Antwortwert |
|---|---|---|---|
| `SDPCommand` | Kommandostring unverändert; `data` = DT-Wert | keine | `DT.get_shng_data(antwort)` |
| `SDPCommandStr` | ausgewerteter String; Request-Argumente aus `template_vars` | `{OPCODE}`, `{VALUE}`, `{PARAM:x}`, `{CUSTOM_PARAMn:x}`, `{CUSTOM_ATTRn}` | `DT.get_shng_data(antwort)` (bytes dekodiert) |
| `SDPCommandParseStr` | ausgewerteter String, danach `str.format()` | wie `SDPCommandStr`, beim Schreiben zusätzlich `{RAW_VALUE}`, `{RAW_VALUE_UPPER}`, `{RAW_VALUE_LOWER}`, `{RAW_VALUE_CAP}` | Capture-Gruppe von `reply_pattern` → DT |
| `SDPCommandJSON` | JSON-RPC-Methode; `data` = `params` | in `params`: `'{VALUE}'`, `'{CUSTOM_ATTRn}'`, `'{ID}'` / Schlüssel `playerid` aus dem Kwarg `playerid` der Sendung, Tupel = eval-Ausdruck | `DT.get_shng_data(antwort['result'])` |
| `SDPCommandViessmann` | Opcode; `data` = `params`-Dict | `'VAL'`, Tupel = eval-Ausdruck | DT mit `len`/`mult`/`signed` |

Hinweise:

- `{VALUE}` ist der vom Datentyp umgewandelte Wert
  (`str(DT.get_send_data(v))`); `{RAW_VALUE*}` ist der unveränderte
  Item-Wert.
- `SDPCommandParseStr` wendet `str.format()` auf Schreibkommandos an:
  Geschweifte Klammern im Text müssen verdoppelt werden (`{{`, `}}`).
- `SDPCommandStr` fügt `request_method`, `params`, `headers`, `data`,
  `cookies`, `files` aus `template_vars` (Parameter oder Laufzeitwerte) jedem
  `data_dict` hinzu — so bekommen HTTP-Geräte Header oder POST-Bodies.
- Tupelwerte in `params` werden mit eingesetztem Item-Wert per `eval()`
  ausgeführt. Alles, was das Item beschreiben kann, kann Code einschleusen;
  siehe die Warnung in `dev/sample_smartdevice_plugin/commands.py`.

## 7. Datentypen

Generische Klassen in `lib/model/sdp/datatypes.py`: `DT_raw` (unverändert),
`DT_none`, `DT_bool`, `DT_int`, `DT_num`, `DT_str`, `DT_list`, `DT_dict`,
`DT_tuple`, `DT_bytes`, `DT_bytearray`, `DT_json`, `DT_webservices`.

`DT_bool` nutzt Pythons Wahrheitswert: Der Gerätestring `'0'` wird `True`.
Geräte, die `0`/`1`, `ON`/`OFF` usw. senden, brauchen einen eigenen Datentyp.

Eigene Datentypen gehören nach `<plugin>/datatypes.py`; jede `DT_*`-Klasse
dort wird eingelesen und ohne Präfix referenziert (`'dev_datatype':
'onoff'`). Beispiel aus `plugins/epson/datatypes.py`:

```python
import lib.model.sdp.datatypes as DT


class DT_onoff(DT.Datatype):
    def get_send_data(self, data, **kwargs):
        return 'ON' if data else 'OFF'

    def get_shng_data(self, data, type=None, **kwargs):
        return False if data == '0' else True if data == '1' else None
```

`get_send_data(wert)` wandelt Item → Gerät, `get_shng_data(daten)` Gerät →
Item. Bei nicht umwandelbaren Eingaben eine Exception werfen; SDP loggt sie
und verwirft den Wert.

## 8. Lookups

Eine Lookup-Tabelle bildet Gerätewerte auf Item-Werte ab:

```python
lookups = {
    'INPUT': {'CD': 'CD', 'TUNER': 'Radio', 'SAT/CBL': 'TV'},
}
```

- Empfangen: Der Antwortwert wird vorwärts nachgeschlagen (Gerät → Item).
- Senden: Der Item-Wert wird rückwärts nachgeschlagen, ohne Beachtung der
  Groß-/Kleinschreibung; ein Wert, der bereits ein Geräteschlüssel ist, wird
  unverändert gesendet.
- `'reply_pattern': '^SI{LOOKUP}$'` passt nur auf bekannte Gerätewerte.
- Items können eine Tabelle enthalten: `x_lookup: INPUT` (Vorwärts-Dict),
  `INPUT#rev`, `INPUT#rci` (kleingeschriebenes Rückwärts-Dict), `INPUT#list`
  (Item-Werte, z. B. für eine Auswahlliste in der Visu). Ein neues Dict im
  Vorwärts-Item ersetzt die Tabelle zur Laufzeit (`update_lookup()`),
  einschließlich aller abgeleiteten Items und Reply-Patterns.
- Mit Modellen: `{'ALL': {...Tabellen...}, 'model1': {...Abweichungen...}}`.

## 9. Modelle

Der Parameter `model` wählt einen Kommandosatz. Zwei Varianten:

1. `commands` hat auf oberster Ebene den Schlüssel `'ALL'` (gemeinsame
   Kommandos) und je einen Schlüssel pro Modell; die Kommandos des Modells
   werden über `ALL` gelegt. Ein konfiguriertes Modell, das weder in
   `commands`, `lookups` noch `structs` vorkommt, stoppt das Plugin.
2. `commands` ohne `ALL`, dazu ein Dict `models`, das pro Modell
   Kommandopfade (oder Abschnittspräfixe) auflistet, optional mit `'ALL'` für
   gemeinsame. Ein in `models` fehlendes konfiguriertes Modell stoppt das
   Plugin; ebenso ein konfiguriertes Modell, wenn `commands.py` weder `ALL`
   noch `models` hat.

Ohne `model` werden alle Kommandos geladen. Die drei kommentierten Varianten
stehen in `dev/sample_smartdevice_plugin/commands.py` (deren Hinweis, ein
Modell ohne `models`-Dict lade alle Kommandos, stimmt nicht mit dem Code
überein).

## 10. Das Lese-/Schreibmodell

- `read` / `write` beschreiben, was das **Gerät** kann.
- Jedes an ein Kommando gebundene Item erhält dessen Werte — aus
  Leseantworten, aus Meldungen oder aus deinem Plugin-Code über
  `dispatch_data()` / `_dispatch_callback()`. `x_read` / `x_write` am Item
  entscheiden nur, ob das Item anfordert oder sendet.
- `send_command(cmd)` ohne Wert wird für Kommandos abgelehnt, die nicht als
  lesbar deklariert sind (Debug-Log, Rückgabe `False`).
- Ein Kommando mit `read: False` und `write: False` ist ein Pseudo-Kommando:
  Es existiert, damit das Plugin es befüllt (kodis `info.*`), oder als reines
  Empfangsziel eines `reply_pattern`.

Das ermöglicht „eine Anfrage, viele Werte“: Ein lesbares Kommando fordert
einen Statusblock an, reine Empfangskommandos picken sich per
`reply_pattern` ihre Zeilen heraus (siehe Tutorial).

## 11. Hooks: Gerätelogik ergänzen

Nur überschreiben, was das Gerät braucht. Hooks im stabilen Vertrag:

| Hook | Aufruf | Typischer Einsatz | Beispiel |
|---|---|---|---|
| `_post_init()` | am Ende von `__init__` | eigene Attribute, `template_vars`, `self._webif = WebInterface` | `plugins/lms` |
| `on_connect(by)` | Verbindung hergestellt | Meldungen abonnieren, Status abfragen — **`super().on_connect(by)` aufrufen** (startet initiales und zyklisches Lesen) | `plugins/lms`, `plugins/kodi` |
| `on_disconnect(by)` | Verbindung verloren | Aufräumen — **`super()` aufrufen** (plant den Reconnect) | Beispiel-Plugin |
| `on_suspend()` / `on_resume()` | nach Suspend / Resume | Gerät schlafen legen / wecken | Beispiel-Plugin |
| `_do_before_send(command, value, kwargs)` | vor dem Bauen der Payload | `(False, ergebnis)` zurückgeben, um ein Kommando im Plugin zu behandeln; Kwargs pro Sendung ergänzen | `plugins/kodi` |
| `_transform_send_data(data_dict, **kwargs)` | nach dem Bauen der Payload | Framing ergänzen; bei `LINE_TERMINATED` **`super()` aufrufen** | — |
| `_transform_received_data(data)` | als Erstes beim Empfang | Rohdaten bereinigen/dekodieren | `plugins/lms` (URL-Dekodierung) |
| `_process_additional_data(command, data, value, custom, by)` | nach einem Item-Update | Folgeabfragen, abgeleitete Werte über `self._dispatch_callback(cmd, value, by)` | `plugins/lms`, `plugins/denon`, `plugins/pioneer` |
| `_send(data_dict, **kwargs)` | Übergabe an die Verbindung | selten nötig | — |

Außerdem verfügbar: `set_custom_item(item, command, index, value)` (beim
Parsen der Items pro Custom-Wert aufgerufen), `run_standalone()` (Diagnose,
viessmann), `send_command(cmd, value=None, return_result=False,
raise_on_error=False, **kwargs)`, `read_all_commands(group)`,
`custom_tokens(index)`, `set_suspend(active, by)`,
`update_lookup(table, data)`.

Deklarationen und `commands.py` vor Code bevorzugen: In 2.0 brauchen epson,
pioneer und denon kein `_set_device_defaults()`, kein überschriebenes
`on_data_received()` und keine Terminator-Behandlung.

JSON-RPC-Plugins: Das JSON-RPC-Protokoll meldet die JSON-**Methode** als
`command`, nicht den SDP-Kommandonamen; `on_data_received()` überschreiben und
Methoden auf Kommandos abbilden (`plugins/kodi`).

## 12. Template-Werte zur Laufzeit

`self.template_vars` ist eine `ChainMap`, deren erste Map dir gehört und
deren Rückfallebene die Plugin-Parameter sind. `{PARAM:x}` und
`{CUSTOM_PARAMn:x}` in Kommandostrings lesen beim Senden daraus:

```python
def _post_init(self):
    self.template_vars['CURRENT_LIST_ID'] = {}     # später pro Player befüllt
```

Werte für eine einzelne Sendung kommen in `_do_before_send()` in `kwargs` (sie
bleiben nicht zwischen Sendungen erhalten), z. B. kodis
`kwargs['playerid'] = self._playerid`.

## 13. Mehrere Geräte hinter einer Verbindung (Custom Tokens)

```python
CUSTOM_TOKEN = CustomTokenSpec(
    index=1,                                                   # nutzt x_custom1
    token_re='([0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}',          # findet das Token in Antworten
    reply_re='(?:[0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}',        # für {CUSTOM_PATTERN1}
    recursive=True,                                            # Kinder erben x_custom1
)
```

(`plugins/lms`, ein Token pro Player-MAC.) Items unterhalb eines Player-Items
mit `lms_custom1: aa:bb:cc:dd:ee:ff` werden an
`kommando#aa:bb:cc:dd:ee:ff` gebunden. Kommandostrings setzen das Token mit
`{CUSTOM_ATTR1}` ein, Reply-Patterns akzeptieren mit `{CUSTOM_PATTERN1}`
jedes Token, und empfangene Werte gehen an die Items des in der Antwort
gefundenen Tokens. Nur Tokens gebundener Items werden akzeptiert. An ein
einzelnes Gerät senden mit `self.send_command('cmd' + CUSTOM_SEP + token)`.

## 14. Item-Structs erzeugen

Aus dem shng-Basisverzeichnis:

```bash
python plugins/<name>/__init__.py -s
```

schreibt `item_structs` in `plugins/<name>/plugin.yaml` (`-a` ergänzt
`visu_acl`, `-l` schreibt Item-Namen klein). Jeder Abschnitt erhält ein Item
`read`, das seine Lesegruppe auslöst, jedes Kommando ein Item mit
`x_command`, `x_read`, `x_write` und Lesegruppen.

Anweisungen in `item_attrs` pro Kommando:

| Anweisung | Erzeugt |
|---|---|
| `initial: True` | `x_read_initial: true` |
| `cycle: n` | `x_read_cycle: n` |
| `cyclic: True` | `x_read_cyclic: true` |
| `enforce: True` | `enforce_updates: true` |
| `read_group_levels: n` | nur die letzten `n` Ebenen der Lesegruppen (0: keine) |
| `read_groups: [{'name': g, 'trigger': 'pfad'}]` | zusätzliche Lesegruppe plus Trigger-Item (führende Punkte gehen eine Ebene hoch) |
| `lookup_item: True\|'fwd'\|'rev'\|'rci'\|'list'` | Kind-Item `lookup` mit der Tabelle |
| `custom1..3: v` | `x_customN: v` |
| `attributes: {...}` | Attribute unverändert übernommen |
| `item_template: name` | Attribute aus `item_templates[name]` |

An einem Abschnitt gelten `initial` / `cycle` für dessen Trigger-Item `read`.

Der Generator schreibt die ganze `plugin.yaml` neu: Kommentare und der
`%YAML`-Kopf verschwinden, Strings werden neu gequotet, und ein
`"\n"`-Terminator kommt als `"\n\n\n"` zurück. Den Diff prüfen und solche Werte
vor dem Commit korrigieren.

## 15. Tests

Plugin-Tests liegen in `plugins/<name>/tests/test_*.py` und nutzen Helfer aus
dem Core:

- **Characterization-Snapshot** (zeichnet auf, was das Plugin für einen
  erzeugten Struct sendet und setzt; 3 Zeilen):

  ```python
  from tests.sdp_harness.characterize import characterize_plugin

  class TestCharacterization(unittest.TestCase):
      def test_matches_snapshot(self):
          characterize_plugin(self, 'epson', 'epson', 'ALL', {'serialport': '/dev/null'})
  ```

  Snapshot anlegen oder aktualisieren mit `SDP_SNAPSHOT_UPDATE=1 pytest …`.
- **Contract-Test**: `SdpPluginContractTest` (`tests/plugin_contract/sdp.py`),
  siehe `dev/sample_smartdevice_plugin/tests/test_contract.py`.
- **Verhaltenstests**: `load_sdp_plugin()` aus `tests/sdp_harness` lädt das
  Plugin über den echten Loader mit einer `RecordingConnection`; Antworten mit
  `rig.plugin.on_data_received(by, data)` einspeisen, `rig.connection.payloads`
  und Item-Werte prüfen, Jobs mit
  `rig.plugin_jobs()['read_initial_values'].fire()` auslösen. Beispiel:
  `doc/dev/sdp/example_mpd/tests/test_mpd_example.py`.

In Tests eine IP-Adresse als `host` verwenden: Der TCP-Client wird erzeugt,
bevor der Harness ihn ersetzt, und ein Hostname bedeutet einen DNS-Lookup pro
Test.

## 16. Ein SDP-1.x-Plugin auf 2.0 migrieren

1. `plugin.yaml`: `sdp_minversion: '2.0.0'`; Parameter `conn_type`,
   `protocol`, `command_class` entfernen; `send_retries_timeout` →
   `send_timeout` umbenennen; `message_timeout`/`message_repeat` entfernen
   (aus der alten Vorlage kopiert, nie von SDP gelesen — die
   Resend-Einstellungen heißen `send_retries`, `send_retries_cycle`,
   `send_timeout`).
2. `_set_device_defaults()` durch Deklarationen ersetzen: Verbindungswahl →
   `TRANSPORTS`, Protokoll → `PROTOCOL`, Kommandoklasse → `COMMAND_CLASS`,
   Terminator escapen und anhängen → `LINE_TERMINATED`, JSON-Schlüssel
   verschieben → `JSON_MOVE_KEYS`, Custom-Token-Einrichtung → `CUSTOM_TOKEN`.
   Schreibzugriffe auf `self._parameters` funktionieren weiter und gewinnen,
   mit einem Debug-Hinweis.
3. `_use_callbacks` entfernen (Callbacks sind immer aktiv; es wird eine
   Warnung geloggt).
4. Kopien von `on_data_received()` und `_transform_send_data()` entfernen, die
   nur das Basisverhalten nachbauen. epson vor 2.0:

   ```python
   def _set_device_defaults(self):
       if PLUGIN_ATTR_SERIAL_PORT in self._parameters and self._parameters[PLUGIN_ATTR_SERIAL_PORT]:
           self._parameters[PLUGIN_ATTR_CONNECTION] = CONN_SER_ASYNC
       else:
           ...
           self._parameters[PLUGIN_ATTR_CONNECTION] = CONN_NULL
       b = self._parameters[PLUGIN_ATTR_CONN_TERMINATOR].encode()
       b = b.decode('unicode-escape').encode()
       self._parameters[PLUGIN_ATTR_CONN_TERMINATOR] = b

   def _transform_send_data(self, data=None, **kwargs): ...   # Terminator anhängen
   def on_data_received(self, by, data, command=None): ...    # 45-zeilige Kopie der Basis
   ```

   epson 2.0: die drei Deklarationen aus Abschnitt 2.
5. Zugriffe auf entfernte Register (`_items_write`, `_items_read_all`,
   `_commands_read`, `_commands_initial`, `_items_custom`, …) durch
   öffentliche Aufrufe ersetzen: `custom_tokens()`, `read_all_commands()`,
   `get_items_for_mapping()`.
6. Eigene Verbindungsklassen: Konstruktor `(config, hooks, scheduler, name)`,
   Einrichtung in `_setup()`, Einstellungen aus `self._config`
   (`self._config.extra` für nicht standardisierte), Standardwerte in
   `CONFIG_DEFAULTS`. `self._params` gibt es nicht mehr.
7. `read`-Flags prüfen: Ein Aktionskommando (play, stop, …) mit `read: True`
   wird jetzt beim Lesen aller Kommandos und beim initialen Lesen gesendet.
   Mit `read: False` kennzeichnen; seine Items erhalten weiterhin Werte.
8. In einem überschriebenen `on_connect()` `super().on_connect(by)` aufrufen.

Verhaltensänderungen für Anwender:

- ein Plugin mit `TRANSPORTS` ohne `host` und `serialport` wird mit Fehler
  deaktiviert, statt auf der Dummy-Verbindung zu laufen;
- Items an Nur-Schreib- oder Pseudo-Kommandos erhalten Werte von Gerät und
  Plugin;
- das Lesen eines nicht als lesbar deklarierten Kommandos wird abgelehnt;
- Plugins, die `_use_callbacks` setzen, und externe Verbindungsklassen mit
  altem Konstruktor loggen einmalig eine Warnung.

## 17. Checkliste und Stolperfallen

- [ ] `sdp_minversion: '2.0.0'` in `plugin.yaml`
- [ ] jedes Kommando hat `item_type`, `read` und `write`
- [ ] jedes Reply-Pattern verankert und über alle Kommandos eindeutig
- [ ] `terminator` deklariert (doppelte Anführungszeichen) bei `LINE_TERMINATED`
- [ ] boolesche Gerätewerte nutzen einen eigenen Datentyp, nicht `DT_bool`
- [ ] Aktionskommandos haben `read: False`
- [ ] überschriebene `on_connect` / `on_disconnect` / `_transform_send_data` rufen `super()` auf
- [ ] Item-Attribute für jedes dokumentierte Suffix deklariert
- [ ] Struct erzeugt, Diff der `plugin.yaml` geprüft
- [ ] Characterization- oder Verhaltenstests in `plugins/<name>/tests/`
