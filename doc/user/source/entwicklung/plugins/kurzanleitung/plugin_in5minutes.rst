
=====================================
In wenigen Minuten zum eigenen Plugin
=====================================


Plugins sind Erweiterungen von SmartHomeNG mit zusätzlichen Funktionen. Sie sind in Python geschrieben.
Um ein neues Plugin hinzuzufügen, wird der Plugin-Code und ein entsprechender Eintrag in der Konfigurationsdatei ``plugin.yaml`` benötigt.

Eine gute Basis für ein eigenes Plugin ist das Beispielplugin, welches komplett
mit allen notwendigen Dateien auf github unter https://github.com/smarthomeng/smarthome im ``/dev``-Ordner zur Verfügung steht.


Beschreibung des Plugins
========================

Übersicht
---------

Das Plugin wird in einem eigenen Ordner unterhalb des ``/plugins``-Ordner abgelegt. Der Name des Ordners entspricht dem Namen des Plugins in **Kleinschreibung**.

Derzeit besteht ein Plugin mindestens aus drei Dateien, die alle im Plugin Ordner liegen. Dies sind:

  - ``__init__.py``
  - ``plugin.yaml``
  - ``user_doc.rst``

Die Datei ``__init__.py`` enthält den Python-Code des Plugins.

Die Datei ``plugin.yaml`` enthält die Metadaten des Plugins.
Diese geben eine formale Beschreibung des Plugins und werden verwendet, um die Dokumentation
zu erstellen und das Plugin im Admin-GUI verwalten zu können.

Die Datei ``user_doc.rst`` beinhaltet zusätzliche Dokumentation zum Plugin,
ausführlichere Beschreibungen, umfangreichere Beispiele oder Anwendungsmöglichkeiten
über die ``plugin.yaml`` hinaus. Auch diese Datei wird verwendet,
um die Dokumentation von SmartHomeNG zu erstellen.

Optional werden im Unterverzeichnis ``webif`` die Dateien dabgelegt, welche das Webinterface implementieren. Das
Verzeichnis hat folgenden Inhalt:

  - ``__init__.py``
  - Verzeichnis ``static``
  - Verzeichnis ``templates``

Die Datei ``__init__.py`` enthält den Python-Code des Webinterfaces des Plugins.

Im Verzeichnis ``static`` werden Dateien abgelegt, die durch das Webinterface an den Browser ausgeliefert werden.
Es gibt mindestens das Unterverzeichnis ``img``, in dem das Logo des Plugins under dem Namen ``plugin_logo.png``
gespeichert wird. Zulässig als Plugin Logos sind auch ``plugin_logo.jpg`` und ``plugin_logo.svg``

Weiterhin kann es ein Unterverzeichnis ``assets`` geben, in dem weitere Dateien (z.B. zur Dokumentation user_doc)
abgelegt werden.


.. hint::

   Das in früheren Versionen verwendete ``README``-Format für die Dokumentation von Plugins ist veraltet.
   Ein Großteil der Dokumentation ist in die Metadaten-Dokumentation in ``plugin.yaml`` übergegangen.
   Die restliche Dokumentation sollte nur noch im ``user_doc``-Format erfolgen.

   Soweit möglich, sollten bestehende ``README`` im Rahmen von Aktualisierungen in entsprechende ``user_doc`` überführt werden.

Um das Plugin zu laden, muss es in der Konfigurationsdatei ``/etc/plugin.yaml`` eingebunden und konfiguriert werden.


Die Metadaten: plugin.yaml
--------------------------

Diese Datei stellt Metadaten über das Plugin in den folgenden Abschnitten bereit:

* `plugin`  -  globale Attribute des Plugins
* `parameters`  -  Definition der Konfigurationsoptionen in ``etc/plugin.yaml``
* `item_attributes`  -  Definition der Item-Attribute, die durch dieses Plugin genutzt werden
* `item_structs`  -  Vorlagen für Item-Structs (Teilbäume) des Plugins
* `logic_parameters`  -  Definition von Parametern für Logiken, soweit das Plugin diese implementiert
* `plugin_functions`  -  Funktionen, die das Plugin für die Nutzung z.B. in Logiken bereitstellt


Der Typ des Plugins muss aus der folgenden Liste ausgewählt werden:

* gateway
* interface
* protocol
* system
* web


Beispiel einer Metadaten-Datei:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    # meta data for the plugin
    plugin:
        # Global plugin attributes
        type: interface                # plugin type (gateway, interface, protocol, system, web)

    parameters:
        # Definition of parameters to be configured in etc/plugin.yaml

    item_attributes:
        # Definition of item attributes defined by this plugin

    item_structs: NONE

    logic_parameters: NONE

    plugin_functions: NONE




