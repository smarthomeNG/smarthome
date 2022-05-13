# Visualisation (smartVISU support)

```
Copyright 2016- Martin Sinn                      m.sinn@gmx.de
Copyright 2012-2013 Marcus Popp                  marcus@popp.mx

This plugin is part of SmartHomeNG.

Visit:  https://github.com/smarthomeNG/
        https://knx-user-forum.de/forum/supportforen/smarthome-py

```

This plugin does the smartVISU specific handling. It installs widgets from the plugin directories to smartVISU and it auto-generates pages for smartVISU.

This plugin (**```visu_smartvisu```**) does not do the communication with the browser. The websocket protocol for the browser communication is implemented in **```visu_websocket```**.

The plugins **```visu_websocket```** and **```visu_smartvisu```** replace the old visu plugin.


## Requirements

None.

**But**: For the visualization to work, the websocket protocol must be configured. This is done by configuring the visu_websocket plugin.


## Configuration

The configuration of the plugin itself is done in the file **`etc/plugin.yaml`**. The configuration of the visualization of the items is done by defining additional attributes of the item in the file **`items/*.yaml`**.

### plugin.yaml

```yaml
smartvisu:
    plugin_name: visu_smartvisu
    # smartvisu_dir: False
    # handle_widgets: True
```

#### visu_dir
** Only used for **old visu** (not for smartVISU) **

Directory in which the generated web pages of the old visa are stored.

#### smartvisu_dir
You could generate pages for the smartVISU visualisation if you specify the **`smartvisu_dir`** which should be set to the root directory of your smartVISU installation.

In the examples directory you could find a configuration with every supported element. `examples/items/smartvisu.yaml`

#### handle_widgets

By default, the visu plugin handles smartVISU widgets. If your run into problems, you can disable the widget handling by setting this attribute to **`False`**.

Widgets that come with a plugin are stored in in a subdirectory to the plugin folder. These widgets are installed into smartVISU upon start of smarthomeNG. These widgets can be used in smartVISU without manually adding include startements to smartVISU.

These widgets can be used in auto-generation of visu pages. Therefor they can be included in the **`sv_widget`** attribute of an item.


### items.yaml
Most of the entries in item.yaml are specific to smartVISU. These parameters beginn with **`sv_`**.

#### visu_acl
Simply set the **`visu_acl`** attribute to something to allow read/write access to the item.


#### sv_page
 Set **`sv_page`** to to one of the following values generate a page for this item. Every widget beneath this item will be included in the page.

Valid values for **`sv_page`** are:

```
+---------------+-----------------------------------------------------+
| value         | description                                         |
+===============+=====================================================+
| room          |  The page appears in the room view of smartVISU     |
+---------------+-----------------------------------------------------+
| seperator     | Inserts a seperator between entries in the room     |
|               | navigation                                          |
+---------------+-----------------------------------------------------+
| overview      | The page groups of different items together         |
+---------------+-----------------------------------------------------+
|               |                                                     |
| category      | The page appears in the category view of smartVISU  |
+---------------+-----------------------------------------------------+
| cat_seperator | Inserts a seperator between entries in the category |
|               | navigation                                          |
+---------------+-----------------------------------------------------+
| cat_overview  | The page groups of different items together and is  |
|               | added to the category navigation                    |
+---------------+-----------------------------------------------------+
|  room_lite    |  The page appears in a lite view of the             |
|               | visualization                                       |
+---------------+-----------------------------------------------------+

```

--> Beschreibung für overview und separator vervollständigen

#### sv_overview
If a page has defined **`sv_page`** as **`overview`**, it shows items of a specific type. The name/identifier of the type is defined by setting **`sv_overview`** to an unique name. For items to be displayed on this page, the items have to define  **`sv_item_type`** and set it to the value of **`sv_overview`**.

#### sv_img
By setting **`sv_img`** you could assign an icon or picture for a page or widget.


#### sv_nav_aside
**`sv_nav_aside`** allows the specification of a widget, that is being displayed at the right side of the navigation bar for a room. (upper line)

Relative item references are supported.


#### sv_nav_aside2
**`sv_nav_aside2`** allows the specification of a widget, that is being displayed at the right side of the navigation bar for a room. (lower line)

Relative item references are supported.


#### sv_widget
**`sv_widget`** allows the specification of a widget. You could define multiple widgets. The widget(s) is/are shown by being encapsulated in a block of type 2 (Collapsable Block).

Relative item references are supported.


#### sv_widget2
**`sv_widget2`** allows the specification of a widget for widget blocks with two pages. You could define multiple widgets. The widget(s) is/are shown by being encapsulated in a block of type 2 (Collapsable Block) with multiple pages.

Widget blocks with three pages are not supported yet.

Relative item references are supported.


#### sv_item_type
**`sv_item_type`** allows items to be displayed on an overview page.


#### sv_heading_left
**`sv_heading_left`** allows the specification of a widget, hat is being displayed at the top of a room-page. This widget is shown without being encapsulated in a block. The widget is aligned to to the left.

For this setting to work, the files **heading.html** and **room.html** have to be installed in the **pages/base/tpl** directory of smartVISU.


#### sv_heading_center
**`sv_heading_center`** allows the specification of a widget, hat is being displayed at the top of a room-page. This widget is shown without being encapsulated in a block. The widget is aligned to to the center.

For this setting to work, the files **heading.html** and **room.html** have to be installed in the **pages/base/tpl** directory of smartVISU.


#### sv_heading_right
**`sv_heading_right`** allows the specification of a widget, hat is being displayed at the top of a room-page. This widget is shown without being encapsulated in a block. The widget is aligned to to the right.

For this setting to work, the files **heading.html** and **room.html** have to be installed in the **pages/base/tpl** directory of smartVISU.


If one of the **`sv_heading_...`** parameters is defined, heading.html from the template directory ?tpldir? is added to the page.

--> tpldir = directory + '/pages/base/tpl'
--> directory = parameter to pages() in smartvisu.py -> self.smartvisu_dir

#### Example

```yaml
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
```

But instead of giving the widget distinct options you could use **`item`** as a keyword.

The page generator will replace it with the current path. This way you could easily copy widget calls and don't type the item path every time.

```yaml
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
```

### logic.yaml

You could specify the **`visu_acl`** attribute to every logic in your logic.yaml. This way you could trigger the logic via the interface.

```yaml
dialog:
    filename: dialog.py
    visu_acl: 'true'
```
