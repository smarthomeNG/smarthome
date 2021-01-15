
==============================
Item Attribute zur Generierung
==============================

Die Namen der Item-Attribute die smartVISU spezifisch sind, beginnen mit **sv_**.

sv_page
~~~~~~~

Mit dem Attribut **sv_page** wird festgelegt, auch welche Art von Visu-Seite generiert wird und welchen
Typ die generierte Seite hat (Content Seite oder Separator).

Dieses Attribut legt fest, auf welche Visu-Seite sich die weiteren smartVISU spezifischen Attribute
beziehen. Dabei gilt diese Einstellung nicht nur für das Item selbst in der das Attribut definiert wird,
sondern auch für alle Items die in der Item-Tree Struktur unterhalb dieses Items definiert werden.

Der Name der Seite und damit auch der Eintrag in der Navogation werden durch das **name:** Attribut des
Items festgelegt.


Gültige Einträge für **sv_page** sind:

+---------------+---------------------------------------------------------------+
| Wert          | Beschreibung                                                  |
+===============+===============================================================+
| room          | Die Seite erscheint in der Raum-Navigation der smartVISU      |
+---------------+---------------------------------------------------------------+
| seperator     | Fügt einen Separator in die Raum-Navigation ein               |
+---------------+---------------------------------------------------------------+
| overview      | Erzeugt eine Seite, die verschiedene Items zusammen gruppiert |
|               | und fügt diese in die Raum-Navigation ein                     |
+---------------+---------------------------------------------------------------+
| category      | Die Seite erscheint in der Category-Navigation der smartVISU  |
+---------------+---------------------------------------------------------------+
| cat_seperator | Fügt einen Separator in die Category-Navigation ein           |
+---------------+---------------------------------------------------------------+
| cat_overview  | Erzeugt eine Seite, die verschiedene Items zusammen gruppiert |
|               | und fügt diese in die Category-Navigation ein                 |
+---------------+---------------------------------------------------------------+


sv_overview
~~~~~~~~~~~

Wenn eine Seite im **sv_page** Attribut als **overview** definiert wurde, zeigt sie Items eines
spezifischen Typs an. Der Name/Identifier des Type wird durch das Setzen des Attributs **sv_overview**
auf einen eindeutigen Namen definiert.
Items die auf dieser Seite angezeigt werden sollten, müssen das Attribut **sv_item_type** definieren
und auf den Wert setzen, der im **sv_overview** definiert wurde.

sv_img
~~~~~~

Die Navigationseinträge und der Kopf der Seite enthalten in Icon. Das Attribut **sv_img**
enthält den Namen des zu verwendenden Icons.


sv_nav_aside
~~~~~~~~~~~~

**sv_nav_aside** erlaubt die Spezifikation eines Widgets, dass im Raum-Menu am rechten Rand der
Navigation-Bar angezeigt wird. (obere Zeile)


sv_nav_aside2
~~~~~~~~~~~~~

**sv_nav_aside2** erlaubt die Spezifikation eines Widgets, dass im Raum-Menu am rechten Rand der
Navigation-Bar angezeigt wird. (untere Zeile)


sv_widget
~~~~~~~~~

**sv_widget** erlaubt die Spezifikation eines Widgets. In diesem Attribut können auch mehrere Widgets angegeben werden.
Die Widgets werden eingebettet in einen Widget-Block angezeigt. Die Widgets werden in einem Widget-Block vom Typ 2
(Collapsable Block) angezeigt.


sv_widget2
~~~~~~~~~~

**sv_widget2** erlaubt die Spezifikation eines Widgets (oder mehrerer Widgets), die in einen Widget-Block eingebettet
werden, der mehrere Seiten unterstützt. Die Widgets werden auf der zweiten Seite eines Widget-Blocks vom Typ 2
(Collapsable Block) mit mehreren Seiten angezeigt.

Widget-Blocks mit drei Seiten werden durch die Autogenerierung bisher nicht unterstützt.


sv_item_type
~~~~~~~~~~~~

**sv_item_type** erlaubt das Anzeigen eines Items auf einer Seite vom Typ **overview**


sv_heading_left
~~~~~~~~~~~~~~~

**sv_heading_left** erlaubt die Spezifikation eines Widgets, welches im Heading Bereich am Kopf der Visu-Seite
angezeigt wird. Dieses Widget ist in einen Block eingebettet und linksbündig ausgerichtet.


sv_heading_center
~~~~~~~~~~~~~~~~~

**sv_heading_center** erlaubt die Spezifikation eines Widgets, welches im Heading Bereich am Kopf der Visu-Seite
angezeigt wird. Dieses Widget ist in einen Block eingebettet und zenzriert ausgerichtet.


sv_heading_right
~~~~~~~~~~~~~~~~

**sv_heading_right** erlaubt die Spezifikation eines Widgets, welches im Heading Bereich am Kopf der Visu-Seite
angezeigt wird. Dieses Widget ist in einen Block eingebettet und rechtsbündig ausgerichtet.


Example
~~~~~~~

.. code-block:: yaml

    first:
     ...
    menu_divider:
        sv_page: seperator
        name: Private area of the house

    second:

        sleeping:
            name: Sleeping Room
            sv_page: room
            sv_img: scene_sleeping.png
            sv_nav_aside: "{{ basic.float('sleep_temp_id', 'second.sleeping.temp', '°') }}"

            light:
                name: Light
                type: bool
                visu_acl: rw
                sv_widget: "&    ## 123;{ device.dimmer('second.sleeping.light', 'Light', 'second.sleeping.light', 'second.sleeping.light.level') }}"
                knx_dpt: 1
                knx_listen: 3/2/12
                knx_send: 3/2/12

                level:
                    type: num
                    visu_acl: rw
                    knx_dpt: 5
                    knx_listen: 3/2/14
                    knx_send: 3/2/14


But instead of giving the widget distinct options you could use **item** as a keyword.

The page generator will replace it with the current path. This way you could easily copy widget calls and don't type the item path every time.

.. code-block:: yaml

    second:

        sleeping:
            name: Sleeping Room
            sv_page: room
            sv_img: scene_sleeping.png

            light:
                name: Light
                type: bool
                visu_acl: rw
                sv_widget: "{{ device.dimmer('item', 'item.name', 'item', 'item.level') }}"
                knx_dpt: 1
                knx_listen: 3/2/12
                knx_send: 3/2/12

                level:
                    type: num
                    visu_acl: rw
                    knx_dpt: 5
                    knx_listen: 3/2/14
                    knx_send: 3/2/14


logic.yaml
----------

You could specify the **visu_acl** attribute to every logic in your logic.yaml. This way you could trigger the logic via the interface.

.. code-block:: yaml

    dialog:
        filename: dialog.py
        visu_acl: 'true'