Die Dokumentation: user_doc.rst
-------------------------------

Die Dokumentation beginnt mit dem Titel, der dem Namen des Plugins entspricht.

.. important::

   Die erste Überschrift der Dokumentationsdatei ``user_doc`` MUSS dem Kurznamen des Plugins in Kleinbuchstaben entsprechen.

   Dieser Eintrag wird als Einstiegspunkt für die Navigation in der Dokumentation genutzt.
   Ein anderer Eintrag als Überschrift sorgt für Inkonsistenzen in den Navigationselementen.

Die Datei sollte die folgende Struktur haben.

Die Konfigurationsparameter selbst müssen in der user_doc.rst nicht beschrieben werden. Die Dokumentation der
Konfigurationsparameter und der Item Attribute wird automatisch aus den Metadaten (aus der plugin.yaml) generiert.
Falls gewünscht kann jeweils auf die (automatisch generierte) Seite mit der Konfigurationsdokumentation verwiesen
werden.


.. literalinclude:: /dev/sample_plugin/user_doc.rst
    :caption: user_doc.rst des Sampe Plugins

|


Konfigurieren des Plugins in der Systemkonfiguration `/etc/plugin.yaml`
-----------------------------------------------------------------------

Die Konfigurationsdatei ``plugin.yaml`` befindet sich im Unterordner ``etc`` der SmartHomeNG-Installation.
Hier wird SmartHomeNG mitgeteilt, welche Plugins geladen werden sollen, wo sie zu finden sind und welche Optionen sie ggf. benötigen.

Dies ist ein typischer Abschnitt für ein neues Plugin. Wir nehmen an, dass das Plugin ``myplugin`` heißt:

.. code-block:: yaml

    # etc/plugin.yaml
    myplugin_instance:
        plugin_name: myplugin
        parameter1: 42


Werfen wir einen Blick auf die einzelnen Angaben:

``myplugin_instance``:

Das ist der Name der tatsächlich geladenen Instanz des Plugins. Er kann frei gewählt werden.
Wenn mehrere Instanzen eines Plugins geladen werden (z.B. für mehrere Geräte des gleichen Typs),
wird anhand dieses Namens zwischen den Instanzen (und damit den Geräten) unterschieden.

``plugin_name``:

Das ist der Name des Plugin, der auch für den Plugin-Ordner verwendet wurde (wieder in Kleinbuchstaben).

``parameter1``:

Es können mehrere Parameter definiert werden, deren Werte dem Plugin bei der Initialisierung übergeben werden.
Sie können zur Konfiguration verwendet werden.


Der Plugin-Code: `__init__.py`
------------------------------

Das Nächste ist das Plugin selbst. Der Code befindet sich in der Datei ``/plugins/myplugin/__init__.py``.
Alle Plugins haben die gleiche Struktur. Der Einfachheit halber wird das oben verlinkte Beispielplugin als Grundlage verwendet.

Es gibt mehrere Funktionen, die erforderlich sind, damit SmartHomeNG mit dem Plugin korrekt kommunizieren kann.
Die meisten davon werden vom SmartHomeNG-Scheduler aufgerufen.

Zusätzlich werden eigene Funktionen im Plugin definiert, die die eigentlichen Aufgaben ausführen.
Der Scheduler kann angewiesen werden, diese zu bestimmten Zeiten oder in festgelegten Intervallen aufzurufen.
Das ist näher im Abschnitt "Der Scheduler" beschrieben.

.. hint::
   Für eine nutzbare Vorlage bitte nicht den folgenden Code, sondern das Beispielplugin (s.o.) verwenden!


