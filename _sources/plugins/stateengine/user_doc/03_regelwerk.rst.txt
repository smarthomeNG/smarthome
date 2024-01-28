
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
Zuerst wird also der als erstes angegebene Status getestet. Die Reihenfolge ergibt sich
aus der YAML Datei oder alternativ aus dem optionalen Attribut ``se_stateorder``.
Kann der Zustand nicht aktiviert werden,
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

Bedingungen und Aktionen beziehen sich üblicherweise auf Items wie beispielsweise
die Höhe einer Jalousie oder die Außenhelligkeit.
Diese Items müssen auf Ebene des Regelwerk-Items über das Attribut
``se_item_<Bedingungsname/Aktionsname>`` bekannt gemacht werden. Um einfacher zwischen Items,
die für Bedingungen und solchen, die für Aktionen genutzt werden, unterscheiden zu können,
können Items, die nur für Bedingungen gebraucht werden, mittels ``se_status_<Bedingungsname>``
deklariert werden.

Anstatt direkt das Item in Form des absoluten oder relativen Pfades zu setzen, kann auch ein
eval-Ausdruck mittels ``eval:<Ausdruck>`` angegeben werden.

.. hint::

  Aus Kompatibilitätsgründen kann für das Setzen "dynamischer" Items auch die Angabe ``se_eval_``
  oder ``se_status_eval_`` genutzt werden. In diesem Fall wird eine beliebige
  Funktion anstelle des Itemnamen angegeben, also beispielsweise
  se_eval_height: se_eval.get_relative_item('..test'). Hierzu in den Kapiteln :ref:`Bedingungen`
  und :ref:`Aktionen` mehr.


Beispiel se_item
================

Im Beispiel wird durch ``se_item_height`` das Item ``beispiel.raffstore1.hoehe``
dem Plugin unter dem Namen "height" bekannt gemacht. Das Item ``beispiel.wetterstation.helligkeit``
wird durch ``se_item_brightness`` als "brightness" referenziert.

Auf diese Namen beziehen sich nun in weiterer Folge Bedingungen und Aktionen. Im Beispiel
wird im Zustand Nacht das Item ``beispiel.raffstore1.hoehe`` auf den Wert 100 gesetzt, sobald
``beispiel.wetterstation.helligkeit`` den Wert 25 übersteigt. Erklärungen zu Bedingungen und
Aktionen folgen auf den nächsten Seiten.

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

Beispiel se_status
==================

Wie erwähnt, können Items, die nur für Bedingungen genutzt werden, auch mittels se_status deklariert
werden. Diese Variante ist aber auch besonders dann relevant, wenn es zwei separate Items
für "Senden" und "Empfangen" gibt, also z.B. Senden der Jalousiehöhe und Empfangen des aktuellen
Werts vom KNX-Aktor.

Im Beispiel wird durch ``se_item_height`` das Item ``beispiel.raffstore1.hoehe`` (das den Befehl an den
KNX Aktor übermittelt) dem Plugin unter dem Namen "height" bekannt gemacht. ``se_status_height`` referenziert auf das
separate Status-Item (das vom KNX Aktor den Rückmeldestatus erhält) ``beispiel.raffstore1.hoehe.status``.
Dies ist aktuell insbesondere dann wichtig, wenn `se_mindelta_height`` genutzt wird (siehe :ref:`Aktionen`).

.. code-block:: yaml

    raffstore1:
        automatik:
            struct: stateengine.general
            rules:
                se_item_height: beispiel.raffstore1.hoehe
                se_status_height: beispiel.raffstore1.hoehe.status
                se_mindelta_height: 10

                Standard:
                    on_enter_or_stay:
                        se_action_height:
                            - 'function: set'
                            - 'to: 100'


Beispiel se_eval
================

Im Beispiel werden zwei Helligkeitswerte addiert und das Resultat durch 2 geteilt
(also der Mittelwert gebildet). Das Resultat wird dann mit dem Wert 5000 verglichen.

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
                se_eval_brightness: (se_eval.get_relative_itemvalue('wetterstation.helligkeit_sueden') + se_eval.get_relative_itemvalue('wetterstation.helligkeit_osten'))/2

                Zustand_Eins:
                    name: sueden
                    enter:
                        se_max_brightness: 5000
