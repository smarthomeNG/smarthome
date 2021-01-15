
scenes/\*.yaml
##############


.. _`scene configuration files`:


Szenen Definitionen im Verzeichnis **../scenes**
================================================

Im Verzeichnis **../scenes** kann eine beliebige Anzahl von Konfigurationsdateien für Szenen
erzeugt werden. Jede Konfigurationsdatei kann dabei nur die Konfiguration einer Szene enthalten.
Das Verzeichnis enthält yaml Dateien (oder Dateien im alten .conf Format) mit den Definitionen
der Szenen, die durch SmartHomeNG genutzt werden sollen. Der Name der yaml Datei kann beliebig sein,
solange die Extension `.yaml` ist.

Zu beachten ist, dass die Konfigurationsdateien für Szenen nur eingelesen werden, wenn ein Item gleichen Namens
definiert ist und der Type dieses Items **scene** ist.

.. note::

   Das alte Format der Konfigurationsdateien für Szenen trägt zwar die Extension .conf. Das
   Dateiformat weicht jedoch vom Dateiformat der anderen .conf Dateien ab.


Weitere Details zur Konfiguration von Items als Szenen sind :doc:`hier <../items/items>` zu finden.



Szenen
------

Für die Verwendung von Szenen ist eine Konfigurationsdatei für jedes 'Szenenobjekt' im Szenenverzeichnis
erforderlich. Diese Dateien können im alten Szenen-Conf Format (Endung '.conf') oder im
yaml Format (Endung '.yaml') erstellt werden und müssen als Dateinamen den Item-Path des Items
tragen in dem die Szene definiert ist und über das der Status der Szene gesteuert wird.


altes Konfigurationsformat
--------------------------

Die Szenenkonfigurationsdatei besteht aus Zeilen mit jeweils drei durch Leerzeichen getrennten
Werten. Jede Zeile bestimmt ein Zielitem(Logik), das verändert werden soll, wenn die Szene einen
bestimmten Status annimmt. Jede Zeile enthält folgende Informationen:

+-----------------+----------------------------------------------------------------------------------------------------------+
| Szenen-Status   | Wert, den das Szenen Item annehmen muss, damit die definierte Zuweisung durchgeführt wird (Wert 0 - 63)  |
+-----------------+----------------------------------------------------------------------------------------------------------+
| Ziel-Item/Logic | Item-Pfad des Items, dass den definierten Wert zugewiesen bekommen soll (oder Logik, die gestartet /     |
|                 | gestoppt werden soll).                                                                                   |
+-----------------+----------------------------------------------------------------------------------------------------------+
| Wert            | Wert der dem Item zugewiesen werden soll (oder run/stop, falls eine Logik angegeben wurde).              |
+-----------------+----------------------------------------------------------------------------------------------------------+


.. code::

   # items/example.conf
   [example]
       type = scene
   [otheritem]
       type = num

.. code::

   # scenes/example.conf
   0 otheritem 2
   1 otheritem 20
   1 LogicName run
   2 otheritem 55
   3 LogicName stop


Neuerungen ab SmartHomeNG v1.4
------------------------------

Mit SmartHomeNG v1.4 kommen folgende neue Features hinzu:

- Es werden Konfigurationsdateien im yaml Format unterstützt.
- Für Szenen Stati können im neuen Dateiformat Namen vergeben werden.
- Der Ziel Item-Pfad einer Szenenaktion kann als relative Referenz angegeben werden.
- Anstelle eines Wertes kann auch ein **eval** Ausdruck angegeben werden. In diesem Ausdruck sind auch relative Item Referenzen möglich.
- Für Szenen Aktionen in denen ein absoluter Wert angegeben wird, wird bei Verwendung des neuen Dateiformats das Lernen (analog zu KNX Szenen) unterstützt


Konfiguration im YAML Format
----------------------------

Im YAML Format erfolgt die Definition wie bisher in einer eigenen Datei für jede Szene. Im
Gegensatz zur Konfiguration von Szenen im alten Dateiformat (wo die Definition der Stati
der Szene ungeordnet in Zeilen erfolgte), ist die Definition einer Szene im YAML Format
hierarchisch geordnet.

Die Keys auf oberster Ebene sind die Stati (Integer Werte zwischen 0 und 63). Jeder dieser Stati
enthält eine Unterstruktur, die den jeweiligen Status definiert. Dazu sind die untergeordneten
Keys ``name:`` und ``actions:`` vorhanden.

Mit dem Key **name** wird der Name des Status festgelegt. Ein Name muss nicht zwingend vergeben
werden, er erhöht jedoch die Verständlichkeit der Szenendefinition und dient der Übersichtlichkeit
z.B. bei der Anzeige von Szenen im Backend Plugin.

Mit dem Key **actions** der aus einer Liste von einzelnen Action-Definitionen besteht, wird
festgelegt, welche Aktionen ausgelöst werden sollen, wenn der entsprechende Status eintritt.

