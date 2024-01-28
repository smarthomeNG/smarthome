
.. index:: Stateengine; Zustand-Templates
.. _Zustand-Templates:

=================
Zustand-Templates
=================

Struktur Templates
------------------

Neben der vom Plugin bereitgestellten Möglichkeit, Templates zu definieren (siehe weiter unten),
bietet sich ab **smarthomeNG 1.6** das ``struct`` Attribut an. Zum einen können in der Datei ``etc/struct.yaml``
eigene Vorlagen definiert werden, zum anderen stellt das Plugin einige Vorlagen fix fertig bereit. Sie
können wie folgt eingebunden werden:

.. code-block:: yaml

    #items/item.yaml
    beispiel:
        trigger:
            type: bool
            enforce_updates: True

        raffstore1:
            automatik:
                struct:
                  - stateengine.general
                  - stateengine.state_lock
                  - stateengine.state_suspend
                  - stateengine_default_raffstore #beispielsweise eine in etc/struct.yaml angelegte Vorlage

                manuell:
                   # Weitere Attribute werden bereits über das Template stateengine.state_suspend geladen
                    eval_trigger:
                       - beispiel.raffstore1.aufab
                       - beispiel.raffstore1.step
                       - beispiel.raffstore1.hoehe
                       - beispiel.raffstore1.lamelle
                    se_manual_exclude:
                       - KNX:y.y.y:1/2/3 # konkrete Gruppenadresse eines konkreten KNX Geräts
                       - Init:*

                rules:
                  eval_trigger:
                      - merge_unique*
                      - beispiel.trigger

                  additional_state1:
                      type: foo

Unter SmarthomeNG Version 1.7.0 werden die eval_trigger Angaben aus den einzelnen Struct-Vorgaben nicht
kumuliert. Es ist daher wichtig, die eval_trigger Liste nochmals manuell im endgültigen Item anzulegen.
Bei neueren Versionen kann man sich das erneute Listen der Trigger wie lock, suspend und release sparen,
da diese bereits im struct des Plugins gelistet sind.

Die Vorlagen beinhalten folgende Strukturen:

general
=======

Die ``general`` Vorlage enthält die Items, die generell für einen Zustandsautomaten
angelegt werden sollten. Das "rules" Item ist das Regelwerk-Item mit aktiviertem
se_plugin. Außerdem werden zwei Settings Items angelegt, um das Log Level und
"Instant Leaveaction" per Item konfigurieren und zur Laufzeit ändern zu können.
Dieser Codeblock wird zwingend von jedem Zustandsautomaten benötigt.

lock
====

Die ``state_lock`` Vorlage beinhaltet zum einen den Lock Zustand mit dem Namen "gesperrt",
zum anderen ein Item mit dem Namen ``lock``. Wird dieses auf "1/True" gesetzt, wird der
Zustand so lange eingenommen, bis das Item wieder auf False gestellt wird. So lässt sich zeitweise
die Evaluierung anderer Zustände pausieren. Der Zustand sollte immer als erster Zustand eingebunden werden.

suspend
=======

Die ``state_suspend`` Vorlage dient dem Abfragen von manuellen Tätigkeiten, wie
z.B. Schalten eines Lichts oder Fahren einer Jalousie mittels Taster oder Visu.
In diesem Fall soll die automatiche Evaluierung für eine gewisse Zeit pausieren.

Beim ``manuell`` Item muss unter Umständen der Eintrag ``se_manual_exclude`` in der eigenen
Baumstruktur überschrieben und durch einen Eintrag (z.B. beim Einsatz von KNX Aktoren) ``- KNX:physikalische Adresse:Gruppenadresse``
ergänzt werden. Außerdem muss ein eval_trigger manuell deklariert werden. Hier sollten alle
Items gelistet sein, die für ein vorübergehendes Aussetzen der Automatisierung sorgen sollen
(z.B. Schalt- und Dimm-Items)

Das Item ``settings.suspendduration`` ermöglicht es, die Dauer der Pausierung bequem
über eine Visu oder das Backend zu ändern. Das darunter angesiedelte ``duration_format``
konvertiert die angegebene Dauer in Minuten in das "Duration Format" mit
Tage-, Stunden- und Minutenangabe, für 5 Minuten also z.B. 0d 0h 5i. Dies ist genau wie das
``suspend_start.unix_timestamp`` Item für das smartvisu Widget clock.countdown notwendig.

Setzt man das Item ``settings.suspend_active`` auf False, wird der Pause-Zustand
deaktiviert und manuelle Betätigungen werden
beim nächsten Durchlauf eventuell durch andere Zustände überschrieben.

