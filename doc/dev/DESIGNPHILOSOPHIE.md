# Designphilosophie von SmartHomeNG

*Eine Einordnung im Vergleich zu anderen Hausautomatisierungssystemen*

## Zweck dieses Dokuments

Dieses Dokument soll nicht für SmartHomeNG werben, sondern die zentralen Designentscheidungen offenlegen,
die SmartHomeNG von anderen Systemen unterscheiden, und ehrlich benennen, welche Konsequenzen (Stärken und
Schwächen) sich aus genau diesen Entscheidungen ergeben. Die Begründung, SmartHomeNG zu nutzen, soll auf
nachvollziehbaren Designfakten beruhen, nicht auf der Größe der Nutzerbasis oder Gewohnheit.

Der Vergleich mit anderen Systemen (Home Assistant, openHAB, FHEM, ioBroker, Node-RED) erfolgt nicht als
Konkurrenzbewertung „besser/schlechter", sondern um herauszuarbeiten, welche architektonischen
Eigenschaften SmartHomeNG bewusst anders löst – und warum das so bleiben sollte.

---

## Das zentrale Designprinzip: das Item ist „intelligent"

In SmartHomeNG ist ein Item nicht nur ein Datencontainer für einen Zustand (wie z. B. eine Entity in Home
Assistant oder ein State-Objekt in ioBroker). Ein Item kann direkt – über YAML-Attribute, ohne zusätzlichen
Code – Verhalten besitzen:

- zeitgesteuerte Wertänderung (`crontab`, `cycle`, `autotimer`)
- Reaktion auf Wertänderung anderer Items (`eval`, `eval_trigger`, `on_change`, `on_update`)
- Hysterese-Logik für Schwellwert-Verhalten
- Wertverlauf/Historie und Caching über Neustarts hinweg

In den meisten anderen Systemen ist diese Art von Verhalten bewusst aus dem „Ding" (Entity/Thing/State)
herausgelöst und in eine eigene Automatisierungs-/Regel-Ebene verschoben:

- **Home Assistant** trennt strikt zwischen Entity (Zustand) und Automation (Regel, meist YAML mit
  Trigger/Condition/Action oder einer UI-Repräsentation davon).
- **openHAB** trennt Item, Thing/Channel (die Hardware-Anbindung) und Rule (das Verhalten) als drei
  getrennte Konzepte.
- **ioBroker** trennt State/Objekt von Skripten (z. B. im JavaScript-Adapter), die das Verhalten definieren.

SmartHomeNG verschmilzt „Ding" und „einfaches Verhalten" bewusst in einem Objekt. Das bedeutet: ein großer
Teil dessen, was in anderen Systemen eine eigene Automatisierung erfordert, ist in SmartHomeNG eine einzige
YAML-Zeile am Item selbst. Das ist kein Zufall, sondern der Kern der Idee.

Diese Verschmelzung ist zum Einen die Besonderheit von SmartHomeNG, und gleichzeitig die Quelle der unten
beschriebenen Einschränkungen – beides folgt direkt aus derselben Entscheidung.

---

## `eval:` als freier Python-Ausdruck

Wo andere Systeme eine eigene, eingeschränkte Ausdruckssprache anbieten (Home Assistants Jinja2-Templates,
openHABs DSL/JavaScript-Regelmaschine), erlaubt SmartHomeNG im `eval:`-Attribut praktisch beliebigen
Python-Code. Das hat einen klaren Vorteil: Anwender sind nicht auf das beschränkt, was eine Template-Sprache
vorgesehen hat – komplexe Logik lässt sich direkt und ohne Umwege formulieren.

Der Preis dafür: Referenzen auf andere Items innerhalb eines `eval`-Ausdrucks (z. B. `sh.wohnzimmer.licht()`)
sind reiner Text, keine strukturierte, vom System verwaltete Verknüpfung. Das System kann diese Referenzen
weder zentral validieren noch automatisch nachführen, wenn sich ein referenziertes Item ändert. Andere
Systeme, die ihre Verknüpfungen strukturiert statt textuell ablegen, können solche Anpassungen automatisch
vornehmen – zahlen dafür aber mit weniger Ausdrucksfreiheit. SmartHomeNG hat sich bewusst für die
Ausdrucksfreiheit entschieden.

---

## Funktionaler Vergleich mit anderen Systemen

**Home Assistant**: Entity-orientiert, Verhalten lebt in Automationen. Stabile, von der Anzeige entkoppelte
`entity_id`. Eine Entity-Registry verwaltet Entities zur Laufzeit. Referenzen aus UI-Automationen sind
strukturierte Daten (und damit beim Umbenennen nachführbar); Referenzen aus frei geschriebenen
Jinja-Templates sind Text (und damit – wie bei SmartHomeNG – nicht automatisch nachführbar).

