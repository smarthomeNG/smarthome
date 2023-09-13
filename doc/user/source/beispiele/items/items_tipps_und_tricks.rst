:tocdepth: 2

.. index:: Items; Tipps & Tricks
.. index:: Tipps & Tricks; Items

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup

==================================
Tipps und Tricks :bluesup:`Update`
==================================


.. index:: Zeitglied
.. index:: Timer
.. index:: Items; Zeitglied


Erstellen eines Zeitgiedes
==========================

Wenn man ein Item benötigt, welches seinen Wert erst nach einer zeitlichen Verzögerung ändert, kann man das mit
Hilfe eines zweiten Items realisieren. Das erste Item (Eingang) wird dabei durch ein Ereignis (Plugins, eval, ...)
verändert. Das zweite Item (Ausgang) nimmt den neuen Wert des ersten Items erst nach einer definierten zeitlichen
Verzögerung an.

Beispiel
--------

In diesem Beispiel ist ein Zeitglied für ein numerischs Item dargestellt, welches eine Verzögerung von 15 Sekunden
implementiert.

.. code-block:: yaml

    Zeitglied:
        Eingang:
            type: num
            on_change:
              - sh...Ausgang.timer(15, value)

        Ausgang:
            type: num

|


.. index:: Items; Wert invertieren

Invertieren eines Item Wertes
=============================

Beispiel 1
----------

Es geht um einen Reed-Kontakt am Fenster, der über einen 1-Wire Multi-I/O-Sensor per 1-Wire-Plugin abgefragt
und auf den KNX-Bus gesendet wird.

Leider sind die Werte vertauscht, 0 soll 1 sein und umgekehrt, ein geschlossenes Fenster wird geöffnet angezeigt
und umgekehrt.

Ein ``eval:`` Attribut zum Item hinzufügen. ``eval: not value`` Value ist der Wert, der vom KNX Bus gelesen wird,
der eval Ausdruck verändert diesen Wert, bevor er in das Item geschrieben wird. Damit wird dann der
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



Beispiel 2
----------

Es geht um einen Lautsprecher, der über einen GPIO Kontakt des Raspberry geschaltet werden soll. Der Wert kommt
von einem Item das per knx bedient wird und dessen Item Wert nicht verfälscht werden soll.

Leider sind auch hier die Werte vertauscht, 0 soll 1 sein und umgekehrt.

Ein Hilfsitem hinzufügen und diesem mit relativer Adressierung auf das Elternelement
ein ``eval_trigger`` und ein ``eval`` zufügen.

.. code-block:: yaml

   Gaestezimmer_Lautsprecher:
       type: bool
       knx_dpt: 1
       knx_listen: 5/0/5
       visu_acl: rw
       GPIO_Ausgabe:
           type: bool
           gpio_out: 38
           eval: not sh...()
           eval_trigger: ..

|

Erstellung von Tag-/Nacht-Items für KNX
=======================================

Ein Tag- oder Nachtobjekt kann zur Ansteuerung von Status-LEDs, Präsenzmeldern oder ähnlichem genutzt werden.

**Tag-Item:** Ist “true” (also 1) von der bürgerlichen Dämmerung am Morgen bis zur Dämmerung am Abend, danach
ist es “false” (also 0)

**Nacht-Item:** Ist “true” (also 1) von der bürgerlichen Dämmerung am Abend bis zur Dämmerung am Morgen, danach
ist es “false” (also 0)

Bürgerliche Dämmerung bedeutet, dass sich die Sonne noch/schon unterhalb des Horizonts befindet, der Himmel aber
dennoch leicht erhellt wird.

Welches der beiden Items man nutzen will, bleibt jedem selbst überlassen. Schließlich ist der Status des
jeweiligen Items bereits eindeutig. Wichtig dafür ist natürlich, dass die richtigen Geo-Koordinaten und die
Zeitzone in der Datei **../etc/smarthome.yaml** hinterlegt sind sowie die aktuelle Uhrzeit auf dem Rechner
eingestellt ist.

Um Tag/Nacht-Items zu erstellen, bringt SmarthomeNG bereits alles mit. Man kann einfach auf die SmarthomeNG
internen Items ``env.location.day`` und ``env.location.night`` zugreifen.

Beispiele
---------

Nutzung mit neuen (zusätzlichen) Items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


Nutzung der SmarthomeNG internen Items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dazu müssen die entsprechenden Items um die KNX Attribute erweitert werden:

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

Da sich die internen Items von Release zu Release ändern könnten, ist der Weg der zusätzlichen Items zu bevorzugen.


Berechnung von Tag und Nacht
----------------------------

Die Berechnung der Items *Tag* und *Nacht* erfolgt SmarthomeNG-intern über *sh.sun.rise(-6).day* (bürgerliche Dämmerung).

Für eine Beleuchtungssteuerung (z.B. mit KNX) wäre es sinnvoll, die Berechnung von Tag/Nacht anders vorzunehmen,
weil z.B. für Flurlichtsteuerung o.ä. vielleicht schon 1h vor Sonnenuntergang die “Nacht” beginnen soll.
Das kann durch die Definition neuer Items erreicht werden. Im folgenden Beispiel wird die Tag/Nacht Grenze bei
einem Sonnenstand von 4° unter dem Horizont festgelegt:

.. code-block:: yaml

       berechnung:
           type: bool
           crontab:
             - init = 1
             - sunrise-4 = 1
             - sunset-4 = 1
           enforce_updates: true

       day:
           type: bool
           eval: sh.sun.rise(-4).day != sh.sun.set(-4).day
           eval_trigger: ..berechnung
           enforce_updates: true


Die Triggerung dieser Berechnung wird im *berechnung* - Item durch das Attribut *crontab* gesteuert. In diesem
Beispiel erfolgt die Berechnung 4° vor Sonnenaufgang, 4° nach Sonnenuntergang, sowie beim Systemstart.

