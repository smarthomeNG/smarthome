
.. index:: Stateengine; Bedingungen
.. _Bedingungen:

===========
Bedingungen
===========

Beispiel
--------

Im folgenden Beispiel wird der Zustand "Daemmerung" eingenommen, sobald
die Helligkeit (über se_item_brightness definiert) über 500 Lux liegt.

.. code-block:: yaml

   #items/item.yaml
   raffstore1:
       automatik:
           struct: stateengine.general
               rules:
                   se_item_brightness: beispiel.wetterstation.helligkeit
                   Daemmerung:
                       name: Dämmerung
                       remark: <Aktionen>
                       enter:
                          se_min_brightness: 500

Bedingungsgruppen
-----------------

Unabhängig davon, ob ein Zustand von nur einer Bedingung oder mehreren Bedingungen
abhängt, werden Bedingungen immer als Attribute unter ein Item gestellt, das
``enter`` heißt. Bei mehreren Bedingungsgruppen kann noch ein beliebiger Name,
getrennt durch einen Unterstrich "_" hinzugefügt werden. Das Bedinungsgruppen-Item
könnte dann ``enter_zuhell`` heißen. Der Name ist dabei völlig beliebig und nimmt
keinen Bezug auf irgendwelche anderen Elemente.

Die folgenden Regeln kommen zur Anwendung:

-  Zustände und Bedingungsgruppen werden in der Reihenfolge
   geprüft, in der sie in der Konfigurationsdatei definiert sind.

-  Eine einzelne Bedingungsgruppe ist erfüllt, wenn alle
   Bedingungen, die in der Bedingungsgruppe definiert sind,
   erfüllt sind (UND-Verknüpfung).

-  Ein Zustand kann aktueller Zustand werden, wenn eine beliebige
   der definierten Bedingungsgruppen des Zustands erfüllt ist. Die
   Prüfung ist mit der ersten erfüllten Bedingungsgruppe beendet
   (ODER-Verknüpfung).

-  Ein Zustand, der keine Bedingungsgruppen hat, kann immer
   aktueller Zustand werden. Solch ein Zustand kann als
   Default-Zustand am Ende der Zustände definiert werden.

Wertevergleich
--------------

Der zu vergleichende Wert einer Bedingung kann auf folgende Arten definiert werden:

- statischer Wert (also z.B. 500 Lux). Wird angegegeben mit ``value:500``, wobei das value: auch weggelassen werden kann.
- Item (beispielsweise ein Item namens settings.helligkeitsschwellwert). Wird angegeben mit ``item:settings.helligkeitsschwellwert``
- Eval-Funktion (siehe auch `eval Ausdrücke <https://www.smarthomeng.de/user/referenz/items/standard_attribute/eval.html>`_). Wird angegeben mit ``eval:1*2*se_eval.get_relative_itemvalue('..bla')``
- Regular Expression (siehe auch ` RegEx Howto <https://docs.python.org/3.7/howto/regex.html#regex-howto>`_) - Vergleich mittels re.fullmatch, wobei Groß/Kleinschreibung ignoriert wird. Wird angegeben mit ``regex:StateEngine Plugin:(.*)``
- Template: eine Vorlage, z.B. eine eval Funktion, die immer wieder innerhalb
  des StateEngine Items eingesetzt werden kann. Angegeben durch ``template:<Name des Templates>``


Name der Bedingung
------------------

Der Name einer Bedingung setzt sich aus folgenden drei Teilen zusammen,
die jeweils mit einem Unterstrich "_" getrennt werden:

- ``se_``: eindeutiger Prefix, um dem Plugin zugeordnet zu werden
- ``<Vergleichsfunktion>``: siehe unten. Beispiel: min = der Wert des <Bedingungsitems> muss mindestens dem beim Attribut angegebenen Wert entsprechen.
- ``<Vergleichsitem/Bedingungsname>``: Hier wird entweder das im Regelwerk-Item mittels ``se_item_<Name>`` deklarierte Item oder eine besondere Bedingung (siehe unten) referenziert.


