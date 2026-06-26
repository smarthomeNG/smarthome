# Entwicklungsrichtlinien: Dynamische Fähigkeiten in SmartHomeNG

*Leitplanken für Code-Änderungen, für Audits/Reviews bestehenden Codes und als Vertrag gegenüber
Plugin-Entwicklern.*

## Geltungsbereich

Dieses Dokument regelt den Umgang mit **dynamischen Fähigkeiten** in SmartHomeNG: Plugins zur Laufzeit
laden/entladen, Items zur Laufzeit erzeugen/löschen.

**Nicht Gegenstand dieses Dokuments** ist das Bearbeiten von Item-Charakteristika zur Laufzeit (z. B. Pfad
oder Typ eines bestehenden Items ändern).

---

## Leitplanke 1: Abwärtskompatibilität — auch auf Verhaltensebene

Die Items-/Item-API und der Plugin-Vertrag müssen abwärtskompatibel bleiben. Das gilt nicht nur für
Methodensignaturen, sondern für das tatsächliche Verhalten, auf das sich bestehende Plugins implizit
verlassen.

**Grundprinzip:** Bestehendes Verhalten bleibt für jedes Plugin unverändert, solange im laufenden System
keine dynamische Operation tatsächlich stattfindet. Findet eine solche Operation statt, gilt: ein Plugin,
das eine neue Fähigkeit nicht explizit unterstützt, erleidet dadurch keinen Absturz und keine Exception —
es nutzt die neue Möglichkeit lediglich nicht. Wer als Plugin-Entwickler eine neue Fähigkeit nutzen möchte,
muss das Plugin dafür explizit anpassen.

### Pflichtmethoden vs. optionale additive Hooks

Es gibt zwei grundlegend verschiedene Arten von Plugin-Methoden, die unterschiedlich behandelt werden:

- **Pflichtmethoden** (z. B. `run()`, `stop()`): jedes Plugin muss sie implementieren. In `SmartPlugin`
  als Stub mit `raise NotImplementedError` hinterlegt — wer es vergisst, bekommt einen lauten, sofortigen
  Fehler. Das ist hier richtig, weil die Methode zwingend ist.
- **Optionale additive Hooks** (z. B. `unparse_item()`): kein Plugin muss sie überschreiben. Der Core
  prüft mit `hasattr(plugin, NAME)`, ob das Plugin die jeweilige Methode implementiert hat. Hier gilt das
  Gegenteil von Pflichtmethoden: **niemals** ein gleichnamiger Stub in `SmartPlugin`, der einen Fehler
  auslöst. Der Grund ist technisch zwingend: Ein vererbter Stub würde `hasattr(plugin, NAME)` für *jedes*
  Plugin auf `True` setzen und damit als Erkennungsmechanismus wertlos machen — der Core müsste dann
  zusätzlich per `try/except` prüfen, was die Prüflogik uneinheitlich macht.

Für optionale Hooks gibt es zwei Unterfälle:

- **Hook mit sinnvollem generischem Default** (wie `unparse_item()` heute schon): echte Implementierung
  in `SmartPlugin`. `hasattr` ist dann für alle Plugins `True` — beabsichtigt, denn der Witz ist gerade,
  dass nicht angepasste Plugins automatisch das Default-Verhalten erhalten. Der `hasattr`-Check am
  Aufrufpunkt im Core dient hier nur noch als Abwehr gegen kaputte/uralte Plugin-Klassen.
- **Hook ohne sinnvollen generischen Default** (nichts Generisches möglich ohne Plugin-Wissen): **kein**
  Stub in `SmartPlugin`. Stattdessen Aufnahme als dokumentierte Vorlage in den `sample_plugins`, damit
  Plugin-Autoren wissen, wo sie ansetzen müssen, ohne dass `hasattr` verfälscht wird.

