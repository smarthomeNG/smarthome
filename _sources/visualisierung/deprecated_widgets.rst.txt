
Warnungen für Deprecated Widgets
================================

Ab dem auf v2.9.2 folgenden Release liefert die smartVISU informationen welche Widgets der smartVISU
als veraltet (deprecated) gekennzeichnet wurden und welche Widgets entfernt wurden. Ab SmartHomeNG v1.8
können diese Informationen ausgewertet werden und Warnungen geloggt werden falls veraltete order entfernte
Widgets in der automatischen Generierung genutzt werden sollen.

Standardmäßig wird eine Warning bei Verwendung veralteter (deprecated) Widgets erzeugt. Der Log Eintrag
enthält eine Liste aller verwendeten Widgets mit der Anzahl Items in denen diese Widgets genutzt werden.

Im folgenden Beispiel wird aufgezeigt, dass das Widget **plot.multiaxis** an 9 Stellen verwendet wird.

.. code:: text

    2020-09-14  21:26:43 WARNING  plugins.smartvisu    Deprecated widget usage={'plot.multiaxis': 9}


Standardmäßig wird ein Error bei Verwendung entfernter (removed) Widgets erzeugt. Es wird ein Error erzeugt,
da die generierten Visu Seiten die diese Widgets enthalten nicht funktionieren werden.

Im folgenden Beispiel wird aufgezeigt, dass das einige Widgets an mehreren Stellen verwendet werden.

.. code:: text

    2020-09-14  21:26:43 ERROR    plugins.smartvisu    Removed widget usage={'basic.button': 18, 'basic.dual': 3, 'basic.switch': 11, 'basic.text': 13}


Weiterhin werden Warnungen geloggt, falls Widgets die von Plugins "mitgebracht" werden, veraltete Widgets
der smartVISU nutzen:

.. code:: text

    2020-09-12  10:37:53 ERROR    plugins.smartvisu    deprecated_widgets: Removed widget(s) ['basic.button', 'basic.formula', 'basic.switch'] used in plugin-widget 'widget_window' of plugin 'priv_widgets'


In der Konfiguration des smartvisu Plugins kann eingestellt werden, dass zusätzlich Warnings/Errors mit
den Details der Nutzung in den Item Definitionen geloggt werden. Diese Logeinträge enthalten die Angabe
des Items und des Attributes des Items, in dem das entsprechende Widget genutzt wird:

.. code:: text

    2020-09-12  10:37:53 WARNING  plugins.smartvisu    Deprecated widget used in item wohnung.kochen.plot_temperaturen 'sv_widget': 'plot.multiaxis'
    2020-09-12  10:56:03 ERROR    plugins.smartvisu    Removed widget used in item wohnung.kochen.visu_insel 'sv_widget': 'basic.button'

|
