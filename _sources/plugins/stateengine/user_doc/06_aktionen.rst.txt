
.. index:: Stateengine; Aktionen
.. _Aktionen:

========
Aktionen
========

Es gibt zwei Möglichkeiten, Aktionen zu definieren. Die :ref:`Aktionen - einzeln`
Variante wird am Ende der Dokumentation der Vollständigkeit halber beschrieben.
Für einfache Aktionen ohne Angabe zusätzlicher Attribute wie delay, order, repeat, etc.
kann diese andere Möglichkeit der Aktionsangabe durchaus Sinn machen. Sie wurde
allerdings in der weiteren Pluginentwicklung nicht mehr getestet.

Bei der hier beschriebenen kombinierten Variante zur Definition von Aktionen werden
alle Parameter einer Aktion in einem Attribut definiert. Der Aktionsname ``se_action_<Bedingungsname/Aktionsname>``
bezieht sich dabei auf das Item, das über ``se_item_<Bedingungsname/Aktionsname>`` unter dem Regelwerk-Item
definiert und benannt wurde. Die Herangehensweise ähnelt also stark der Deklaration von Bedingungen.

Zusätzlich zu ``se_item_<Bedingungsname/Aktionsname>`` lässt sich über den Eintrag
``se_mindelta_<Bedingungsname/Aktionsname>`` definieren, um welchen Wert
sich ein Item mindestens geändert haben muss, um neu gesetzt zu werden. Im unten
stehenden Beispiel wird der Lamellenwert abhängig vom Sonnenstand berechnet. Ohne mindelta
würden sich die Lamellen ständig um wenige Grad(bruchteile) ändern. Wird jedoch mindelta
beispielsweise auf den Wert 10 gesetzt, findet eine Änderung erst statt, wenn sich der
errechnete Wert um mindestens 10 Grad vom aktuellen Lamellenwert unterscheidet.

Beispiel zu Aktionen
--------------------

Das folgende Beispiel führt je nach Zustand folgende Aktionen aus:

- Daemmerung: Höhe des Raffstores: 100(%), Lamellendrehung: 25(%)
- Nachfuehren: Höhe des Raffstores: 100(%), Lamellendrehung: je nach Sonnenausrichtung, aber erst, wenn eine Mindeständerung von 10 Grad vorhanden ist.
- Sonder: Ausführen der Logic myLogic mit dem Wert 42 und einer Verzögerung von 10 Sekunden.

.. code-block:: yaml

    #items/item.yaml
    raffstore1:
        automatik:
            struct: stateengine.general
            rules:
                se_item_height: raffstore1.hoehe # Definition des zu ändernden Höhe-Items
                se_item_lamella: raffstore1.lamelle # Definition des zu ändernden Lamellen-Items
                se_mindelta_lamella: 10 # Mindeständerung von 10 Grad, sonst werden die Lamellen nicht aktualisiert.
                Daemmerung:
                    <...>
                    se_action_height:
                        - 'function: set'
                        - 'to: value:100'
                    se_action_lamella:
                        - 'function: set'
                        - 'to: value:25'
                    <...>
                Nachfuehren:
                    <...>
                    se_action_height:
                        - 'function: set'
                        - 'to: value:100'
                    se_action_lamella:
                        - 'function: set'
                        - 'to: eval:se_eval.sun_tracking()'
                    <...>
                Sonder:
                    <...>
                    se_action_logic1:
                        - 'function: trigger'
                        - 'logic: myLogic'
                        - 'value: 42'
                        - 'delay: 10'
                    <...>

Aufbau von Aktionen
-------------------

Bei yaml Files werden die Parameter mittels Aufzählungszeichen "-"
untereinander definiert, die Listeneinträge müssen in Anführungszeichen oder
Hochkommas gesetzt werden:

.. code-block:: yaml

    se_action_<Aktionsname>:
       - 'function: <func>'
       - Detailparameter der Funktion, z.B. "to: .."
       - 'delay: <delay>'
       - 'order: <order>'
       - 'repeat: <repeat>'
       - 'conditionset: <conditionset regex>'

Auszuführende Aktionsart
------------------------

Mit dem Parameter ``<func>`` wird die auszuführende Funktion
festgelegt. In Abhängigkeit zur gewählten Funktion werden
zusätzliche Detailparameter erforderlich.
Folgende Werte sind möglich:

**Funktion set: Item auf einen Wert setzen**

.. code-block:: yaml

   se_action_<Aktionsname>:
       - 'function: set'
       - 'to: <val>/<eval>/<var>/<item>'
       - 'force: [True/False]'

