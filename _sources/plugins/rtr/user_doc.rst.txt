.. index:: Plugins; rtr
.. index:: rtr

===
rtr
===

Das Plugin implementiert einen Raumtemperaturregler (PI-Regler). Ein Regler besteht aus
drei Items: einem Istwert (**rtr_current**), einem Sollwert (**rtr_setpoint**) und einer
Stellgröße (**rtr_actuator**). Alle drei Items eines Reglers erhalten dieselbe
ganzzahlige ID, über die sie zu einem Controller zusammengefasst werden. Zusätzlich
unterstützt das Plugin drei Sollwert-Modi (Standard/Boost/Absenkung) inklusive
zeitgesteuerter Rückstellung sowie einen optionalen Ventilschutz.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/rtr`
beschrieben.

Beispiele
=========

Im folgenden Beispiel bilden die Items **temp**, **set** und **state** über die ID **1**
einen Regler. Über **rtr_stops** kann ein beliebiges Bool-Item als Stopp-/Pause-Auslöser
für einen oder mehrere Regler dienen - solange es den Wert True hat, wird die Stellgröße
des Reglers auf 0 gesetzt und die Regelung pausiert.

::

    gf:

        floor:

            temp:
                name: Temp
                type: num
                knx_dpt: 9
                knx_send: 4/2/120
                knx_reply: 4/2/120
                ow_addr: 28.52734A030000
                ow_sensor: T
                rtr_current: 1

                set:
                    type: num
                    visu: 'yes'
                    cache: 'On'
                    knx_dpt: 9
                    knx_send: 4/3/120
                    knx_listen: 4/3/120
                    rtr_setpoint: 1

                state:
                    type: num
                    visu: 'yes'
                    knx_dpt: 9
                    knx_send: 4/1/120
                    knx_listen: 4/1/120
                    rtr_actuator: 1

            door:
                name: Frontdoor
                open:
                    rtr_stops:
                      - '1'

**cache: 'On'** auf dem Sollwert-Item ist wichtig, damit der eingestellte Sollwert einen
Neustart von SmartHomeNG übersteht.

Verwendung der Plugin-Funktionen
=================================

Die Umschaltung zwischen den drei Sollwert-Modi erfolgt über die Funktionen
**default()**, **boost()** und **drop()**, die z. B. aus einer Logik heraus aufgerufen
werden können. Sie sind nicht über die Metadaten des Plugins deklariert und erscheinen
daher nicht auf der Konfigurationsseite.

- **default(c)** setzt den Sollwert des Controllers **c** auf die in
  **rtr_temp_default** hinterlegte Temperatur zurück und bricht laufende Boost- oder
  Absenk-Timer ab.
- **boost(c, timer=True, edt=None)** setzt den Sollwert auf die in **rtr_temp_boost**
  hinterlegte Temperatur. Ist **timer** nicht False, wird automatisch ein Timer
  angelegt, der den Sollwert nach **rtr_temp_boost_time** (bzw. dem globalen
  **defaultBoostTime**) Minuten wieder auf Standard zurücksetzt. Mit **edt** kann
  stattdessen ein fester Endzeitpunkt (``datetime``) übergeben werden.
- **drop(c, edt=None)** setzt den Sollwert auf die in **rtr_temp_drop** hinterlegte
  Temperatur. Ohne Angabe von **edt** wird kein automatischer Rückstell-Timer angelegt.

Der Parameter **c** ist die ID des Controllers, also derselbe Wert, der auch bei
**rtr_current**/**rtr_setpoint**/**rtr_actuator** verwendet wird.

::

    sh.rtr.boost(1)
    sh.rtr.drop(2, sh.shtime.now() + datetime.timedelta(hours=3))
    sh.rtr.default(1)

Ein laufender Timer übersteht einen Neustart von SmartHomeNG, da sein Endzeitpunkt in
einer Datei unterhalb von ``var/rtr/timer/`` gespeichert und beim Start wiederhergestellt
wird.

Alternativ kann ein Item mit dem Attribut **rtr_hvac_mode** verknüpft werden, um die
Modi über einen Item-Wert auszulösen (entsprechend KNX DPT 20.102): **1** löst Boost,
**2** löst Standard und **3** löst Absenkung aus.

Web Interface
=============

Das Webinterface zeigt in der Kopftabelle die aktuell wirksamen globalen
Standardwerte (**default_Kp**, **default_Ki**, **cycle_time**, **defaultBoostTime**,
**defaultOnExpiredTimer**, Ventilschutz-Standard). Auf dem Tab **Controller** werden
alle konfigurierten Regler mit ihrem internen Zustand (Istwert-, Sollwert- und
Stellgrößen-Item, aktuelle Kp-/Ki-Werte, Modus usw.) aufgelistet.
