.. index:: Standard-Attribute; eval_trigger
.. index:: eval_trigger
.. index:: Standard-Attribute; eval
.. index:: eval

*eval* und *eval_trigger*
=========================

Attribut *eval*
---------------

Wenn ein Item einen neuen Wert zugewiesen bekommen soll (z.B. via KNX
oder Logik), wird der neue Wert zunächst in **value**
zwischengespeichert. Wenn ein Attribut **eval** existiert, so wird der
Ausdruck hinter **eval: …** ausgeführt und das Ergebnis dieses
Ausdrucks als neuer Wert ins Item übernommen. Sollten alter und neuer
Wert des Items unterschiedlich sein oder ist das Attribut
**enforce_updates** vorhanden und auf **True** gesetzt, dann werden
abhängige Logiken getriggert.

Im folgenden Beispiel liefert ein Sensor die Temperatur in Fahrenheit.
Das Item soll aber die Temperatur in °Celsius speichern.

.. code-block:: yaml

   Temperatur:
       # Formel (°F  -  32)  x  5/9 = °C
       type: num
       eval: (value - 32 ) * 5 / 9  # Aus 68°F werden somit 20°C

Die Auswertung des **eval** Ausdrucks wird gestartet, wenn:
 - dem Item ein neuer Wert zugewiesen wird (siehe Erläuterug im ersten Absatz)
 - sich der Wert des oder der Items aus dem **eval_trigger** ändert (siehe Erläuterug weiter unten)
 - ein **timer** verwendet wird und die angegebene Zeit abgelaufen ist
 - ein **autotimer** verwendet wird und die angegebene Zeit abgelaufen ist
 - ein ** crontab** definiert ist und die zeitlichen Angaben zutreffen

Das Eval Attribut kann auch bis zu einem gewissen Grad Logiken
beinhalten. Wichtig ist, dass bei der Angabe eines if auch ein else
implementiert sein muss. Außerdem ist dem Item ein **sh.** voran zu
setzen. Die () Klammern hinter dem Item sind nötig, um den Item-Wert
abzufragen.

.. code-block:: yaml

   Temperatur:
       Trigger:
           # Wird wahr, wenn die Temperatur über 20 Grad wird und falsch, wenn nicht.
           type: bool
           eval: 1 if sh.Temperatur() > 20 else 0
           eval_trigger: Temperatur

Weiter ist es möglich, direkt die Werte der eval_trigger im eval
entsprechend auszuwerten:

::

   | keyword | Beschreibung                                                            |
   | ------- | ----------------------------------------------------------------------- |
   |   sum   | Errechnet die Summe aller eval_trigger Items.                           |
   |   avg   | Errechnet den Mittelwert aller Items auf die sich eval_trigger bezieht. |
   |   min   | Errechnet den Minimalwert aller Items auf die sich eval_trigger bezieht.|
   |   max   | Errechnet den Maximalwert aller Items auf die sich eval_trigger bezieht.|
   |   and   | Setzt den Wert des Items auf True, wenn alle Items auf die sich         |
   |         | eval_triggers bezieht den Wert True haben.                              |
   |   or    | Setzt den Wert des Items auf True, wenn eines der Items auf die sich    |
   |         | eval_triggers bezieht den Wert True haben.                              |

Beispiel:

.. code-block:: yaml

   Raum:

       Temperatur:
           type: num
           name: average temperature
           eval: avg
           eval_trigger:
             - room_a.temp
             - room_b.temp

       Praesenz:
           type: bool
           name: movement in on the rooms
           eval: or
           eval_trigger:
             - room_a.presence
             - room_b.presence

Ab SmartHomeNG v1.3 wird das Python Modul
`math <https://docs.python.org/3.4/library/math.html>`__ bereitgestellt
und es können entsprechende Funktionen genutzt werden.

Beispiel:

.. code-block:: yaml

   oneitem:
     type: num
     eval: ceil(sh.otheritem() / 60.0)