Das Item, das verändert werden soll, muss auf Ebene des
Regelwerk-Items über das Attribut ``se_item_<Aktionsname>``
oder ``se_eval_<Aktionsname>`` angegeben werden.

Der Parameter ``to: <val>`` legt fest, auf welchen Wert das Item
gesetzt werden soll. Der Wert,
auf den das Item gesezt wird, kann als statischer Wert, als
Wert eines Items oder als Ergebnis der Ausführung einer Funktion
festgelegt werden. Wichtig ist, dass bei z.B. ``to: item:<item>``
nach dem item: kein Leerzeichen eingesetzt werden darf!

Wie bei den Bedingungen sind die entsprechenden Prefixe value, item, eval zu nutzen:
- statischer Wert, beispielsweise ``value:500``, wobei das value: auch weggelassen werden kann.
- Item, z.B. ``item:settings.helligkeitsschwellwert``
- Eval-Funktion wie ``eval:1*2*se_eval.get_relative_itemvalue('..bla')``
- Template: eine Vorlage, z.B. ``template:<Name des Templates>``

Über den optionalen Parameter
``force: True`` kann eine Item-Aktualisierung erzwungen werden,
auch wenn sich der Wert nicht ändert. Damit erfolgt auf jeden Fall eine
Wertänderung (ggf. sogar zwei) mit allen damit in Zusammenhang
stehenden Änderungen (evals, Aktualisierung der Änderungszeiten,
etc).

**Funktion add: Wert zu einem Listenitem hinzufügen**

.. code-block:: yaml

   se_action_<Aktionsname>:
       - 'function: add'
       - 'value: <val>/<eval>/<var>/<item>'
       - 'force: [True/False]'

Das Item, das verändert werden soll, muss auf Ebene des
Regelwerk-Items über das Attribut ``se_item_<Aktionsname>`` oder
``se_eval_<Aktionsname>`` angegeben werden.

Der Parameter ``value: <val>`` legt fest, welcher Wert zum Item
mit dem Typ ``list`` hinzugefügt werden soll. Wird hier direkt ein
Wert angegeben, ist darauf zu achten, dass ein String unter Anführungszeichen
stehen muss, während eine Zahl das nicht sollte.

**Funktion remove: Wert von einem Listenitem entfernen**

.. code-block:: yaml

   se_action_<Aktionsname>:
       - 'function: remove'
       - 'value: <val>/<eval>/<var>/<item>'
       - 'mode: [first/last/all]'

Das Item, das verändert werden soll, muss auf Ebene des
Regelwerk-Items über das Attribut ``se_item_<Aktionsname>`` oder
``se_eval_<Aktionsname>`` angegeben werden.

Der Parameter ``value: <val>`` legt fest, welcher Wert vom Item
mit dem Typ ``list`` entfernt werden soll. Dabei ist zu beachten,
dass zwischen String (Anführungszeichen) und Zahlen unterschieden wird.
Ist der angegegeben Wert nicht in der Liste, wird der originale
Itemwert erneut geschrieben, ohne etwas zu entfernen. Über den Parameter
``mode`` lässt sich einstellen, ob jeweils alle mit dem Wert übereinstimmenden
Einträge in der Liste (mode: all) oder nur der erste (first) bzw. der letzte (last)
Eintrag gelöscht werden sollen. Wird der Parameter nicht angegeben, werden immer
alle passenden Einträge gelöscht.

**Funktion run: Ausführen einer Funktion**

.. code-block:: yaml

   se_action_<Aktionsname>:
       - 'function: run'
       - 'eval: (Funktion)'

Die Angabe ist vergleichbar mit dem Ausführen einer Funktion zur
Ermittlung des Werts für ein Item, hier wird jedoch kein Item
benötigt. Außerdem wird der Rückgabewert der Funktion ignoriert.

**Funktion trigger: Auslösen einer Logikausführung**

.. code-block:: yaml

   se_action_<Aktionsname>:
       - 'function: trigger'
       - 'logic: <Logikname>'
       - 'value: <val>/<eval>/<var>/<item>'

Löst die Ausführung der Logik ``<Logikname>`` aus. Um beim
Auslösen einen Wert an die Logik zu übergeben, kann dieser Wert
über die Angabe von ``value: <Wert>`` hinter dem Logiknamen
angegeben werden. Die Angabe kann aber auch entfallen.

**Funktion byattr: Alle Items mit bestimmtem Attribut auf einen Wert setzen**

.. code-block:: yaml

   se_action_<Aktionsname>:
       - 'function: byattr'
       - 'attribute: <Attributname>'