Templates für Bedingungsabfragen
--------------------------------

Setzt man für mehrere Bedingungsabfragen (z.B. Helligkeit, Temperatur, etc.) immer die
gleichen Ausdrücke ein (z.B. eine eval-Funktion), so kann Letzteres als Template
definiert und referenziert werden. Dadurch wird die  Handhabung
komplexerer Abfragen deutlich vereinfacht. Diese Templates müssen wie se_item/se_eval
auf höchster Ebene des StateEngine Items (also z.B. rules) deklariert werden.

.. code-block:: yaml

    rules:
      se_template_test: eval:sh...settings.max_bright' - 20
      se_item_specialitem: meinitem.specialitem # declare an existing item here

      state_one:
          enter_testlast: #has to start with enter, can be called whatever
              se_value_laststate: 'template:test' #laststate is a special conditionname
          enter_testother:
              se_value_specialitem: 'template:test' #specialitem must be declared with se_item/se_eval

Bei sämtlichen Bedingungen ist es möglich, Werte als Liste anzugeben. Es ist allerdings
nicht möglich, Templates als Listen zu definieren.


Bedingungslisten
----------------

Sämtliche nun gelisteten Bedingungen können entweder eine einzelne Angabe haben
oder aus einer Liste mit mehreren Bedingungen bestehen.
In letzterem Fall fungiert die Liste als ODER Abfrage. Sobald eine der gelisteten
Werte eingetroffen ist, wird die Bedingung als wahr angenommen
und der Zustand aktiviert.

.. code-block:: yaml

      se_value_laststate:
          - 'kochen'
          - 'eval:1+2'
          - 'regex:Nachfuehren(.*)'
          - 'item:..laststate_id'

Im oben gezeigten Beispiel kann der letzte Status einen von drei Werten beinhalten,
damit die Bedingung wahr ist. In welcher Form diese Werte
angegeben werden, ist offen - es müssen also nicht nur reine Strings in die
Liste eingefügt werden.

Werden sowohl min(age) als auch max(age) als Liste definiert, spielt die
Reihenfolge der Liste eine Rolle, da die beiden Werte als Paar herangezogen werden.

.. code-block:: yaml

      se_minage_<Bedingungsname>:
          - '5'
          - 'eval:1+2'
          - 'novalue'

      se_maxage_<Bedingungsname>:
         - '10'
         - 'eval:5*sh.meinwert()'
         - 'item:EinzweitesItem'

Obige Bedingung wird beispielsweise wahr bei:
- einem Wert zwischen 5 und 10
- einem Wert zwischen 3 und 5 * der Wert des Items meinwert
- einem Wert maximal so hoch wie der in EinzweitesIem hinterlegte


Vergleichsfunktion
------------------

**Minimum**

.. code-block:: yaml

       se_min_<Bedingungsname>: [Wert]

Die Bedingung ist erfüllt, wenn der aktuelle Wert größer als das
angegebene Minimum ist.

**Maximum**

.. code-block:: yaml

       se_max_<Bedingungsname>: [Wert]

Die Bedingung ist erfüllt, wenn der aktuelle Wert kleiner als das
angegebene Maximum ist.

**Bestimmter Wert**

.. code-block:: yaml

       se_value_<Bedingungsname>: [Wert]

Die Bedingung ist erfüllt, wenn der aktuelle Wert gleich dem
angegebenen Wert oder gleich einem der in einer Liste angegebenen Wert ist.

.. code-block:: yaml

       se_value_<Bedingungsname>:
          - [Wert1]
          - [Wert2]
          - [WertN]

**Negieren**

.. code-block:: yaml

       se_negate_<Bedingungsname>: True|False

Die gesamte Bedingung (Minimum, Maximum und Wert) wird negiert
(umgekehrt). Für das Attribut wird der Datentyp Boolean verwendet,
zulässige Werte sind "true", "yes", "on" bzw. "false", "no", "off"

**Aktualisierung des Items durch**

.. code-block:: yaml

       se_updatedby_<Bedingungsname>: [Wert]

