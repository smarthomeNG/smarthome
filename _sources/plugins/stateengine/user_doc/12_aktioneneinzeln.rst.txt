
.. index:: Stateengine; Aktionen - einzeln
.. _Aktionen - einzeln:

==================
Aktionen - einzeln
==================

Es gibt zwei Möglichkeiten, Aktionen zu definieren.

Bei der Einzelvariante werden alle
Parameter einer Aktion in separaten Attributen definiert. Über den
gemeinsamen Aktionsnamen gehören die Attribute einer Aktion
zusammen.

Ähnlich wie Bedingungen benötigen auch Aktionen einen Namen. Der
Name ist auch hier beliebig und wird lediglich in der Benennung
der Attribute verwendet. Die Namen aller Attribute, die zu einer
Bedingung gehören, folgen dem Muster ``se_<Funktion>_<Aktionsname>``.

Definition der Aktion
---------------------

**Aktion set: Item auf einen Wert setzen**

.. code-block:: yaml

       se_set_<Aktionsname>: <val>/<eval>/<var>/<item>

Das Item, das verändert werden soll, muss auf Ebene des
Regelwerk-Items über das Attribut ``se_item_<Aktionsname>``
angegeben werden.

Der Wert, auf den das Item gesezt wird, kann als statischer Wert, als Wert eines
Items oder als Ergebnis der Ausführung einer Funktion festgelegt
werden.

**Aktion force: Item zwangsweise auf einen Wert setzen**

.. code-block:: yaml

       se_force_<Aktionsname>: <val>/<eval>/<var>/<item>

Diese Aktion funktioniert analog zu ``se_set_<Aktionsname>``.
Einziger Unterschied ist, dass die Wertänderung erzwungen wird:
Wenn das Item bereits den zu setzenden Wert hat, dann ändert
smarthomeNG das Item nicht. Selbst wenn beim Item das Attribut
``enforce_updates: yes`` gesetzt ist, wird zwar der Wert neu
gesetzt, der von smarthomeNG die Änderungszeit nicht neu gesetzt. Mit
dem Attribut ``se_force_<Aktionsname>`` wird das Plugin den Wert
des Items bei Bedarf zuerst auf einen anderen Wert ändern und dann
auf dem Zielwert setzen. Damit erfolgt auf jeden Fall eine
Wertänderung (ggf. sogar zwei) mit allen damit in Zusammenhang
stehenden Änderungen (eval's, Aktualisierung der Änderungszeiten,
etc).

**Aktion run: Ausführen einer Funktion**

.. code-block:: yaml

       se_run_<Aktionsname>: eval:(Funktion)

Die Angabe ist vergleichbar mit dem Ausführen einer Funktion zur
Ermittlung des Werts für ein Item, hier wird jedoch kein Item
benötigt. Außerdem wird der Rückgabewert der Funktion ignoriert.

**Aktion trigger: Auslösen einer Logikausführung**

.. code-block:: yaml

       se_trigger_<Aktionsname>: meineLogik:Zu übergebender Wert

Um beim Auslösen einen Wert an die Logik zu übergeben, kann dieser
Wert im Attribut über die Angabe von ``:<Wert>`` hinter dem
Logiknamen angegeben werden.

**Funktion byattr: Alle Items mit bestimmtem auf den Wert setzen**

.. code-block:: yaml

       se_byattr_<Aktionsname>: mein_eigenes_Attribut

Mit diesem Attribut wird der Name eines anderen (beliebigen)
Attributs angegeben. Beim Ausführen werden alle Items
herausgesucht, die das angegebene Attribut enthalten. Diese Items
werden auf den Wert gesetzt, der dem genannten Attribut in den
Items jeweils zugewiesen ist.

.. code-block:: yaml

       dummy:
               type: num
               mein_eigenes_Attribut: 42

wird dann auf ``42`` gesetzt.
Ein anderes Item

.. code-block:: yaml

       dummy2:
               type: str
               mein_eigenes_Attribut: Rums

wird gleichzeitig auf ``Rums`` gesetzt.

**Aktion add: Wert zu einem Listenitem hinzufügen**

.. code-block:: yaml

   se_add_<Aktionsname>: <val>/<eval>/<var>/<item>

Der Wert des Attributs legt fest, welcher Wert zum Item
mit dem Typ ``list`` hinzugefügt werden soll. Wird hier direkt ein
Wert angegeben, ist darauf zu achten, dass ein String unter Anführungszeichen
stehen muss, während eine Zahl das nicht sollte.

**Aktion remove: Wert von einem Listenitem entfernen**

.. code-block:: yaml

   se_remove_<Aktionsname>: <val>/<eval>/<var>/<item>

Der Wert des Attributs legt fest, welcher Wert vom Item
mit dem Typ ``list`` entfernt werden soll. Dabei ist zu beachten,
dass zwischen String (Anführungszeichen) und Zahlen unterschieden wird.
Ist der angegegeben Wert nicht in der Liste, wird der originale
Itemwert erneut geschrieben, ohne etwas zu entfernen. Über
``se_mode`` lässt sich einstellen, ob jeweils alle mit dem Wert übereinstimmenden
Einträge in der Liste (mode: all) oder nur der erste (first) bzw. der letzte (last)
Eintrag gelöscht werden sollen. Wird der Parameter nicht angegeben, werden immer
alle passenden Einträge gelöscht.