Mit dieser Funktion wird der Name eines anderen (beliebigen)
Attributs angegeben. Beim Ausführen werden alle Items
herausgesucht, die das angegebene Attribut enthalten. Diese Items
werden auf den Wert gesetzt, der dem genannten Attribut in den
Items jeweils zugewiesen ist.

.. code-block:: yaml

       dummy1:
               type: num
               <Attributname>: 42

dummy1 wird auf ``42`` gesetzt.
Ein anderes Item, dummy2,

.. code-block:: yaml

       dummy2:
               type: str
               <Attributname>: Rums

wird gleichzeitig auf ``Rums`` gesetzt.

**Funktion special: Sondervorgänge**

.. code-block:: yaml

   se_action_<Aktionsname>:
       - function: special
       - value: <Sondervorgang>

Für bestimmte Sondervorgänge sind besondere Aktionen im Plugin
definiert. Aktuell gibt es zwei besondere Vorgänge:

- suspend:<suspend_item>,<manuell_item> (z.B. suspend:..suspend,..manuell)
- retrigger:<trigger_item> (z.B. retrigger:..retrigger)

In den Beispielen wurden also die relativen Items suspend, manuell und retrigger referenziert.

Zusätzliche Parameter
---------------------

**delay: <int>**

Über den optionalen Parameter ``<delay>`` wird die Verzögerung angegeben, nach der die
Aktion ausgeführt werden soll.

Die Angabe erfolgt in Sekunden oder mit dem Suffix "m" in Minuten. Die Verzögerungszeit
kann auch durch ein eval oder Item zur Laufzeit berechnet werden.

.. code-block:: yaml

       'delay: <eval>/<item>' --> Ergebnis eines Eval-Ausdrucks oder eines Items
       'delay: 30'            --> 30 Sekunden
       'delay: 30m'           --> 30 Minuten

Der Timer zur Ausführung der Aktion nach der angegebenen
Verzögerung wird entfernt, wenn eine gleichartige Aktion
ausgeführt werden soll (egal ob verzögert oder nicht).

**instanteval: <bool>**

Über den optionalen Parameter ``<instanteval>`` wird für verzögerte Aktionen angegeben,
ob etwaige eval Ausdrücke sofort evaluiert und gespeichert werden sollen oder
die Evaluierung erst zum Ausführungszeitpunkt stattfinden soll.

.. code-block:: yaml

       'instanteval: [True|False]'

Beispiel: Ein Item soll auf einen Wert aus einem Item gesetzt werden. Das Item wird
anhand des gerade aktuellen Zustands durch ein eval eruiert:

.. code-block:: yaml

        eval:sh.return_item(se_eval.get_relative_itemid('..settings.{}'.format(se_eval.get_relative_itemvalue('..state_name'))))()

Angenommen, der aktuelle Zustand heißt ``regen``, so wird durch den obigen Code das Item
auf den Wert aus ``settings.regen`` gesetzt. Ändert sich aber während der Verzögerungszeit (delay)
der Zustand auf ``sonne``, würde zum Ausführungszeitpunkt der Aktion der Wert aus dem Item ``settings.sonne``
herangezogen werden. Wenn dies nicht erwünscht ist und das Item also auf den Vorgabewert des
ursprünglichen Zustands (regen) gesetzt werden soll, kann der Parameter ``instanteval: True`` gesetzt werden.

**repeat: <bool>**

.. code-block:: yaml

       'repeat: [True|False]'

Über das Attribut wird unabhängig vom globalen Setting für das
stateengine Item festgelegt, ob eine Aktion auch beim erneuten
Eintritt in den Status ausgeführt wird oder nicht. Das globale Setting
kann im Regelwerk Item unter rules durch ``se_repeat_actions: false`` dezidiert
auf False gesetzt werden. Standardmäßig, wenn das Attribut also nicht angegeben wird,
werden Aktionen wiederholt ausgeführt.

**order: <int>**

Die Reihenfolge, in der die Aktionen ausgeführt werden, ist nicht
zwingend die Reihenfolge in der die Attribute definiert sind. In
den meisten Fällen ist dies kein Problem, da oftmals die Aktionen
voneinander unabhängig sind und daher in beliebiger Reihenfolge
ausgeführt werden können. In Einzelfällen kann es jedoch
erforderlich sein, mehrere Aktionen in einer bestimmten
Reihenfolge auszuführen. Dies kann über den Parameter
``order: <order>`` erfolgen. Mit diesem Attribut wird der Aktion
eine Zahl zugewiesen, die als value, item oder eval vorliegen kann.
Aktionen werden in aufsteigender Reihenfolge der zugewiesenen Zahlen ausgeführt.

.. code-block:: yaml

       'order: [1|2|...]'

**conditionset: <conditionset regex>**

