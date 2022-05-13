
.. index:: Stateengine; Zustand-Item

============
Zustand-Item
============

Zustände
--------

Alle Items unterhalb des Regelwerk-Items (``rules``)
beschreiben Zustände des Objekts ("Zustands-Item").
Die Ids der Zustands-Items sind beliebig, im Beispiel ``day``.

.. code-block:: yaml

    #items/item.yaml
    raffstore1:
        automatik:
            struct: stateengine.general
            rules:
                day:
                    name: Tag # optional, wie bei allen Items

Bedingungen
-----------

Jeder Zustand kann eine beliebige Anzahl von Bedingungsgruppen
haben. Jede Bedingungsgruppe definiert ein Set an Bedingungen das
überprüft wird, wenn der aktuelle Status neu ermittelt wird.

Jede Bedingungsgruppe wird durch ein Item
("Bedingungsgruppen-Item") unterhalb des Zustands-Items
abgebildet. Details zu den Bedingungen
werden im Abschnitt :ref:`Bedingungen` erläutert.

Aktionen
--------

Jeder Zustand kann eine beliebige Anzahl an Aktionen definieren.
Sobald ein Zustand aktueller Zustand wird, werden die Aktionen des
Zustands ausgeführt. Für die Aktionen gibt es vier Ereignisse, die
festlegen, wann eine Aktion ausgeführt wird.

Details zu den Aktionen werden im Abschnitt
:ref:`Aktionen` erläutert.

Templates für Zustände
----------------------

Da viele Items immer wieder die gleichen Zustände inklusive Aktionen und Bedingungen
nutzen, gibt es die Möglichkeit, Zustände als Vorlagen zu deklarieren und diese
dann in die entsprechenden Zustandsautomaten der jeweiligen Items zu integrieren.

Beispielsweise wird man alle Items mit den identen Sperr- und Aussetz/Suspendfunktionen
ausstatten wollen. Außerdem werden vermutlich mehrere Jalousien auf die selbe Weise
auf den aktuellen Sonnenstand reagieren oder mehrere Lichter in der Nacht gemeinsam abgedunkelt.

Neben der vom Plugin bereitgestellten Möglichkeit, :ref:`Zustand-Templates` zu definieren
und mittels ``se_use`` zu referenzieren, bietet sich ab **smarthomeNG 1.6** das ``struct`` Attribut an.
Zum einen können in der Datei ``etc/struct.yaml`` eigene Vorlagen definiert werden,
zum anderen stellt das Plugin folgende Vorlagen fix fertig bereit:

- stateengine.state_lock: Sperren der Zustandsevaluierung, sobald das Sperritem "lock" aktiv ist.
- stateengine.state_suspend: Aussetzen der Evaluierung für eine bestimmte Zeit bei manueller Betätigung (z.B. Taster)
- stateengine.state_release: Sofortiges Entsperren und Beenden des Suspend-Modus und Neuevaluierung

Gemeinsam mit der Vorlage stateengine.general, die allgemein relevante Items automatisch erstellt, könnte
ein Item wie unten zu sehen bestückt werden. Das Einbinden der Zustandsvorlagen findet dabei auf gleicher
Hierarchieebene wie das Regelwerk-Item statt. Genauere Angaben hierzu sind unter :ref:`Zustand-Templates` zu finden.
Informationen zu ``se_use`` findet man unter :ref:`Sonstiges`.

Zusätzlich können eigene Zustände (beispielsweise day) definiert werden.

.. code-block:: yaml

    #items/item.yaml
    raffstore1:
        automatik:
            struct:
              - stateengine.general
              - stateengine.state_lock
              - stateengine.state_suspend
              - stateengine.state_release

            rules:
                day:
                    name: Tag # optional, wie bei allen Items