Die Bedingung ist erfüllt, wenn das Item durch den angegebenen Wert bzw.
einen der angegebenen Werte geändert wurde. Hier bietet es sich an,
den Wert als Regular Expression mittels ``se_updatedby_<Bedingungsname>: regex:StateEngine Plugin`` zu definieren.
Die Werte(liste) kann auch durch ``se_updatedbynegate_<Bedingungsname>`` negiert werden.

.. code-block:: yaml

       se_updatedby_<Bedingungsname>:
          - [Wert1]
          - [Wert2]
          - regex:[WertN]

       se_updatedbynegate_<Bedingungsname>: True|False

**Änderung des Items durch**

.. code-block:: yaml

       se_changedby_<Bedingungsname>: [Wert]

Die Bedingung ist erfüllt, wenn das Item durch den angegebenen Wert bzw.
einen der angegebenen Werte geändert wurde. Hier bietet es sich an,
den Wert als Regular Expression mittels ``se_changedby_<Bedingungsname>: regex:StateEngine Plugin`` zu definieren.
Die Werte(liste) kann auch durch ``se_changedbynegate_<Bedingungsname>`` negiert werden.

.. code-block:: yaml

       se_changedby_<Bedingungsname>:
          - [Wert1]
          - [Wert2]
          - regex:[WertN]

       se_changedbynegate_<Bedingungsname>: True|False


**Mindestalter**

.. code-block:: yaml

       se_agemin_<Bedingungsname>: [Wert]

Die Bedingung ist erfüllt, wenn das Alter des Items, das zur
Ermittlung des Werts angegeben ist, größer als das angegebene
Mindestalter ist. Die age Bedingungen sollten immer mit einer value Bedingung verknüpft werden
(z.B. ``se_value_<Bedingungsname>: True``)

**Höchstalter**

.. code-block:: yaml

       se_agemax_<Bedingungsname>: [Wert]

Die Bedingung ist erfüllt, wenn das Alter des Items, das zur
Ermittlung des Werts angegeben ist, kleiner als das angegebene
Höchstalter ist. Die age Bedingungen sollten immer mit einer value Bedingung verknüpft werden
(z.B. ``se_value_<Bedingungsname>: True``)

**Altersbedingung negieren**

.. code-block:: yaml

       se_agenegate_<Bedingungsname>: True|False

Die Altersbedingung (Mindestalter, Höchstalter) wird negiert
(umgekehrt). Für das Attribut wird der Datentyp Boolean verwendet,
zulässige Werte sind "true", "1", "yes", "on" bzw. "false", "0",
"no", "off"


"Besondere" Bedingungen
-----------------------

Das Plugin stellt die Werte für einige "besondere" Bedingungen
automatisch bereit. Für diese Bedingungen muss daher kein Item und
keine Eval-Funktion zur Ermittlung des aktuellen Werts angegeben
werden. Die "besonderen" Bedingungen werden über reservierte
Bedingungsnamen gekennzeichnet. Diese Bedingungsnamen dürfen daher
nicht für andere Bedingungen verwendet werden.

Die folgenden "besonderen" Bedingungsnamen können verwendet werden

**time**
*Aktuelle Uhreit*
Die Werte für ``se_value_time``, ``se_min_time`` und
``se_max_time`` müssen im Format "hh:mm" (":") angegeben werden.
Es wird ein 24 Stunden-Zeitformat verwendet. Beispiele: "08:00"
oder "13:37". Um das Ende des Tages anzugeben kann der Wert
"24:00" verwendet werden, der für die Prüfungen automatisch zu
"23:59:59" konvertiert wird. Wichtig sind die Anführungszeichen
oder Hochkommas!

**weekday**
*Wochentag*
0 = Montag, 1 = Dienstag, 2 = Mittwoch, 3 = Donnerstag, 4 =
Freitag, 5 = Samstag, 6 = Sonntag

**month**
*Monat*
1 = Januar, ..., 12 = Dezember

