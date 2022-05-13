
.. index:: Stateengine; Regelwerk-Item

==============
Regelwerk-Item
==============

Unter jedem Item, für das eine State Machine angelegt werden soll, muss ein "Regelwerk-Item" erstellt werden.
Es wird empfohlen, dieses mit dem Namen ``rules`` als Child-Item unter das Item, das automatisiert werden soll, zu legen.
Dieses Item benötigt einige vorgegebene Definitionen, die am einfachsten über das ``struct`` Attribut
eingebunden werden. Das Item sieht dann folgendermaßen aus:

.. code-block:: yaml

   #items/item.yaml
   raffstore1:
       automatik:
           struct: stateengine.general

           rules:
              cycle: 60

Bei jedem Aufruf des Regelwerk-Items - im Beispiel auf Grund der cycle Angabe also
alle 60 Sekunden - werden die Zustände hierarchisch evaluiert.
Zuerst wird also der erste Status getestet. Kann dieser nicht aktiviert werden,
folgt der darunter angegebene, etc. Details hierzu finden sich im nächsten Teil
der Dokumentation.

Möchte man die Evaluierung eines Items deaktivieren, ist unter rules
das Attribute ``se_plugin`` auf inactive zu setzen:

.. code-block:: yaml

   #items/item.yaml
   raffstore1:
       automatik:
           struct: stateengine.general

           rules:
              se_plugin: inactive


Item-Definitionen
-----------------

Bedingungen und Aktionen beziehen sich überlicherweise auf Items wie beispielsweise
die Höhe einer Jalousie oder die Außenhelligkeit.
Diese Items müssen auf Ebene des Regelwerk-Items über das Attribut
``se_item_<Bedingungsname/Aktionsname>`` bekannt gemacht werden.

Anstatt direkt das Item in Form des absoluten oder relativen Pfades mittels ``se_item_`` zu
setzen, kann auch die Angabe ``se_eval_`` genutzt werden. In diesem Fall wird eine beliebige
Funktion anstelle des Itemnamen angegeben. Dies ist sowohl für Bedingungsabfragen,
als auch für das Setzen von "dynamischen" Items möglich.

An dieser Stelle ist es auch möglich, über ``se_mindelta_`` zu definieren, um welchen Wert
sich ein Item mindestens geändert haben muss, um neu gesetzt zu werden. Siehe auch :ref:`Aktionen`.

Außerdem ist es möglich, über ``se_repeat_actions`` generell zu definieren,
ob Aktionen für die Stateengine wiederholt ausgeführt werden sollen oder nicht. Diese Konfiguration
kann für einzelne Aktionen individuell über die Angabe ``repeat`` überschrieben werden. Siehe auch :ref:`Aktionen`.

Beispiel se_item
================

Im Beispiel wird durch ``se_item_height`` das Item ``beispiel.raffstore1.hoehe``
dem Plugin unter dem Namen "height" bekannt gemacht. Das Item ``beispiel.wetterstation.helligkeit``
wird durch ``se_item_brightness`` als "brightness" referenziert.

Auf diese Namen beziehen sich nun in weiterer Folge Bedingungen und Aktionen. Im Beispiel
wird im Zustand Nacht das Item ``beispiel.raffstore1.hoehe`` auf den Wert 100 gesetzt, sobald
``beispiel.wetterstation.helligkeit`` den Wert 25 übersteigt. Erklärungen zu Bedingungen
und Aktionen folgen auf den nächsten Seiten.

.. code-block:: yaml

    #items/item.yaml
    raffstore1:
        automatik:
            struct: stateengine.general
            rules:
                se_log_level: 2
                se_item_height: beispiel.raffstore1.hoehe
                se_item_brightness: beispiel.wetterstation.helligkeit

                Nacht:
                    name: Nacht
                    on_enter_or_stay:
                        se_action_height:
                            - 'function: set'
                            - 'to: 100'
                    enter_toodark:
                        se_max_brightness: 25

Beispiel se_eval
================

se_eval ist für Sonderfälle und etwas komplexere Konfiurationen sinnvoll, kann aber
im ersten Durchlauf ignoriert werden. Es wird daher empfohlen, als Beginner
dieses Beispiel einfach zu überspringen ;)

Im Beispiel wird durch ``se_eval_brightness`` das Item für den Check von
Bedingungen bekannt gemacht. Aufgrund der angegebenen Funktion wird das Item
abhängig vom aktuellen Zustandsnamen eruiert. Da Zustand_Eins den Namen "sueden"
hat, wird somit auch der Wert von wetterstation.helligkeit_sueden abgefragt.
Würde der Zustand "osten" heißen, würde der Helligkeitswert vom Osten getestet werden.

.. code-block:: yaml

    #items/item.yaml
    wetterstation:
        helligkeit_sueden:
            type: num
            knx_cache: 1/1/1
            knx_dpt: 5

        helligkeit_osten:
            type: num
            knx_cache: 1/1/2
            knx_dpt: 5

    raffstore1:
        automatik:
            struct: stateengine.general
            rules:
                se_eval_brightness: se_eval.get_relative_itemvalue('wetterstation.helligkeit_{}'.format(se_eval.get_variable('current.state_name')))

                Zustand_Eins:
                    name: sueden
                    enter:
                        se_max_brightness: 5000