suspend_dynamic
===============

Eine Variante des Suspendmodus, bei dem es möglich ist, bis zu drei verschiedene
Suspendzeiten zu deklarieren. Außerdem kann man definieren, ob noch zusätzliche Zustände
integriert werden sollen. Dabei ist zu beachten, dass standardmäßig der "Standard"-Status
mit eingebunden wird. Da dieser leer ist, wird nichts passieren. Bei Bedarf kann der Wert
in den Items ``automatik.settings.suspendvariant.additionaluse[0-2]`` geändert werden.

Welche Zeiten und Zustände letztlich genutzt werden, wird durch Setzen des Items
``suspendvariant`` bestimmt. Der Wert muss zwischen 0 und 2 liegen.

Weitere Informationen sind unter :ref:`Besondere Zustände` zu finden.

release
=======

Die ``state_release`` Vorlage ist nicht unbedingt nötig, kann aber dazu genutzt werden,
schnell den Sperr- oder Pause-Zustand zu verlassen und die erneute Evaluierung
der Zustände anzuleiern.

standard
========

Ein praktisch leerer Status, der immer am Ende angehängt werden sollte. Dieser Status wird
eingenommen, wenn keine Bedingungen der anderen Zustände erfüllt sind.

Pluginspezifische Templates
---------------------------

Es ist neben der oben beschriebene Variante möglich, Vorgabezustände in
der Item-Konfiguration über ``se_use`` zu definieren
und diese später für konkrete Regelwerke durch Plugin-interne Attribute zu nutzen.
Dabei können im konkreten Zustand auch Einstellungen des Vorgabezustands
überschrieben werden. Alternativ ist es möglich, die struct Vorlagen aus
SmarthomeNG >= 1.6 zu nutzen bzw. selbst welche zu erstellen.

Vorgabezustände werden als Item an beliebiger Stelle innerhalb der
Item-Struktur definiert. Es ist sinnvoll, die Vorgabezustände
unter einem gemeinsamen Item namens ``default`` zusammenzufassen. Innerhalb der
Vorgabezustand-Items stehen die gleichen Möglichkeiten wie in
normalen Zustands-Items zur Verfügung. Das dem
Vorgabezustands-Item übergeordnete Item darf nicht das Attribut
``se_plugin: active`` haben, da diese Items nur Vorlagen und keine
tatsächlichen State Machines darstellen. Im Item über dem
Vorgabezustands-Item können jedoch Items über
``se_item_<Bedingungsname|Aktionsname>`` angegeben werden. Diese
stehen in den Vorgabezuständen und in den von den Vorgabezuständen
abgeleiteten Zuständen zur Verfügung und müssen so nicht jedes Mal
neu definiert werden.

Im konkreten Zustands-Item kann das Vorgabezustand-Item über das
Attribut

.. code-block:: yaml

   se_use:
     - struct:stateengine.state_suspend.rules.suspend
     - item:<string item mit Verweis auf Vorgabezustand>
     - eval:<Ausdruck zum dynamischen Einbinden von Vorgabezuständen>
     - <(relative) Itemangabe zum Vorgabezustand> #z.B. .suspend

eingebunden werden. Die Vorgabezustand-Items können als Liste angegben
und geschachtelt werden; das heißt ein Vorgabezustand kann also selbst wiederum
über ``se_use`` von einem weiteren Vorgabezustand abgeleitet
werden. Um unnötige Komplexität und Zirkelbezüge zu vermeiden, ist
die maximale Tiefe jedoch auf 5 Ebenen begrenzt. Jede in einem ``se_use`` angegebene
Definition kann durch eine höher geordnete Angabe mit dem gleichen Namen überschrieben
werden.

Beispiel
========

Die Konfiguration...

