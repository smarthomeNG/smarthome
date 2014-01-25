# Visualisation

This plugin provides an WebSocket interface for the smartVISU visualisation framework.
Right now the WebSocket interface only supports unencrypted connections. Please use a internal network or VPN to connect to the service.

# Requirements
None.

# Configuration

## plugin.conf
<pre>
[visu]
    class_name = WebSocket
    class_path = plugins.visu
#   ip='0.0.0.0'
#   port=2424
#   acl = ro
#   smartvisu_dir = False
</pre>

This plugins listens by default on every IP address of the host on the TCP port 2424.
It provides read only access to every item. By changing the `acl` attribute to `rw` or `no` you could modify this default 
The `smartvisu_dir` attribute is described in the smartVISU section.

## items.conf

Simply set the visu_acl attribute to something to allow read/write access to the item.


<pre>
[example]
    [[toggle]]
        value = True
        type = bool
        visu_acl = rw
</pre>

## logic.conf
You could specify the `visu_acl` attribute to every logic in your logic.conf. This way you could trigger the logic via the interface.
<pre>
[dialog]
    filename = 'dialog.py'
    visu_acl = true
</pre>


# smartVISU

You could generate pages for the [smartVISU](http://code.google.com/p/smartvisu/) visualisation if you specify the `smartvisu_dir` which should be set to the root directory of your smartVISU installation.
In the examples directory you could find a configuration with every supported element. `examples/items/smartvisu.conf` 

The attribute keywords are:

   * sv_page: to generate a page for this item. You have to specify `sv_page = room` to activate it. Every widget beneath this item will be included in the page.
   * sv_img: with this attribute you could assign an icon or picture for a page or widget.
   * sv_widget: This has to be a double quoted encapsulated string with the smartVISU widget. You could define multiple widgets by separating them by a comma. See the example below:

<pre>
[second]
    [[sleeping]]
        name = Sleeping Room
        sv_page = room
        sv_img = scene_sleeping.png
        [[[light]]]
            name = Light
            type = bool
            visu_acl = rw
            sv_widget = &#123;&#123; device.dimmer('second.sleeping.light', 'Light', 'second.sleeping.light', 'second.sleeping.light.level') &#125;&#125;
            knx_dpt = 1
            knx_listen = 3/2/12
            knx_send = 3/2/12
            [[[[level]]]]
                type = num
                visu_acl = rw
                knx_dpt = 5
                knx_listen = 3/2/14
                knx_send = 3/2/14
</pre>

But instead of giving the widget distinct options you could use `item` as a keyword.
The page generator will replace it with the current path. This way you could easily copy widget calls and don't type the item path every time.
<pre>
[second]
    [[sleeping]]
        name = Sleeping Room
        sv_page = room
        sv_img = scene_sleeping.png
        [[[light]]]
            name = Light
            type = bool
            visu_acl = rw
            sv_widget = &#123;&#123; device.dimmer('item', 'item.name', 'item', 'item.level') &#125;&#125;
            knx_dpt = 1
            knx_listen = 3/2/12
            knx_send = 3/2/12
            [[[[level]]]]
                type = num
                visu_acl = rw
                knx_dpt = 5
                knx_listen = 3/2/14
                knx_send = 3/2/14
</pre>