**openHAB**: Item, Thing/Channel und Rule sind getrennte Konzepte. Die Verbindung zwischen einem Item und
der dahinterliegenden Hardware ist ein eigenständiges Objekt (der „Link"), nicht im Item selbst verdrahtet.
Das ist eine echte Indirektionsebene, die SmartHomeNG so nicht besitzt. Die neuere, UI-basierte
Regel-Engine speichert Item-Referenzen strukturiert; die ältere Rules-DSL referenziert Items dagegen
textuell, mit denselben Einschränkungen wie SmartHomeNG.

**FHEM**: Architektonisch der nächste Verwandte von SmartHomeNG – ebenfalls dynamisch zur Laufzeit
veränderbar (`define`/`delete`/`rename` ohne Neustart), und Geräte referenzieren sich gegenseitig per Name
in Attributen und Perl-Code. FHEM bietet einen `rename`-Befehl, der versucht, Referenzen in anderen
Definitionen per Textersatz nachzuziehen – ein Ansatz, der in der FHEM-Community als fehleranfällig bekannt
ist (Teilstring-Kollisionen, berechnete Namen, bedingte Logik werden nicht erkannt). Das ist ein praktischer
Beleg dafür, dass dieses Problem nicht einfach „gelöst" werden kann, ohne die Ausdrucksfreiheit selbst
einzuschränken.

**ioBroker**: Objekte besitzen eine stabile, mehrteilige ID (`adapter.0.pfad`) in einer echten
Objekt-Datenbank. Das Umbenennen einer Objekt-ID ist selten und wird aktiv vermieden. Wo eine
Indirektionsebene gebraucht wird, nutzt ioBroker explizite Alias-Objekte – wieder eine strukturierte
Verknüpfung statt einer Text-Referenz. Direkte Referenzen aus selbst geschriebenen JavaScript-Skripten
(`getState('adapter.0.pfad')`) sind dagegen genauso textuell und fragil wie SmartHomeNGs `eval`.

**Node-RED**: Das stärkste Beispiel für strukturierte Verknüpfungen – Knoten sind über ein explizites
Graph-Modell verbunden (`wires`), die Verbindung *ist* die Datenstruktur, kein Text, der sie beschreibt. Das
ermöglicht sicheres Umverdrahten. Sobald aber in einem Function-Node Code geschrieben wird, der über einen
globalen Kontext per String auf andere Werte zugreift, taucht dieselbe Fragilität wieder auf.

---

## Weitere SmartHomeNG-Eigenschaften im Vergleich

**Kein separater Datenbank- oder Broker-Prozess.** Items sind einfache Python-Objekte im Speicher eines
einzigen Prozesses. Ein Zugriff wie `sh.pfad()` ist direkter Attributzugriff, kein Netzwerk- oder
IPC-Aufruf über einen Message-Bus (wie bei ioBrokers Adapter-Architektur) oder eine Event-/State-Machine
(wie bei Home Assistant). Das hält die Architektur einfach, latenzarm und auch auf kleiner Hardware (z. B.
Raspberry Pi) gut betreibbar. Der `--interactive`-Modus erlaubt direkten Zugriff auf den laufenden Item-Baum
über eine Python-REPL – ein Debugging-Komfort, den ein mehrprozessiges System so nicht bieten kann.

**Ein gemeinsamer Plugin-Vertrag.** Alle Plugins erben von derselben `SmartPlugin`-Basisklasse mit
einheitlichen Methoden (`add_item`, `remove_item`, `parse_item`, Scheduler-Hilfsfunktionen,
Asyncio-Hilfsfunktionen). Bei einer über 150 Plugins umfassenden, von vielen verschiedenen Personen
gepflegten Codebasis ist diese Einheitlichkeit ein erheblicher Stabilitätsfaktor – Erweiterungen am Kern
lassen sich an einer Stelle vornehmen und wirken additiv auf alle Plugins, statt 150 unterschiedliche Muster
einzeln anpassen zu müssen.

**Structs.** SmartHomeNG erlaubt es, wiederverwendbare Item-Vorlagen (Structs) zur Konfigurationszeit zu
definieren und zu expandieren. Das löst einen Teil des Wiederverwendungsproblems, das andere Systeme über
eine Laufzeit-Verknüpfungsebene lösen, bereits *vor* der Erzeugung der eigentlichen Objekte – einfacher und
ohne eine zusätzliche Indirektionsebene pflegen zu müssen.

**Langlebigkeit.** SmartHomeNG existiert seit über zehn Jahren mit einer aktiven, breiten Plugin-Landschaft.
Diese Reife – etablierte Konventionen, ein eingespieltes Ökosystem, viel praktische Erfahrung in der
Community – ist selbst ein Wert, den jede Weiterentwicklung respektieren muss.

---

## Fazit: was SmartHomeNG ausmacht

Die Stärken und die Schwächen von SmartHomeNG entstehen aus derselben Designentscheidung: der Verschmelzung
von „Ding", „einfachem Verhalten" und „freier Ausdrucksmächtigkeit" in einem einzigen, leichtgewichtigen
Item-Objekt, ohne separate Datenbank, ohne separate Regel-Maschine, ohne erzwungene Indirektionsebene.

Das ist kein Kompromiss aus Mangel an Möglichkeiten, sondern eine bewusste Setzung von Prioritäten:
Einfachheit der Architektur und Ausdrucksfreiheit für den Anwender wiegen schwerer als zentrale
Validierbarkeit und automatische Konsistenzgarantien. Jede Weiterentwicklung von SmartHomeNG sollte sich an
dieser Priorität messen lassen – Funktionen anderer Systeme zu übernehmen ist dort sinnvoll, wo sie diese
Priorität stärken, und sollte unterbleiben, wo sie sie aufgeben würde.