Ab SmartHomeNG v1.3 können für **eval** auch relative `Relative Item
Referenzen <https://github.com/smarthomeNG/smarthome/wiki/Items:-Relative-Item-Referenzen>`__
genutzt werden. Dann müssen Bezüge auf andere Items nicht mehr absolut
angegeben werden sondern können sich relative auf andere Items beziehen.


.. tip::

   Im Abschnitt **Logiken** ist auf der Seite :doc:`Feiertage, Daten und Zeiten </logiken/objekteundmethoden_feiertage_datum_zeit>`
   beschrieben, welche Feiertags- und Datums-Funktionen in Logiken benutzt werden können. Diese Funktionen können auch
   in eval Attributen genutzt werden können.

Eval Syntax
------------

Der Syntax eines **eval** Ausdrucks ist der Syntax einer `Python conditional expression <https://www.python.org/dev/peps/pep-0308/>`_
Dieser Syntax wird bei den Item Attributen **eval**, **on_change** und **on_update** verwendet.
Zu beachten ist, dass der Syntax einer if-Bedingung in einer Python conditional Expression folgender ist:

``eval: <expression-if-true> if <condition> else <expression-if-false>``


Beispiel:

``eval: value if value>0 else 0``

Die Expression setzt den Item-Wert auf den bisherigen Wert, falls er >0 ist, sonst wird der Wert auf 0 gesetzt.
Damit findet eine Zuweisung statt und on_change bzw. on_update Trigger werden ausgelöst.

Wenn das Beispiel folgendermaßen formuliert wird:

``eval: 0 if value <0 else None``

Hätte es auf den Item-Wert letztlich die selben Auswirkungen: Hier wird der Item-Wert auf 0 gesetzt, falls der Wert <0 ist,
sonst (None) wird keine Aktion ausgeführt (damit bleibt der Wert unverändert erhalten).
Damit werden on_change bzw. on_update Trigger nur ausgelöst, wenn der Wert vorher <0 war. Bei Erhalt des Wertes (None),
werden keine Trigger ausgelöst.


.. tip::

   Im Abschnitt **Logiken** ist auf der Seite :doc:`Feiertage, Daten und Zeiten </logiken/objekteundmethoden_feiertage_datum_zeit>`
   beschrieben, welche Feiertags- und Datums-Funktionen in Logiken benutzt werden können. Diese Funktionen können auch
   in eval Attributen genutzt werden können.



Attribut *eval_trigger*
-----------------------

Das Attribut eval_trigger legt, bei welchen Items eine Wertänderung eine 
Neuberechnung des **eval** Ausdruckes startet. Das obige Beispiel könnte 
so erweitert werden:

.. code-block:: yaml

   TemperaturFahrenheit:
       type: num
   TemperaturCelsius:
       # Formel (°F  -  32)  x  5/9 = °C
       type: num
       eval: (sh.TemperaturFahrenheit() - 32 ) * 5 / 9  # Aus 68°F werden somit 20°C
       eval_trigger: TemperaturFahrenheit

Hier gibt es ein Attribut **eval_trigger** mit dem Item Namen
**TemperaturFahrenheit**. Sobald sich dieses Item ändert, wird auch der
Wert von **TemperaturCelsius** neu berechnet.

Im Attribut **eval_trigger** kann eine Liste mehrerer Items angegeben
werden. Die Items müssen für das alte .conf Format jeweils durch ein
‘\|’ voneinander getrennt werden. In der .yaml kann eine Liste angegeben
werden. Der Ausdruck unter **eval** wird neu berechnet,
wenn sich eines dieser Items verändert. Die Items können auch mit einem
Stern generalisiert werden. Temperatur.\* bedeutet, dass alle
Kinderitems des Temperatur-Items zum Evaluieren des Items führen. Oder
\*.Trigger sorgt dafür, dass das Item durch alle Kind-Items mit dem
Namen “Trigger” aktualisiert werden kann, also z.B. durch
Temperatur.Trigger, Licht.OG.Trigger, etc.