.. code-block:: yaml

      'conditionset: ["regex:enter_(.*)_test", "eval:sh.itemX.property.value"]'

Über das Attribut wird festgelegt, dass die Aktion nur dann ausgeführt werden
soll, wenn der Zustand durch die angegebene Bedingungsgruppe eingenommen wurde.
Zum Vergleich wird immer der volle Pfad (die ID) der Bedingungsgruppe herangezogen.
Conditionset erlaubt sowohl einzelne Werte mittels value, regex oder eval, als auch eine Liste.
Die Liste kann zum einen wie oben angeführt mit eckigen Klammern, als auch wie gewohnt mit
"-" in einzelnen Zeilen (siehe unten) angegeben werden. Wichtig ist, im ersten Fall reguläre Ausdrücke
unter Anführungszeichen zu setzen (und dann Hochkomma um den gesamten Eintrag). Im zweiten Fall sind keine
Anführungszeichen notwendig.

Die einzelnen Angaben einer Liste werden als ``OR`` evaluiert.

.. code-block:: yaml

screens:
    conditionset_to_check:
        type: str
        value: "screens.osten_s1.automatik.rules.abend.enter_abend"

      conditionset:
        - regex:enter_(.*)_test
        - eval:sh.screens.conditionset_to_check.property.name

Der gesamte Pfad könnte wie folgt evaluiert werden:

.. code-block:: yaml

      "eval:se_eval.get_relative_itemid('{}.<bedingungsset>'.format(se_eval.get_relative_itemvalue('..state_id')))"

Eine sinnvolle Anwendung hierfür wäre, anstelle von verschiedenen Zuständen mit
leicht anderen Bedingungen, alles in einen Zustand zu packen und anhand des Conditionsets
unterschiedliche Aktionen ausführen zu lassen. Ein ähnliches Setup könnte im gegebenen
Beispiel zwar auch mittels ``se_use`` umgesetzt werden, allerdings gibt es auch
andere Situationen, wo das komplizierter oder weniger zielführend wäre. Im Beispiel
wird abends die Höhe des Raffstores auf 100 gesetzt, falls es regnet. Falls es nicht
regnet hingegen auf den Wert, der in den Settings hinterlegt ist.

.. code-block:: yaml

    abend:
        on_enter_or_stay:
            se_action_hoehe:
              - 'function: set'
              - 'to: item:..settings.abend.hoehe'
              - 'order: 1'
              - 'conditionset: regex:(.*)enter(?!_regen)(.*)'
            se_action_hoehe_regen:
              - 'function: set'
              - 'to: 100'
              - 'order: 1'
              - 'conditionset: regex:(.*)enter_regen'

        enter_normal:
            diverse Bedingungen

        enter_regen:
            diverse andere Bedingungen

**previousconditionset: <conditionset regex>**

.. code-block:: yaml

      previousconditionset: regex:enter_(.*)_test"

Über das Attribut wird festgelegt, dass die Aktion nur dann ausgeführt werden
soll, wenn die vorherige Bedingungsgruppe des aktuellen Zustands mit dem angegebenen Ausdruck übereinstimmt.
Die Abfrage erfolgt dabei nach den gleichen Regeln wie bei ``conditionset`` oben angegeben.

**previousstate_conditionset: <conditionset regex>**

.. code-block:: yaml

      previousstate_conditionset: regex:enter_(.*)_test"

Über das Attribut wird festgelegt, dass die Aktion nur dann ausgeführt werden
soll, wenn die Bedingungsgruppe, mit der der vorherige Zustand eingenommen wurde, mit dem angegebenen Ausdruck übereinstimmt.
Die Abfrage erfolgt dabei ebenfalls nach den gleichen Regeln wie bei ``conditionset`` oben angegeben.

Templates für Aktionen
----------------------

Setzt man für mehrere Aktionen (z.B. Setzen auf einen Wert abhängig vom aktuellen
Zustand) immer die gleichen Ausdrücke ein, so kann Letzteres als Template
definiert und referenziert werden. Dadurch wird die Handhabung
komplexerer Wertdeklarationen deutlich vereinfacht. Diese Templates müssen wie se_item/se_eval
auf höchster Ebene des StateEngine Items (also z.B. rules) deklariert werden.

.. code-block:: yaml

    rules:
      se_template_test: se_eval.get_relative_itemid('wetterstation.helligkeit_{}'.format(se_eval.get_relative_itemvalue('..state_name')))
      se_item_specialitem: meinitem.specialitem # declare an existing item here

      state_one:
          on_enter:
              se_action_specialitem:
                  - 'function: set'
                  - 'to: template:test'
