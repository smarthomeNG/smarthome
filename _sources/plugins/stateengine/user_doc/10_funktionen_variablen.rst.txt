
.. index:: Stateengine; Funktionen und Variablen

========================
Funktionen und Variablen
========================

Vordefinierte Funktionen
------------------------

Das stateengine Plugin stellt verschiedene vordefinierte
Funktionen zur Verfügung, die einfach für
``se_set_<Aktionsname>`` und ``se_run_<Aktionsname>`` Aktionen
mittels ``eval:`` verwendet werden können:

**Sonnenstandsabhängige Lamellenausrichtung**
*Die Neigung der Lamellen wird automatisch von der Höhe der Sonne bestimmt.*
Optional kann noch ein Offset in Klammer mitgegeben werden, um etwaige kleine Abweichungen auszugleichen. Diese Abweichung
kann auch global bei der Pluginkonfiguration mittels ``lamella_offset`` eingestellt werden, was sich dann auf
sämtliche Aufrufe der Funktion auswirkt. Der Offset wird in Grad angegeben, wobei ein negativer Offset dafür sorgt, dass sich die Lamellen weniger weit drehen. Bei einem positiven Offset hingegen werden die Lamellen mehr geschlossen. Die Angabe beim direkten Aufruf der Funktion hat dabei immer Vorrang. Da verschiedene Lamellenarten unterschiedliche Prozentwerte im offenen Zustand
haben können, kann die Berechnung auch mittels ``lamella_open_value`` manipuliert werden.

.. code-block:: yaml

   se_eval.sun_tracking(-10)

**Zufallszahl**
*Über min und max kann die kleinste/größte Nummer, die zurückgegeben werden soll, festgelegt werden.*

.. code-block:: yaml

   se_eval.get_random_int(min,max)

``min`` und ``max`` können weggelassen werden, in diesem Fall sind die
Vorgabewerte 0 für ``min`` und 255 für ``max``.

**Shell-Kommando ausführen**
*Führt ein Shell-Kommando aus*

.. code-block:: yaml

   se_eval.execute(command)

**Wert einer Variable ermitteln**
*Liefert den Wert der Variablen <varname>*

.. code-block:: yaml

   se_eval.get_variable(varname)

**Item relativ zum Regelwerk-Item ermitteln**
*Ein Item Objekt relativ zur Item-Id des Regelwerk-Items wird ermittelt.*

.. code-block:: yaml

  se_eval.get_relative_item(subitem_id)
  se_eval.get_relative_item('..suspend')

Das zurückgelieferte Item kann nun genutzt werden, um in einem eval Ausdruck
gesetzt oder abgefragt zu werden.

**Wert eines Item-Attributs ermitteln**
*Der Wert eines Attributs wird ermittelt.*

.. code-block:: yaml

  se_eval.get_attribute_value(item or var, attribute)
  se_eval.get_attribute_value('..settings', 'some_special_attribute')
  se_eval.get_attribute_value('var:current.state_id', 'some_special_attribute')

Der erste Wert muss ein String sein, der entweder ein (relatives) Item enthält
oder eine StateEngine Variable (startet mit var:). Der zweite Wert ist der
Attributname, der eruiert werden soll. Gerade in Kombination mit der Abfrage
der aktuellen Status- oder Conditionset-ID können hier Konfigurationen vereinfacht werden.

**Suspend-Ende in einen Text einsetzen**
*Das Ende der Suspend-Zeit wird in den Text suspend_text eingesetzt.*

.. code-block:: yaml

   se_eval.insert_suspend_time(suspend_item_id, suspend_text="Ausgesetzt bis %X")

Im Text sind entsprechende Platzhalter
vorzusehen (Siehe `strftime() and strptime()
Behavior <https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior>`_).
Wird kein ``suspend_text`` angegeben, so wird als Vorgabewert
"Ausgesetzt bis %X" verwendet.

Zur Ermittlung des Endes der Suspend-Zeit muss über
``suspend_item_id`` ein Item angegeben werden, dessen Wert bei
Eintritt in den Suspend-Status geändert wird. Über das Alter des
Werts in diesem Item wird die bereits abgelaufene Suspend-Zeit
bestimmt. Dies könnte auch über ein relatives Item angegeben werden,
wobei dieses unbedingt in Anführungszeichen gesetzt werden muss, z.B. ``'..suspend'``

**Item-Id relativ zum Regelwerk-Item ermitteln**
*Eine Item-Id relativ zur Item-Id des Regelwerk-Items wird ermittelt.*

.. code-block:: yaml

   se_eval.get_relative_itemid(subitem_id)
   se_eval.get_relative_itemid('..suspend')

Statt dieser Funktion kann se_eval.get_relative_itemproperty('..suspend', 'path')
verwendet werden. Alternativ ist es auch möglich, die aus SmarthomeNG bekannte Syntax
``sh...suspend.property.path`` zu verwenden. Insofern hat diese Funktion nur wenig Relevanz.

**Item-Wert relativ zum Regelwerk-Item ermitteln**
*Der Wert eines Items relativ zur Item-Id des Regelwerk-Items wird ermittelt.*

