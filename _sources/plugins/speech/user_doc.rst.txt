
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
