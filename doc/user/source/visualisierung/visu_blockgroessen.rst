Unterschiedliche Blockgrößen
============================

Möglichkeiten
-------------

Die smartVISU unterstützt Blöcke mit drei unterschiedlichen Größen.
Gemeint ist hierbei die Mindestgröße des Blocks. Wenn in dem Block
Widgets platziert werden, die mit dem Platz nicht auskommen, wird der
Block automatisch höher. Die Blockhöhen unterscheiden sich in etwa um
die Höhe der Heading-Zeile.

In den bisherigen Releases von smarthome.py/SmartHomeNG wurden beim
automatischen generieren von smartVISU Seiten immer Blöcke der Größe
**2** (mittel) verwendet.

Im aktuellen Release können auch Blöcke der Größen **1** (groß) und
**3** (klein) in die Seiten generiert werden.

Dieses kann als Item-Attribut **``sv_blocksize``** festgelegt werden.

Am Beispiel des Trenners **``Tests``** zeigt die folgende Konfiguration,
wie Trenner konfiguriert werden:

.. code-block:: yaml

    %YAML 1.1
    ---

    wohnung:

        buero:

            verbraucher:
                name: Verbraucher
                sv_blocksize: 1
                sv_widget: "{{ basic.switch('wohnung.buero.tv', 'wohnung.buero.tv', icon0~'control_on_off.png', icon0~'control_standby.png') }} <br> {{ basic.switch('wohnung.buero.computer', 'wohnung.buero.computer', icon0~'control_on_off.png', icon0~'control_standby.png') }} <br> {{ basic.switch('wohnung.buero.schrank', 'wohnung.buero.schrank', icon0~'control_on_off.png', icon0~'control_standby.png') }} <br> {{ basic.switch('wohnung.buero.steckdose_tuer', 'wohnung.buero.steckdose_tuer', icon0~'control_on_off.png', icon0~'control_standby.png') }}"

``sv_blocksize`` dient zur Einstellung der (minimalen) Blockhöhe und
darf die Werte 1, 2 oder 3 annehmen. Wird ``sv_blocksize``\ nicht
angegeben, so wird der Default-Wert **2** benutzt.
