
.. index:: Plugins; speech
.. index:: speech

======
speech
======

Das Speech Plugin nutzt Android um aus Sprachbefehlen Text zu machen, die dann mit dem Plugin analysiert werden um um Aktionen im Haus auszulösen.
Es wird eine Kombination aus Tasker und AutoVoice Plugin verwendet in Verbindung mit der Google Spracherkennung.
Das bedeutet natürlich im Gegenzug, das die Sprachdaten in die Cloud zur Erkennung geschickt werden.

Der erste Abschnitt enthält Listen die Begriffe und Rückgabewerte beinhalten, z.B. werden Begriffe unter unterschiedlichen Namen angesprochen,
das Licht in einem Raum als "Beleuchtung", "Lampe", "Licht", "Leuchte" usw. In der Konfigurationsdatei gibt es für die häufigsten Fälle Wortkombinationen die als Basis für die eigene Sprachsteuerung verwendet werden können.

Der zweite Abschnitt sind die Regeln nach denen die Items angesprochen werden.
Im wesentlichen werden verschiedene vorher definierte Variablen/Listen kombiniert um Aktionen auszuführen,
z.B. Raum, Licht, Schalten um die Beleuchtung zu schalten. Beispiele finden sich in der beiliegenden Konfigurationsdatei.

Der dritte Abschnitt enthält Fehlermeldungen die zurückgegeben werden, wenn z. B. ein Befehl nicht erkannt wurde, hier muss am Anfang nicht verändert werden.

Funktionsweise
==============

* Spracherkennung mit "OK Google" oder durch betätigen des Mikrofon-Symbols starten.

* Befehl sprechen, z.B. "Licht in der Küche einschalten", "Licht in der Küche ein", "Beleuchtung in der Küche einschalten" usw.

* Der Befehl wird von Google nicht erkannt und das AutoVoice-Plugin tritt in Aktion.

* Das AutoVoice-Plugin übergibt den kompletten Satz an Tasker und es wird an das speech-Plugin per http-URL übertragen.

* Das speech-Plugin durchsucht den Text nach vorgegebenen Regeln.
  Wenn eine Regel zutrifft dann wird das entsprechende Item gesetzt oder die Logik getriggert.
  Am Ende wird noch eine Antwort generiert und über das Smartphone als Sprache ausgegeben.


Konfiguration
=============

Diese Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/speech` beschrieben.

Die eigentliche Sprachsteuerung wird nicht über die Item-Konfiguration, sondern über eine separate
Python-Konfigurationsdatei (Standardname ``speech.py``) festgelegt, die über den Parameter ``config_file``
eingebunden wird. Eine Beispieldatei liegt im Plugin-Verzeichnis (``plugins/speech/speech.py``) und sollte
als Ausgangspunkt kopiert werden.


Aufbau von speech.py
=====================

Die Konfigurationsdatei enthält Wortlisten sowie eine Liste ``varParse`` mit den eigentlichen Regeln, nach
denen ein erkannter Satz einem Item- oder Logik-Aufruf zugeordnet wird.

Eine Wortliste bildet Suchbegriffe auf einen Rückgabewert ab, der später als Platzhalter in ``varParse``
verwendet wird:

.. code:: python

    varLicht = [
        ['Licht', ['Licht', 'Lampe', 'Leuchte', 'Beleuchtung']],
        # ...
    ]

``varParse`` selbst kombiniert solche Listen zu einer Regel. Jeder Eintrag besteht aus dem Item- bzw.
Logik-Namen (mit nummerierten Platzhaltern), einer Rückgabe-Textvorlage, den zu durchsuchenden Wortlisten
sowie optional dem Ziel-Typ ("item", Standard, oder "logic"):

.. code:: python

    varParse = [
        ["%0%.licht.%1%.schalten", "%y%", [varRaum, varLicht, varSchalten], "OK, wird ausgeführt", 'item'],
        # ...
    ]

Die Nummerierung der Platzhalter (``%0%``, ``%1%``, ...) entspricht der Reihenfolge der angegebenen Listen:
Bei ``[varRaum, varLicht, varSchalten]`` liefert ``%0%`` den Rückgabewert von ``varRaum``, ``%1%`` den von
``varLicht`` usw. Wird kein Typ angegeben, wird ein Item angenommen; für eine Logik muss ``'logic'``
angegeben werden.

Die Reihenfolge der Einträge in ``varParse`` bestimmt die Priorität: Es wird immer nur die erste
zutreffende Regel ausgeführt, alle folgenden werden ignoriert. ``varParse`` muss diesen Namen tragen und
als letzte Liste in der Datei stehen. Suchbegriffe werden ausschließlich kleingeschrieben ausgewertet.

Der Rückgabewert einer Wortliste kann auch direkt ein Item-Wert sein: Wird als Rückgabewert ``%status%``
angegeben, wird stattdessen der aktuelle Wert des zugehörigen Items ermittelt und zurückgegeben
(z.B. um eine Temperatur anzusagen).

Fehlermeldungen für nicht erkannte Befehle werden getrennt davon im Dictionary ``dictError`` der
Konfigurationsdatei gepflegt; der Aufbau ist dort selbsterklärend.


Einrichtung auf dem Smartphone
===============================

Das Plugin erwartet Sprachbefehle als Text per HTTP-GET von einer Android-App. Getestet ist die Kombination
aus Tasker und dem AutoVoice-Plugin:

1. In Tasker ein neues Profil anlegen, als Kontext "Event" → "Plugin" → "AutoVoice No Match" wählen.
2. Als Task "New Task" wählen und einen Namen vergeben, z.B. ``speech_parser``.
3. Eine Aktion "Variables" → "Variable Set" hinzufügen, Name ``%avcommsEncode``, Wert ``%avcomms()``.
4. Eine weitere Aktion "Variables" → "Variable Convert" hinzufügen, Name ``%avcommsEncode``, Funktion "URL Encode".
5. Eine dritte Aktion "Net" → "HTTP Get" hinzufügen, Server:Port z.B. ``http://smarthome.local:2788``, Pfad ``/%avcommsEncode``.
6. Eine vierte Aktion "Alert" → "Say" hinzufügen, Text ``%HTTPD``.

Danach kann über das Mikrofon-Symbol ein Befehl gesprochen werden, der von smarthome.py als Text empfangen wird.
Laut Berichten aus dem KNX-User-Forum funktioniert die Einrichtung analog auch mit der App Automagic.

- `Tasker <https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm>`_
- `AutoVoice <https://play.google.com/store/apps/details?id=com.joaomgcd.autovoice>`_
- `AutoVoice Pro <https://play.google.com/store/apps/details?id=com.joaomgcd.autovoice.unlock>`_
- `Automagic <https://play.google.com/store/apps/details?id=ch.gridvision.ppam.androidautomagic>`_