**Sonderfall — generischer Hook mit nicht überschreibbarem Aufrufer:** `remove_item()`/`add_item()` sind
der vom Kern verwaltete, **niemals zu überschreibende** Methodenvertrag (siehe `lib/model/smartplugin.py`,
Abschnitt „the following methods should NOT be overwritten"). `remove_item()` ruft intern bereits
`unparse_item()` auf — das ist der tatsächliche, plugin-spezifische Erweiterungspunkt. Bei künftigen Hooks
nach diesem Muster gilt: der vom Core aufgerufene Einstiegspunkt bleibt generisch und fest, die
Plugin-spezifische Anpassung erfolgt über eine separate, klar benannte, überschreibbare Methode, die der
generische Einstiegspunkt selbst aufruft — nicht durch Überschreiben des Einstiegspunkts mit
`super()`-Aufruf.

Im Core wird auf das Vorhandensein/Fehlen einer Methode **durchgängig per `hasattr` geprüft**, niemals
per `try/except`.

### Checkliste für jeden neuen additiven Hook

1. Methodenname als Konstante in `lib/constants.py` definiert (z. B. `PLUGIN_REMOVE_ITEM`) — niemals ein
   hartcodierter String an der Aufrufstelle.
2. Aufruf am Core ausschließlich über `hasattr(plugin, KONSTANTE)` — nie ein Aufruf in der Annahme, die
   Methode existiere.
3. Je nach Unterfall: generische Default-Implementierung in `SmartPlugin` **oder** bewusst kein Stub
   (siehe oben).
4. Fehlen des Hooks darf nie zum Absturz im Core führen — wird geloggt als „Plugin unterstützt diese
   Fähigkeit nicht", nicht als Fehler behandelt.
5. Dokumentation der neuen Methode in der Plugin-Entwickler-Dokumentation.
6. Aufnahme als (ggf. auskommentierte) Vorlage in `sample_plugins`, als Anleitung zur Implementierung.
7. Der Core erhält mit der neuen Fähigkeit eine neue Versionsnummer. Plugins, die den Hook nutzen wollen,
   müssen ein entsprechendes `sh_minversion` in ihrer `plugin.yaml` deklarieren.
8. Für den neuen Hook existiert eine Testpflicht (s.u.).

### Sonderfall `parse_item()`

`parse_item()` war schon immer dynamisch: Es wird für jedes Item einzeln aufgerufen, ohne dass ein Plugin
unterscheiden kann, ob das Item statisch beim Start geladen oder zur Laufzeit neu erzeugt wurde. Es bleibt
**beliebig oft aufrufbar**.
Der einzige relevante Unterschied ist, ob der Aufruf vor oder nach `run()` erfolgt: Plugins, die ihre
Item-Verwaltung über `add_item()`/`get_item_list()` abbilden (statt einer eigenen, einmalig in `run()`
aufgebauten Liste), erfassen neu erzeugte Items automatisch.

Das ist eine **Empfehlung** an Plugin-Autoren, keine neue Pflicht — Plugins, die das nicht nutzen, können
zur Laufzeit erzeugte Items schlicht nicht verarbeiten, was als bekannte Einschränkung akzeptiert wird,
nicht als Fehler im Kern.

### Testpflicht

Jeder PR, der einen neuen additiven Hook einführt oder bestehendes Lifecycle-Verhalten in `lib/item` /
`lib/plugin` ändert, **muss**:

1. mindestens einen Test in `tests/` mitbringen, der das alte Verhalten (Plugin **ohne** den neuen Hook —
   kein Absturz, korrektes Fallback) und das neue Verhalten (Plugin **mit** dem neuen Hook — Hook wird
   tatsächlich aufgerufen, tut das Erwartete) abdeckt, **sowie**
2. einen entsprechenden Test der Hook-Methode für das Sample-Plugin mitbringen.

---

## Leitplanke 2: SmartHomeNG bleibt SmartHomeNG

Gute Einzelideen anderer Systeme (Home Assistant, openHAB, FHEM, ioBroker, Node-RED) dürfen übernommen
werden — SmartHomeNG soll dabei aber nicht zu einem dieser Systeme werden. Damit das mehr ist als eine
Absichtserklärung, wird zwischen unantastbaren und offenen Eigenschaften unterschieden.

### Unantastbar

- **`eval`/`on_change`/`on_update` bleiben freier Python-Code.** Keine Einschränkung auf eine
  sichere/eingeschränkte Teilmenge, keine Pflicht zu strukturierten Trigger-Objekten als Ersatz.
- **Ein Item bleibt nach außen ein einziges Objekt, das Zustand und Verhalten zugleich trägt** — keine
  Aufspaltung wie Entity/Automation (Home Assistant) oder Item/Thing/Rule (openHAB) auf der nach außen
  sichtbaren Ebene (Plugin-API, Anwender-Konfiguration). **Interne** Code-Aufteilung (wie es heute schon mit
  `lib/item/_autotimer.py`, `_hysteresis.py`, `_parsing.py` etc. gemacht wird) ist davon ausdrücklich nicht
  betroffen und jederzeit erlaubt — entscheidend ist die nach außen sichtbare Verschmelzung, nicht die
  interne Organisation.
- **Pfad bleibt zur Laufzeit unveränderlich** (siehe Geltungsbereich).

### Offen für Einzelfallprüfung

- Eine Indirektionsebene nach openHAB-Vorbild (Item↔Hardware-Verknüpfung als eigenes Objekt statt direkt im
  Item) — denkbar, ohne die unantastbaren Punkte zu verletzen, im Einzelfall zu prüfen.
- Optionale Hilfswerkzeuge (z. B. Pfad-Text-Suche, siehe unten) — ergänzend, nie ersetzend für die
  Ausdrucksfreiheit von `eval`.

**Entscheidungsregel:** Jede geplante Idee wird gegen die Liste der unantastbaren Eigenschaften geprüft.
Verletzt sie eine davon, wird sie nicht übernommen — unabhängig davon, wie gut sie ist.

---

## Item-Löschung

Aus den Besonderheiten von SmartHomeNG ergeben sich Konsequenzen für Item-Referenzen (`eval`, `eval_trigger`,
`trigger`, `on_change`, `on_update`), die beim Löschen von Items zu beachten sind:

- **Fall A (erfassbar):** Item B referenziert Item A über das explizite `trigger`/`eval_trigger`-Attribut.
  Das wird bereits strukturiert erfasst und hier nicht relevant.
- **Fall B (nicht erfassbar):** Item B referenziert Item A ausschließlich dadurch, dass der `eval`-Text von
  B irgendwo `sh.<Pfad_von_A>()` aufruft, ohne dass A in B's `trigger`-Liste steht. Das System hat zur
  Löschzeit von A keine Möglichkeit, das eindeutig zu erkennen — es gibt keine durchsuchbare Struktur dafür,
  ohne den in Leitplanke 2 unantastbaren freien `eval`-Text einzuschränken.

Für Fall B gilt **„best effort mit dokumentierter Einschränkung"**: keine automatische Erkennung, keine
Laufzeit-Garantie. Verantwortlich für die Prüfung ist, wer ein Item löscht. Als Unterstützung — nicht als
Garantie — wird ein Werkzeug bereitgestellt, das Textvorkommen eines Item-Pfads (absolut und relativ) in
`eval`/`on_change`/`on_update`/`trigger`-Texten anderer Items auffindet und auflistet, damit der Anwender
alle Referenzen vor dem Löschen prüfen, anpassen oder bewusst akzeptieren kann.

---

## Performance-Disclosure-Pflicht

Neue dynamische Fähigkeiten dürfen für ein Item, das nie dynamisch angefasst wird, keinen zusätzlichen
Suchlauf über andere Items, Scheduler-Jobs oder Plugins einführen — also nichts, was mit der Größe des
Item-Baums oder der Pluginzahl skaliert. Erlaubt sind höchstens konstante, lokale Prüfungen am Item selbst
(z. B. ein Flag).

Diese Garantie bezieht sich auf die algorithmische Klasse, nicht auf Mikrosekunden — sie ist eine
Code-Review-Regel, keine Messung.

Ist nicht ausschließbar, dass eine Änderung für den statischen Fall mehr als konstanten Aufwand einführt,
**muss das im PR explizit benannt werden**, damit eine gesonderte fachliche Prüfung stattfinden kann.
Stillschweigend eingeführte Skalierungseffekte sind nicht zulässig — explizit benannte und geprüfte schon.

---

## Begriffe

- **Additiver Hook**: eine optionale Plugin-Methode, deren Fehlen kein Fehlerzustand ist, sondern bedeutet
  „dieses Plugin nutzt bzw. unterstützt die Fähigkeit nicht".
- **Pflichtmethode**: eine Methode, die jedes Plugin implementieren muss (`run()`, `stop()`); Fehlen ist ein
  Fehler, signalisiert über `NotImplementedError`.