Jede einzelne Aktion ist durch die Keys ``item:`` , ``value:`` und ``learn:`` definiert.

Die Verwendung von Wildcards (*) in den ``item:`` Definitionen ist nicht möglich.

Der Key **item** enthält den Pfad des Items, das verändert werden soll. Der Key **value** enthält
den Wert auf den das Item gesetzt werden soll. Anstelle eines festen Wertes, kann hier auch ein
**eval** Ausdruck angegeben werden. Der Key **learn** ist optional. Wird er nicht angegeben,
wird der Wert False für **learn** angenommen. Außerdem wird der Wert für **learn** immer auf False
gesetzt, wenn **value** einen Ausdruck und keinen absoluten  Wert enthält.

Sowohl bei der Angabe des Ziel-Items, als auch im eval-Ausdruck ist die Nutzung relativer Item
Referenzen möglich.

Die Konfiguration der Szene in den Items erfolgt wie bisher.

.. code-block:: yaml
   :caption: Struktur einer Status Definition

   <Status>:
       name: <Status Name>
       actions:
        - {item: <Ziel Item 1>, value: <Wert für Ziel 1>, learn: <true|false>}
        - {item: <Ziel Item 2>, value: <Wert für Ziel 2>}
        - {item: <Ziel Item 3>, value: <Wert für Ziel 3>, learn: <true|false>}
        # ...

.. note::

   Für die einzelnen Aktionen innerhalb einer YAML Definition ist eine alternative Schreibweise
   möglich. Hierbei ist auf die genaue Einrückung der einzelnen Teile der **actions** Liste zu
   achten:

   .. code-block:: yaml
      :caption: Struktur einer Status Definition

      <Status>:
          name: <Status Name>
          actions:
            - item: <Ziel Item 1>
              value: <Wert für Ziel 1>
              learn: <true|false>
            - item: <Ziel Item 2>
              value: <Wert für Ziel 2>
            - item: <Ziel Item 3>
              value: <Wert für Ziel 3>
              learn: <true|false>
           # ...


Im folgenden ist eine Beispiel Szene beschrieben, die als Ergänzung zu einer KNX-Szene eine
Philips Hue Leuchte ansteuert.

Dafür muss ein Szenen-Item angelegt werden:

.. code-block:: yaml
   :caption: Ausschnitt aus einer Item Datei

   wohnung:
       buero:
           szenen:
               type: scene

Um festzulegen wie die Szenen aussehen sollen, muss im Verzeichnis **../scenes** eine
Konfigurationsdatei für die Szene-Definition angelegt werden. Für das obige
Beispiel muss die Datei den Namen **wohnung.buero.szenen.yaml** tragen.


.. code-block:: yaml
   :caption: wohnung.buero.szenen.yaml: Beispiel einer Szenen-Definition (Datei scenes/wohnung.buero.szenen.yaml)

   0:
       name: Aus
       # Sonderfall: Leuchte Dreieckschrank ausschalten, falls die Schreibtischleuchte nicht eingeschaltet ist, sonst level 126 setzen
       actions:
        - {item: wohnung.buero.dreieckschrank.level, value: 0 if (sh.wohnung.buero.schreibtischleuchte.status() < 2) else 126}
        - {item: wohnung.buero.dreieckschrank.ct, value: 345, learn: false}
        - {item: wohnung.buero.dreieckschrank.onoff, value: False if (sh.wohnung.buero.schreibtischleuchte.status() < 2) else True}

   1:
       name: Ambiente
       actions:
        - {item: wohnung.buero.dreieckschrank.level, value: sh...dreieckschrank.ambiente_level(), learn: false}
        - {item: wohnung.buero.dreieckschrank.ct, value: 345, learn: true}
        - {item: wohnung.buero.dreieckschrank.onoff, value: True, learn: true}

   2:
       name: Hell
       actions:
        - {item: wohnung.buero.dreieckschrank.level, value: 126, learn: true}
        - {item: wohnung.buero.dreieckschrank.ct, value: 345, learn: true}
        - {item: wohnung.buero.dreieckschrank.onoff, value: True, learn: true}

   3:
       name: Putzen
       actions:
        - {item: wohnung.buero.dreieckschrank.level, value: 255, learn: false}
        - {item: wohnung.buero.dreieckschrank.ct, value: 345, learn: false}
        - {item: wohnung.buero.dreieckschrank.onoff, value: True, learn: false}

   4:
       name: Party
       actions:
        - {item: wohnung.buero.dreieckschrank.level, value: 200, learn: false}
        - {item: wohnung.buero.dreieckschrank.hue, value: 59635, learn: false}
        - {item: wohnung.buero.dreieckschrank.sat, value: 230, learn: false}
        - {item: wohnung.buero.dreieckschrank.onoff, value: True, learn: false}
<<<<<<< HEAD
        
=======

.. code-block:: yaml
   :caption: Beispiel der Szenen Item-Definition in der items.yaml

   szenen:
       wohnung:
           buero:
               type: scene
>>>>>>> origin/release-1.6
