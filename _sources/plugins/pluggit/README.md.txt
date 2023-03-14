# pluggit
SmartHomeNG plugin pluggit

Das SmartHomeNG plugin für eine Pluggit AP310 KWL

## Einbindung in der plugin.yaml mit:

```python
pluggit:
    class_name: Pluggit
    class_path: plugins.pluggit
    host: 192.168.1.4
    #cycle: 300
```

host = IP-Adresse der pluggit  
cycle = Update-Interfall der abzufragenden Werte (optional)

## Einbindung in den Items per Item-Struct:

```python
struct: pluggit.pluggit
```

## Änderungen:

V2.0.4 - 13.11.2022
- Verbesserungen zur Versionsprüfung "pymodbus"

V2.0.3 - 25.10.2022
- Support für pymodbus 3.0

22.05.2022:
- Fehler mit manuellem Bypass behoben

16.02.2022:
- CurentUnitMode.ManualBypass dem Item-struct zugefügt
- Log-Level für verschiedene Ausgaben angepasst
- CurrentUnitMode.AwayMode repariert

24.02.2021:
- Item-struct um Zugriffe für SmartVISU erweitert
- item_attribut um pluggit_convert erweitert
- scheduler.remove eingebaut

29.08.2020:
 - bool-Werte konnten nicht geschrieben werden

## Folgende Vorteile ergeben sich zu dem Plugin 1.x

- wesentlich mehr Parameter der pluggit können abgefragt werden
- einige Parameter lassen sich auch schreiben
- die Werte können intern auch konvertiert werden, sodass man eine vernünftige Ausgabe erhält

## Es fehlen auch noch ein paar Dinge:

- die Programmierung des Auto-Wochenprogramms ist noch nicht implementiert
- eine Dokumentation der Parameter