Ab SmartHomeNG v1.3 können für **eval_trigger** auch relative `Relative
Item
Referenzen <https://github.com/smarthomeNG/smarthome/wiki/Items:-Relative-Item-Referenzen>`__
genutzt werden. Dann müssen Bezüge auf andere Items nicht mehr absolut
angegeben werden sondern können sich relative auf andere Items beziehen.

Ein häufiger Fehler bei der Nutzung von **eval** im Zusammenspiel mit **eval_trigger** ist,
bei **eval_trigger** auch den vollen Python-Pfad zu einem SmartHomeNG Item zu verwenden, wie
im **eval** Ausdruck.

Richtig ist es, bei **eval_trigger** nur der Item-Pfad zu nutzen (ohne führendes **sh.** und
ohne folgende **()**).


**Korrekt**:

- eval: **sh.** my.value **()**
- eval_trigger: my.value | my.other.value

**Falsch**:

- eval: sh.my.value
- eval_trigger: **sh.** my.value | **sh.** my.other.value


Gemeinsame Verwendung von eval und on\_\.\.\. Item Attributen
-------------------------------------------------------------

Bei Verwendung des **eval** Attributes zusammen mit **on_change** oder **on_update** in der
selben Item Definition ist zu beachten, dass value unterschiedliche Werte hat/haben kann.

Im Ausdruck des **eval** Attributes hat value den alten Wert des Items. Nach Abschluss dieser
Berechnung, wird dem Item das Ergebnis zugewiesen. Anschließend werden die Ausdrücke für
**on_change** und **on_update** berechnet. Zu diesem Zeitpunkt hat das Item (und damit
**value**) bereits den neuen Wert.

Wenn in **eval** Ausdrücken in **on_change** oder **on_update** Attributen auf den alten Wert
des Items zugegriffen werden soll, muss dazu die Item Funktion **prev_value()** genutzt werden.
Auf den alten Wert des aktuellen Items kann ohne die Angabe der vollständigen Item Pfades durch
den Ausdruck **sh.self.prev_value()** zugegriffen werden.


.. attention::

   Bei **eval** Ausdrücken (wie sie in den Item Attributen **eval**, **on_update** und **on_change**
   verwendet werden) ist zu beachten, dass bei Verwendung von **if** auch immer ein **else**
   Zweig angegeben werden muss!

   Wenn man jedoch ein Item nur verändern möchte wenn die **if** Bedingung erfüllt ist und sonst
   unverändert lassen möchte, muss als **else** Zweig der Ausdruck **else None** angegeben werden.
   **None** bewirkt, dass das Item unverändert bleibt, und somit auch keine Trigger ausgelöst werden.


Beispiele für die Anwendung von *eval* und *eval_trigger*
---------------------------------------------------------

**Bearbeiten von Werten**

Wird einem Item ein neuer Wert zugewiesen, wird dieser erst einmal als **value** zwischengespeichert. Ist ein **eval** vorhanden, wird dies erst ausgeführt, bevor dem Item der Wert final zugewiesen wird.
Das kann man sich für Nachbearbeitungen zu nutze machen, bspw. wenn der zugewiesene Wert zu viele Nachkommastellen hat. In folgenden Beispiel wird auf eine Nachkommastelle gerundet.

.. code-block:: yaml

    item:
        type: num
        eval: round(value, 1)
        
**Wertermittung durch Datenbankabfrage**

Mit Hilfe eines **eval** kann auch eine Datenbankabfrage (Plugin **database**) realisiert werden. Im folgenden Beispiel wird täglich um 0:01 Uhr das **eval** ausgeführt und der Wert ermittelt.

.. code-block:: yaml

    item:
        type: num
        eval: 
        crontab: 0 1 * *

**Wert invertieren**

Mit Hilfe eines **eval** kann der Wert einfach invertiert werden. Man bedient sich wieder dem **value**, also dem "Zwischenspeicher" bevor der Wert final dem Item zugewiesen wird

.. code-block:: yaml

    item:
        type: bool
        eval: not value

