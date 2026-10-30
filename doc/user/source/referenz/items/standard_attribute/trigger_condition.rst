
.. index:: Items; trigger_condition
.. index:: Standard-Attribute; trigger_condition
.. index:: trigger_condition


.. role:: redsup
.. role:: bluesup

trigger und trigger_condition
=============================

.. attention::

    Die Attribute **trigger** und **trigger_condition** sind experimentell. Sie werden nur ausgewertet, wenn in der
    ``etc/smarthome.yaml`` der Parameter ``use_conditional_triggers: true`` gesetzt ist. Ohne diesen Parameter
    werden beide Attribute ignoriert.

**trigger** ist eine Liste von Items, bei deren Auslösung der **eval** Ausdruck des Items ausgewertet wird. Es wirkt
wie **eval_trigger**.

**trigger_condition** legt Bedingungen fest, die bei einer Auslösung erfüllt sein müssen, damit der **eval** Ausdruck
ausgeführt wird. Ist keine der Bedingungen erfüllt, wird die Auswertung übersprungen und der Wert des Items bleibt
unverändert.

**trigger_condition** ist eine Liste von ODER-Klauseln. Jede Klausel ist ein dict mit einem frei wählbaren Namen
als Schlüssel und einer Liste von Bedingungen, die UND-verknüpft werden. Die Bedingungen sind Python-Ausdrücke,
in denen dieselben Namen wie im **eval** Ausdruck zur Verfügung stehen (z.B. ``value``, ``sh``,
siehe :doc:`eval <./eval>`). Relative Item-Referenzen sind möglich.

Beim Umsetzen in einen Python-Ausdruck wird ein einfaches ``=`` zu ``==``, ``true`` und ``false`` werden (unabhängig
von der Groß-/Kleinschreibung) zu ``True`` und ``False``. Ein Schlüssel mit dem Namen ``value`` wird ignoriert.

.. code-block:: yaml

    heizung:
        sollwert:
            type: num
            eval: sh.heizung.vorgabe()
            trigger: heizung.vorgabe
            trigger_condition:
              - anwesend:
                  - sh.wohnung.anwesend() = true
                  - sh.heizung.vorgabe() > 15
              - frostschutz:
                  - sh.heizung.vorgabe() <= 7

Der **eval** Ausdruck wird im Beispiel nur ausgeführt, wenn jemand anwesend ist und die Vorgabe über 15 liegt, oder
wenn die Vorgabe höchstens 7 beträgt.
