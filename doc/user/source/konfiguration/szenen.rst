
.. role:: bluesup

======
Szenen
======

Für die Verwendung von Szenen ist eine Konfigurationsdatei für jedes 'Szenenobjekt' im Szenenverzeichnis
erforderlich. Diese Dateien müssen als Dateinamen den Item-Path des Items tragen in dem die Szene definiert
ist und über das der Status der Szene gesteuert wird.

Seit SmartHomeNG v1.4 werden folgende Features für Szenen unterstützt:

- Für Szenen Stati können Namen vergeben werden.
- Der Ziel Item-Pfad einer Szenenaktion kann als relative Referenz angegeben werden.
- Wenn dem Zielitem Stringwerte zugewiesen werden sollen, müssen diese zweifach in Anführungszeichen angegeben werden,
  z.B. `"'Wert'"`, Zahlen können direkt angegeben werden, und andere Werte wie z.B. Listen oder dicts müssen einfach
  in Anführungszeichen stehen, z.B. `"{'key': 'value'}"` oder `'["listitem1", "listitem2"]'`.
- Anstelle eines Wertes kann auch ein **eval** Ausdruck angegeben werden. In diesem Ausdruck sind auch relative
  Item Referenzen möglich. eval-Ausdrücke werde wie andere Werte einfach in Anführungszeichen gesetzt.
- Für Szenen Aktionen in denen ein absoluter Wert angegeben wird, wird bei Verwendung des neuen Dateiformats das
  Lernen (analog zu KNX Szenen) unterstützt

Das alte Dateiformat (.conf)  von smarthome.py wird weiterhin unterstützt. Allerdings gibt es in diesem Dateiformat
keine Unterstützung für die neueren Features.

Die Nutzung der neuen Features ist unter :doc:`Konfiguation/Konfigurationsdateien/scenes/\*.yaml <./konfigurationsdateien/scenes>`
beschrieben. Zu beachten ist, dass die Konfigurationsdateien für Szenen nur eingelesen werden, wenn ein Item
gleichen Namens definiert ist und der Type dieses Items **scene** ist.


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
gehörenden Aktoren (analog hier Items mit gesetztem Learn-Flag) abgefragt und die
aktuellen Werte werden gespeichert. Diese Werte werden dann bei nachfolgenden Aufrufen
der Szene (anstelle der initial gesetzten Werte) gesetzt.

Bei Szenen Items ohne Learn wird kein aktueller Wert abgespeichert. Learn funktioniert
nur wenn absolute Initialwerte gesetzt werden und keine Formeln.