**Auslesen / Teilen von eines Dictionary**

Hier wird im dictonary des Item 'input' nach den Schlüsseln 'RfReceived' und 'RfKey' gesucht. Ist dieser 
gleich 4 wird, das item 'received_key4' auf True gesetzt.

.. code-block:: yaml

    input:
        type: dict
        cache: yes
        received_key4:
            type: bool
            eval: 1 if int(sh...()['RfReceived']['RfKey']) == 4 else None
            eval_trigger: ..

**Erzeugen eines String aus den Werten anderer Items**

Hier wird aus den 3 Werten der Unteritems ein formatierter String gebildet. Dies wird u.a. für Farbsteuerungen benötigt.

.. code-block:: yaml

    HSB:
        type: str
        eval: "'{0},{1},{2}'.format(sh...Hue(), sh...Sat(), sh...Bright())"
        eval_trigger:
          - .Hue
          - .Sat
          - .Bright

        Hue:
            type: num
            cache: yes
            visu_acl: rw
        
        Sat:
            type: num
            cache: yes
            visu_acl: rw
        
        Bright:
            type: num
            cache: yes
            visu_acl: rw
            
            
**Erzeugen einer Liste aus den Werten anderer Items**

Hier wird aus den 3 Werten der Unteritems eine Liste gebildet. Dies wird u.a. für Farbsteuerungen benötigt.

.. code-block:: yaml            
            
            
    rgb:
        name: RGB
        type: list
        cache: yes
        eval: "[sh..r(), sh..g(), sh..b()]"
        eval_trigger:
          - .r
          - .g
          - .b
        
        r:
            name: Wert für Rot
            type: num
            cache: yes
            visu_acl: rw

        g:
            name: Wert für Grün
            type: num
            cache: yes
            visu_acl: rw

        b:
            name: Wert für Blau
            type: num
            cache: yes
            visu_acl: rw

**Enumeration über Liste**

.. code-block:: yaml

    heizung_status:
        name: numerischer Heizungsstatus (0 -> "Ausgeschaltet", 1 -> "Heizung startet", 2 -> "Heizung läuft")
        type: num

        heizung_status_string:
            type: str
            eval: ['Ausgeschaltet','Heizung startet','Heizung läuft'][value]
            eval_trigger: ..


Hier wird basierend auf dem Wert eines Items 'windBearing', dass die Windrichtung als Wert in Grad erhält, mit einem eval die Windrichtung bestimmt. Dazu wird aus einer Liste der Himmelsrichtungen, mit entspechender Umwandlung der Windrichtung, gewählt und dem Item zugewiesen.

.. code-block:: yaml

    windBearing:
        type: num
        ds_matchstring: currently/windBearing
        cache: yes
            
        windBearing_compass_string:
            type: str
            eval: "['N','NO','O','SO','S','SW','W','NW','N'][(int(value) + 22.5) / 45]"
            eval_trigger: ..

**Enumeration über Diconary mit Lockup-Item**

.. code-block:: yaml
    
    aktuelleregeneration:
        name: Aktueller Regenerationsschritt als num
        type: num
 
        text:
            name: Aktueller Regenerationsschritt als String
            type: str
            eval: [sh..lookup()][value]
            eval_trigger: ..
            
            lookup:
                type: dict
                initial_value: { 0: 'keine Regeneration', 1: 'Soletank füllen', 2: 'Besalzen', 3: 'Verdrängen', 4: 'Rückspülen', 5: 'Auswaschen' }

**Basierend auf einem numerischen Wert einen boolschen erzeugen**

Hier wird basierend auf dem Wert eines num Items, der Wert für ein korrespondierendes bool-Item erzeugt. Das bool Item ist TRUE, wenn der Wert des passenden num-Items > 0 ansonsten FALSE.

.. code-block:: yaml

    stellgr_rueckmeldung:
        type: num
        knx_dpt: '5.001'
        knx_cache: 0/3/68
    
        stellgr_rueckmeldung_bool:
            type: bool
            eval: value
            eval_trigger: ..