.. code-block:: python

    #!/usr/bin/env python3

    import logging
    logger = logging.getlogger(__name__)

    from lib.model.smartplugin import *
    from lib.item import Items

    class Myplugin(SmartPlugin):

    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = "a.b.c"

        def __init__(self, sh):
            """
            Initializes the plugin. The parameters describe for this method are pulled from the entry in plugin.conf.

            :param sh:  The instance of the smarthome object, save it for later references
            """
            # attention:
            # if your plugin runs standalone, sh will likely be None so do not rely on it later or check it within your code

            self._sh = sh
            self.logger = logging.getLogger(__name__) 	# get a unique logger for the plugin and provide it internally

            # todo:
            # put any initialization for your plugin here


        def run(self):
            """
            Run method for the plugin
            """
            self.logger.debug("run method called")
            self.alive = True


        def stop(self):
            """
            Stop method for the plugin
            """
            self.logger.debug("stop method called")
            self.alive = False


        def parse_item(self, item):
            """
            Default plugin parse_item method. Is called when the plugin is initialized.
            The plugin can, corresponding to its attribute keywords, decide what to do with
            the item in future, like adding it to an internal array for future reference

            :param item:    The item to process.
            :return:        If the plugin needs to be informed of an items change you should return a call back function
                            like the function update_item down below. An example when this is needed is the knx plugin
                            where parse_item returns the update_item function when the attribute knx_send is found.
                            This means that when the items value is about to be updated, the call back function is called
                            with the item, caller, source and dest as arguments and in case of the knx plugin the value
                            can be sent to the knx with a knx write function within the knx plugin.

            """
            if self.has_iattr(item.conf, 'foo_itemtag'):
                self.logger.debug("parse item: {0}".format(item))

            # todo
            # if interesting item for sending values:
            #   return update_item


        def parse_logic(self, logic):
            """
            Default plugin parse_logic method
            """
            if 'xxx' in logic.conf:
                # self.function(logic['name'])
                pass


        def update_item(self, item, caller=None, source=None, dest=None):
            """
            Write items values

            :param item: item to be updated towards the plugin
            :param caller: if given it represents the callers name
            :param source: if given it represents the source
            :param dest: if given it represents the dest
            """
            # todo
            # change 'foo_itemtag' into your attribute name
            if item():
                if self.has_iattr(item.conf, 'foo_itemtag'):
                    self.logger("update_item ws called with item '{}' from caller '{}', source '{}' and dest '{}'".format(item, caller, source, dest))
                    pass


    def run_logic(self, logic, caller=None, source=None, dest=None):
        # …

    def bla(self):
        logger.info("bla")



Zuerst werden die benötigten Module importiert und der Logger verfügbar gemacht.
Diese ermöglicht es, Informationen in die Logdateien von SmartHomeNG auszugeben.
Danach beginnt die Klassendefinition. Der Klassenname muss dem ``classname``-Parameter
in der ``/etc/plugin.yaml`` entsprechen. Danach werden die notwendigen Funktionen definiert.


Vordefinierte Funktionen des Plugins
====================================


.. code-block:: python

    def __init__(self, sh):


Die ``__init__``-Funktion wird einmal aufgerufen, wenn SmartHomeNG im Rahmen der Initialisierung
das Plugin lädt, bevor die Items geladen sind. Hier wird der Code eingefügt,
den das Plugin zur Einrichtung benötigt.
Zum Beispiel könnte ein serieller Port zur Verbindung mit einem externen Gerät vorbereitet,
Dateien geöffnet, Variablen initialisiert usw. werden. Die Parameter der ``/etc/plugin.yaml``
können ausgelesen und verarbeitet oder durch Vorgabewerte ersetzt werden, wenn sie nicht konfiguriert sind.

Die Funktion erhält den Parameter ``sh``, die den Zugriff auf SmartHomeNG-Funktionen ermöglicht. Dieser Parameter sollte in einer Klassenvariable gesichert werden, um ihn später zur Verfügung zu haben.


----

.. code-block:: python

    def run(self):


Die ``run``-Funktion wird einmalig aufgrufen, wenn SmartHomeNG startet. Zu diesem Zeitpunkt sind die Items bereits geladen. Die Variable ``self.alive`` muss hier auf ``True`` gesetzt werden.


----

.. code-block:: python

    def stop(self):


Diese Routine wird aufgerufen, wenn SmartHomeNG beendet wird.
Hier können Dateien und Verbindungen geschlossen werden.
Es müssen alle Threads beendet werden, die das Plugin ggf. gestartet hat.
Die Variable ``self.alive`` muss auf ``False`` gesetzt werden.

Wenn ``self.alive`` auf ``False`` gesetzt ist, sollte das Plugin Änderungen an Items
nicht mehr weitergeben und auch keine Daten empfangen und in Items sichern.


----

.. code-block:: python

    def parse_item(self, item):


Diese Funktion wird während des Starts für jedes Item einmal aufgerufen, wenn SmartHomeNG
die Datei ``/items/items.yaml`` liest. Hier können Item-Parameter ausgelesen und entsprechende Aktionen ausgelöst werden.
Wenn z.B. das folgende Item definiert ist:

.. code-block:: yaml

    # items/xxx.yaml
    upstairs:
        lamp:
            type: bool
            visu_acl: rw
            ivalue: 1
            knx_dpt: 1
            …


dann kann mit dem folgenden Code auf den Parameter ``ivalue`` zugegriffen werden:

