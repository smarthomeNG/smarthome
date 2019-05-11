Tipps und Tricks
================

Invertieren eines Item Wertes
-----------------------------

Aufgabenstellung
~~~~~~~~~~~~~~~~

Es geht um einen Reed-Kontakt am Fenster, der über einen 1-Wire
Multi-I/O-Sensor per 1-Wire-Plugin abgefragt und auf den KNX-Bus
gesendet wird.

Leider sind die Werte vertauscht, 0 soll 1 sein und umgekehrt, ein
geschlossenes Fenster wird geöffnet angezeigt und umgekehrt.

Lösung
~~~~~~

Ein ``eval:`` Attribut zum Item hinzufügen. ``eval = not value`` Value
ist der Wert, der vom KNX Bus gelesen wird, der eval Ausdruck verändert
diesen Wert, bevor er in das Item geschrieben wird. Damit wird dann der
invertierte Wert auf den KNX Bus geschrieben.

.. code-block:: yaml

   OW:
       Fenster:
           EsszimmerLinks:
               type: bool
               visu_acl: rw
               ow_addr: 3A.CBF713000000
               ow_sensor: IB
               knx_dpt: 1
               knx_send: 2/1/82
               knx_reply: 2/1/82
               eval: not value

Item Strukturen bequem kopieren mit Hilfe relativer Item Adressierung
---------------------------------------------------------------------

.. _aufgabenstellung-1:

Aufgabenstellung
~~~~~~~~~~~~~~~~

Es sollen Fensterkontakte ausgewertet werden (zwei Kontakte je Fenster
oder z.B. Hoppe Fenstergriffe). Hierbei ergeben zwei Kontakte drei
sinnvolle Stati (verschlossen, gekippt, offen). Die Auswertung setzt die
Informationen der zwei Kontakte auf eigene Items für die drei Stati um.

Diese Lösung soll mit möglichst wenig Aufwand für alle Fenster des
Objekts kopiert werden. Mit normaler (absoluter) Item Adressierung kann
das folgendermaßen gelöst werden:

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

Wenn dieser Block für weitere Fenster kopiert wird, muss jedoch außer
der Anpassung der Adressen für ``Reed1`` und ``Reed2`` auch noch
``Buero`` an diversen Stellen ersetzt werden, was einen gewissen Aufwand
erfordert und auch noch fehlerträchtig ist.

.. _lösung-1:

Lösung
~~~~~~

Mit relativer Item Adressierung kann das einfacher gelöst werden. Dann
müssen nach dem Kopieren des Blocks nur noch die Adressen für ``Reed1``
und ``Reed2`` angepasst werden:

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

``..<item>`` referenziert hierbei ein sister-Item. Es ist darauf zu
achten, dass dort wo Items über ``sh.<item>()`` angesprochen werden (wie
im ``eval`` Attribut) dann drei statt der erwarteten zwei Punkte stehen.

Ausführliche Informationen zur relativen Item Adressierung sind auf der
Wiki Seite `Relative Item
Referenzen <https://github.com/smarthomeNG/smarthome/wiki/Items:-Relative-Item-Referenzen>`__
zu finden.

Nutzung der Tag-/Nacht-Items in KNX
-----------------------------------

Einleitung
~~~~~~~~~~

Ein Tag- oder Nachtobjekt kann zur Ansteuerung von Status-LEDs,
Präsenzmeldern oder ähnlichem genutzt werden.

**Tag-Item:** Ist “true” (also 1) von Sonnenaufgang bis Sonnenuntergang,
danach ist es “false” (also 0)

**Nacht-Item:** Ist “true” (also 1) von Sonnenuntergang bis
Sonnenaufgang, danach ist es “false” (also 0)

Welches der beiden Items man nutzen will, bleibt jedem selbst
überlassen. Schließlich ist der Status des jeweiligen Items bereits
eindeutig. Wichtig dafür ist natürlich, dass die richtigen
Geo-Koordinaten und die Zeitzone in der Datei **../etc/smarthome.yaml**
hinterlegt sind sowie die aktuelle Uhrzeit auf dem Rechner eingestellt
ist.

Um Tag/Nacht-Items zu erstellen, bringt SmarthomeNG bereits alles mit.
Man kann einfach auf die SmarthomeNG internen Items ``env.location.day``
und ``env.location.night`` zugreifen.

Beispiele:
~~~~~~~~~~

Nutzung mit neuen (zusätzlichen) items:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   tag:
       type: num
       knx_dpt: 1
       knx_send: 0/0/103
       knx_reply: 0/0/103
       eval: sh.env.location.day()
       eval_trigger: env.location.day

   nacht:
       type: num
       knx_dpt: 1
       knx_send: 0/0/104
       knx_reply: 0/0/104
       eval: sh.env.location.night()
       eval_trigger: env.location.night


Nutzung der SmarthomeNG internen Items:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Dazu müssen die entsprechenden Items um die KNX Attribute erweitert
werden:

.. code-block:: yaml

   env:
       location:
           day:
               name: Tag
               knx_dpt: 1
               knx_send: 0/0/103
               knx_reply: 0/0/103
           night:
               name: Nacht
               knx_dpt: 1
               knx_send: 0/0/104
               knx_reply: 0/0/104

Da sich die internen Items von Release zu Release ändern könnten, ist
der Weg der zusätzlichen Items zu bevorzugen.

Berechnung von Tag und Nacht
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Die Berechnung der Items *Tag* und *Nacht* erfolgt SmarthomeNG-intern
über *sh.sun.rise(-6).day* (bürgerliche Dämmerung).

Für eine Beleuchtungssteuerung (z.B. mit KNX) wäre es sinnvoll, die
Berechnung von Tag/Nacht anders vorzunehmen, weil z.B. für
Flurlichtsteuerung o.ä. vielleicht schon 1h vor Sonnenuntergang die
“Nacht” beginnen soll. Das kann durch die Definition neuer Items
erreicht werden. Im folgenden Beispiel wird die Tag/Nacht Grenze bei
einem Sonnenstand von 4° unter dem Horizont festgelegt:

.. code-block:: yaml

       berechnung:
           type = bool
           crontab:
           - init = 1
           - sunrise-4 = 1
           - sunset-4 = 1
           enforce_updates = true

       day:
           type = bool
           eval = sh.sun.rise(-4).day != sh.sun.set(-4).day
           eval_trigger = ..berechnung
           enforce_updates = true


Die Triggerung dieser Berechnung wird im *berechnung* - Item durch das
Attribut *crontab* gesteuert. In diesem Beispiel erfolgt die Berechnung
4° vor Sonnenaufgang, 4° nach Sonnenuntergang, sowie beim Systemstart.