**Basierend auf dem Wert eines numerischen andere Items setzen**

Bei dem folgenden Beispiel werden basierend auf dem Wert des Items "Sollzustand" die Items "FolgeA", "FolgeB", "FolgeC" und "FolgeD" gesetzt.
Änderungen des Items "Sollzustand" löst für die Folgeitems den **eval_trigger** aus und übergibt seinen Wert als "value" and diese. Im **eval** wird nun die Bedingung basierend auf "value" geprüft, und das Item entsprechend gesetzt.
Für das Item "FolgeA" bedeutet es konkret: Ändert sich das Wert von "Sollzustand", wird die Neuberechnung des Items "FolgeA" angestoßen und der Wert von "Sollzustand" wird als "value" mit übergeben. Das eval ergibt TRUE, wenn "value" einer 2 entspricht, ansonsten FALSE.

.. code-block:: yaml

    Sollzustand:
        type: num
        
        FolgeA:
            type: bool
            eval: value == 2
    ​​​​​​​        eval_trigger: ..
        
        FolgeB:
            type: bool
            eval: value == 3
    ​​​​​​​        eval_trigger: ..
        
        FolgeC:
            type: bool
            eval: value == 4
    ​​​​​​​        eval_trigger: ..
        
        FolgeD:
            type: bool
            eval: value == 5
    ​​​​​​​        eval_trigger: ..

**Berechnung einer Zeitdauer in Sekunden von beliebigen datetime bis jetzt**

In diesem Beispiel wird die Dauer eines **autotimer** mit einem **eval** aus einem **datetime** Wertes eines Hilfsitem berechnet.
Die Berechnung des Item "laufzeit_autotimer" wird durch Änderungen im Item "enddatetime_autotimer" getriggert und berechnet die Zeitdauer in Sekunden zwischen dem Wert (datetime im ISO-format) des Items "enddatetime_autotimer" und jetzt.
Dieser errechnete Wert wird dann als Dauer für den **autotimer** verwendet.

.. code-block:: yaml

    abwesenheit:
        type: num
        autotimer: sh.heizung.abwesenheit.laufzeit_autotimer() = 1
        
        laufzeit_autotimer:
            name: Dauer des Autotimer in Sekunden
            type: num
            eval: int((datetime.datetime.strptime(sh.heizung.abwesenheit.enddatetime_autotimer(), '%Y-%m-%dT%H:%M:%S') - datetime.datetime.now()).total_seconds())
            eval_trigger: abwesenheit.enddatetime_autotimer
          
        enddatetime_autotimer:
            name: Datetime für Ende des Standby
            type: str
            cache: yes

**Importieren weitere Python Module in ein eval**

Hier ein Beispiel, wie man weitere (nicht standardmäßig verfügbare) Python Module für ein eval importiert.

.. code-block:: yaml

    boost_remaining_a:
        type: num
        eval: __import__('math').ceil(sh.ventilation.booster.logics.boost_duration()/60)
        eval_trigger = ventilation.booster.logics.boost_duration
        
        
**Verwendung der ItemFunktion timer**

siehe https://knx-user-forum.de/forum/supportforen/smarthome-py/1447847-autotimer-sperren-garage-automatisch-zu


.. code-block:: yaml

    tor:
        vorne:
            aufzu:
                name: Tor vorne
                type: bool
                cache: yes
                # nach 10 Minuten automatisch runter
                autotimer: 10m = 1


**Countdown für Timer bzw. Autotimer**

siehe https://knx-user-forum.de/forum/supportforen/smarthome-py/1403134-countdown-f%C3%BCr-timer-bzw-autotimer

 - Item das den Bewässerungskreis (Lampe, ...) schaltet. In meinem Fall ist das das Item "Rundbeet"
 - Item über das ich in der Visu die Dauer setze
 - Item das zyklisch die Restdauer berechnet in dem es das Alter des Items zwei Ebenen höher von dem Wert des Items eine Ebene höher abzieht. Da dies ständig geschiet, wird die Häufigkeit der Berechnung über **cycle** (hier alle 10s) gesteuert.

