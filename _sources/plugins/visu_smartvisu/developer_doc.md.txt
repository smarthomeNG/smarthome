# visu_smartvisu

## Visualisation plugin (smartVISU support) - for developers

```
Copyright 2012-2013 Marcus Popp                  marcus@popp.mx
Copyright 2016- Martin Sinn                      m.sinn@gmx.de

This plugin is part of SmartHomeNG.

Visit:  https://github.com/smarthomeNG/
        https://knx-user-forum.de/forum/supportforen/smarthome-py
```

This file gives **smarthomeNG** developers additional information about the smartvisu plugin. For information about the configuration of the plugin refer to **README.md**.

This file describes the widget handling for smartVISU widgets and the autogeneration of smartVISU pages.


## Files of the Plugin
The plugin is made up by several files, which are described below.


### __ init __.py
Main file of the plugin.

### sv_widgets subdirectory
This directory stores general-use widgets, which are not specific to a plugin. These plugins are installed together with widgets from different plugins.

### tplNG subdirectory
This directory stores template files, that are used while auto-generating pages for smartVISU. The files in this directory are copied to the pages/base/tplNG directory, which is created.

## Handling of smartVISU widgets
The visu plugin handles widgets, which a plugin developer delivers with the plugin he has written. For this to work, the attribute **`smartvisu_dir`** in the visu section of **`plugin.yaml`** must be set to the base directory of smartVISU. 

It handles widgets that define their own Javascript or css. The Javascript and css files must follow the same naming convention as the html file.

### Add a widget to a plugin
A developer of a plugin can add widgets to the plugin. He has to create a directory named **sv_widgets** in his plugin directory and add the file(s) of the widget to that directory.

All files in the **sv_widgets** directory are copied to the smartVISU installation.

A widget html-file may contain multiple widgets.

For further automatic integration the widget must follow a name convention. It must be named **`widget_<class>.html`**. Where **`<class>`** is the class name for the import statement in smartVISU. If this convention is followed, a statement in the form of

```
	{% import "widget_<class>.html" as <class> %}
```
is generated.

**Example**:
>For a file **`widget_hue.html`** the statement

>```
	{% import "widget_hue.html" as hue %}
```
is generated.
The widgets in that file can be called by the directives

```
	{{ hue.control( ... ) }}
 or
	{{ hue.control_group( ... ) }}
```

If a Javascript file would exist for the hue widget, it would have to have the name  **`widget_hue.js`**. To include this file in smartVISU, the following lines are added to root.html:
>
>```
{% if isfile('widgets/sh_widgets/widget_hue.js') %}
	<script type="text/javascript" src="widgets/sh_widgets/widget_hue.js"></script>{% endif %}
```

The handling of a css file is analog to the Javascript handling.


### Modifications to smartVISU made by the visu plugin
For this functionality to work, smarthome.py must have write access to the smartVISU directory structure. The modifications to smartVISU are minimal invasive. The implementation may change, if smartVISU is forked.

The visu plugin creates a directory named **_sh_widgets** in the **widgets** directory of smartVISU. All files copied from the different plugins are stored in this directory.

On the first run the visu plugin creates a copy of the file **root.html** in the **pages/base** directory of smartVISU. The copied file is called **root_master.html**.

On each start of smarthome.py the visu plugin creates a new version of **root.html**. The new version is made of the contents of **root_master.html** and the necessary statements are inserted.