.. code-block:: yaml

    wetter:
      helligkeit:
        type: num
        initial_value: 400
      temperatur:
        type: num
        initial_value: 15

    beispiel:
       define_use:
           type: str
           initial_value: 'beispiel.default.Mittags'

       default:
           se_eval_height: se_eval.get_relative_item('...hoehe')
           se_item_helligkeit: wetter.helligkeit
           se_item_temperatur: wetter.temperatur
           Nacht:
               enter:
                   se_min_helligkeit: 300
                   se_min_temperatur: 0
                   se_max_helligkeit: 4000
               se_set_height: value:100
               se_set_lamella: 0
           Morgens:
               enter:
                   se_min_helligkeit: 900
                   se_max_temperatur: 12
               se_set_height: value:90
               se_set_lamella: 25
           Mittags:
               se_set_lamella: 55
               enter:
                   se_min_helligkeit: 5900
                   se_min_temperatur: 18

       raffstore1:
           lamelle:
              type: num
           hoehe:
              type: num

           automatik:
               struct: stateengine.general
               lock:
                  type: bool

               rules:
                   se_item_lamella: ...lamelle
                   se_item_helligkeit: wetter.helligkeit
                   Nacht:
                       se_use: beispiel.default.Nacht
                       se_set_lamella: 10
                       enter_additional:
                           se_min_helligkeit: 20
                       enter:
                           se_min_helligkeit: 500
                           se_min_temperatur: 0
                   Morgens:
                       name: morgens
                       se_use:
                         - beispiel.default.Morgens
                         - .Nacht
                         - struct:stateengine.state_lock.rules.lock
                         - item:beispiel.define_use

führt zu folgendem Ergebnis:

.. code-block:: console

    State beispiel.raffstore1.automatik.rules.Nacht:
    	State Name: Nacht
    	Updating Web Interface...
    	Finished Web Interface Update
    	State configuration extended by se_use: beispiel.default.Nacht
    	Condition sets to enter state:
    		Condition Set 'enter':
    			Condition 'helligkeit':
    			 item: helligkeit (wetter.helligkeit)
    			 min: 500
    			 max: 4000
    			 negate: False
    			Condition 'temperatur':
    			 item: temperatur (wetter.temperatur)
    			 min: 0
    			 negate: False
    		Condition Set 'enter_additional':
    			Condition 'helligkeit':
    			 item: helligkeit (wetter.helligkeit)
    			 max: 200
    			 negate: False
    	Actions to perform on enter or stay:
    		Action 'height':
    			name: height
    			item from eval: se_eval.get_relative_item('...hoehe')
    			value: 100
    		Action 'lamella':
    			name: lamella
    			item from eval: beispiel.raffstore1.lamelle
    			value: 10
    State beispiel.raffstore1.automatik.rules.Morgens:
    	State Name: morgens
    	Updating Web Interface...
    	Finished Web Interface Update
    	State configuration extended by se_use: [Item: beispiel.default.Morgens, Item: beispiel.raffstore1.automatik.rules.Nacht, Item: beispiel.default.Nacht, SeStructMain stateengine.state_lock.rules.lock, Item: beispiel.default.Mittags]
    	Condition sets to enter state:
    		Condition Set 'enter':
    			Condition 'lock':
    			 item: lock (beispiel.raffstore1.automatik.lock)
    			 value: True
    			 negate: False
    			Condition 'temperatur':
    			 item: temperatur (wetter.temperatur)
    			 min: 18
    			 max: 12
    			 negate: False
    			Condition 'helligkeit':
    			 item: helligkeit (wetter.helligkeit)
    			 min: 5900
    			 max: 12000
    			 negate: False
    		Condition Set 'enter_additional':
    			Condition 'helligkeit':
    			 item: helligkeit (wetter.helligkeit)
    			 max: 200
    			 negate: False
    	Actions to perform on enter or stay:
    		Action 'height':
    			name: height
    			item from eval: se_eval.get_relative_item('...hoehe')
    			value: 100
    		Action 'lamella':
    			name: lamella
    			item from eval: beispiel.raffstore1.lamelle
    			value: 55

.. note::

    Folgende Besonderheiten sind bei der Konfiguration zu beachten:

    - Beim Laden via se_use werden relative Itemdeklarationen NICHT relativ
      zum StateEngine Item (rules) gesucht, sondern relativ zu dem Item,
      wo das Attribut ``se_item_..`` steht. Daher muss hier unbedingt ``se_eval_..``
      wie z.B. ``se_eval_height: se_eval.get_relative_item('...hoehe')``
      genutzt werden.
    - Auf gleicher Ebene zum StateEngine Item (rules) müssen mittels
      ``struct: stateengine.general`` die Standarditems und Attribute des Plugins
      eingebunden werden, damit eine korrekte Funktion garantiert werden kann.
    - Über ``se_use`` eingebundene Zustandsvorlagen suchen zwar im darüber gelegenen
      Item nach den entsprechenden se_item/eval Deklarationen, binden aber keine
      darüber liegenden Items ein. Daher muss z.B. beim Referenzieren des Lock-Zustands
      aus dem Plugin Struct das **lock** Item manuell angelegt werden. Beim Nutzen
      von ``struct: stateengine.state_lock`` wäre das nicht notwendig, weshalb sich
      eine Referenzierung auf die Plugin Templates via ``se_use`` nur bedingt eignet.