.. code-block:: yaml

    Bewaesserung:
        OnOff:
            type: bool
            autotimer: sh..Dauer() = false
            visu_acl: rw
            enforce_updates: 'true'
          
            Dauer:
                type: num
                cache: true
                visu_acl: rw
                enforce_updates: 'true'
              
                Rest:
                    type: num
                    visu_acl: ro
                    enforce_updates: 'true'
                    eval: sh...() - sh....age() if sh....() else 0
                    eval_trigger: ...                  
                    cycle: 10
                    
**Item mit verzögertem Status**

siehe https://knx-user-forum.de/forum/supportforen/smarthome-py/1430942-item-mit-verz%C3%B6gertem-status

Das folgende Beispiel setzt das Item "out":
 - Wenn Item in = True wird, soll Item out = True werden
 - Wenn Item in = False wird, soll Item out in 5 Sekunden = False werden. Wird IN vor 5 Sekunden wieder True, soll out nicht False werden.

.. code-block:: yaml

    in:
        type: bool 
        on_change:
            - sh.out.timer(0,1) if value else sh.out.timer(5,0)
            
    out:
        type: bool
    
**Konsolidieren von Itemwerten**

siehe https://knx-user-forum.de/forum/supportforen/smarthome-py/1346543-eval-und-autotimer

Das folgende Beispiel zeigt, wie aus 5 Präsenzmelderrückmeldungen der Anwesenheitsstatus ermittelt werden. Die Präsenzmelder senden immer True, wenn Präsenz da ist (es wird keine False gesendet).

Konkret wird das Item "anwesend" 10 min nachdem der letzte Präsenzmelder ein TRUE gesendet hat. Bei jedem **eval_trigger** wird der **autotimer** neu gestartet.

.. code-block:: yaml

    anwesend:
        type: bool
        autotimer = 10m = 0
        eval: value
        eval_trigger:
        -   pm1.meldung
        -   pm2.meldung
        -   pm3.meldung
        -   pm4.meldung
        -   pm5.meldung
        
**Item Änderung nach bestimmter Zeit**

siehe: https://knx-user-forum.de/forum/supportforen/smarthome-py/1270756-item-%C3%A4nderung-in-bestimmter-zeit-ohne-cron

Das Beispiel zeigt, die Ermittung einer Wertabweichung (Luftfeuchtigkeit) innerhalb einer definierten Zeit (5 min) um mehr als 5%. 
Das Wichtigste steckt im Item "Luftfeuchte.Abweichung":
- es wird alle 5 Minuten mit **cycle** getriggert
- es wird erstmal im **eval** berechnet, wie die Abweichung zum letzten gemerkten Luftfeuchte-Wert ist (und falls noch kein Wert von vor 5 Minuten da ist, bleibt es bei 0)
- Anschließend wird der aktuelle Luftfeuchte-Wert gemerkt **on_update** (der wird dann ja in 5 Minuten wieder gebraucht).

.. code-block:: yaml

    Luftfeuchte:
        name: Aktuelle Luftfeuchte
        type: num
        knx_dpt: 5.001
        knx_listen: ...
        Vor5Minuten:
            name: Luftfeuchte vor 5 Minuten
            type: num
        Abweichung:
            name: Abweichung in %
            type: num
            cycle: 5m = 1
            eval: sh.Luftfeuchte.Vor5Minuten() - sh.Luftfeuchte() if sh.Luftfeuchte.Vor5Minuten() > 0 else 0
            on_update: Luftfeuchte.Vor5Minuten = sh.Luftfeuchte()
        MehrAls5Prozent:
            name: Abweichung größer gleich 5 Prozent
            type: bool
            eval: sh.Luftfeuchte.Abweichung() >= 5 or sh.Luftfeuchte.Abweichung() <= -5
            eval_trigger: Luftfeuchte.Abweichung