**sun_azimut**
*Sonnenstand (Horizontalwinkel)*
Der Azimut (Horizontalwinkel) ist die Kompassrichtung, in der die
Sonne steht. Der Azimut wird von smarthomeNg auf Basis der
aktuellen Zeit sowie der konfigurierten geographischen Position
berechnet. Siehe auch `Dokumentation <https://www.smarthomeng.de/user/logiken/objekteundmethoden_sonne_mond.html>`_
für Voraussetzungen zur Berechnung der Sonnenposition.
Beispielwerte: 0 → Sonne exakt im Norden, 90 → Sonne exakt im
Osten, 180 → Sonne exakt im Süden, 270 → Sonne exakt im Westen

**sun_altitude**
*Sonnenstand (Vertikalwinkel)*
Die Altitude (Vertikalwikel) ist der Winkel, in dem die Sonne über
dem Horizont steht. Die Altitude wird von smarthomeNG auf Basis
der aktuellen Zeit sowie der konfigurierten geographischen
Position berechnet. Siehe auch `SmarthomeNG
Dokumentation <https://www.smarthomeng.de/user/logiken/objekteundmethoden_sonne_mond.html>`_
für Voraussetzungen zur Berechnung der Sonnenposition. Werte:
negativ → Sonne unterhalb des Horizonts, 0 →
Sonnenaufgang/Sonnenuntergang, 90 → Sonne exakt im Zenith
(passiert nur in äquatorialen Bereichen)

**age**
*Zeit seit der letzten Änderung des Zustands (Sekunden)*
Das Alter wird über die letzte Änderung des Items, das als
``se_laststate_item_id`` angegeben ist, ermittelt.

**condition_age**
*Zeit seit der letzten Änderung des Bedingungssets (Sekunden)*
Das Alter wird über die letzte Änderung des Items, das als
``se_lastconditionset_item_id`` angegeben ist, ermittelt.

**random**
*Zufallszahl zwischen 0 und 100*
Wenn etwas zufällig mit einer Wahrscheinlichkeit von 60% passieren
soll, kan beispielsweise die Bedingung ``se_max_random: 60``
verwendet werden.

**laststate**
*Id des Zustandsitems des aktuellen Status*
Die Abfrage se_value_laststate ist besonders wichtig für
Bedingungsabfragen, die über das Verbleiben im aktuellen Zustand
bestimmen (z.b. enter_stay). So können aber auch Stati übersprungen
werden, wenn sie nicht nach einem bestimmten anderen Zustand aktiviert
werden sollen.
Wichtig: Hier muss die vollständige Item-Id angegeben werden

**lastconditionset_id/name**
*Id des Bedingungssets des aktuellen Status*
Wie bei laststate sind auch die lastconditionset Bedingungsabfragen
primär relevant für Abfragen zum Verbleiben in einem Zustand. Gerade bei
komplexeren Bedingungssets macht es oftmals Sinn, nach dem Set zu fragen,
das denn nun wirklich für die letzte Zustandsbestimmung relevant war.

**trigger_item, trigger_caller, trigger_source, trigger_dest**
*item, caller, source und dest-Werte, durch die die
Zustandsermittlung direkt ausgelöst wurde*
Über diese vier Bedingungen kann der direkte Auslöser der
Zustandsermittlung abgeprüft werden, also die Änderung, die
smarthomeNG veranlasst, die Zustandsermittlung des
stateengine-Plugins aufzurufen.

**original_item, original_caller, original_source**
*item, caller, source und dest-Werte, durch die die
Zustandsermittlung ursprünglich ausgelöst wurde*
Über diese vier Bedingungen kann der ursprüngliche Auslöser der
Zustandsermittlung abgeprüft werden. Beim Aufruf der
Zustandsermittung über einen ``eval_trigger`` Eintrag wird über
``trigger_caller`` beispielsweise nur ``Eval`` weitergegeben.
In den drei ``original_*`` Bedingungen wird in diesem Fall der
Auslöser der Änderung zurückverfolgt und der Einstieg in die
``Eval``-Kette ermittelt.