.. code-block:: yaml

   se_eval.get_relative_itemvalue(subitem_id)
   se_eval.get_relative_itemvalue('..suspend')

Statt dieser Funktion kann se_eval.get_relative_itemproperty('..suspend', 'value')
verwendet werden. Alternativ ist es auch möglich, die aus SmarthomeNG bekannte Syntax
``sh...suspend.property.value`` oder ``sh...suspend()`` im eval zu verwenden.
Insofern hat diese Funktion nur wenig Relevanz.

**Item-Property relativ zum Regelwerk-Item ermitteln**
*Eine Property eines Items relativ zur Item-Id des Regelwerk-Items wird ermittelt.*

.. code-block:: yaml

  se_eval.get_relative_itemproperty(subitem_id, property)
  se_eval.get_relative_itemproperty('..suspend', 'last_change_age')

Welche Werte für ``property`` genutzt werden können, ist hier nachzulesen:
`Item Properties <https://www.smarthomeng.de/user/referenz/items/properties.html>`_).
Prinzipiell ist auch diese Funktion nicht zwingend zu verwenden, da sie ebenfalls
durch bekannt Syntax ersetzt werden kann: ``sh...suspend.property.last_change_age``

Variablen
---------

Im Plugin stehen folgende Variablen zur Verfügung:

**item.suspend_time:**
*Die Suspend-Time des Items*
Sie wird durch ``se_suspend_time`` im Regelitem mittels value,
item oder eval initialisiert.

**item.suspend_remaining:**
*Die übrige Dauer des Suspend Zustands*

Beide obigen Variablen werden vom Suspendzustand genutzt, können bei
Bedarf aber auch für andere Zwecke, welche auch immer, genutzt werden.

**item.instant_leaveaction:**
*Information, wie das leave_action Attribut für das Regelwerkitem gesetzt ist*
Die Option instant_leaveaction kann sowohl in der globalen Pluginkonfiguration
mittels ``instant_leaveaction``, als auch pro Item mittels ``se_instant_leaveaction``
festgelegt werden. Sie bestimmt, ob on_leave Aktionen sofort nach dem Verlassen
eines Zustands ausgeführt werden oder erst am Ende der Statusevaluierung.

**current.action_name:**
*Der Name der Aktion, in der auf die Variable zugegriffen wird*

Der Name der aktuellen Aktion, also der Teil hinter ``se_action_`` kann für
das Setzen oder Eruieren von Werten herangezogen werden. Dies macht insbesondere
dann Sinn, wenn auf Setting-Items in der Aktion Bezug genommen wird. Durch
diese Variable ist es so je nach Setup möglich, ein Template für sämtliche
Aktionen zu nutzen. Sobald die Statusevaluierung
abgeschlossen ist, ist diese Variable leer.
Ein Beispiel: Das Template "setvalue" wird für das
Setzen mehrerer Items herangezogen. Der eval Ausdruck schafft eine Referenz
auf das passende Unteritem in licht1.automatik.settings.

.. code-block:: yaml

    #items/item.yaml
    licht1:
        irgendeinitem:
            type: bool

        dimmen:
            warm:
                sollwert:
                    type: num
            kalt:
                sollwert:
                    type: num

        automatik:
            settings:
                sollwert_warm:
                    type: num
                sollwert_kalt:
                    type: num
                wasauchimmer:
                    type: bool

            rules:
                se_item_sollwert_warm: licht1.dimmen.warm.sollwert
                se_item_sollwert_kalt: licht1.dimmen.kalt.sollwert
                se_item_wasauchimmer: licht1.irgendeinitem
                se_template_setvalue: "eval:sh.return_item(se_eval.get_relative_itemid('..settings.{}'.format(
                                       se_eval.get_variable('current.action_name'))))()"
                zustand1:
                   name: 'Ein Zustand'
                   on_enter_or_stay:
                       se_action_sollwert_warm:
                         - 'function: set'
                         - "to: template:setvalue"
                       se_action_sollwert_kalt:
                         - 'function: set'
                         - "to: template:setvalue"
                       se_action_wasauchimmer:
                         - 'function: set'
                         - "to: template:setvalue"

**current.state_id:**
*Die Id des Status, der gerade geprüft wird*

Diese Variable wird leer, sobald die Statusevaluierung beendet wurde, noch bevor die Aktionen des
zuletzt eingenommenen Zustands ausgeführt werden. Sie kann daher nur in der Evaluierung, nicht aber
in on_enter(_or_stay) genutzt werden. Hierfür wird stattdessen ``se_eval.get_relative_itemvalue('..state_id')`` genutzt.

**current.state_name:**
*Der Name des Status, der gerade geprüft wird*

Wie die state_id Variable wird diese nur während der Statusevaluierung entsprechend befüllt und sofort beim Eintritt
in einen neuen Zustand geleert (noch vor dem Durchführen der Aktionen).