.. code-block:: python

    if 'ivalue' in item.conf:
        ad=item.conf['ivalue']
        return self.update_item
    else:
        return None


Hier wird geprüft, ob der Parameter ``ivalue`` im Item definiert ist.
Falls ja, wird der Variable ``ad`` der Wert des Parameters zugewiesen und die Funktion
``update_item()`` zurückgegeben. Diese Funktion wird dann von SmartHomeNG jedes mal aufgerufen,
wenn sich der Wert des Items ändert. Jedes Mal, wenn die Lampe z.B. per KNX ein- oder ausgeschaltet wird,
wird wieder die Funktion ``update_item()`` aufgerufen. Parameterwerte sind immer Stringwerte.
Auch wenn der Wert mit ``ivalue: 1`` definiert ist, wird der String "1" zurückgegeben.
Wenn eine Zahl benötigt wird, muss der Wert selbst umgewandelt werden.
Wenn der Parameter ``ivalue`` nicht in der Item-Konfiguration enthalten ist, wird keine Aktion
ausgelöst und das Item hat keinen Einfluss auf und keine Verbindung zum Plugin.


----

.. code-block:: python

    def parse_logic(self, logic):


Diese Funktion wird beim Systemstart für jede Logik aufgerufen, wenn SmartHomeNG die Datei ``/etc/logic.yaml`` liest.
Hier können Logikparameter ausgelesen und Aktionen ausgeführt werden. Wenn z.B. die folgende Logik definiert ist:

.. code-block:: yaml

    etc/logic.yaml
    jalousie_up:
        filename: jalousie-up.py
        crontab: sunrise+20m
        some_plugin_setting: send-notify

kann das Plugin jetzt den Parameter ``some_plugin_setting`` prüfen und feststellen, ob es mit der
Logik interagieren soll. Der folgende Code könnte genutzt werden, um einen Callback für die Logik einzurichten:

.. code-block:: python

    if 'some_plugin_setting' in logic.conf:
        return self.run_logic
    else:
        return None


----

.. code-block:: python

    def update_item(self, item, caller=None, source=None, dest=None):


Diese Funktion wird jedes mal aufgerufen, wenn sich der Wert eines Items ändert,
für das der Aufruf in ``parse_item()`` eingerichtet wurde. Sie erhält die folgenden Parameter:

`caller`
    Dieser String gibt an, wer das Item geändert hat. Der Wert kann z.B. "KNX", wenn der Wert des Items vom KNX-Plugin gesetzt wurde.

`source`
    …

`dest`
    …


----

Erstellung eines Webinterfaces
------------------------------

Die Datei ``dev/sample_plugin/webif/templates/index.html`` sollte als Grundlage für Webinterfaces genutzt werden.
Um Tabelleninhalte nach Spalten filtern und sortieren zu können, muss der entsprechende Code Block mit Referenz
auf die relevante Table ID eingefügt werden (siehe Doku).

SmartHomeNG liefert eine Reihe Komponenten von Drittherstellern mit, die für die Gestaltung des Webinterfaces
genutzt werden können. Erweiterungen dieser Komponenten usw. finden sich im Ordner ``/modules/http/webif/gstatic``.

Wenn das Plugin darüber hinaus noch Komponenten benötigt, werden diese im Ordner ``webif/static`` des Plugins abgelegt.

----

.. code-block:: python

    def run_logic(self, logic, caller=None, source=None, dest=None):    # (version>=1.3)


Diese Funktion ist analog zu ``update_item()``, nur dass sie bei der Ausführung von Logiken aufgerufen wird.


Neben diesen vordefinierten Funktionen können auch eigene Funktionen erstellt werden, die Funktionen im Plugin ausführen.


Funktionen von SmartHomeNG
==========================


Der Scheduler
-------------

Der Scheduler ist eine der wichtigsten Komponenten von SmartHomeNG.
Es ist die zentrale Uhr, die Funktionen zu bestimmten Zeiten aufruft.
Damit eigene Funktionen ausgeführt werden, müssen diese dem Scheduler bekannt gemacht werden.
Dies erfolgt durch den Aufruf spezieller Funktionen.
Der Scheduler ist Teil von SmartHomeNG, also muss er über die Variable angesprochen werden,
die an die ``__init__``-Funktion des Plugins übergeben wurde.

Die wichtigste Funktion ist `add`:

`scheduler_add`
~~~~~~~~~~~~~~~

.. code-block:: python

    self.scheduler_add('name',
                       obj,
                       prio=3,
                       cron=None,
                       cycle=None,
                       value=None,
                       offset=None,
                       next=None)


