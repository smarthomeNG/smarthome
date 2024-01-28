
.. index:: Tipps & Tricks; structs bequem kopieren

Item Strukturen bequem kopieren
===============================

Bei Verwendung von relativer Item Adressierung können Teile des Item-Baumes einfach kopiert werden, um sie an
anderer Stelle im Item-Baum zu verwenden.

Es sollen Fensterkontakte ausgewertet werden (zwei Kontakte je Fenster oder z.B. Hoppe Fenstergriffe). Hierbei
ergeben zwei Kontakte drei sinnvolle Stati (verschlossen, gekippt, offen). Die Auswertung setzt die
Informationen der zwei Kontakte auf eigene Items für die drei Stati um.

Diese Lösung soll mit möglichst wenig Aufwand für alle Fenster des Objekts kopiert werden. Mit normaler
(absoluter) Item Adressierung kann das folgendermaßen gelöst werden:

.. code-block:: yaml

   Test:
       Buero:
           Reed1:
               type: num
               knx_dpt: 1
               knx_cache: 4/1/5
               visu_acl: rw

           Reed2:
               type: num
               knx_dpt: 1
               knx_cache: 4/1/6
               visu_acl: rw

           zu:
               type: bool
               enforce_updates: yes
               eval: True if sh.Test.Buero.Reed1() == 1 and sh.Test.Buero.Reed2() == 1 else False
               eval_trigger:
                 - Test.Buero.Reed1
                 - Test.Buero.Reed2

           gekippt:
               type: bool
               enforce_updates: yes
               eval: True if sh.Test.Buero.Reed1() == 0 and sh.Test.Buero.Reed2() == 1 else False
               eval_trigger:
                 - Test.Buero.Reed1
                 - Test.Buero.Reed2

           offen:
               type: bool
               enforce_updates: yes
               eval: True if sh.Test.Buero.Reed1() == 0 and sh.Test.Buero.Reed2() == 0 else False
               eval_trigger:
                 - Test.Buero.Reed1
                 - Test.Buero.Reed2

Wenn dieser Block für weitere Fenster kopiert wird, muss jedoch außer der Anpassung der Adressen für
``Reed1`` und ``Reed2`` auch noch ``Buero`` an diversen Stellen ersetzt werden, was einen gewissen Aufwand
erfordert und auch noch fehlerträchtig ist.

Mit relativer Item Adressierung kann das einfacher gelöst werden. Dann müssen nach dem Kopieren des Blocks nur
noch die Adressen für ``Reed1`` und ``Reed2`` angepasst werden:

.. code-block:: yaml

   Test:
       Buero:
           Reed1:
               type: num
               knx_dpt: 1
               knx_cache: 4/1/5
               visu_acl: rw

           Reed2:
               type: num
               knx_dpt: 1
               knx_cache: 4/1/6
               visu_acl: rw

           zu:
               type: bool
               enforce_updates: yes
               eval: True if sh...Reed1() == 1 and sh...Reed2() == 1 else False
               eval_trigger:
                 - ..Reed1
                 - ..Reed2

           gekippt:
               type: bool
               enforce_updates: yes
               eval: True if sh...Reed1() == 0 and sh...Reed2() == 1 else False
               eval_trigger:
                 - ..Reed1
                 - ..Reed2

           offen:
               type: bool
               enforce_updates: yes
               eval: True if sh...Reed1() == 0 and sh...Reed2() == 0 else False
               eval_trigger:
                 - ..Reed1
                 - ..Reed2

``..<item>`` referenziert hierbei ein Geschwister-Item. Es ist darauf zu achten, dass dort wo Items über
``sh.<item>()`` angesprochen werden (wie im ``eval`` Attribut) dann drei statt der erwarteten zwei Punkte stehen.

Ausführliche Informationen zur relativen Item Adressierung sind unter
:doc:`relative Itemreferenzen </referenz/items/attributes_relative_referenzen>` zu finden.

Das Beispiel ließe sich noch weiter vereinfachen, indem die Einträge durch **structs** referenziert werden.
Detaillierte Informationen hierzu gibt es auf :doc:`structs (Item Strukturen) </konfiguration/item_structs>`