Das angeführte Beispiel zeigt, wie eine Bedingung mit einem Wert abgeglichen
werden kann, der in einem passenden Settingitem hinterlegt ist. Konkret
würde beim Evaluieren vom Zustand_Eins mit dem Namen "sueden" die maximale
Helligkeit der Wetterstation mit dem Wert von automatik.settings.sueden.max_bright
verglichen werden. Im Zustand_Zwei namens osten würde der Vergleich hingegen
mit dem Item automatik.settings.osten.max_bright stattfinden. Zu beachten ist,
dass die Eval Ausdrücke exakt gleich sind, wodurch ein Anlegen von eigenen Templates
die Situation deutlich vereinfachen würde.

.. code-block:: yaml

    #items/item.yaml
    raffstore1:
        automatik:
            struct: stateengine.general

            settings:
                sueden:
                    max_bright:
                        type: num
                        value: 80

                osten:
                    max_bright:
                        type: num
                        value: 30

            rules:
                se_item_brightness: wetterstation.helligkeit
                cycle: 10

                Zustand_Eins:
                    name: sueden
                    enter:
                        se_max_brightness: eval:se_eval.get_relative_itemvalue('..settings.{}.max_bright'.format(se_eval.get_variable('current.state_name'))

                Zustand_Zwei:
                    name: osten
                    enter:
                        se_max_brightness: eval:se_eval.get_relative_itemvalue('..settings.{}.max_bright'.format(se_eval.get_variable('current.state_name'))


**current.conditionset_id:**
*Die Id der Bedingungsgruppe, die gerade geprüft wird*

**current.conditionset_name:**
*Der Name der Bedingungsgruppe, die gerade geprüft wird*

Beide current.conditionset Variablen können ebenso wie die oben erwähnten current.state_id/name
nur während der Prüfung der Bedingungen genutzt werden, nicht jedoch für Aktionen.

Das Beispiel zeigt einen Windzustand. Dieser übernimmt keine Funktionen,
sondern dient lediglich der Visualisierung (Sicherheitsrelevante Features
sollten unbedingt z.B. über den KNX Bus erfolgen!). Außerdem wird davon
ausgegangen, dass es einen untergeordneten Zustand names x gibt.

- enter_normal wird angenommen, sobald das Wind-Item aktiv ist, zuvor aber
  nicht der x-Zustand aktiv war.

- enter_after_x wird angenommen, sobald das Wind-Item aktiv ist und zuvor
  der x-Zustand aktiv war.

- enter_stayafter_x wird angenommen, sobald das Wind-Item aktiv ist und zuvor
  der x-Zustand aktiv war.

Beim Verlassen des Windzustands (on_leave) wird nun ein bestimmtes Item (y)
auf True gesetzt - aber nur, wenn zuvor der x-Zustand aktiv war.

.. code-block:: yaml

    #items/item.yaml
    raffstore1:
        automatik:
            struct: stateengine.general
            rules:
                se_item_wind: ....sicherheit
                wind:
                    name: wind
                    on_leave:
                        se_action_y:
                          - function:set
                          - to:True
                          - conditionset:(.*)enter_(.*)_x

                    enter_after_x:
                        se_value_wind: True
                        se_value_laststate: eval:stateengine_eval.get_relative_itemid('..rules.x')

                    enter_stayafter_x:
                        se_value_wind: True
                        se_value_laststate: var:current.state_id
                        se_value_lastconditionset_name:
                            - 'var:current.conditionset_name'
                            - 'enter_after_x'

                    enter_normal:
                        se_value_wind: True

**previous.conditionset_id:**
*Die Id der Bedingungsgruppe, die beim vorigen Durchlauf aktiv war*

**previous.conditionset_name:**
*Der Name der Bedingungsgruppe, die beim vorigen Durchlauf aktiv war*

Bei den previous.conditionset Variablen spielt es keine Rolle, ob ein neuer Zustand eingenommen wurde oder nicht.
Beispiel: Ein Item ist aktuell im Zustand "Suspend" auf Grund einer manuellen Triggerung,
also der Bedingungsgruppe "enter_manuell". Die Variable ``previous.conditionset_name``
beinhaltet nun den Namen der Bedingungsgruppe vom vorherigen Zustand. Bei einer erneuten
Zustandsevaluierung bleibt (höchstwahrscheinlich) das Item im Zustand suspend auf Grund
der Bedingungsgruppe "enter_stay". Die Variable beinhaltet nun den Wert der vorigen Gruppe "enter_manuell".

**previous.state_id:**
*Die Id des vorherigen Zustands*

In dieser Variable ist die ID des Zustands gespeichert, der vor dem Eintreten in den aktuellen
Zustand aktiv gewesen ist. Ansonsten gelten alle vorhin beschriebenen Regeln.

**previous.state_name:**
*Der Name des vorherigen Zustands*

In dieser Variable ist der Name des Zustands gespeichert, der vor dem Eintreten in den aktuellen
Zustand aktiv gewesen ist. Ansonsten gelten alle vorhin beschriebenen Regeln.

**previous.state_conditionset_id:**
*Die Id der Bedingungsgruppe, die beim vorigen Zustand zuletzt aktiv war*

**previous.state_conditionset_name:**
*Der Name der Bedingungsgruppe, die beim vorigen Zustand zuletzt aktiv war*
