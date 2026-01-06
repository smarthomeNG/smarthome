.. index:: smartVISU; Beispiel
.. index:: smartVISU; Hello World Beispiel

======================
Vollständiges Beispiel
======================

Das folgende Beispiel zeigt die Definition einiger Items und die notwendigen Item Definitionen um daraus eine
Visualisierung zu erzeugen. (Quasi ein Hello-World für die Visualisierung)

Die eigentlichen Items sind eine Deckenleuchte und eine Tresenbeleuchtung in der Küche, sowie eine dimmbare Stehlampe
im Wohnzimmer:

.. code-block:: yaml

    world:

        kochen:

            deckenlicht:
                name: Decke
                type: bool
                #knx_dpt: 1
                #knx_send: 2/1/10
                #knx_init: 2/2/10

            tresenlicht:
                name: Tresen
                type: bool
                #knx_dpt: 1
                #knx_send: 2/1/11
                #knx_init: 2/2/11

        wohnen:

            stehlampe:
                name: Stehlampe
                type: bool
                #knx_dpt: 1
                #knx_send: 2/1/8
                #knx_init: 2/2/8

                level:
                    type: num
                    #knx_dpt: 5
                    #knx_send: 2/4/8
                    #knx_init: 2/5/8


Um die Räume für die Navigation der Visualisierung zu definieren, müssen folgende Attribute hinzugefügt werden:

    - ``name`` legt den Namen des Raumes fest
    - ``sv_page`` definiert die Art des Navigationseintrages, (hier eine Seite für einen Raum)
    - ``sv_img`` legt das anzuzeigende Icon fest.

Das folgende Beispiel würde eine Visualisierung erzeugen, die zwei Seiten (Küche und Wohnzimmer) hat. Die beiden Seiten
sind jedoch noch leer.

.. code-block:: yaml

    world:

        kochen:
            sv_page: room
            name: Küche
            sv_img: scene_cooking.svg

            deckenlicht:
                name: Decke
                type: bool
                #knx_dpt: 1
                #knx_send: 2/1/10
                #knx_init: 2/2/10

            tresenlicht:
                name: Tresen
                type: bool
                #knx_dpt: 1
                #knx_send: 2/1/11
                #knx_init: 2/2/11

        wohnen:
            sv_page: room
            name: Wohnzimmer
            sv_img: scene_livingroom.svg

            stehlampe:
                name: Stehlampe
                type: bool
                #knx_dpt: 1
                #knx_send: 2/1/8
                #knx_init: 2/2/8

                level:
                    type: num
                    #knx_dpt: 5
                    #knx_send: 2/4/8
                    #knx_init: 2/5/8


Das Ergebnis siht folgendermaßen aus:

.. figure:: assets/hello_world_01.jpg
   :alt: smartVISU Hauptseite


Nun muss noch definiert werden, was auf den Seiten angezeigt werden soll. Das geschieht durch Items, für die das
Attribut ``sv_widget`` definiert ist. Ein ``sv_widget`` Attribut definiert jeweils einen Block auf einer Visu Seite.

Es gibt diverse Varianten das ``sv_widget`` Attribut anzugeben. Im folgenden ist für jeden Block ein Dummy Item
(visublock01, visublock02, visublock03) angelegt, der das ``name`` Attribut angibt (die Überschrift für den Block)
und mit dem ``sv_widget`` Attribut den jeweiligen Block definiert.

Dabei ist im folgenden Beispiel folgendes definiert:

Küche:

    - visublock01: Ein Schalter für das Deckenlicht
    - visublock02: Ein Schalter für das Tresenlicht
    - visublock03: Zwei Schalter (einer für das Deckenlicht und einer für das Tresenlicht)

Wohnzimmer:

    - visublock01: Ein Dimmer für die Stehlampe

.. code-block:: yaml

    world:

        kochen:
            sv_page: room
            name: Küche
            sv_img: scene_cooking.svg

            visublock01:
                name: Raum Beleuchtung
                sv_widget: "{{ basic.stateswitch('', 'world.kochen.deckenlicht') }} Deckenlicht"

            visublock02:
                name: Tresen
                sv_widget: "{{ basic.stateswitch('', 'world.kochen.tresenlicht') }} Arbeitsfläche"

            visublock03:
                name: Gesamte Beleuchtung
                sv_widget: "{{ basic.stateswitch('', 'world.kochen.deckenlicht') }} Deckenlicht <br>
                            {{ basic.stateswitch('', 'world.kochen.tresenlicht') }} Arbeitsfläche"

            deckenlicht:
                name: Decke
                type: bool
                #knx_dpt: 1
                #knx_send: 2/1/10
                #knx_init: 2/2/10

            tresenlicht:
                name: Tresen
                type: bool
                #knx_dpt: 1
                #knx_send: 2/1/11
                #knx_init: 2/2/11

        wohnen:
            sv_page: room
            name: Wohnzimmer
            sv_img: scene_livingroom.svg

            visublock01:
                name: Beleuchtung
                sv_widget: "{{ device.dimmer('', 'Stehlampe', 'world.wohnen.stehlampe', 'world.wohnen.stehlampe.level') }}"

            stehlampe:
                name: Stehlampe
                type: bool
                #knx_dpt: 1
                #knx_send: 2/1/8
                #knx_init: 2/2/8

                level:
                    type: num
                    #knx_dpt: 5
                    #knx_send: 2/4/8
                    #knx_init: 2/5/8


Die Seiten für die beiden Räume sehen dann folgendermaßen aus:

Die Seite für die Küche:

.. figure:: assets/hello_world_02.jpg
   :alt: smartVISU Seite 'Küche'


Die Seite für das Wohnzimmer:

.. figure:: assets/hello_world_03.jpg
   :alt: smartVISU Seite 'Wohnzimmer'