**Aktion special: Sondervorgänge**

.. code-block:: yaml

       se_special_<Aktionsname>: (Sondervorgang)

Für bestimmte Sondervorgänge sind besondere Aktionen im Plugin
definiert (z. B. für das Suspend). Diese werden jedoch nicht hier
erläutert, sondern an den Stellen, an denen Sie verwendet werden.

Weitere Einstellungen
---------------------

**mindelta: <int>**

Es ist möglich, eine Minimumabweichung für
Änderungen zu definieren. Wenn die Differenz zwischen dem
aktuellen Wert des Items und dem ermittelten neuen Wert kleiner
ist als die festgelegte Minimumabweichung wird keine Änderung
vorgenommen. Die Minimumabweichung wird über das Attribut
``se_mindelta_<Aktionsname>`` auf der Ebene des Regelwerk-Items
festgelegt.

**delay: <int>**

.. code-block:: yaml

       se_delay_<Aktionsname>: 30 (Sekunden)|30m (Minuten)

Über das Attribut wird die Verzögerung angegeben, nach der die
Aktion ausgeführt werden soll. Die Angabe erfolgt in Sekunden oder
mit dem Suffix "m" in Minuten.

Der Timer zur Ausführung der Aktion nach der angegebenen
Verzögerung wird entfernt, wenn eine gleichartike Aktion
ausgeführt werden soll (egal ob verzögert oder nicht). Wenn also
die Verzögerung größer als der ``cycle`` ist, wird die Aktion
nie durchgeführt werden, es sei denn die Aktion soll nur
einmalig ausgeführt werden.

**repeat: <bool>**

.. code-block:: yaml

       se_repeat_<Aktionsname>: [True|False]

Über das Attribut wird unabhängig vom globalen Setting für das
stateengine Item festgelegt, ob eine Aktion auch beim erneuten
Eintritt in den Status ausgeführt wird oder nicht.

**order: <int>**

.. code-block:: yaml

       se_order_<Aktionsname>: <int>
       se_order_aktion1: 3
       se_order_aktion2: 2
       se_order_aktion3: 1
       se_order_aktion4: 2

Die Reihenfolge, in der die Aktionen ausgeführt werden, ist nicht
zwingend die Reihenfolge in der die Attribute definiert sind. In
den meisten Fällen ist dies kein Problem, da die Aktionen
voneinander unabhängig sind und daher in beliebiger Reihenfolge
ausgeführt werden können. In Einzelfällen kann es jedoch
erforderlich sein, mehrere Aktionen in einer bestimmten
Reihenfolge auszuführen.

Es ist möglich, zwei Aktionen die gleiche Zahl zuzuweisen, die
Reihenfolge der beiden Aktionen untereinander ist dann wieder
zufällig. Innerhalb der gesamten Aktionen werden die beiden
Aktionen jedoch an der angegebenen Position ausgeführt.

**instanteval: <bool>**

Über das optionale Attribut ``se_instanteval`` wird für verzögerte Aktionen angegeben,
ob etwaige eval Ausdrücke sofort evaluiert und gespeichert werden sollen oder
die Evaluierung erst zum Ausführungszeitpunkt stattfinden soll.

.. code-block:: yaml

       se_instanteval_<Aktionsname>: [True|False]

Beispiel: Ein Item soll auf einen Wert aus einem anderen Item gesetzt werden. Das andere Item wird
anhand des gerade aktuellen Zustands durch ein eval eruiert:

.. code-block:: yaml

        eval:sh.return_item(se_eval.get_relative_itemid('..settings.{}'.format(se_eval.get_relative_itemvalue('..state_name'))))()

Angenommen, der aktuelle Zustand heißt ``regen``, so wird durch den obigen Code das Item
auf den Wert aus ``settings.regen`` gesetzt. Ändert sich aber während der Verzögerungszeit (delay)
der Zustand auf ``sonne``, würde zum Ausführungszeitpunkt der Aktion der Wert aus dem Item ``settings.sonne``
herangezogen werden. Wenn dies nicht erwünscht ist und das Item also auf den Vorgabewert des
ursprünglichen Zustands (regen) gesetzt werden soll, kann das Attribut
``se_instanteval_<Aktionsname>: True`` gesetzt werden.

Beispiel zu Aktionen
--------------------

.. code-block:: yaml

   beispiel:
       raffstore:
           automatik:
               rules:
                   <...>
                   se_item_height: beispiel.raffstore1.hoehe
                   se_mindelta_height: 10
                   se_item_lamella: beispiel.raffstore1.lamelle
                   se_mindelta_lamella: 5

                   Daemmerung:
                       <...>
                       se_set_height: value:100
                       se_set_lamella: value:25
                       <...>
                   Nacht:
                       <...>
                       se_set_height: value:100
                       se_set_lamella: value:0
                       <...>
                   Sonnenstand:
                       <...>
                       se_set_height: value:100
                       se_set_lamella: eval:se_eval.sun_tracking()
                       <...>
                   Sonder:
                       <...>
                       se_trigger_logic1: myLogic:42
                       se_delay_logic1: 10
                       <...>