``scheduler_add`` fügt dem Scheduler einen Eintrag hinzu. Es müssen mindestens ``name``,
``object`` und einer der Timing-Parameter übergeben werden.


`name=string`
^^^^^^^^^^^^^
Das ist der Name, der diesem Scheduler-Eintrag gegeben wird. Er wird benötigt, um den Scheduler-Eintrag zu verändern oder zu löschen.


`obj=function`
^^^^^^^^^^^^^^
``obj`` ist eine Funktion, die im Plugin definiert wird (ein sogenannter Callback).
Diese Funktion wird vom Scheduler aufgerufen. Wenn die Funktion Parameter benötigt,
können diese mit ``**kwargs`` übergeben werden (siehe weiter unten in der Beschreibung der Parameter).


`cron`
^^^^^^
…


`cycle=int`
^^^^^^^^^^^
``cycle`` ist eine Ganzzahl in Sekunden. Damit wird der Scheduler angewiesen,
die Funktion ``obj`` alle ``cycle`` Sekunden aufzurufen.
Wenn das Intervall auf 60 gesetzt wird, ruft der Scheduler die Funktion alle 60 Sekunden auf, so lange SmartHomeNG läuft.

`next=dateobject`
^^^^^^^^^^^^^^^^^
``next`` fordert die einmalige Ausführung von ``obj`` zu dem Zeitpunkt an, der als Argument übergeben wird.
Das Argument ist ein ``dateobject``, das z.B. mit ``datetime`` erstellt werden kann:

.. code-block:: python

    nd = datetime.strptime('Jan 14 2015 8:09PM','%b %d %Y %I:%M%p').replace(tzinfo=self._sh.tzinfo())


.. important ::
   Die Zeitzone muss im ``datetime``-Objekt mit angegeben werden, ansonsten kann der Scheduler abstürzen. Im Beispiel wird die Zeitzone von SmartHomeNG benutzt.

`value`
^^^^^^^
Mit dem Parameter ``value`` können Argumente an die Funktion ``obj`` übergeben werden, wenn der Scheduler sie aufruft. Dies ist eine List von `keyword=value`-Wertpaaren. Diese können wie folgt definiert werden:

.. code-block:: python

    _bla(self, **kwargs):
        if 'heinz' in kwargs:
            logger.info("found")
            em = kwargs['heinz']


In dem Fall sollte der Scheduler mit einer Werteliste aufgerufen werden:

.. code-block:: python

    self.scheduler.add('name',
                        self._bla,
                        value={'heinz': bla, 'tom': 10},
                        next=_ndate)


..warning::

   Werte können über den Scheduler nur weitergegeben werden, wenn dieser mit dem Parameter ``next`` für eine einmalige Ausführung aufgerufen wird. Für eine periodische Ausführung können keine Argumente übergeben werden.

`offset=int`
^^^^^^^^^^^^
Wenn eine periodische Ausführung mit ``cycle`` angefordert wurde, wird die erste Ausführung um ``offset`` Sekunden verzögert. Wenn z.B. ein `cycle=10` und `offset=20` gesetzt wurde, dann wird die erste Ausführung 20 Sekunden nach Abschluss der Initialisierung erfolgen und jede weitere jeweils 10 Sekunden später.

Wenn ``offset`` nicht definiert oder auf 0 gesetzt wird, legt SmartHomeNG einen Zufallswert zwischen 10 und 15 Sekunden fest.


`scheduler_remove`
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    self.scheduler_remove(name)


Diese Funktion löscht den mit ``name`` bezeichneten Eintrag aus dem Scheduler.

`Name=string`
^^^^^^^^^^^^^
Der Name der Schedulereintrags als String.


Items suchen
------------

.. code-block:: python

    sh.return_item(item_path)


``return_item`` gibt das Item mit dem Pfad ``item_path`` zurück.

`item_path=string`
~~~~~~~~~~~~~~~~~~
Der Pfad des Items, wie er in der Item Konfiguration festgelegt ist, z.B. Ebene1.Raum4.Lampe2
Die Funktion gibt das Item-Objekt zurück, welches aufgerufen werden kann,
um den Wert zu lesen oder zu ändern oder auf andere Eigenschaften zuzugreifen.


Items verändern
---------------

.. code-block:: python

    item(value, caller)


`value`
~~~~~~~

Der Wert, der dem Item zugewiesen werden soll. Für boolesche Items ist dies ``True`` oder ``False``.

`caller=string`
~~~~~~~~~~~~~~~
Ein selbst gewählter Name, der denjenigen identifiziert, der das Item verändert hat. Dieses Argument wird an die Funktion ``update_item`` übergeben.

