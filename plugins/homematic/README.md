# homematic - Plugin

Requirements
============
Homematic Hardware Gateway


Configuration
=============

## plugin.conf

<pre>
[homematic]
    class_name = Homematic
    class_path = plugins.homematic
    host = 192.168.50.250
    port = 2001
</pre>

## items.conf
<pre>
    [[deckenlicht_sofa]]
        name = Deckenlicht Sofa
        visu = yes
        type = bool
        hm_address = JEQ0017982
        hm_type = switch
</pre>

#
