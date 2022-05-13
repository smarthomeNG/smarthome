# Kodi

## Changelog

### v1.6.0
* Konfiguration und Struktur grundlegend überarbeitet, Konfiguration von Befehlen über commands.py
* Makros können als Wert auch eine Folge von Befehlen enthalten, [[Befehl1, Wert1],[Befehl2,Wert2],...]
* Weitere Funktionen hinzugefügt
* Abfrage von Wiedergabeinformationen hinzugefügt
* Aktualisierung von Wiedergabeinformationen über neues Item 'update'

### v1.5.0
* Einbinden von Makros (Abfolgen von Befehlen)
* Befehle werden in eine Warteschleife gelegt, die in der korrekten Reihenfolge abgearbeitet werden
* Weitere Parameter zum Einstellen von Verbindungsversuchen, etc.
* Befehle werden erneut gesendet, wenn eine direkte Antwort nicht mit dem Befehl übereinstimmt (sofern es sich um keine Fehlermeldung handelt)
* Beim Verbindungsaufbau werden Initialisierungsbefehle gesendet, auch nachdem die Verbindung unterbrochen wurde
* Bug Fix: on_off, Mute, etc. funktionieren nun sowohl mit True als auch False Werten
* Sendet Kodi mehrere Antworten gleichzeitig, werden diese nacheinander abgearbeitet (führte früher zu einem Freeze des Plugins)
* Optimierungen von Logging und Code
* zusätzliche Kommandos
