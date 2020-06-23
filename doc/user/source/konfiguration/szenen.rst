
.. role:: bluesup

######
Szenen
######

Für die Verwendung von Szenen ist eine Konfigurationsdatei für jedes 'Szenenobjekt' im Szenenverzeichnis
erforderlich. Diese Dateien können im alten Szenen-Conf Format (Endung '.conf') oder im
yaml Format (Endung '.yaml') erstellt werden und müssen als Dateinamen den Item-Path des Items
tragen in dem die Szene definiert ist und über das der Status der Szene gesteuert wird.


Neuerungen ab SmartHomeNG v1.4
------------------------------

Mit SmartHomeNG v1.4 kommen folgende neue Features hinzu:

- Es werden Konfigurationsdateien im yaml Format unterstützt.
- Für Szenen Stati können im neuen Dateiformat Namen vergeben werden.
- Der Ziel Item-Pfad einer Szenenaktion kann als relative Referenz angegeben werden.
- Anstelle eines Wertes kann auch ein **eval** Ausdruck angegeben werden. In diesem Ausdruck sind auch relative Item Referenzen möglich.
- Für Szenen Aktionen in denen ein absoluter Wert angegeben wird, wird bei Verwendung des neuen Dateiformats das Lernen (analog zu KNX Szenen) unterstützt


Die Nutzung dieser neuen Features ist unter :doc:`Konfiguation/Konfigurationsdateien/scenes/\*.yaml <./konfigurationsdateien/scenes>`
beschrieben.


Funktionsweise von Szenen
-------------------------

Szenen sind in SmartHomeNG analog zu KNX implementiert.

Bei KNX gibt es 64 Szenen (0 - 63) die auf einer Gruppenadresse (analog hier auf
einem Szenen-Item) angewählt werden können.

Bei KNX Aktoren erfolgt die Zuordnung zu Szenen dadurch, dass die Aktoren mit der
entsprechenden Gruppenadresse verbunden werden. In SmartHomeNG müssen in der Szenen-
Definition entsprechende Aktions-Items angelegt werden, die durch die Szene angesteuert
werden sollen.

KNX kennt zwei unterschiedliche Modi für Aktoren. Entweder wird der gewünschte Wert
zu einem Szenenstatus bei Programmierung des Aktors als Konstante festgelegt oder
des entsprechende Wert kann gelernt werden. Dabei kann ein Default-Wert als Konstante
vorgegeben werden. Das ist in SmartHomeNG analog implementiert.

Zum Lernen der Szenenstati ist auf die Szenennummer 128 zu addieren und dieser Wert an
die Gruppenadresse (bzw. an das Szenen-Item) zu senden. Wird auf die Gruppenadresse
(analog hier auf das Item) ein Wert >=128 geschrieben, werden für die zur Gruppe
gehörenden Aktoren (analog hier Items mit gesetztem learn-Flag) abgefragt und die
aktuellen Werte werden gespeichert. Diese Werte werden dann bei nachfolgenden Aufrufen
der Szene (anstelle der initial gesetzten Werte) gesetzt.

Bei Szenen Items ohne Learn wird kein aktueller Wert abgespeichert. Learn funktioniert
nur wenn absolute Initialwerte gesetzt werden und keine Formeln.
